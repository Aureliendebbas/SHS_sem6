'''
cette fonction prend en input une année, et crée un site en blanc
pour cette année
Si le site existe déjà, il ne fait rien
'''
import requests

def create_site(year):
    #check if year is a four digit number
    year=str(year)
    if(len(year)!=4)or not(year.isnumeric()):
        
        return
    
    user = "ChronoBOT"
    passw = "sajas2017"
    baseurl='http://wikipast.epfl.ch/wikipast/'
    summary='ChronoBOT page creation'

    #check if page already exists
    if(requests.get('http://wikipast.epfl.ch/wikipast/index.php/'+year)).status_code!=404:
        
        return

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

    content=""
    
    # save action
    payload={'action':'edit','assert':'user','format':'json','utf8':'','text':content,'summary':summary,'title':year,'token':edit_token}
    r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
