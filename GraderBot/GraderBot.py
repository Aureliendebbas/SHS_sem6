import re
import sys
import urllib
import requests
import json
import hashlib
from bs4 import BeautifulSoup

def tokenizepage(pagetext) : 
    tokens = []
    tk = pagetext.split('\n')
    for t in tk:
        if t:
            if t[0] == '*':
                tokens.append(t)
    return tokens


def checkpage(pagetext, report):
    text = fetchPageData(pagetext)
    tokens = tokenizepage(text)
    grade = 6.0

    grade -= checkentries(tokens, report)

    if len(tokens) <= 10:
        return 0.0

    if checksource(tokens, report) > 0:
        grade -= 0.5
    
    if not checklinkpages(tokens, report) :
        grade -= 0.5

    grade -=  checkformat(tokens, report) 

    if not checkhyperwords(tokens, report) : 
        grade -= 0.5 



    return max(grade, 0)


def checksource(tokens, report):
    r = '\*.*\[https?:\/\/w?w?w?\.?letemps[^\]]*\].*'
    p = re.compile(r)
    badsourced = 0
    index = 0

    for t in tokens:
        match = p.match(t)
        if not match:
            badsourced += 1
            report.write("Bad source at entry #" + str(index) + " : " + t + "\n")
        index +=1


    return badsourced


def checkentries(tokens, report):
    malus = 0
    malus += max(15 - len(tokens), 0)

    if (len(tokens) < 15):
        report.write("Only " + str(len(tokens)) + " entries when at least 15 are expected\n")

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
        report.write("Insufficient use of hyperwords\n")

    if chrono_count > 0:
        report.write(str(chrono_count) + " entries did not have a chronology\n")

    return min(malus, 4)

def checkformat(tokens, report) : 
    bullet_error = 0 
    date_error = 0
    slash_or_dot_error = 0 
    malus = 0

    for t in tokens : 
        formats = re.findall('(\*)(\[\[\d{4}\.?\d{0,2}\.?\d{0,2}\]\])?\-?(\[\[\d{4}\.?\d{0,2}\.?\d{0,2}\]\])?[^\/]*(\/?)[^\.]*(\.?)\d*(.*)(\[.+\]\s*)$',t)
        if formats[0][0] == '' : 
           bullet_error += 1
        if formats[0][1] == '' : 
           date_error += 1
        if formats[0][3] == '' or formats[0][4] == '': 
            slash_or_dot_error += 1

    if bullet_error > 0 : 
         report.write("No bullet\n")
         malus += 0.25

    if date_error > 0 : 
         report.write("No date\n")
         malus += 0.25

    if slash_or_dot_error > 0 : 
         report.write("No slash or dot\n")
         malus += 0.25
    
    if malus > 0.5 : 
        return 0.5
    else : 
        return malus 


def checkhyperwords(tokens, report) : 
    hyperword_count_open = 0 
    hyperword_count_close = 0 
    for t in tokens:
        hyperword_count_open += t.count("[[")
        hyperword_count_close += t.count("]]")

    if  hyperword_count_open != hyperword_count_close : 
        report.write('Syntax of hyperwords is not respected\n ')
        return False 
    if hyperword_count_close < 10 : 
        report.write('Not enough hyperwords' + str(10) +'expected but' +str(hyperword_count_close) +'found \n' )
        return False
    return True
def checklinkpages(tokens, report):
    link_pages_count = 0
    current_page = 'Louise_Michel'
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
        report.write("Only " + str(link_pages_count) + " linked pages are created / updated when at least 5 are expected\n") 
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
    baseurl = 'http://wikipast.epfl.ch/wikipast/'
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

argc = len(sys.argv)

if argc < 3:
    read_file  = open("LouiseMichel.txt", "r", encoding='latin-1')
    write_file = open("report.txt", "w")
else:
    read_file = sys.argv[1] #= open(sys.argv[1], "r",  encoding='latin-1')
    write_file = open(sys.argv[2], "w")

grade = checkpage(read_file, write_file)
if grade > 5.95:
    write_file.write("No relevant error found.\n")
write_file.write("\n\nFINAL GRADE : " + str(grade) + " / 6.0\n")


