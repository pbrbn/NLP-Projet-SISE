from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def extraire_mots_cles(avis: list[str], top_n: int = 5) -> dict:
    """
    Extrait les mots-clés les plus significatifs à partir d'une liste d'avis en utilisant TF-IDF.

    Paramètres : 
        - avis: Liste de chaînes de caractères représentant les avis.
        - top_n: Nombre de mots-clés à extraire pour chaque avis.
    Retourne : 
        - mots_cle_par_avis : Dictionnaire contenant les mots-clés et leurs scores TF-IDF pour chaque avis.
    """

    #Initialiser le vecteur TF-IDF
    tfidf_vectorizer = TfidfVectorizer( 
        max_features=1000, #Limiter aux 1000 mots les plus fréquents
        lowercase=True,       
        ngram_range=(1, 2) #Considérer les mots simples et les paires de mots (bigrammes)
    )
    
    #Ajuster et transformer les données
    tfidf_matrix = tfidf_vectorizer.fit_transform(avis)
    
    #Obtenir les noms des mots (vocabulaire)
    mots = tfidf_vectorizer.get_feature_names_out()
    
    mots_cle_par_avis = {}
    
    #Parcourir chaque avis pour extraire les top_n mots-clés
    for index, ligne in enumerate(tfidf_matrix):
        #Convertir les scores TF-IDF pour cet avis en DataFrame
        scores = pd.DataFrame({
            "mot": mots,
            "score": ligne.toarray().flatten()
        })
        #Trier par score décroissant et sélectionner les top_n mots
        top_keywords = scores.sort_values(by="score", ascending=False).head(top_n)
        mots_cle_par_avis[f"Avis {index + 1}"] = list(zip(top_keywords["mot"], top_keywords["score"]))
    
    return mots_cle_par_avis