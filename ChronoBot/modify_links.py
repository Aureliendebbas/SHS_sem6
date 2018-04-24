
'''
cette fonction prend en input le nom d'une page.
Pour toutes les dates de type [[AAAA/MM/JJ]], elle crée le
lien de redirection vers la page de l'année.
Pour les dates de type [[AAAA]] elle ne fait
rien puisqu'elles sont déjà un lien vers l'année
'''
import requests
from bs4 import BeautifulSoup
from retrieve_content import retrieve_content

months=["Janvier","F.C3.A9vrier","Mars","Avril","Mai","Juin","Juillet","Ao.C3.BBt","Septembre","Octobre","Novembre","D.C3.A9cembre"]

def modify_links(page_name):
    ###############
    ###############
    #retrieve dates
    text=retrieve_content(page_name)
    text=text.split("\n")
    dates=[]
    for line in text:
        d_start=line.find("[[")
        if (d_start!=-1) and line[d_start+2:d_start+6].isnumeric():
            d_start=d_start+2
            d_end=line[d_start:].find("]]")+d_start
            date=line[d_start:d_end]
            if len(date)!=4:
                dates.append(date)

    ###############
    ###############
    #create pages with redirection code
    user = "ChronoBOT"
    passw = "sajas2017"
    baseurl='http://wikipast.epfl.ch/wikipast/'
    summary='ChronoBOT page creation'

    # Login request
    payload={'action':'query','format':'json','utf8':'','meta':'tokens','type':'login'}
    r1=requests.post(baseurl + 'api.php', data=payload)

    #login confirm
    login_token=r1.json()['query']['tokens']['logintoken']
    payload={'action':'login','format':'json','utf8':'','lgname':user,'lgpassword':passw,'lgtoken':login_token}
    r2=requests.post(baseurl + 'api.php', data=payload, cookies=r1.cookies)

    #get edit token2
    params3='?format=json&action=query&meta=tokens&continue='
    r3=requests.get(baseurl + 'api.php' + params3, cookies=r2.cookies)
    edit_token=r3.json()['query']['tokens']['csrftoken']

    edit_cookie=r2.cookies.copy()
    edit_cookie.update(r3.cookies)

    for date in dates:
        year=date[:4]
        if(int(date[5:7])<13):
            month=months[int(date[5:7])-1]
            content="#REDIRECT [["+year+"#"+month+"]]"
        else:
            content="#REDIRECT [["+year+"]]"
    
        # save action
        payload={'action':'edit','assert':'user','format':'json','utf8':'','text':content,'summary':summary,'title':date,'token':edit_token}
        r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
