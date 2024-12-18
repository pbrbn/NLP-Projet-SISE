from textblob import TextBlob

def sentiments_analyse(avis : list[str]) -> dict:
    '''
    Cette fonction permet de faire une analyse des sentiments du texte

    Paramètres : 
        - avis : Liste de chaines de caractères représentant les avis
    
    Retourne : 
        - results : Dictionnaire contenant la polarité et la subjectivité du texte
    '''

    #Regroupement des avis dans un texte uniforme 
    full_avis = " ".join(avis)

    #Analyse des sentiments
    blob = TextBlob(full_avis)

    #Dictionnaire avec les résultats 
    results = {
        "Polarité" : blob.sentiment.polarity,
        "Subjectivité" : blob.sentiment.subjectivity
    }

    return results