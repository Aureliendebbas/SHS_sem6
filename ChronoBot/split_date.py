def split_date(date): #format date: 'aaaa.mm.jj'  /!\ la date doit être au format string
    date=str(date); #on est jamais trop sûr
    annee='';
    mois='';
    jour='';
    for i in range(len(date)):
        if(i<4): annee=annee+date[i];
        if(i>4 and i<7): mois=mois+date[i];
        if(i>7 and i<10): jour=jour+date[i];
    return [annee, mois, jour];
