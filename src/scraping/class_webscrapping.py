import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
import re
import pandas as pd

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
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

    def fetch_html(self, url):
        """Récupére le contenu HTML à partir d’une URL donnée."""
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")
        return response.text

    def infos_avis(self, max_pages=None):
        """
        Scrape les informations des avis sur plusieurs pages.
        Retourne un DataFrame avec les dates, notes et commentaires.
        """
        clean_dates, clean_notes, clean_texte = [], [], []
        url_next_page = self.base_url
        page_count = 0

        #Parser l'URL 
        parsed_url = urlparse(self.base_url)
        base_url = parsed_url.scheme + "://" + parsed_url.netloc

        while url_next_page:
            # Vérifie si la limite de page est atteinte
            if max_pages is not None and page_count >= max_pages:
                break

            # Récupère et parse le contenu de la page
            html_content = self.fetch_html(url_next_page)
            soup = BeautifulSoup(html_content, "html.parser")

            # Trouver les blocs contenant les commentaires
            commentaires_blocs = soup.find_all('div', {"class":'_c'})

            for bloc in commentaires_blocs:
                # Extraire la date
                date_elt = bloc.find('div', {'class': 'aVuQn'})
                date = (date_elt.text).split(' • ')[0] if date_elt else "NA"
                clean_dates.append(date)

                # Extraire la note
                note_elt = bloc.find('svg', {'class': "UctUV d H0"})
                if note_elt:
                    match = re.search(r"(\d+,\d+)", note_elt.text)
                    note = match.group(1) if match else "NA"
                else:
                    note = "NA"
                clean_notes.append(note)

                # Extraire le commentaire
                texte_elt = bloc.find('span', class_='JguWG')
                if texte_elt and not texte_elt.find_parent(class_="csNQI PJ"):
                    texte = texte_elt.text
                else:
                    texte = "NA"
                clean_texte.append(texte)

            # Trouver le lien de la page suivante
            next_page = soup.find('a', {'aria-label': 'Page suivante'})
            if next_page :
                #Construit l'URL de la page suivante 
                url_next_page = urljoin(base_url, next_page['href'])
                #Compteur de page
                page_count += 1
            else :
                #Pas de page suivante, stop la boucle 
                url_next_page = None

            # Pause pour éviter de se faire bloquer
            time.sleep(1 + (2 * random.random()))

        # Créer un DataFrame des résultats
        results = {
            "Date": clean_dates,
            "Notes": clean_notes,
            "Commentaires": clean_texte
        }

        return pd.DataFrame(results)

    def infos_resto(self):
        """
        Scrape les informations d'un restaurant à partir de la page actuelle.
        Retourne un DataFrame avec le nom, type de cuisine, fourchette de prix, adresse et note moyenne.
        """
        html_content = self.fetch_html(self.base_url)
        soup = BeautifulSoup(html_content, "html.parser")

        #Initialisation
        fourchette_resto = []

        # Nom du restaurant
        nom_resto = [nom.text for nom in soup.find_all('h1', {'class': 'biGQs _P egaXP rRtyp'})]

        # Type de cuisine
        borne_tc = soup.find_all('div', {'class': 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})
        type_c = [tc.text for tc in borne_tc[1]] if len(borne_tc) > 1 else ["NA"]

        # Fourchette de prix
        borne_four = soup.find('div', {'class': 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})
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

        # Adresse
        borne_adresse = soup.find_all('div', {'class': 'akmhy e j'})
        adresse_resto = [adresse.text for adresse in borne_adresse[:1]] if borne_adresse else ["NA"]  # Premier élément uniquement

        # Note moyenne
        borne_note = soup.find_all('div', {'class': 'sOyfn u f K'})
        note_resto = None
        if borne_note:
            match = re.search(r"(\d+,\d)", borne_note[0].text)
            note_resto = match.group(1) if match else None
        else :
            note_resto = "NA"

        # Créer un DataFrame des résultats
        results = {
            "Nom": nom_resto,
            "Type_Cuisine": type_c,
            "Fourchette_prix": fourchette_resto,
            "Adresse": adresse_resto,
            "Note_moyenne": [note_resto]
        }
        return pd.DataFrame(results)
