import re
import spacy
from nltk.corpus import stopwords
import pandas as pd
from sqlalchemy import create_engine
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
# Charger le modèle spaCy pour le français
nlp = spacy.load("fr_core_news_sm")

def preprocess_reviews(reviews):
    """
    Nettoie et prépare les avis pour le traitement NLP.
    Utilise spaCy pour la lemmatisation et la suppression des stopwords/ponctuations.
    """
    processed_reviews = []
    stop_words = set(stopwords.words('french'))

    for avis in reviews:  # reviews est une liste de chaînes de caractères
        #Supprimer les mots de moins de 2 caractères 
        avis = re.sub(r'\b\w{1,2}\b', '', avis).strip()
        # Supression des chiffres 
        chiffres = list("0123456789")
        avis = "".join([w for w in list(avis) if not w in chiffres])
        # Suppression des retours à la ligne et des espaces supplémentaires
        avis = re.sub(r'\r\n|\r|\n', ' ', avis)
        avis = re.sub(r'\s+', ' ', avis)
        # Conversion en minuscules
        avis = avis.lower()
        # Traiter le texte avec spaCy
        doc = nlp(avis)
        # Lemmatisation et suppression des stopwords et ponctuation
        cleaned_avis = " ".join([token.lemma_ for token in doc if token.text not in stop_words and not token.is_punct])
        
        # Ajouter l'avis nettoyé à la liste
        processed_reviews.append(cleaned_avis)
    
    return processed_reviews

# Combinaison et agrégation des datasets
def combine_and_aggregate(infos_avis, infos_resto):
    """Combine les datasets des avis et des restaurants, puis agrège les commentaires par restaurant."""
    # Combinaison des datasets
    merged_df = pd.merge(infos_avis, infos_resto, left_on='id_restaurant', right_on='id')
    
    # Agrégation des commentaires
    aggregated_df = merged_df.groupby(['id_x', 'nom'], as_index=False).agg({
        'commentaire': lambda comments: ' | '.join(comments),  # Joindre les commentaires
        'type_cuisine': 'first',                              # Garder une seule valeur par restaurant
        'fourchette_prix': 'first',
        'description': 'first',
        'adresse': 'first',
        'note_moyenne': 'first'
    })

    # Renommer id_x pour plus de clarté
    aggregated_df.rename(columns={'id_x': 'id_restaurant'}, inplace=True)
    return aggregated_df

# Sauvegarde des données prétraitées dans un fichier CSV
def save_preprocessed_data(data, filename):
    """Sauvegarde les données prétraitées dans un fichier CSV."""
    df = pd.DataFrame(data, columns=['text'])
    df.to_csv(filename, index=False)


# Sauvegarde dans une base SQLite
def save_to_sqlite(df, db_name, table_name):
    """Sauvegarde un DataFrame dans une base de données SQLite."""
    engine = create_engine(f'sqlite:///{db_name}')
    with engine.connect() as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Données sauvegardées dans la table '{table_name}' de la base '{db_name}'.")

print("Processing module loaded successfully!")
print("You can now use the functions preprocess_reviews, save_preprocessed_data, create_dtm and generate_wordcloud.")