from textblob import TextBlob

def sentiments_analyse(avis : list[str]) -> dict:
    '''
    Cette fonction permet de faire uen analyse des sentiments du texte
    Elle prend en entrée une liste d'avis 
    Elle retourne en sortie un dictionnaire contenant : 
        - La polarité de la totalité des avis 
        - La subjectivité de la totalité des avis
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