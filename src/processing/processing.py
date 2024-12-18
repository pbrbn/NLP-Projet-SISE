# Préparation des bibliothèques
import sqlite3
import pandas as pd
import nltk
from bs4 import BeautifulSoup
import requests
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sqlalchemy import create_engine
nltk.download('punkt')
nltk.download('stopwords')


def preprocess_reviews(reviews):
    """
    Nettoie et prépare les avis pour le traitement NLP.
    """
    processed_reviews = []
    stop_words = set(stopwords.words('french'))

    for text in reviews:  # Ici, reviews est une liste de chaînes de caractères
        text = text.lower()  # Conversion en minuscule
        text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', text)  # Suppression des caractères spéciaux
        tokens = word_tokenize(text) # Tokenisation
        tokens = [word for word in tokens if word not in stop_words]  # Suppression des stopwords
        processed_reviews.append(' '.join(tokens)) # Reconstitution de la chaîne de caractères

    return processed_reviews


# Sauvegarde dans une base de données SQLite
def save_to_sqlite(df, db_name, table_name):
    """
    Sauvegarde un DataFrame dans une base SQLite.
    """
    engine = create_engine(f'sqlite:///{db_name}')
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
