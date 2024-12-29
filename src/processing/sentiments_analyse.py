from textblob import TextBlob

def sentiments_analyse(avis : list[str], join : bool = True) -> list[dict]:
    '''
    Cette fonction permet de faire une analyse des sentiments du texte

    Paramètres : 
        - avis : Liste de chaines de caractères représentant les avis
        - join : Possibilité de joindre tout les avis ensemble pour avoir la polarité et le sentiment de l'ensemble des avis
    
    Retourne : 
        - results : une liste avec le/les dictionnaire(s) contenant la polarité et la subjectivité du texte
    '''
    results = []

    #Regroupement des avis dans un texte uniforme 
    if join == True :
        full_avis = " ".join(avis)
        #Analyse des sentiments
        blob = TextBlob(full_avis)
        #Dictionnaire avec les résultats 
        sortie = {
            "Polarité" : blob.sentiment.polarity,
            "Subjectivité" : blob.sentiment.subjectivity
        }
        #Ajout dans la liste 
        results.append(sortie)

    else :
        for i in range(len(avis)) :
            full_avis = avis[i]
            #Analyse des sentiments
            blob = TextBlob(full_avis)
            #Dictionnaire avec les résultats 
            sortie = {
                "Polarité" : blob.sentiment.polarity,
                "Subjectivité" : blob.sentiment.subjectivity
            }
            #Ajout dans la liste 
            results.append(sortie)

    return results