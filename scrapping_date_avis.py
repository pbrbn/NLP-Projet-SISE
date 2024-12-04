import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import time
import random

def liste_dates(url : str, max_pages : int = None) -> list[str]:
    '''
    Scrape les dates des avis sur plusieurs pages à partir d'une URL de base.
    Arguments : 
        - url : une URL de la page web contenant les avis.
        - max_pages : Nombre maximum de pages à scraper.
    
    Retourne : 
        - Une liste contenant les dates des avis 
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

    #Parser l'URL 
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + "://" + parsed_url.netloc

    clean_dates = []
    url_next_page = url
    page_count = 0

    while url_next_page : 
        #Vérifie si la limite de page est atteinte 
        if max_pages is not None and page_count >= max_pages:
            break

        #Récupère le contenu HTML de la page concernée
        response = requests.get(url_next_page, headers = headers)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")

        #Parser avec BS4
        fullcorpus = response.text
        soup = BeautifulSoup(fullcorpus, "html.parser")

        # Trouver les balises title avec l'id ":lithium-r10f:"
        date_avis = soup.find_all('div', {'class' : 'aVuQn'})

        #Extraire uniquement la date 
        for date in date_avis:
            clean_dates.append(date.text)

        #Trouver le lien vers la page suivante 
        next_page = soup.find('a', {'aria-label':'Page suivante'})
        if next_page :
            #Construit l'URL de la page suivante 
            url_next_page = urljoin(base_url, next_page['href'])
            #Compteur de page
            page_count += 1
        else :
            #Pas de page suivante, stop la boucle 
            url_next_page = None 
        
        #Pause de 1 à 2 secondes entre les pages pour éviter de se faire bloquer
        time.sleep(1 + (4 * random.random()))  #Pause aléatoire entre 1 et 5 secondes
    
    return clean_dates