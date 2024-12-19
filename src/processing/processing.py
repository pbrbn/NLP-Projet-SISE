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
        'adresse': 'first',
        'note_moyenne': 'first'
    })

    # Renommer id_x pour plus de clarté
    # Renommer id_x pour plus de clarté
    aggregated_df.rename(columns={'id_x': 'id_restaurant'}, inplace=True)
    return aggregated_df

# Sauvegarde des données prétraitées dans un fichier CSV
def save_preprocessed_data(data, filename):
    """Sauvegarde les données prétraitées dans un fichier CSV."""
    df = pd.DataFrame(data, columns=['text'])
    df.to_csv(filename, index=False)

# Création de matrice Documents-Termes
def create_dtm(corpus, method='tfidf'):
    """Crée une matrice documents-termes à partir d'un corpus."""
    if method == 'tfidf':
        vectorizer = TfidfVectorizer()
    else:
        vectorizer = CountVectorizer()
    dtm = vectorizer.fit_transform(corpus)
    return dtm, vectorizer

# Génération de nuage de mots
def generate_wordcloud(corpus):
    """Génère et affiche un nuage de mots à partir d'un corpus."""
    text = ' '.join(corpus)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

print("Processing module loaded successfully!")
print("You can now use the functions preprocess_reviews, save_preprocessed_data, create_dtm and generate_wordcloud.")