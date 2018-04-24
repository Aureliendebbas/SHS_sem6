# -*- coding: utf-8 -*-
#return a list of str containing all the name of wikipast page, without the one beginin with "Fichier:" or the one beginin with 4 number (ex:"1945")
#only pages changed by user in the "whiteliste.txt" and done AFTER the date write in "lastdate.txt" are given
#to change the "lastdate.txt", please put those line where needed :
#if needed, it strated with "2017-02-05T16:00:00Z"


import requests
from bs4 import BeautifulSoup

def select_page():
    baseurl='http://wikipast.epfl.ch/wikipast/'

    fichier=open('whiteliste.txt', 'r')
    protected_logins=fichier.read()
    fichier.close()
    protected_logins=protected_logins.split('\n')
    protected_logins=protected_logins[:(len(protected_logins)-1)]

    fichier=open('lastdate.txt', 'r')
    depuis_date=fichier.read()
    fichier.close()
       

    liste_pages=[]
    for user in protected_logins:
        result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend='+depuis_date)
        soup=BeautifulSoup(result.content,'html.parser')
        for primitive in soup.usercontribs.findAll('item'):
            title=primitive['title']
            if title[0:8]!='Fichier:':
                if not title[0:3].isnumeric():
                    liste_pages.append(title)

    liste_pages=list(set(liste_pages))
    return liste_pages
