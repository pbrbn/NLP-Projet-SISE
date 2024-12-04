'''
IMPORTANT : CE QUI EST EN COMMENTAIRE NE FONCTIONNE PAS
'''
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd


def infos_resto(url : str) -> pd.DataFrame : 
    '''
    Scrape les informations d'un restaurant à partir d'une URL de base.
    Arguments : 
        - url : une URL de la page web contenant les avis.
    
    Retourne : 
        - Un data frame pandas contenant : 
            - Le nom,
            - Le type de cuisine 
            - L'adresse 
            - Note moyenne
            - Site web
            - Infos pratiques 
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
    url_resto = []

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
    # borne_tc = soup.find_all('a', {'class' : ''})
    # for tc in borne_tc : 
    #     type_c.append(tc.text)


    ##### ADRESSE #####
    borne_adresse = soup.find_all('div', {'class' : 'akmhy e j'})
    for adresse in borne_adresse[0]: #Uniquement le premier élément qui contient l'adresse
        adresse_resto.append(adresse.text)

    
    ##### NOTe MOYENNE #####
    borne_note = soup.find_all('div', {'class' : 'sOyfn u f K'})
    match = re.search(r"(\d+,\d)", borne_note[0].text)
    note_resto = match.group(1)

    
    ##### SITE WEB #####
    # site_internet = soup.find_all('a', {'data-automation':'restaurantsWebsiteButton'})
    # for site in site_internet:
    #     href = site.get('href')  # Récupère la valeur de l'attribut href
    #     if href:  # Vérifie que l'attribut href existe
    #         url_resto.append(href)

    return url_resto
