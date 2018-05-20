import re
import sys
import urllib
import requests
import json
import hashlib
from bs4 import BeautifulSoup

baseurl = 'http://wikipast.epfl.ch/wikipast/'
content = '==GraderBot Report==\n'

def tokenizepage(pagetext) :
    tokens = []
    tk = pagetext.split('\n')
    ignore = False
    for t in tk:
        if t:
            if "==" in t:
                if "Biographie" in t:
                    ignore = False
                else:
                    ignore = True
            if (t[0] == '*') and not ignore:
                tokens.append(t)
    return tokens


def checkpage(pagetext):
    text = fetchPageData(pagetext)
    tokens = tokenizepage(text)
    grade = 6.0

    grade -= checkentries(tokens)

    if len(tokens) <= 10:
        return 0.0

    if checksource(tokens) > 0:
        grade -= 0.5

    if not checklinkpages(tokens, pagetext) :
        grade -= 0.5

    grade -=  checkformat(tokens)

    if not checkhyperwords(tokens) :
        grade -= 0.5



    return max(grade, 0)


def checksource(tokens):
    r = '\*.*\[https?:\/\/w?w?w?\.?letemps[^\]]*\].*'
    p = re.compile(r)
    badsourced = 0
    index = 0

    global content

    for t in tokens:
        match = p.match(t)
        if not match:
            badsourced += 1
            content += ("\n*Bad source at entry #" + str(index) + " : " + t + "\n")
        index +=1


    return badsourced


def checkentries(tokens):
    malus = 0
    malus += max(15 - len(tokens), 0)

    global content

    if (len(tokens) < 15):
        content += ("\n*Only " + str(len(tokens)) + " entries when at least 15 are expected\n")

    dates_isolator_expr = ['\* \[\[(.*)\]\] \/', '\*\[\[(.*)\]\]\:', '\*\[\[(.*)\]\]\/', '\*\[\[(.*)\]\] \/']

    hyperword_count = 0
    chrono_count    = 0
    for t in tokens:
        didmatch = False

        hyperword_count += t.count("[[")

        for i in dates_isolator_expr:
            d = re.compile(i)
            match = d.match(t)
            if match:
                didmatch = True
        if not didmatch:
            chrono_count += 1

    malus += max(4 - hyperword_count, 0) * 0.5
    malus += round(chrono_count/2)/4.0

    if hyperword_count <= 4:
        content += ("\n*Insufficient use of hyperwords\n")

    if chrono_count > 0:
        content += ("\n*" + str(chrono_count) + " entries did not have a chronology\n")

    return min(malus, 4)

def checkformat(tokens) :
    bullet_error = 0
    date_error = 0
    slash_or_dot_error = 0
    malus = 0

    global content

    for t in tokens :
        try:
            formats = re.findall('(\*)(\[\[\d{4}\.?\d{0,2}\.?\d{0,2}\]\])?\-?(\[\[\d{4}\.?\d{0,2}\.?\d{0,2}\]\])?[^\/]*(\/?)[^\.]*(\.?)\d*(.*)',t)
            if formats[0][0] != '*' :
                content += ("\n*No bullet point for line : " + t + "\n")
                bullet_error += 1
            if formats[0][1] == '' :
                content += ("\n*Error on date for line : " + t + "\n")
                date_error += 1
            if formats[0][3] == '' and formats[0][4] == '' :
                content += ("\n*Invalid dot and slash arrangement for line : " + t + "\n")
                slash_or_dot_error += 1
            if bullet_error > 0:
               malus += 0.25

            if date_error > 0:
                malus += 0.25

            if slash_or_dot_error > 0:
                malus += 0.25
        except:
            malus += 0.5
            content += ("\n*Format completely invalid for line : " + t + "\n")

    if malus > 0.5 :
        return 0.5
    else :
        return malus


def checkhyperwords(tokens) :
    hyperword_count_open = 0
    hyperword_count_close = 0

    global content

    for t in tokens:
        hyperword_count_open += t.count("[[")
        hyperword_count_close += t.count("]]")

    if  hyperword_count_open != hyperword_count_close :
        content += ('\n*Syntax of hyperwords is not respected\n ')
        return False
    if hyperword_count_close < 10 :
        content += ('\n*Not enough hyperwords' + str(10) +'expected but' +str(hyperword_count_close) +'found \n' )
        return False
    return True
def checklinkpages(tokens, bio):
    link_pages_count = 0
    current_page = bio

    global content

    for t in tokens :
        if isValidEntry(t) :
            line_links = getHyperLinks(t, '')
            for link in line_links :
                if  link != current_page : #isNewPage(link, ) && Il faut passer la liste de pages a vérifier, on ne l'a pas encore pour le test !
                    page = fetchPageData(link)
                    new_page_token = tokenizepage(page)
                    for new_tokens in new_page_token :
                        if areEntrySimilar(t, new_tokens) :
                            link_pages_count += 1

    if link_pages_count < 5 :
        content += ("\nOnly " + str(link_pages_count) + " linked pages are created / updated when at least 5 are expected\n")
        return False
    else :
        return True

'''
Teste si la page donnée en argument existe déjà.
@oaram name : String
			  Le nom de la page à tester.
@oaram name : List(String)
			  La liste des pages existantes.
'''
def isNewPage(name, listOfPagesToCompare):
	return (name in listOfPagesToCompare)

'''
À l'aide du titre de la page donné en argument,
récupère les données de cette page,
sous la forme d'une string
@param pageName : String
				le titre de la page wikipast où aller chercher les données.
'''
def fetchPageData(pageName):
    result=requests.post(baseurl+'api.php?action=query&titles='+pageName+'&export&exportnowrap')
    soup=BeautifulSoup(result.text, "lxml")
    pageData=''
    for primitive in soup.findAll("text"):
        if primitive.string != None:
            pageData+=primitive.string
    return pageData

'''
Vérifie que l'entrée donnée en argument soit bien une
entrée biographie (c'est à dire une entrée à puce commencant par une date)
@param entre : String
				l'entrée à vérifier.
'''
def isValidEntry(entry):
	if (entry[0:3] == '*[[' and entry[3:7].isdigit()) or (entry[0:4] == '* [[' and entry[4:8].isdigit()):
		return True
	else:
		return False

'''
retourne une liste d'hyperLinks contenu
dans cette entrée sous une forme de liste
de String, mais en excluant de cette liste l'argument
toExclude.
'''
def getHyperLinks(entry, toExclude):
	hyperLinks = re.findall('\[\[(.*?)\]\]', entry)
	hyperLinks = set([x.split('|')[0] for x in hyperLinks])
	if toExclude in hyperLinks: hyperLinks.remove(toExclude)
	return list(hyperLinks)

'''
retourne une liste d'hyperLinks contenu
dans cette entrée sous une forme de liste
de String, mais en excluant de cette liste l'argument
toExclude.
'''
def getReferences(entry):
	return re.findall('\[(.*?)\]', entry)

'''
Détermine si deux entrées sont identiques.
Pour ce faire on teste que
les dates, les lieux et la liste des hypermots
sont identiques.
(Pas de comparaison entre les PUBId!)
Si toutes les conditions énumérées ci dessus
sont satisfaites, alors on renvoit True,
autrement Talse.
@param entry1 : String
				La première entrée à comparer
@param entry2 : String
				La seconde entrée avec laquelle on compare la première
'''
def areEntrySimilar(entry1, entry2):
	#la liste des hypermots inclus également la date
	listOfHyperLinks1 = getHyperLinks(entry1, '')
	listOfHyperLinks2 = getHyperLinks(entry2, '')
	listOfReferences1 = getReferences(entry1)
	listOfReferences2 = getReferences(entry2)

	return (listOfHyperLinks1 == listOfHyperLinks2) and (listOfReferences1 == listOfReferences2)

user='Vlaedr'
passw='Alextall007'
summary='GraderBot Notation'

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

argc = len(sys.argv)

biopage = "Biographies"
biopage_txt = fetchPageData(biopage)

bios = re.findall("\|\s*?\[\[(.*?)\]\]" ,biopage_txt)

for b in bios:
    content = ""
    b = b.replace(' ', '_')
    print(b + '\n')
    grade = checkpage(b)
    if grade > 5.95:
        content += ("\nNo relevant error found.\n")
    content += ("\n\nFINAL GRADE : " + str(grade) + " / 6.0\n")

    payload = {'action': 'edit', 'assert': 'user', 'format': 'json', 'utf8': '', 'text': content,
               'summary': summary, 'title': ('Discussion:' + b), 'token': edit_token}
    r4 = requests.post(baseurl + 'api.php', data=payload, cookies=edit_cookie)
