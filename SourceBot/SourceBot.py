import urllib
import requests
from bs4 import BeautifulSoup
import re

user='Vlaedr'
passw='Alextall007'
baseurl='http://wikipast.epfl.ch/wikipast/'
summary='Wikipastbot update'


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


fullbios = ''
name = 'Biographies'
result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
soup=BeautifulSoup(result.text, "lxml")
code=''
for primitive in soup.findAll("text"):
    code+=primitive.string
fullbios = code


protected_logins=["Frederickaplan","Maud","Vbuntinx","Testbot","SparqlBot","IB","SourceBot","PageUpdaterBot","Orthobot","BioPathBot","ChronoBOT","Amonbaro","AntoineL","AntoniasBanderos","Arnau","Arnaudpannatier","Aureliver","Brunowicht","Burgerpop","Cedricviaccoz","Christophe","Claudioloureiro","Ghislain","Gregoire3245","Hirtg","Houssm","Icebaker","JenniCin","JiggyQ","JulienB","Kl","Kperrard","Leandro Kieliger","Marcus","Martin","MatteoGiorla","Mireille","Mj2905","Musluoglucem","Nacho","Nameless","Nawel","O'showa","PA","Qantik","QuentinB","Raphael.barman","Roblan11","Romain Fournier","Sbaaa","Snus","Sonia","Tboyer","Thierry","Titi","Vlaedr","Wanda"]
depuis_date='2017-05-02T16:00:00Z'

#pages created by Bots or people in the class but not the ones like Fichier:Annonce biopath.png
liste_pages=[]
for user in protected_logins:
    result=requests.post(baseurl+'api.php?action=query&list=usercontribs&ucuser='+user+'&format=xml&ucend='+depuis_date)
    soup=BeautifulSoup(result.content,'lxml')
    for primitive in soup.usercontribs.findAll('item'):
        if primitive['title'][:7] != 'Fichier':
            liste_pages.append(primitive['title'])
        
#pages not to be considered.
bad_pages_list = ['Accueil', 'Bots','HypermotBot', 'OrthoBot', 'SourceBot','VandalBot','PageUpdaterBot', 'BioPathBot', 'SPARQLBot','InferenceBot/CheckerBot','LinkBot','CheckerBot', 'InferenceBot', 'MiningBot','Chronobot', 'ChronoBot', 'ImageBot','FormatBot', 'TangoBot']
liste_pages_correct = list(set(liste_pages) - set(bad_pages_list))
for p in liste_pages_correct:
    print(p)
         

allnames = []
for p in liste_pages_correct :
    allnames.append(p)
pattern = '\* ?\[\[([^\]]*)\]\].*'
p = re.compile(pattern)
bioNames = fullbios.split('\n')
for c in bioNames:
  tk = c.split('\n')
  for t in tk:
    if t:
        match = p.match(t)
        if match:
            allnames.append(match.group(1))
            

fullCode = []
for name in allnames:
    result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
    soup=BeautifulSoup(result.text, "lxml")
    code=''
    for primitive in soup.findAll("text"):
        if primitive.string :
            code += primitive.string
    if code :
        print(name)
        fullCode.append((code, name))


# the argument is the plain text of the page
# this fonction returns a tuple:
# first element is a boolean: true if all entries are sourced
#       false if sources are missing
# second element is a list of : (modification) all dates where the source is wrong.
#int: all the bad lines indexes
def findBadPage(pageText):
    # get all the lines
    tokens = []
    tk = pageText.split('\n')
    for t in tk:
        if t:
            if t[0] == '*':
                tokens.append(t)
       
    #check if line is sourced
    r = '\*.*\[https?:\/\/w?w?w?\.?letemps[^\]]*\].*'
    p = re.compile(r)
    dates_isolator_expr = ['\* \[\[(.*)\]\] \/', '\*\[\[(.*)\]\]\:', '\*\[\[(.*)\]\]\/', '\*\[\[(.*)\]\] \/']
    index = 0
    allSourced = True
    wrongDatesSources = []
    
    for t in tokens:
        match = p.match(t)
        if not match:
            allSourced = False
            count = 0;
            didmatch = False
            for i in dates_isolator_expr :
                count +=1
               
                d = re.compile(i)
                match = d.match(t)
                if match:
                    didmatch = True
                    wrongDatesSources.append(match.group(1))
            if not didmatch :
                wrongDatesSources.append('false source at line: ' + str(index))
                otherSource = '\*.*\[(https?:\/\/.*)\].*'
                pOth = re.compile(otherSource)
                match = pOth.match(t)
        index +=1
    return (allSourced, wrongDatesSources)


content = '\n'
content += 'Cette page liste toutes les biographies ayant des entrées non sourcées.'
content +=  '\n==Bad page==\n'

badpage = []
wrongDatesSources = []
ok =True
for (c, name) in fullCode:
    (ok, wrongDatesSources) = findBadPage(c)
    if not ok:
        badpage.append(name)
        content += name
        content += '\n The wrong entries in this page are the sources with the following dates: ' 
        content += str(wrongDatesSources) 
        content += '\n\n'


'''content = '\n'
content += 'Cette page liste toutes les biographies ayant des entrées non sourcées.'
content +=  '\n==Bad page=='
content += '\n[[' + badpage[0] + ']]' '''
payload = {'action':'edit','assert':'user','format':'json','utf8':'','text':content,
           'summary':summary,'title':'FactChecking','token':edit_token}
r4=requests.post(baseurl+'api.php',data=payload,cookies=edit_cookie)
