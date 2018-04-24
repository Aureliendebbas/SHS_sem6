from create_new_site import create_new_site
from create_site import create_site
from modify_links import modify_links
from place_evenement import place_evenement
from event_not_in_page import event_not_in_page
from recherchedates2 import recherchedates2
#ajouter ici les autres fonctions dont on aura besoin

def main_one_page(page):
    page=page.replace(" ","_")
    #modifie les dates pour rediger vers une année
    modify_links(page)

    #renvoie un array de deux colonnes: une colonne de dates et une colonne d'evenements
    elements=recherchedates2(page)
    
    for element in elements:
        evenement = element[1]
        date      = element[0]
        annee     = date[:4]
        #cree le site si il existe pas encore
        create_site(annee)
               
        if event_not_in_page(annee,evenement):
            content=place_evenement(date,evenement)
            create_new_site(annee,content)

