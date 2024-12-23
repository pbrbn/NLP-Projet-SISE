import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def infos_resto(url : str) -> pd.DataFrame : 
    '''
    Scrape les informations d'un restaurant à partir d'une URL de base.
    Arguments : 
        - url : une URL de la page web contenant les avis.
    
    Retourne : 
        - Un data frame pandas contenant : 
            - Nom
            - Type de cuisine 
            - Fourchette de prix
            - Adresse 
            - Note moyenne
    '''

    #Ajouter un en-tête User-Agent pour simuler un navigateur
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    #Initialisation 
    nom_resto = []
    type_c = []
    adresse_resto = []
    note_resto = []
    fourchette_resto = []

    #Récupère le contenu HTML de la page concernée
    response = requests.get(url, headers = headers)
    if response.status_code != 200:
        raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")

    #Parser avec BS4
    fullcorpus = response.text
    soup = BeautifulSoup(fullcorpus, "html.parser")

    ##### NOM DU RESTAURANT ######
    borne_nom = soup.find_all('h1', {'class' : 'biGQs _P egaXP rRtyp'})
    for nom in borne_nom :
        nom_resto.append(nom.text)
    

    ###### TYPE DE CUISINE ######
    borne_tc = soup.find_all('div', {'class' : 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})
    for tc in borne_tc[1] : #Uniquement le deuxième élément qui contient le type de cuisine
        type_c.append(tc.text)

    
    ##### FOURCHETTE DE PRIX #####
    borne_four = soup.find('div', {'class' : 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})

    if borne_four:
        #Trouve la balise précédente
        previous_div = borne_four.find_previous('div', {'class': 'biGQs _P ncFvv NaqPn'})

        if previous_div:
            #Vérifie le contenu de la balise précédente
            if previous_div.text.strip() == "FOURCHETTE DE PRIX":  
                fourchette_resto.append(borne_four.text)
            else:
                fourchette_resto.append("NA")
        else:
            #Si la balise précédente n'est pas trouvée, ajouter NA
            fourchette_resto.append("NA")
    else:
        #Si la balise principale n'est pas trouvée, ajouter NA
        fourchette_resto.append("NA")
    
    #Formatage
    fourchette_resto = [four.replace('\xa0', '') for four in fourchette_resto]


    ##### ADRESSE #####
    borne_adresse = soup.find_all('div', {'class' : 'akmhy e j'})
    for adresse in borne_adresse[0]: #Uniquement le premier élément qui contient l'adresse
        adresse_resto.append(adresse.text)

    
    ##### NOTe MOYENNE #####
    borne_note = soup.find_all('div', {'class' : 'sOyfn u f K'})
    match = re.search(r"(\d+,\d)", borne_note[0].text)
    note_resto = match.group(1)


    #Stocke les résultats dans un dataframe
    results = {
        "Nom" : nom_resto,
        "Type_Cuisine" : type_c,
        "Fourchette_prix" : fourchette_resto,
        "Adresse" : adresse_resto,
        "Note_moyenne" : note_resto
    }

    df_results = pd.DataFrame(results)

    return df_results