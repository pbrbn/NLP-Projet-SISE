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
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate","Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    #Recherche sur Google 
    requete = f"{nom_resto} tripadvisor.fr".replace(" ", "+")
    url = f"https://search.brave.com/search?q={requete}"
    response = requests.get(url, headers=headers)

    #Vérification de la réponse 
    if response.status_code != 200:
        print("Erreur de récupération")

        return None

    #Parse le contenu de la page 
    soup = BeautifulSoup(response.text, "html.parser")

    #Cherche le lien du restaurant
    for lien in soup.find_all('a', class_ = "svelte-yo6adg l1 heading-serpresult"):
        url_resto = lien.get("href")

        if "tripadvisor.fr/Restaurant_Review" in url_resto :
            return url_resto
        
    #Si il ne le trouve pas
    print("Aucun lien Tripadvisor valide trouvé. Merci de vérifier si il s'agit bien d'un restaurant et non d'une 'activité' sur TripAdvisor. \nSinon, n'hésitez pas à ajouter le nom de la ville/arrondissement dans lequel se situe le restaurant.")
    return None