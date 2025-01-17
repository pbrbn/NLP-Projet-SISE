import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
import re
import pandas as pd

class RestaurantScraper:
    """ Classe pour scraper les informations des restaurants et des avis sur TripAdvisor. """
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

    def _fetch_html(self, url):
        """Récupére le contenu HTML à partir d’une URL donnée."""
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")
        return response.text

    def scrape_infos_avis(self, max_pages=None):
        """
        Scrape les informations des avis sur plusieurs pages.
        Retourne un DataFrame avec le nom du restaurant, les dates, notes et commentaires.
        """

        html_content = self._fetch_html(self.base_url)
        soup = BeautifulSoup(html_content, "html.parser")
        nom_resto = [nom.text for nom in soup.find_all('h1', {'class': 'biGQs _P egaXP rRtyp'})]
        # Pas toujours une liste
        if len(nom_resto) > 1:
            nom_resto = str(nom_resto[0])
        else:
            nom_resto = str(nom_resto)
        # print(nom_resto)
        clean_nom, clean_dates, clean_notes, clean_texte = [], [], [], []
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
            html_content = self._fetch_html(url_next_page)
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

                # Ajouter le nom du restaurant
                clean_nom.append(nom_resto)

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
            "nom_restaurant": clean_nom, 
            "Date": clean_dates,
            "Notes": clean_notes,
            "Commentaires": clean_texte
        }

        return pd.DataFrame(results)

    def scrape_infos_resto(self, max_retries=10):
        '''
        Permet de relancer la fonction infos_resto tant qu'elle ne sort pas le résultat attendu
        '''
        attempts = 0
        while attempts < max_retries:
            try:
                time.sleep(1 + (2 * random.random()))
                return self._infos_resto()
            except Exception as e:
                attempts += 1
                print(f"Erreur détectée : {e}. Nouvelle tentative ({attempts}/{max_retries})...")
        raise RuntimeError("Echec après plusieurs tentatives")

    def _infos_resto(self):
        """
        Scrape les informations d'un restaurant à partir de la page actuelle.
        Retourne un DataFrame avec le nom, type de cuisine, fourchette de prix, adresse et note moyenne.
        Doit être utilisé uniquement via la fonction scrape_infos_resto() !!!
        """
        html_content = self._fetch_html(self.base_url)
        soup = BeautifulSoup(html_content, "html.parser")

        #Initialisation
        fourchette_resto = []
        type_c = []

        #Nom du restaurant
        nom_resto = [nom.text for nom in soup.find_all('h1', {'class': 'biGQs _P egaXP rRtyp'})]

        #Type de cuisine
        borne_tc = soup.find_all('div', {'class': 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})

        #Boucle pour trouver la balise soeur correspondante
        for div in borne_tc:
            soeur = div.find_previous_sibling('div', class_="Wf")
            if soeur and soeur.text.strip() == 'CUISINES':
                type_c.append(div.text.strip())
        
        if not type_c:
            type_c.append("NA")
            
        #Fourchette de prix
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

        #Adresse
        borne_adresse = soup.find_all('div', {'class': 'akmhy e j'})
        adresse_resto = [adresse.text for adresse in borne_adresse[:1]] if borne_adresse else ["NA"]

        #Note moyenne
        borne_note = soup.find_all('div', {'class': 'sOyfn u f K'})
        note_resto = None
        if borne_note:
            match = re.search(r"(\d+,\d)", borne_note[0].text)
            note_resto = match.group(1) if match else None
        else :
            note_resto = "NA"

        # Test Catégorie prix
        categorie_prix = soup.find_all('div', {'class': 'CsAqy u Ci Ph w'})
        # print(categorie_prix) # renvoie tout les spans, on va faire du regex pour récupérer la bonne catégorie
        categorie_prix_regex = re.search(r'€[€-]*€', str(categorie_prix))
        categorie_prix_regex = categorie_prix_regex.group() if categorie_prix_regex else "NA"

        # print(categorie_prix_regex)



        #Créer un DataFrame des résultats
        results = {
            "Nom": nom_resto,
            "Type_Cuisine": type_c,
            "Fourchette_prix": fourchette_resto,
            "Adresse": adresse_resto,
            "Note_moyenne": [note_resto],
            "Categorie_prix": categorie_prix_regex
        }
        return pd.DataFrame(results)

    def scrape_description_resto(self, max_retries=10):
        '''
        Permet de relancer la fonction _description_resto tant qu'elle ne sort pas le résultat attendu
        '''
        attempts = 0
        while attempts < max_retries:
            try:
                time.sleep(1 + (2 * random.random()))
                return self._description_resto()
            except Exception as e:
                attempts += 1
                print(f"Erreur détectée : {e}. Nouvelle tentative ({attempts}/{max_retries})...")
        raise RuntimeError("Echec après plusieurs tentatives")

    def _description_resto(self): 
        '''
        Scrape la description d'un restaurant à partir de la page principale.
        Retourne un dataframe pandas contenant le nom du restaurant et sa description.
        '''
        #Initialisation 
        description = []
        nom_resto = []
        
        #Récupère le code html du site
        html_content = self._fetch_html(self.base_url)
        
        soup = BeautifulSoup(html_content, "html.parser")

        ##### NOM RESTO #####
        borne_nom = soup.find_all('h1', {'class' : 'biGQs _P hzzSG rRtyp'})
            
        #Récupère le nom du resto
        for nom in borne_nom :
            nom_resto.append(nom.text)


        ##### DESCRIPTION #####
        #Trouver le grand parent 
        grand_parent = soup.find("div", {"class": "_T FKffI"})

        if grand_parent:
            # Trouver le parent à partir du grand-parent
            parent = grand_parent.find("div", {"class": "fIrGe _T bgMZj"})

            if parent:
                # Trouver les éléments cibles dans le parent
                child = parent.find_all("div", {"class": "biGQs _P pZUbB avBIb KxBGd"})

                if child:
                    # Récupérer la description
                    for descr in child:
                        description.append(descr.text)
                else:
                    description.append("NA")
            else:
                description.append("NA")
        else:
            description.append("NA")

        #Stocke les résultats dans un dataframe
        # Vérifier que toutes les listes ont la même longueur
        min_length = min(len(nom_resto), len(description))

        # Ajuster les listes pour qu'elles aient toutes la même longueur
        nom_resto = nom_resto[:min_length]
        description = description[:min_length]
        results = {
            "Nom" : nom_resto,
            "Description" : description
        }

        df_results = pd.DataFrame(results)

        return df_results
