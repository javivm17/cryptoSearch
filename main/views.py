from django.shortcuts import render
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser,MultifieldParser
import os
import shutil
from .scrapping_criptos import *
import sys
from .forms import *
from .models import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.conf import settings
from .recommendations import *
from datetime import datetime


# Create your views here.
def index(request):
    try:
        if request.user.is_authenticated:
            rec = recommend_cryptos(request.user)[:4]
            rec_cryptos=[]
            for r in rec:
                rec_cryptos.append(Crypto.objects.get(name=r[0]))
            return render(request, 'index.html', {'rec_cryptos':rec_cryptos})
    except(Exception):
        return render(request,'index.html')
    return render(request,'index.html')

@login_required(login_url='/login')
def charge_index(request):
    #Check if user is superuser
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    else:
        sys.setrecursionlimit(100000000)

        if os.path.exists("Schema"):
            shutil.rmtree("Schema")
        os.mkdir("Schema")

        s = Schema(name=ID(unique=True, stored=True), abv=TEXT(stored=True), desc=TEXT(stored=True), url_img=TEXT(stored=True), marketcap = TEXT(stored=True), labels = TEXT(stored=True), price = TEXT(stored=True))
        ix = create_in("Schema", s)
        writer = ix.writer()
        data = get_coin_data()

        Crypto.objects.all().delete()

        for item in data:
            writer.add_document(name=item[0], abv=item[1], desc=item[4], url_img=item[6], marketcap=str(item[3]), labels=item[5], price=str(item[2]))
            crypto= Crypto.objects.create(name=item[0], abv=item[1],labels=item[5], img_url=item[6])
            crypto.save()
        writer.commit()

        Ico.objects.all().delete()
        icos = get_upcoming_icos()
        for ico in icos:
            Ico.objects.create(name=ico[0], icon_url=ico[1], date=ico[2], desc=ico[3], url_vid= ico[4]).save()

        return render(request, 'index.html')

@login_required(login_url='/login')
def charge_rs(request):
    #Check if user is superuser
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    else:
        load_similarities()
        #Redirect to /index 
        return HttpResponseRedirect('/')

def search_by_desc(request):
    formulario = DescrForm()
    desc = None
    results_ = []
    cryptos = Crypto.objects.all()
    for c in cryptos:
        if request.user.is_authenticated:
            usuario_crypto = UsuarioCrypto.objects.filter(user=request.user, crypto=c)
            if usuario_crypto:
                guardada = True
            else:
                guardada = False
        else:
            guardada = None
        results_.append((c.name, c.abv, "", c.img_url,guardada))

    if request.method == 'POST':
        formulario = DescrForm(request.POST)
        if formulario.is_valid():
            desc = formulario.cleaned_data['desc']
            min_mc = formulario.cleaned_data['min_mc']
            max_mc = formulario.cleaned_data['max_mc']
            ix = open_dir("Schema")
            s = ix.searcher()
            query = MultifieldParser(["name","desc"], ix.schema)
            results = s.search(query.parse(desc), limit=None)
            results_ = []
            for i in results:
                CLEANR = re.compile('<.*?>')
                if request.user.is_authenticated:
                    usuario_crypto = UsuarioCrypto.objects.filter(user=request.user, crypto=Crypto.objects.get(name=i['name']))
                    if usuario_crypto:
                        guardada = True
                    else:
                        guardada = False
                else:
                    guardada = None
 
                if (min_mc and max_mc):
                   if(float(min_mc) <= float(i['marketcap'])and (float(max_mc) >= float(i['marketcap']))):
                        c_result = (i['name'], i['abv'], re.sub(CLEANR, '', "..."+i.highlights("desc")+"..."),i['url_img'],guardada, i['marketcap'],i['labels'],i['price'],i['desc'])#delete html tags
                        results_.append(c_result)
                elif(min_mc and not max_mc): 
                    if(float(min_mc) <= float(i['marketcap'])):
                        c_result = (i['name'], i['abv'], re.sub(CLEANR, '', "..."+i.highlights("desc")+"..."),i['url_img'],guardada,i['marketcap'],i['labels'],i['price'],i['desc'])
                        results_.append(c_result)
                elif(not min_mc and max_mc):
                    if(float(max_mc) >= float(i['marketcap'])):
                        c_result = (i['name'], i['abv'], re.sub(CLEANR, '', "..."+i.highlights("desc")+"..."),i['url_img'],guardada,i['marketcap'],i['labels'],i['price'],i['desc'])
                        results_.append(c_result)
                else:
                    c_result = (i['name'], i['abv'], re.sub(CLEANR, '', "..."+i.highlights("desc")+"..."),i['url_img'],guardada,i['marketcap'],i['labels'],i['price'],i['desc'])
                    results_.append(c_result)
                       
            

                

    return render(request, 'search_desc.html', {'formulario':formulario, 'desc':desc, 'results':results_, 'desc':True})

def fear_and_greed(request):
    today = datetime.today().strftime('%Y-%m-%d')
    history = FearGreed.objects.all().order_by('-date')[:8]
    fear_greed= history[0]
    
    return render(request, 'fear_and_greed.html', {'data':(fear_greed.name,fear_greed.index, today),'historial':history})


def ingresar(request):
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/'))
    formulario = AuthenticationForm()
    if request.method=='POST':
        formulario = AuthenticationForm(request.POST)
        usuario=request.POST['username']
        clave=request.POST['password']
        acceso=authenticate(username=usuario,password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return (HttpResponseRedirect('/'))
            else:
                return render(request, 'ingresar.html',{'formulario':formulario,'error':"Usuario no activo",'STATIC_URL':settings.STATIC_URL})
        else:
            return render(request, 'ingresar.html',{'formulario':formulario,'error':"Usuario o contraseña incorrectos",'STATIC_URL':settings.STATIC_URL})
                     
    return render(request, 'ingresar.html', {'formulario':formulario,'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/login')
def cerrar_sesion(request):
    logout(request)
    return(HttpResponseRedirect('/'))

def registro(request):
    if request.user.is_authenticated:
        return(HttpResponseRedirect('/'))
    formulario = UserCreationForm()
    if request.method=='POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/login')
    return render(request, 'registro.html', {'formulario':formulario,'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/login')
def save_crypto(request, crypto_name):
    data = Crypto.objects.get(name=crypto_name)
    user = request.user
    UsuarioCrypto.objects.create(user=user, crypto=data).save()
    favs = UsuarioCrypto.objects.filter(user=user)
    cryptos=[]
    for crypto in favs:
        cryptos.append(crypto.crypto)
    return render(request, 'favoritos.html', {'mensaje' : "Se ha guardado "+crypto_name+" en favoritos",'data':cryptos})

@login_required(login_url='/login')
def delete_favorite(request,crypto_name):
    data = Crypto.objects.get(name=crypto_name)
    user = request.user
    UsuarioCrypto.objects.filter(user=user, crypto=data).delete()
    favs = UsuarioCrypto.objects.filter(user=user)
    cryptos=[]
    for crypto in favs:
        cryptos.append(crypto.crypto)
    return render(request, 'favoritos.html', {'mensaje' : "Se ha eliminado "+crypto_name+" de favoritos",'data':cryptos})

@login_required(login_url='/login')
def favoritos(request):
    user = request.user
    favs = UsuarioCrypto.objects.filter(user=user)
    cryptos=[]
    for crypto in favs:
        cryptos.append(crypto.crypto)
    return render(request, 'favoritos.html', {'data':cryptos})

def upcoming_icos(request):
    icos = Ico.objects.all()
    return render(request, 'ico_list.html', {'data':icos})