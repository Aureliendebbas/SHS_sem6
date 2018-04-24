'''
cette fonction prend en input le nom d'une page
et retourne tout le text qu'il y a dedans, en code wiki
'''
import requests
from bs4 import BeautifulSoup

def retrieve_content(name):
    baseurl='http://wikipast.epfl.ch/wikipast/'
    result=requests.post(baseurl+'api.php?action=query&titles='+name+'&export&exportnowrap')
    soup=BeautifulSoup(result.text, "html.parser")
    code=''
    if soup.findAll("text")[0]['bytes']=='0':
        return code
    for primitive in soup.findAll("text"):
        code+=primitive.string
    return code