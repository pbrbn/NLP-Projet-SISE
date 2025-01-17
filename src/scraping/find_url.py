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
        "Cookie" : "SEARCH_SAMESITE=CgQI-ZwB; SID=g.a000sQhz8qA59Z6wn70tIFfDkTM4pjt_CQZ2V2NHh9MUQUrRIxaPJPsBq7xlVz7dtjuHvWXmNgACgYKAZkSARASFQHGX2MikbOxF7yg-IJ2BMne4s8iLxoVAUF8yKo5qEcGstR4m4A1qWuF3rwB0076; __Secure-1PSID=g.a000sQhz8qA59Z6wn70tIFfDkTM4pjt_CQZ2V2NHh9MUQUrRIxaPHURgkGWeU-BedPSahbixpAACgYKAW0SARASFQHGX2MiPjYlnlku3vocyzA2837mWBoVAUF8yKoIDU9BiPGsiwg4sj1jTn4r0076; __Secure-3PSID=g.a000sQhz8qA59Z6wn70tIFfDkTM4pjt_CQZ2V2NHh9MUQUrRIxaPtRYAcUs-QNXiFw6yfaBgoAACgYKAecSARASFQHGX2MiWLZT8-t0qRJojNdOR2K-whoVAUF8yKqWBfVT5LPhBuR_l0gw7gRQ0076; HSID=AtQ9fRSCtC1t3Ezeu; SSID=AfIyO0LW54ZBa6p36; APISID=O-D962Dinjz3nMgG/AHSXjgEgxKUYrBiq9; SAPISID=E3614eYZlvhcT05F/A8dDPfKi_Gr4pDY5s; __Secure-1PAPISID=E3614eYZlvhcT05F/A8dDPfKi_Gr4pDY5s; __Secure-3PAPISID=E3614eYZlvhcT05F/A8dDPfKi_Gr4pDY5s; AEC=AZ6Zc-XN_TqarrT6QIn_NdBThSTMV9uBqZzhdCaPB5UA4fwb-pKjdIalL2c; NID=520=rQNG5k9rUkAuqC0RtIxFJ5bwaqmbLapbFj503ukDwKJqk39Q8iUVxeIzUqORYBPR6sO0ElPdnLSM6u4oDMQO1j_-bfJ1lyDYDUaQ-o938z4d4xaWARUzPI_tHzInThb0xvdEiiy4S8rOHdcBe__6slHkavqt7jlQoilLdYfOPfreA0c2UVraE6465o9QBsuvFy6EP1NaEwcyk0N2YktD-yWaj6j3PYem2cCSMnrcs0aCEcyRtd-d1NZqcN8dMaqxJU3_bQCOhnGhOThh8s22VHxVRjk7gnQ3B0xsYg2EetKZ7TYud1RQSt-yAIuRtfl8sMyUlXZv; __Secure-ENID=25.SE=AOrlQ-4-Rqxz-by29MZmwrO7f6O_jmdkwvgEXuRGUs4UWc1zLfCZgvlByr5igZByTQzr8huF6SgF5CIreux9JvgxVXVSsQJNyG6ZCJqSTYkdWBnBpJVwBdP4VT4O7GI6-LDUIrAEq2i3c5Oos9nSjFNnbAcSXwsClyaetZLOkOq_CvX6uZx9TKJsw1RivMIBekCKwcByoZ6q9ygsWwIMcAWnOVq3mqTYc39ARVZwc1xgTKVsUc_u3evNfUtF1NLC4egR11tyePpUmVIBA_LLlPKniInw1sGTG6uTOnytbUWLf9448iKZC-mfjz5Fh3XfVdTL8Xdn3YxOXMxVeSD69ViNHhqMEX_FQc5zByG6FDarN7RL2ZF7kpYTIihP964GPqyy2QT6Il9mQ1iJnfFxD4UmYjKTTyqjcat2WS3Xa4RxY2-6YTFnhDs2tf5TnxthqDry04u3oWVc; __Secure-1PSIDTS=sidts-CjIBmiPuTXcLEAJOXPEG_E8ujOPy5qjre4KDRvZXGOco-5AoUnPM3iS_ap5sR6JasyuF-RAA; __Secure-3PSIDTS=sidts-CjIBmiPuTXcLEAJOXPEG_E8ujOPy5qjre4KDRvZXGOco-5AoUnPM3iS_ap5sR6JasyuF-RAA; DV=w1flkL-EO0dccC38Z5-bAljQnBlkR9mJV5getGLfqQAAABAYEUSZHNXSoQAAAAgH7s-UDNE6MAAAACDi14a58OXZDAAAAA; SIDCC=AKEyXzW3uu2MzteWuCD8_-yb4x1qOuynjB7ZaShJHV7yb3tusGS5WxhMzlMvkh727IuszBQ2ELU; __Secure-1PSIDCC=AKEyXzWAPQKqBDiWzg69BN6KrACUkBbSar0oWl1TR9fvDxdYI_r2SfQHLomDx6F8bWSl2p9SYqk; __Secure-3PSIDCC=AKEyXzWkdTuXgDQu2OOpLfJGq5yG-w9YfUa0nL_dk-Yd3n3-bM7jP8RjCeNBq1JqkGu5-sJXJ6Oz",
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
    for lien in soup.find_all('a', jsname = "UWckNb"):
        url_resto = lien.get("href")

        if "tripadvisor.fr/Restaurant_Review" in url_resto :
            return url_resto
        
    #Si il ne le trouve pas
    print("Aucun lien Tripadvisor valide trouvé. Merci de vérifier si il s'agit bien d'un restaurant et non d'une 'activité' sur TripAdvisor. \nSinon, n'hésitez pas à ajouter le nom de la ville/arrondissement dans lequel se situe le restaurant.")
    return None