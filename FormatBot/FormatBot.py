# -*- coding: utf-8 -*-

import urllib
import requests
from bs4 import BeautifulSoup

user="formatbot"
passw='accjjlms'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'

protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","IB","SourceBot","Formatbot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
depuis_date='2017-05-02T16:00:00Z'

liste_pages=[]
for user1 in protected_logins:
    result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user1+'&format=xml&ucend='+depuis_date)
    soup=BeautifulSoup(result.content,'lxml')
    for primitive in soup.usercontribs.findAll('item'):
        liste_pages.append(primitive['title'])
        #print(primitive['title'])

liste_pages=list(set(liste_pages))
names=liste_pages

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

    
#fonction qui détecte le début d'une ligne et retourne l'indice du premier caractere apres '*'
def line_start_detect(code):
    line_index_lst=[]
    for i in range(len(code)):
        if (code[i]=='\n'):
            line_index_lst.append(i+2)
    line_index_lst.append(len(code))
    return line_index_lst

def hypertext(code, line_index1, line_index2):
    hypermot_lst=[]
    for i in range(line_index1, line_index2):
        if (code[i]== '[' and code[i+1]=='['):
            j=0
            while code[i+j]!=']' and code[i+j+1]!= ']':
                j+=1
            hypermot=''
            for k in range(i+2,i+j+1):
                hypermot+=code[k]
            hypermot_lst.append(hypermot)
            j=0
            i=i+j+2
    return hypermot_lst

def is_number(char):
    if(char=='0' or char=='1' or char=='2' or char=='3' or
       char=='4' or char=='5' or char=='6' or char=='7' or
       char=='8' or char=='9'):
        return True
    else :
        return False


#decode l'hypermot
#retourne s'il s'agit d'une date, si le format est correct, et le vecteur de date
#sortie : [is_date, (bool) est-ce que cet hypermot peut etre vu comme une date ?
#          date_format_correct, (bool) le format de date est-il respecte ?
#          date_format, (int) 1:aaaa    2:aaaa.mm    3:aaaa.mm.jj
#          ['aaaa','mm','jj']  ]   vecteur de la date interpretee
#Si is_date est False, le vecteur de date et data_format_correct sont incorrects
def date_decode(hypermot):
    date_format_correct=True
    is_date=True
    date_format=0;
    accepted_separator = ['.','-','. ',' .',' . ',',','/','\ ','_','pizza']
    temp_bool_separator_in_lst = False

    year_index=-1
    month_index=-1
    day_index=-1

    #cree si possible la liste des annee/mois/jours, et les listes des séparateurs
    number_lst=['']
    num_index=0
    separator_index_lst=[]
    separator_lst=[]
    sep_index=-1
    boo=False
    for i in range(len(hypermot)):
        if is_number(hypermot[i]):
            boo=True
    if boo==False:  
        return [False, False, 0,[]]
            
    if not is_number(hypermot[0]):
        if hypermot[0]== ' ':
            date_format_correct=False
            if not is_number(hypermot[1]): #un espace accepté mais pas deux
                is_date=False
                return [is_date,date_format_correct,date_format,number_lst]
        else:
            is_date=False
            return [is_date,False,0,[]]
    else:
        number_lst[num_index]+=hypermot[0]
            
    for i in range(1,len(hypermot)):
        if not is_number(hypermot[i]):
            if is_number(hypermot[i-1]):
                num_index+=1
                number_lst.append('')
                sep_index+=1
                separator_lst.append(hypermot[i])
            else:
                separator_lst[sep_index]+=hypermot[i]
                
            separator_index_lst.append(i)
        else:
            number_lst[num_index]+=hypermot[i]

    #test de la validite des separateurs
    for i in range(len(separator_lst)):
        if separator_lst[i]!='.':
            date_format_correct=False
    if len(separator_lst)>2:
        date_format_correct=False
        if len(separator_lst)!=3 or separator_lst[2]!=' ':
            is_date=False
    for i in range(len(separator_lst)):
        temp_separator_in_lst = False
        for j in range(len(accepted_separator)):
            if separator_lst[i]== accepted_separator[j]:
                temp_bool_separator_in_lst = True
        if not temp_bool_separator_in_lst:
            is_date=False
    
    #test de la validite de la date, classification du format de date
    if len(number_lst)==4: 
        if number_lst[3]=='':
            date_format=3
    elif len(number_lst)<1 or len(number_lst)>3:
        is_date=False
        date_format_correct=False
    else:
        date_format=len(number_lst)

    #print(number_lst)
    
    for i in range(date_format): #detection de l'annee dans la liste
        if(len(number_lst[i])==3 or len(number_lst[i])==4):
            if(year_index !=-1): #s'il y a au moins deux nombres à 3 ou 4 chiffres
                is_date=False
                date_format_correct=False
            year_index=i
    #print(year_index)

    if year_index==-1: #si aucune annee n'a ete trouvee
        is_date=False
        date_format_correct=False
        return [is_date,date_format_correct,date_format,number_lst,'pas trouve year']

    if date_format==3:
        if year_index==0:
            day_index=2
            month_index=1
        elif year_index==2:
            day_index=0
            month_index=1
            date_format_correct = False
        else:
            is_date=False
            date_format_correct=False
            return [is_date,date_format_correct,date_format,number_lst]
        
        if (int(number_lst[month_index])>12 or int(number_lst[month_index])<0 or
            int(number_lst[day_index])>31 or int(number_lst[day_index])<0):
            is_date=False
            date_format_correct=False
            return [is_date,date_format_correct,date_format,number_lst]         

    if date_format==2:
        if year_index==0:
            month_index=1
        else:
            month_index=0
        if ( int(number_lst[month_index])>12 or int(number_lst[month_index])<0 ):
            is_date=False
            date_format_correct=False
            return [is_date,date_format_correct,date_format,number_lst]

    if int(number_lst[year_index])>2050:
        is_date=False
        date_format_correct=False

    if date_format==1:
        date_final=[ number_lst[year_index] ]
    if date_format==2:
        date_final=[number_lst[year_index],number_lst[month_index]]

    if date_format==3:
        date_final=[number_lst[year_index],number_lst[month_index], number_lst[day_index]]
        


    #rmq: separator_index_lst et separator_lst sont retournes uniquement pour la phase de debugging
    return [is_date,date_format_correct,date_format,date_final,separator_index_lst,separator_lst]
            
            

def date_format(decode_lst):
    date_temp="" 
 
    for i in range(0,decode_lst[2]) :
        if i<(decode_lst[2]-1):
            date_temp+=decode_lst[3][i]+decode_lst[5][i]
        else :
            date_temp+=decode_lst[3][i]

    char_lst=decode_lst[5]        
    for c in char_lst :
        date_temp=date_temp.replace(c,".")
        
    date_final=date_temp.replace(" ","")
    return date_final

## fonction qui reçoit en argument le code wiki complet la date à modifier et la date formatée
## la fonction ne retourne rien et écrit directement sur la page wiki
def wiki_write(code,old_date,new_date,name):

    new_code = []
    new_code = code.replace(old_date,new_date)
    payload={'action':'edit','assert':'user','format':'json','utf8':'','text':new_code,'summary':summary,'title':name,'token':edit_token}
    r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
    print(r4.text)
    print('Modification dans '+name+', '+old_date+' remplacé par '+new_date)
    return new_code

def barre_detect(hypermot):
    barre=False
    syntax_part=""
    for i in range(len(hypermot)) :
        if hypermot[i]== "|" :
            barre=True
            for k in range(i+1, len(hypermot)) :
                syntax_part+=hypermot[k]
    if barre==False :
        syntax_part=hypermot
    return[barre,syntax_part]
        

for name in names:
    if(name != "FormatBot"):
        result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
        soup=BeautifulSoup(result.text, "lxml")
        #soup=BeautifulSoup(result.text)
        code=''
        print(name)
        for primitive in soup.findAll("text"):
            if isinstance(primitive.string,str):
                code+=primitive.string

        line_index_lst=line_start_detect(code)
        a=hypertext(code, line_index_lst[0], line_index_lst[len(line_index_lst)-1])
        for i in range(len(a)):
            barre=barre_detect(a[i])
            b=date_decode(barre[1])
            if (b[0]==1 and b[1]==0) :
                date_final=date_format(b)
            
                code = wiki_write(code,barre[1],date_final,name)