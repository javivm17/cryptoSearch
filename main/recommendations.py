from .models import *
from collections import Counter
import shelve
from django.contrib.auth import get_user_model

def load_similarities():
    shelf = shelve.open('dataRS.dat')
    crypto_tags = tags_by_crypto()
    user_tags = top_tags_by_user(crypto_tags)
    shelf['similarities'] = compute_similarities(crypto_tags, user_tags)
    shelf.close()

def recommend_cryptos(user):
    shelf = shelve.open("dataRS.dat")
    #conjunto de artistas que ya ha escuchado el usuario, que no se consideran para recomendar
    listened = set()
    listened = set(a.crypto.name for a in UsuarioCrypto.objects.filter(user=user))
    res = []
    for crypto_name, score in shelf['similarities'][user.username]:
        if crypto_name not in listened:
            crypto_name = Crypto.objects.get(name=crypto_name).name
            res.append([crypto_name, 100 * score])
    shelf.close()
    return res

def tags_by_crypto():
    cryptos = {}
    for element in Crypto.objects.all():
        crypto_name = element.name
        labels = element.labels.split(',')
        cryptos.setdefault(crypto_name, [])
        #append to crypto name all elemets in labels
        cryptos[crypto_name].extend(labels)
    return cryptos

def top_tags_by_user(crypto_tags):
    users_tags = {}
    User = get_user_model()
    users = User.objects.all()
    for element in users:
        user_name = element.username
        cryptos= UsuarioCrypto.objects.filter(user=element)
        tag_freq= {}
        for crypto in cryptos:
            tags = crypto_tags[crypto.crypto.name]
            for tag in tags:
                tag_freq.setdefault(tag, 0)
                tag_freq[tag] += 1
        users_tags[user_name] = Counter(tag_freq).most_common(10)
    return users_tags

def compute_similarities(crypto_tags, user_tags):
    res = {}
    for u in user_tags:#Recorre todas las criptos con sus tags-> crypo:[tag1, tag2, tag3]
        top_cryptos = {}
        for c in crypto_tags:
            usertags=set([a[0] for a in user_tags[u]])
            top_cryptos[c] = dice_coefficient(usertags, crypto_tags[c])
        res[u] = Counter(top_cryptos).most_common(100)
    return res

def dice_coefficient(set1, set2):
    return 2 * len(set(set1).intersection(set(set2))) / (len(set1) + len(set2))