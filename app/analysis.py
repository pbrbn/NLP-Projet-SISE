import streamlit as st
import pandas as pd
import os
import sys
# Définition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))

from processing.data_handler import DataHandler
from processing.text_preprocessor import TextPreprocessor
from processing.restaurant_classifier import RestaurantClassifier
from processing.review_clusterer import ReviewClusterer
from processing.sentiment_analyzer import SentimentAnalyzer
from processing.visualizer import Visualizer
from processing.keyword_extractor import KeywordExtractor



# Chemin du fichier de données
data_path = "../data/DataClean/restaurants.csv"

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv(data_path)
    # Conversion des notes en float (remplacement des virgules par des points)
    df['note_moyenne'] = df['note_moyenne'].str.replace(',', '.').astype(float)
    return df

df = load_data()

# Titre principal
st.title('Restaurant Review Analysis')

# Filtrer les données pour obtenir une seule ligne par restaurant
restaurant_list = df[['nom', 'type_cuisine', 'fourchette_prix', 'note_moyenne']].drop_duplicates(subset=['nom'])

# Sélection du restaurant
selected_restaurant = st.selectbox("Sélectionnez un restaurant :", restaurant_list['nom'])

# Filtrer les informations du restaurant sélectionné
restaurant_data = restaurant_list[restaurant_list['nom'] == selected_restaurant].iloc[0]

# Afficher les informations du restaurant sélectionné
st.subheader('Restaurant Information')
st.write(f"Cuisine Type: {restaurant_data['type_cuisine']}")
st.write(f"Price Range: {restaurant_data['fourchette_prix']}")
st.write(f"Average Rating: {restaurant_data['note_moyenne']:.2f}")

# Filtrer les avis pour le restaurant sélectionné
restaurant_reviews = df[df['nom'] == selected_restaurant]

# Analyse des sentiments
analyzer = SentimentAnalyzer()
sentiments = analyzer.analyze_sentiments(restaurant_reviews['commentaire'].tolist())
polarities = [s['Polarité'] for s in sentiments]
subjectivities = [s['Subjectivité'] for s in sentiments]

average_polarity = sum(polarities) / len(polarities) if polarities else 0
average_subjectivity = sum(subjectivities) / len(subjectivities) if subjectivities else 0

st.subheader('Sentiment Analysis')
st.write(f"Average Polarity: {average_polarity:.2f}")
st.write(f"Average Subjectivity: {average_subjectivity:.2f}")


