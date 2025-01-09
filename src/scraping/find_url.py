import requests
from bs4 import BeautifulSoup

def find_url_restaurant(nom_resto:str) -> str : 
    '''
    Cette fonction effectue une recherche Google et trouve l'url Trip Advisor du restaurant à partir de son nom 

    Args :
        - nom_resto : str, nom du restaurant 

    Retourne : 
        - url_resto : str, l'url Trip Advisor du restaurant
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

    #Recherche sur Google 
    requete = f"{nom_resto} tripadvisor.fr".replace(" ", "+")
    url = f"https://www.google.com/search?q={requete}"
    response = requests.get(url, headers=headers)

    #Vérification de la réponse 
    if response.status_code != 200:
        print("Erreur de récupération")

        return None

    #Parse le contenu de la page 
    soup = BeautifulSoup(response.text, "html.parser")

    #Cherche le lien du restaurant
    lien = soup.find('a', jsname = "UWckNb")
    url_resto = lien["href"]

    return url_resto