from retrieve_content import retrieve_content
def place_evenement(annee,evenement): #format annee: 'aaaa'
                                    #format dans wikipast: '*[[aaaa.mm.jj]] (...)' seulement le début du format nous intéress
    return retrieve_content(annee)+'\n'+evenement
