from collections import defaultdict
from mots_cles_avis import extraire_mots_cles

def aggreger_mots_cles(avis : list[str], top_n=10) -> list:
    """
    Agrège les mots-clés extraits d'une liste d'avis pour obtenir les mots-clés globaux.

    Paramètres : 
        - avis: Liste de chaînes de caractères représentant les avis.
        - top_n: Nombre de mots-clés globaux à retourner.
    Retourne : 
        - mots_cles_globaux : Liste des top_n mots-clés avec leurs scores globaux.
    """
    # Appel de la fonction pour extraire les mots-clés par avis
    mots_cles_par_avis = extraire_mots_cles(avis)
    
    # Dictionnaire pour agréger les scores des mots-clés
    aggregation = defaultdict(float)
    
    # Parcourir les mots-clés de chaque avis
    for mots_cles in mots_cles_par_avis.values():
        for mot, score in mots_cles:
            aggregation[mot] += score  # Ajouter le score TF-IDF au mot
    
    # Trier les mots-clés agrégés par score décroissant
    mots_cles_globaux = sorted(aggregation.items(), key=lambda x: x[1], reverse=True)
    
    # Retourner les top_n mots-clés
    return mots_cles_globaux[:top_n]