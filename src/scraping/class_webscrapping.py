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

    def _fetch_html(self, url):
        """Récupére le contenu HTML à partir d’une URL donnée."""
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")
        return response.text

    def scrape_infos_avis(self, max_pages=None):
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

    def scrape_infos_resto(self, max_retries=5):
        '''
        Permet de relancer la fonction infos_resto tant qu'elle ne sort pas le résultat attendu
        '''
        attempts = 0
        while attempts < max_retries:
            try:
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

        #Nom du restaurant
        nom_resto = [nom.text for nom in soup.find_all('h1', {'class': 'biGQs _P egaXP rRtyp'})]

        #Type de cuisine
        borne_tc = soup.find_all('div', {'class': 'biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD'})
        type_c = [tc.text for tc in borne_tc[1]] if len(borne_tc) > 1 else ["NA"]

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

        #Créer un DataFrame des résultats
        results = {
            "Nom": nom_resto,
            "Type_Cuisine": type_c,
            "Fourchette_prix": fourchette_resto,
            "Adresse": adresse_resto,
            "Note_moyenne": [note_resto]
        }
        return pd.DataFrame(results)

    def scrape_description_resto(self): 
        '''
        Scrape la description d'un restaurant à partir de la page principale.
        Retourne un dataframe pandas contenant le nom du restaurant et sa description.
        '''

        #Ajouter un en-tête User-Agent pour simuler un navigateur Safari
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie" : "datadome=OTKb6teBCxRFcUWdBKg2bv4vPk5gp9Bq_fkIX9M1hv0l1O~7pql~t0rLcrF55OYjZXg2SCppVdhowYkaf3ZdULII4Zll_jo1HyXfNR~INwS2GHqo~hKFbqZOe9WZU3Lh; OTAdditionalConsentString=1~; OptanonAlertBoxClosed=2024-12-24T09:58:45.860Z; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Dec+24+2024+10%3A58%3A45+GMT%2B0100+(heure+normale+d%E2%80%99Europe+centrale)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=6991eb73-bdbd-4e03-acef-bef21c460a40&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A0%2CC0002%3A0%2CC0003%3A0%2CV2STACK42%3A0&intType=2; eupubconsent-v2=CQKIzJgQKIzJgAcABBFRBVFgAAAAAAAAACiQAAAVZgEAGfAn2BRQCi0FGgUcAprBVEFUgKsgFAgBIAOgAuADZAIgAYQBOgC5AG2AQOCABgAdACuAIgAYQBOgEDgwAcAHQAXABsgEQAMIAuQCBwgAOADoAbIBEADCAJ0AXIBA4UADAC4AYQCBwwAEAYQCBw4AMADoAiABhAE6AQOAiuQABAGEAgcSABgEQAMIBA4oAFAB0ARAAwgCdAIHAAAA.YAAAAAAAAAAA; TATrkConsent=eyJvdXQiOiJBRFYsQU5BLEZVTkNUSU9OQUwsU09DSUFMX01FRElBIiwiaW4iOiIifQ==; TASession=V2ID.18E0AAD8A77C935A940F7057DC1423DE*SQ.1*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true; PAC=ALKsDVC4ZxRLx1HQQPmNn9OyXVJMOSNT-9830SswWPA42mjDxYKnXGVvDgkbIGObOsxSrfKPVx6tOigcqaXrnXg-obWVOZ21zNP6uTD-HPNtDp2hB7irPNivOJRcCOZtPepLaHDn52esV2AnsaYYfHn6EXbqX_qCGxoOstlDLMjUztIgtoxll7MHuCzAebS4CMdblBKnuOFMaBxr2SYvc8Jn_Q9DjP1rHe1iM1QYioUZGSmPYGrEPmFcRM9YrHIXqS8NptGCaJMxLeFu8SMSca7xklyC_ktFMMltwyliOKbVrkFDcpC2QWI0otDihMuGtX--380hTsnoNT8ix5yV5_I1XSQibh9S0mqLVIefwPXrWDWNxMMIgPjaWAzO9kO8tA%3D%3D; TART=%1%enc%3A4tUMhd4q3TD%2B1NMSuIeRG%2FjRGvqwbTm5qYMlblKgeSBtDdnsiNLiNbcgolkcrHNZJBhQ%2Fpo5O08%3D; TASSK=enc%3AAGHeXyYUbIGVxQbJHCA1NLvliVlMzxadvB2XsGGT%2Bs8%2ByigSc5LAukJTgYlMbnvcKXvu07qOkJnMx9GLHynJzYyObeXKvFN%2FyJsUKAK%2F283mVHLTCzcAtoMHoZBT%2FUX10w%3D%3D; TADCID=Ia-JSp9PJbEVTH7-ABQCrj-Ib21-TgWwDB4AzTFpg4J3w1Pk8Xv76ewUbYEXqC89GXrTKPUooPFZK22sA8d13dgcB2jeJ-dP2fc; TASameSite=1; TAUnique=%1%enc%3A9F7tFOO5uZNo7bQsGEa2I30I33FEfU0vakxPVUC%2BgEC2VWcLBajUG4nL9ocREQ%2BQNox8JbUSTxk%3D",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

        #Initialisation 
        description = []
        nom_resto = []
        borne_nom = None

        #Boucle pour refaire la requête si il ne trouve pas la balise
        while borne_nom == None : 
            #Pause en cas de requêtes multiples
            time.sleep(1 + (2 * random.random()))
            #Récupère le contenu HTML de la page concernée
            response = requests.get(self.base_url, headers = headers)
            if response.status_code != 200:
                raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")

            #Parser avec BS4
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            ##### NOM RESTO #####
            borne_nom = soup.find('h1', {'class' : 'biGQs _P hzzSG rRtyp'})
            
            #Récupère le nom du resto
            for nom in borne_nom :
                nom_resto.append(nom.text)


        ##### DESCRIPTION #####
        # #Trouver le parent
        parent = soup.find("div", {"class" : "fIrGe _T bgMZj"})

        #Trouver l'élément cible dans le parent
        child = parent.find_all("div",{ "class" : "biGQs _P pZUbB avBIb KxBGd"}) 

        if child :
            #Récupérer la description
            for descr in child :
                description.append(descr.text)
        else :
            description.append("NA")

        #Stocke les résultats dans un dataframe
        results = {
            "Nom" : nom_resto,
            "Description" : description
        }

        df_results = pd.DataFrame(results)

        return df_results
