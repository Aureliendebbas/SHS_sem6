'''
Alors ça c'est le main. Si on le lance ça crée
toutes las pages année normalement.
'''

from select_page import select_page
from main_one_page import main_one_page
import datetime
from order_all import order_all

page_list=select_page()
i=0
years_modified=[]
for page in page_list:
    print('Je suis en train de faire la page: '+page)
    print("J'ai fait un "+str(i/len(page_list)*100)+'%')
    years_modified=years_modified+main_one_page(page)
    i=i+1
print("j'ai fini, il me reste qu'à tout ordonner")
#ici il ordonne toutes les pages, parce que la fonction place_evenement
    #met les evenements juste à la fin de la page
order_all(years_modified)

now = datetime.datetime.now()
year=str(now.year)
month=str(now.month)
day=str(now.day)
hour=str(now.hour)
minute=str(now.minute)
if len(month)==1:
    month='0'+month
if len(day)==1:
    day='0'+day
if len(hour)==1:
    hour='0'+hour
if len(minute)==1:
    minute='0'+minute

fichier=open('lastdate.txt','w')
fichier.write(year+'-'+month+'-'+day+'T'+hour+':'+minute+':00Z')
fichier.close()
