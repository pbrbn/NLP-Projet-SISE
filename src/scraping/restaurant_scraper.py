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

    def scrape_infos_resto(self, max_retries=10):
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
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie" : "datadome=MkRr2HR9uCdHMeLSXS_m~7Bo0b6JMEwW6ggMAMK2fDPXVqxDencQIPcBJ17_PvlxpW5Wdmpxy_QwrEDGfnpVUBrKqDke5o4ilFr9HNwpEJ_Syjt2szCSfzRkyTsJOWV0; __eoi=ID=d63e74d3ff06ae7a:T=1736365491:RT=1736411117:S=AA-AfjYI1VoN38dKCIH4rqvnwdyv; __gads=ID=f5eeeacaf68f013c:T=1736365491:RT=1736411117:S=ALNI_MaKXms5IT7FNE3OG8nWUuQDTdFWBQ; __gpi=UID=00000fc5de7fce37:T=1736365491:RT=1736411117:S=ALNI_MbLgiMwk8VpRKXtodNRzm8rxz2Q1Q; _gcl_au=1.1.1750750334.1736365490; _gcl_aw=GCL.1736411116.null; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jan+09+2025+09%3A25%3A13+GMT%2B0100+(heure+normale+d%E2%80%99Europe+centrale)&version=202405.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a5f163f6-bddc-4d1c-ac53-d288bfa8a7e2&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0002%3A1%2CC0003%3A1%2CV2STACK42%3A1&intType=1&geolocation=FR%3BARA&AwaitingReconsent=false; TATrkConsent=eyJvdXQiOiJTT0NJQUxfTUVESUEiLCJpbiI6IkFEVixBTkEsRlVOQ1RJT05BTCJ9; TASession=V2ID.49EC08096935B476C13BD1C3417BC7D2*SQ.1*LS.Restaurant_Review*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*FA.1*DF.0*TRA.true; TASID=49EC08096935B476C13BD1C3417BC7D2; TASameSite=1; __vt=m1olqFADRRWscutpABQCjdMFtf3dS_auw5cMBDN7STKvBs6K64Wmmo0WW1Kz0LVrYrr2eeEJ3lUf3HbDageoxc4SJ7Lpg2vj1M1-hVaCavYbF8Lx__HV9udogtXwUHASSYCHZqmAJVY4sy582efi-DQkvxc; _lr_env_src_ats=false; _lr_retry_request=true; PAC=ADRwXAbhdPZLzTNHaP1w9SsXdihCkgROaQ7VYf0i74IdTsK_BhDaooTUSzsjog_ScBFCLkIxemIuLrOeM0B-i2c48oyiIgav1OtAgq06dBLgv8_wk39BB-zpCfWNv7ZYQFZYJUM2wweWoe_7qMl8ZtMEH8gkTGlXvzFYiT04gCvx1haair7n8znOSuNvPlw7Sdkfr0aeV1XKnB2DMDUTKdyjt0a4t2X2SpGFI5DAfRGaDtktl6FoCNnHwpIWknrOWj2k6q1fbCcAinAwK-wngyg%3D; SRT=TART_SYNC; _lr_sampling_rate=100; pbjs_unifiedID=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222025-01-08T19%3A44%3A50%22%7D; pbjs_unifiedID_cst=qiw%2BLJcs6g%3D%3D; OTAdditionalConsentString=1~43.46.55.61.70.83.89.93.108.117.122.124.135.143.144.147.149.159.192.196.211.228.230.239.259.266.286.291.311.318.320.322.323.327.367.371.385.394.397.407.415.424.430.436.445.486.491.494.495.522.523.540.550.559.560.568.574.576.584.587.591.737.802.803.820.821.839.864.899.904.922.931.938.979.981.985.1003.1027.1031.1040.1046.1051.1053.1067.1092.1095.1097.1099.1107.1135.1143.1149.1152.1162.1166.1186.1188.1205.1215.1226.1227.1230.1252.1268.1270.1276.1284.1290.1301.1307.1312.1345.1356.1375.1403.1415.1416.1421.1423.1440.1449.1455.1495.1512.1516.1525.1540.1548.1555.1558.1570.1577.1579.1583.1584.1591.1603.1616.1638.1651.1653.1659.1667.1677.1678.1682.1697.1699.1703.1712.1716.1721.1725.1732.1745.1750.1765.1782.1786.1800.1810.1825.1827.1832.1838.1840.1842.1843.1845.1859.1866.1870.1878.1880.1889.1899.1917.1929.1942.1944.1962.1963.1964.1967.1968.1969.1978.1985.1987.2003.2008.2027.2035.2039.2047.2052.2056.2064.2068.2072.2074.2088.2090.2103.2107.2109.2115.2124.2130.2133.2135.2137.2140.2147.2150.2156.2166.2177.2186.2205.2213.2216.2219.2220.2222.2225.2234.2253.2279.2282.2292.2305.2309.2312.2316.2322.2325.2328.2331.2335.2336.2337.2343.2354.2358.2359.2370.2376.2377.2387.2400.2403.2405.2407.2411.2414.2416.2418.2425.2440.2447.2461.2465.2468.2472.2477.2481.2484.2486.2488.2493.2498.2501.2510.2517.2526.2527.2532.2535.2542.2552.2563.2564.2567.2568.2569.2571.2572.2575.2577.2583.2584.2596.2604.2605.2608.2609.2610.2612.2614.2621.2628.2629.2633.2636.2642.2643.2645.2646.2650.2651.2652.2656.2657.2658.2660.2661.2669.2670.2677.2681.2684.2687.2690.2695.2698.2713.2714.2729.2739.2767.2768.2770.2772.2784.2787.2791.2792.2798.2801.2805.2812.2813.2816.2817.2821.2822.2827.2830.2831.2834.2838.2839.2844.2846.2849.2850.2852.2854.2860.2862.2863.2865.2867.2869.2873.2874.2875.2876.2878.2880.2881.2882.2883.2884.2886.2887.2888.2889.2891.2893.2894.2895.2897.2898.2900.2901.2908.2909.2916.2917.2918.2919.2920.2922.2923.2927.2929.2930.2931.2940.2941.2947.2949.2950.2956.2958.2961.2963.2964.2965.2966.2968.2973.2975.2979.2980.2981.2983.2985.2986.2987.2994.2995.2997.2999.3000.3002.3003.3005.3008.3009.3010.3012.3016.3017.3018.3019.3025.3028.3034.3038.3043.3052.3053.3055.3058.3059.3063.3066.3068.3070.3073.3074.3075.3076.3077.3089.3090.3093.3094.3095.3097.3099.3100.3106.3109.3112.3117.3119.3126.3127.3128.3130.3135.3136.3145.3150.3151.3154.3155.3163.3167.3172.3173.3182.3183.3184.3185.3187.3188.3189.3190.3194.3196.3209.3210.3211.3214.3215.3217.3219.3222.3223.3225.3226.3227.3228.3230.3231.3234.3235.3236.3237.3238.3240.3244.3245.3250.3251.3253.3257.3260.3270.3272.3281.3288.3290.3292.3293.3296.3299.3300.3306.3307.3309.3314.3315.3316.3318.3324.3328.3330.3331.3531.3731.3831.4131.4531.4631.4731.4831.5231.6931.7235.7831.7931.8931.9731.10231.10631.10831.11031.11531.12831.13632.13731.14237.14332.15731.16831.16931.21233.23031.25131.25731.25931.26031.26831.27731.27831.28031.28731.28831.29631.31631.32531.33631.34231.34631.36831.39131.39531; OptanonAlertBoxClosed=2025-01-08T19:44:49.268Z; eupubconsent-v2=CQK6PNgQK6PNgAcABBFRBXFsAP_gAEPgACiQKvtX_C5ebWli8XZUIbtkaYwP55gz4kQhBhaIEewFwBOG7BgCB2EwNAV4JiACGBAAkiDBAQNlGABUAQAAAIgRiSCMYEyEgTNKJKBAiFMRM0NYCBxmmoFDWQCY5kqssxdxmBeAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAA_cff_9Pn_-uB_-_X_vf_H34KvgEmChUQAlgSEBAoGEECAAQRhARQAAgAASAoAIAQBAE7AgAHWEgAAAIAAQAAAAAgiABAAAJAAhEAAABAIAAABAIAAwAABgIACBAABABYAAQAAgGgIBAQQCAYAIGIFQpgQBAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANoytMCwfMFz2mAZIEQRk5JoBQIASADoALgA2QCIAGEAToAuQBtgEDggAYAHQArgCIAGEAToBA4MAHAB0AFwAbIBEADCALkAgcIADgA6AGyARAAwgCdAFyAQOFAAwAuAGEAgcMABAGEAgcOADAA6AIgAYQBOgEDgIrkAAQBhAIHEgAYBEADCAQOKABQAdAEQAMIAnQCBwAAA.f_wACHwAAAAA; pbjs_sharedId=e4d28e9a-1141-43e1-8c79-53abb5694a90; pbjs_sharedId_cst=qiw%2BLJcs6g%3D%3D; TART=%1%enc%3ACsCRrudfUa4vaA2HcdgbZCRT5oevlI8oeiCbtmMOj9m99yFc3Trn9P04iFh5gtLjJjJiwUHPBz0%3D; TASSK=enc%3AADnwyPyeGAncpUBvsXBZPRGHYBH68uYuk4ee0U5XHUJzdZEpM%2FV4DscG3Vw7GaoFra3iVJ5zkDjRPAe5BoOUDJIAzOrGYKaifTGxIXu2potQ%2BB3IM%2BEdo%2F8uXyVPX4ndcw%3D%3D; VRMCID=%1%V1*id.10568*llp.%2FRestaurant_Review-g187265-d695217-Reviews-Brasserie_Georges-Lyon_Rhone_Auvergne_Rhone_Alpes%5C.html*e.1736970285504; TAUnique=%1%enc%3AMiZPBMSkXxCvIWsmdEqiUo4SYGmsOfGa0jz64A1voxAgE3t%2FyetRjHhqCDipPLBxNox8JbUSTxk%3D; TADCID=oG5XiakeKCtV_IzdABQCrj-Ib21-TgWwDB4AzTFpg4LObZUiAdr0T_4EAlxKpFYgBUZ8QRR4MnITpG6mGN9Dss1-COMFh8cxe84",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

        #Initialisation 
        description = []
        nom_resto = []
        
        #Récupère le code html du site
        response = requests.get(self.base_url, headers = headers)
        if response.status_code != 200:
            raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")

        #Parser avec BS4
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        ##### NOM RESTO #####
        borne_nom = soup.find_all('h1', {'class' : 'biGQs _P hzzSG rRtyp'})
            
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
