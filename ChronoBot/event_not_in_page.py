'''
cette fonction prend en input une annee et un evenement.
Si cet evenement est déja dans la page de l'année il renvoie 0
Si il n'est pas encore dans la page de l'année il renvoie 1
'''

from retrieve_content import retrieve_content

def event_not_in_page(date,evenement):
    text=retrieve_content(str(date)).replace(' ','')
    text=text.replace(',','')
    text=text.replace('.','')
    pos=evenement.find(']]')
    evenement=evenement[pos+2:].replace(' ','')
    evenement=evenement.replace(',','')
    evenement=evenement.replace('.','')
    if evenement in text:
        return 0
    else:
        return 1
