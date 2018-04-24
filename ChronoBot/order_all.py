from order import order
from retrieve_content import retrieve_content
from create_new_site import create_new_site

def order_all(years):#ça ordonne toutes les annees
    done=[]
    for year in years:
        if year not in done:
            print('I am ordering page '+year)
            content=order(retrieve_content(year))
            create_new_site(year,content)
            done.append(year)