from bs4 import BeautifulSoup
import ssl
import urllib.request
import re
from urllib.request import Request

def get_coin_data():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    base_url = 'https://coinmarketcap.com'
    r = urllib.request.urlopen(
        base_url, context=ssl_context)

    soup = BeautifulSoup(r.read().decode("utf-8"), "html5lib")
    div = soup.find("table", {'class': 'cmc-table'}).tbody
    items = div.find_all("tr")
    data=[]
    for item in items:
        uri=""
        tds = item.find_all("td")
        if tds[2].div != None:     
            precio= tds[3].div.a.string.replace("$","").replace(",","")
            uri=base_url+str(tds[2].div.a["href"])
        else:
            precio = str(tds[3].span.text).replace("$","").replace(",","")
            uri=base_url+str(tds[2].a["href"])
        retry=True
        while retry:
            try:
                r2 = urllib.request.urlopen(uri, context=ssl_context)
                soup_item = BeautifulSoup(r2.read().decode("utf-8"), "html5lib")
                retry = False
            except:
                retry=True
        nombre= re.search(">(.*)<small",str(soup_item.find("div", {'class': 'nameHeader'}).h2)).group(1)
        simbolo = soup_item.find("div", {'class': 'nameHeader'}).h2.small.string
        url_img = soup_item.find("img", {'alt': simbolo})['src']
        capitalizacion = soup_item.find("div", {'class': 'statsValue'}).string.replace("$","").replace(",","")
        descripcion = soup_item.find("div", {'class': 'contentClosed'})
        etiquetas =""
        div_categorias = soup_item.find("div", {'class':'sc-16r8icm-0 sc-10up5z1-1 gGKCJe'})
        if div_categorias != None:
            div_categorias = div_categorias.ul.find_next("ul")
            etiquetas_ls = div_categorias.find_all("a", {'class':'cmc-link'})
            if len(etiquetas_ls)==0:
                etiquetas_ls = div_categorias.find_all("div", {'class':'tagBadge'})
            cont=0
            for etiqueta in etiquetas_ls:
                if cont==0:
                    etiquetas=etiqueta.string
                else:
                    etiquetas += (","+etiqueta.string)
                cont+=1
        if descripcion != None:
            descripcion = descripcion.text
        else:
            descripcion = soup_item.find("div", {'class': 'seo-accordion-section collapsed'}).text
        data.append([nombre,simbolo,precio,capitalizacion,descripcion,etiquetas,url_img])
    return data
    

def get_fear_and_greed_index():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    r = urllib.request.urlopen(
        "https://alternative.me/crypto/fear-and-greed-index/", context=ssl_context)
    soup = BeautifulSoup(r.read().decode("utf-8"), "html5lib")
    div = soup.find("div", {'class': 'fng-value'})
    index_without_format = div.find("div", {'class': 'status'}).string
    index_value = div.find("div", {'class': 'fng-circle'}).string
    return (index_without_format, index_value)

def get_upcoming_icos():
    base_url = Request('https://icodrops.com/category/upcoming-ico/', headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(base_url)

    soup = BeautifulSoup(r.read().decode("utf-8"), "html5lib")
    div = soup.find_all("div", {'class': 'ico-main-info'})[:50]
    data=[]
    for ico in div:
        name = ico.h3.a.string
        url_ico = ico.h3.a["href"]
        url = Request(url_ico, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(url)
        soup_ico = BeautifulSoup(r.read().decode("utf-8"), "html5lib")
        icon_url = soup_ico.find("div", {'class': 'ico-icon'}).img["src"]
        date= soup_ico.find("i", {'class': 'fa fa-calendar'}).find_next("h4").string.split("\n")[2]
        desc = soup_ico.find("div", {'class': 'ico-description'}).text.split("\n")[1]
        try:
            video = soup_ico.find("iframe")["src"]
        except:
            video = None
        data.append((name,icon_url,date,desc,video))
    return data
   


