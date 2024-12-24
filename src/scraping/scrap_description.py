import requests
from bs4 import BeautifulSoup
import pandas as pd

def description_resto(url :str) : 
    '''
    Scrape la description d'un restaurant à partir d'une URL de base.
    Arguments : 
        - url : une URL de la page web contenant les avis.
    
    Retourne : 
        - un dataframe pandas contenant : 
            - le nom du restaurant 
            - la description du restaurant
    '''

    #Ajouter un en-tête User-Agent pour simuler un navigateur
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

    #Récupère le contenu HTML de la page concernée
    response = requests.get(url, headers = headers)
    if response.status_code != 200:
        raise Exception(f"Échec de la récupération du contenu, code de statut : {response.status_code}")

    #Parser avec BS4
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    ##### NOM RESTO #####
    borne_nom = soup.find('h1', {'class' : 'biGQs _P hzzSG rRtyp'})
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
