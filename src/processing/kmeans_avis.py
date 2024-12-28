from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
from processing import preprocess_reviews
from sentiments_analyse import sentiments_analyse
from mots_cles_liste_avis import aggreger_mots_cles
import pandas as pd
import spacy

def clustering_avis(avis : list[str], vector_size : int = 100, n_clusters : int = 3, top_n:int = 5) : 
    ''' 
    Cette  fonction entraine un modèle K-Means à partir d'une sortie Doc2Vec sur une liste d'avis. 
    Elle permet ensuite d'extraire l'analyse des sentiments et les mots clés pour chaque clusters.

    Arguments :
        - avis : Liste de str correspondant à la liste d'avis.
        - vector_size : int correspondant a la taille des vecteurs du modèle Doc2Vec
        - n_clusters : int correspondant au nombre de clusters désirés. (3 par défaut)
        - top_n : int correspondant aux nombres de mots clés à extraire. (5 par défaut)

    Retourne : 
        - Un DataFrame pandas avec pour chaque cluster : 
            - Numéro du cluster
            - Le nombre d'avis 
            - La polarité des avis 
            - La subjectivité des avis 
            - Les mots clés des avis

    '''
    ##### PRE-PROCESSING AVIS #####

    clean_avis = preprocess_reviews(avis)

    #Tokenistion
    #Passage en liste de liste 
    cleaned_avis_liste = [avis.split(",") for avis in clean_avis]
    nlp = spacy.load('fr_core_news_sm')

    #Tokenisation des listes de listes 
    tokenized_avis_liste = [
        [token.text for avis in sous_liste for token in nlp(avis)]
        for sous_liste in cleaned_avis_liste
    ]


    ##### DOC2VEC #####

    #Création de la liste de TaggedDocument
    avis_numerotes = [TaggedDocument(avis, [i]) for i, avis in enumerate(tokenized_avis_liste)]

    #Initialisation du modèle Doc2Vec
    model = Doc2Vec(vector_size=vector_size, window=2, min_count=1, workers=4, epochs=10)

    #Entraînement du modèle avec les avis tokenisés
    model.build_vocab(avis_numerotes)
    model.train(avis_numerotes, total_examples=model.corpus_count, epochs=model.epochs)


    ##### K-MEANS #####

    #Vecteurs des avis 
    Vecs = [model.dv[i] for i in range(len(tokenized_avis_liste))]

    #Appliquer KMeans pour regrouper les avis en clusters
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(Vecs)

    #Récupérer les étiquettes des clusters pour chaque avis
    labels = kmeans.labels_

    #Extraire les avis de chaque clusters 
    liste_avis_clusters = []
    for i in range (n_clusters) : 
        liste_avis_clusters.append([avis for j, avis in enumerate(cleaned_avis_liste) if labels[j] == i])

    #Conversion en listes plates
    clean_liste_clusters = []
    for i in range (n_clusters) : 
        clean_liste_clusters.append([element for sous_liste in liste_avis_clusters[i] for element in sous_liste])

    
    ##### ANALYSE DES CLUSTERS #####

    #ANALYSE DES SENTIMENTS 
    analyse_sent = []
    for i in clean_liste_clusters : 
        sentiments = sentiments_analyse(i)
        analyse_sent.append(sentiments)

    #MOTS-CLES 
    mots_cles = []
    for i in clean_liste_clusters : 
        mots_cles_avis = aggreger_mots_cles(i, top_n=top_n)
        mots_cles.append(mots_cles_avis)


    ##### SORTIE #####

    #Construction du DataFrame
    data = []
    for i in range(len(analyse_sent)):
        mots_cles_format = ', '.join([f"{mot} ({score:.2f})" for mot, score in mots_cles[i]])
        data.append({
            "Cluster": f"Cluster {i + 1}",
            "Nombres d'avis" : len(liste_avis_clusters[i]),
            "Polarité": analyse_sent[i]['Polarité'],
            "Subjectivité": analyse_sent[i]['Subjectivité'],
            "Mots Clés": mots_cles_format,
        })

    df = pd.DataFrame(data)

    return df