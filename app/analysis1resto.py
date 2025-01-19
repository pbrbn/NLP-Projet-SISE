import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from textblob import TextBlob
import sqlite3
import spacy
import re
import numpy as np
from streamlit_js_eval import streamlit_js_eval
import random
import folium
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from geopy.distance import geodesic
from utils import conexion_db
from mistralai import Mistral
from dotenv import load_dotenv

# Charger le modèle de langue française de spaCy
nlp = spacy.load('fr_core_news_md')

# Définition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))

from processing.data_preprocessor import DataPreprocessor
from processing.keyword_extractor import KeywordExtractor
from processing.resume_avis import ResumerAvis
from processing.review_clusterer import ReviewClusterer

# Charger les variables d'environnement
load_dotenv()

def get_data_from_db(db_path):
    """Charge les données depuis la base de données."""
    return conexion_db(db_path)

# Chemin vers la DB
db_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'database.db'))
df = get_data_from_db(db_path)



# charger les données

#def load_data():
    #charger les données
#   df = pd.read_csv("data/data_100.csv")
#   return df


#df = load_data()

# Initialiser la classe ResumerAvis
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
resumer_avis = ResumerAvis(api_key=MISTRAL_API_KEY, type_query="analyze_clusters")

def extract_price_range(price_string):
    """Extrait les valeurs min et max d'une fourchette de prix"""
    numbers = re.findall(r'(\d+(?:,\d+)?)', price_string)
    if len(numbers) >= 2:
        min_price = float(numbers[0].replace(',', '.'))
        max_price = float(numbers[1].replace(',', '.'))
        return min_price, max_price
    return None, None

def filter_by_price_range(df, selected_range):
    """Filtre les restaurants selon la fourchette de prix sélectionnée"""
    if selected_range == "Toutes les fourchettes":
        return df

    selected_min, selected_max = extract_price_range(selected_range)
    if selected_min is None or selected_max is None:
        return df

    return df[
        ((df['prix_min'] >= selected_min) & (df['prix_min'] <= selected_max)) |
        ((df['prix_max'] >= selected_min) & (df['prix_max'] <= selected_max)) |
        ((df['prix_min'] <= selected_min) & (df['prix_max'] >= selected_max))
    ]

def filter_restaurants(df):
    # Diviser les cuisines et obtenir une liste unique triée
    cuisines = df['type_cuisine'].str.split(', ').explode()
    types_uniques = ["Toutes les cuisines"] + sorted(cuisine for cuisine in cuisines.unique() if cuisine)

    # Gérer les fourchettes de prix
    fourchettes_prix = ["Toutes les fourchettes"]
    valid_fourchettes = sorted(df['fourchette_prix'].dropna().unique().tolist())
    fourchettes_prix.extend([f for f in valid_fourchettes if f != ""])

    # Widgets Streamlit pour les sélections
    selected_cuisine = st.sidebar.selectbox("Type de cuisine", types_uniques)
    selected_prix = st.sidebar.selectbox("Fourchette de prix", fourchettes_prix)
    note_min = st.sidebar.number_input("Note minimum", min_value=0.0, max_value=5.0, value=0.0)

    # Filtrage du DataFrame
    if selected_cuisine != "Toutes les cuisines":
        filtered_df = df[df['type_cuisine'].str.contains(selected_cuisine, na=False)]
    else:
        filtered_df = df.copy()

    filtered_df = filter_by_price_range(filtered_df, selected_prix)
    filtered_df = filtered_df[filtered_df['note_moyenne_resto'].astype(float) >= note_min]

    return filtered_df

# Coordonnées par défaut : Université Lumière Lyon 2, Campus de Bron
DEFAULT_LATITUDE = 45.7324
DEFAULT_LONGITUDE = 4.9116

def get_user_location():
    """Utilise JavaScript pour récupérer la position géographique de l'utilisateur."""
    location = streamlit_js_eval(js_extras="geolocation", key="user_location")
    if location and "coords" in location:
        latitude = location["coords"]["latitude"]
        longitude = location["coords"]["longitude"]
        return latitude, longitude
    return DEFAULT_LATITUDE, DEFAULT_LONGITUDE

def display_restaurant_information(restaurant_data, user_location):
    """Affiche les informations sur le restaurant et une carte avec la localisation."""
    st.write(f"🏠 **Nom du restaurant**: {restaurant_data['nom_resto']}")
    st.write(f"🍳 **Type de cuisine**: {restaurant_data['type_cuisine']}")
    st.write(f"💰 **Fourchette de prix**: {restaurant_data['fourchette_prix']}")
    st.write(f"⭐ **Note moyenne**: {restaurant_data['note_moyenne_resto']}")

    restaurant_coords = (restaurant_data['latitude'], restaurant_data['longitude'])

    # Distance et temps estimés
    if user_location:
        distance_km = geodesic(user_location, restaurant_coords).kilometers
        estimated_time = distance_km / 50 * 60  # 50 km/h en moyenne
        st.write(f"🚗 **Distance estimée** : {distance_km:.2f} km")
        st.write(f"⏱️ **Temps estimé** : {estimated_time:.0f} minutes")

    else:
        st.warning("Impossible de calculer la distance sans localisation.")

    # Carte interactive
    st.subheader("Carte de l'emplacement")
    map_center = user_location if user_location else restaurant_coords
    map_ = folium.Map(location=map_center, zoom_start=13)

    # Marqueur restaurant
    folium.Marker(
        location=restaurant_coords,
        popup=f"{restaurant_data['nom_resto']} ({restaurant_data['type_cuisine']})",
        tooltip="Restaurant",
        icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
    ).add_to(map_)

    # Marqueur utilisateur (si localisation disponible)
    if user_location:
        folium.Marker(
            location=user_location,
            popup="Votre position (ou position par défaut)",
            tooltip="Vous êtes ici",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(map_)

    st_folium(map_, width=700, height=500)

def filter_reviews(df, selected_restaurant):
    """Filtre les avis pour le restaurant sélectionné."""
    return df[df['nom_resto'] == selected_restaurant]

def analyze_sentiments(reviews):
    """Analyse les sentiments (polarité, subjectivité) d'une liste de commentaires."""
    polarities = [TextBlob(review).sentiment.polarity for review in reviews]
    subjectivities = [TextBlob(review).sentiment.subjectivity for review in reviews]
    return (
        sum(polarities) / len(polarities) if polarities else 0,
        sum(subjectivities) / len(subjectivities) if subjectivities else 0,
        polarities,
    )

def display_sentiment_analysis(average_polarity, average_subjectivity):
    """Affiche la polarité et la subjectivité moyennes."""
    st.subheader('Analyse des sentiments')
    st.write(f"😊Polarité : {average_polarity:.2f}")
    st.write(f"😞 Subjectivité : {average_subjectivity:.2f}")


def plot_sentiment_distribution(polarities):
    """Affiche un histogramme de la distribution des polarités avec Plotly."""
    st.subheader("Distribution des sentiments")
    if polarities:
        fig = px.histogram(x=polarities, nbins=20, labels={'x': 'Polarité', 'y': 'Fréquence'},
                           title="Distribution des sentiments")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
    else:
        st.warning("Aucun sentiment n'a été calculé pour ce restaurant.")

def generate_wordcloud(reviews):
    st.subheader("Nuage de mots")
    if reviews:
        all_text = " ".join(reviews)
        if all_text.strip():
            # Générer le nuage de mots
            wordcloud = WordCloud(
                background_color='white',
                width=800,
                height=400,
                max_words=200
            ).generate(all_text)

            # Récupérer les mots et leurs fréquences
            word_list = list(wordcloud.words_.keys())
            freq_list = list(wordcloud.words_.values())

            # Définir les couleurs des mots en fonction de leur fréquence
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                # Appliquer une couleur en fonction de la fréquence du mot
                freq = wordcloud.words_[word]
                # Plus le mot est fréquent, plus il est foncé
                color_value = int(255 - freq * 255)
                return f"rgb({color_value}, {color_value}, {random.randint(0, 255)})"
            
            # Créer un nuage de mots avec la fonction de couleur personnalisée
            wordcloud = WordCloud(
                background_color='white',
                width=800,
                height=400,
                max_words=200,
                color_func=color_func  # Appliquer la fonction de couleur
            ).generate(all_text)

            # Afficher le nuage de mots
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis('off')

            # Afficher dans Streamlit
            st.pyplot(fig)
        else:
            st.warning("Le texte du nuage de mots est vide.")
    else:
        st.warning("Aucun avis disponible pour générer un nuage de mots.")

def analyze_restaurant(df, selected_restaurant):
    """Gère l'analyse complète pour le restaurant sélectionné."""
    restaurant_reviews = filter_reviews(df, selected_restaurant)
    if not restaurant_reviews.empty:
        avg_polarity, avg_subjectivity, polarities = analyze_sentiments(
            restaurant_reviews['commentaire'].tolist()
        )
        display_sentiment_analysis(avg_polarity, avg_subjectivity)
        plot_sentiment_distribution(polarities)
        generate_wordcloud(restaurant_reviews['commentaire'].tolist())
    else:
        st.warning("Aucun avis disponible pour ce restaurant.")

def analyse_restaurant():
    st.title("Analyse d'un restaurant")
    st.sidebar.title("Sélection du restaurant")

    filtered_df = filter_restaurants(df)

    if filtered_df.empty:
        st.warning("Aucun restaurant ne correspond à vos critères de sélection.")
        return

    selected_restaurant = st.sidebar.selectbox("Choose a restaurant:", filtered_df["nom_resto"].unique())

    restaurant_data = filtered_df[filtered_df['nom_resto'] == selected_restaurant].iloc[0]
    user_location = get_user_location()
    display_restaurant_information(restaurant_data, user_location)

    restaurant_reviews = filter_reviews(df, selected_restaurant)
    if not restaurant_reviews.empty:
        avg_polarity, avg_subjectivity, polarities = analyze_sentiments(
            restaurant_reviews['commentaire'].tolist()
        )
        display_sentiment_analysis(avg_polarity, avg_subjectivity)
        plot_sentiment_distribution(polarities)
    else:
        st.warning("Aucun avis disponible pour ce restaurant.")

    if not restaurant_reviews.empty:
        generate_wordcloud(restaurant_reviews['commentaire'].tolist())
    else:
        st.warning("Aucun avis disponible pour générer un nuage de mots.")

    if not restaurant_reviews.empty:
        clustering_interface(restaurant_reviews)
    else:
        st.warning("Aucun avis disponible pour générer un nuage de mots.")

def clustering_interface(restaurant_reviews):
    st.subheader("Clustering des Avis")
    st.subheader("Analysez les avis en clusters.")

    # Initialisation
    clusterer = ReviewClusterer()
    clustering_result = None

    # Bouton pour lancer le clustering
    if st.button("Lancer le clustering"):
        with st.spinner("Clustering en cours..."):
            try:
                avis = restaurant_reviews['commentaire'].tolist()
                clustering_result = clusterer.cluster_reviews(avis, n_clusters=3)
                st.subheader("Résultats du clustering")
                st.dataframe(clustering_result[0])
                #Résumé avec LLM      
                avis_clusters = clustering_result[1].iloc[:, 1].tolist()
                resultat = resumer_avis.generer_resume(avis_restaurant_1=["ignore"], avis_restaurant_2=["ignore"], avis_clusters=avis_clusters)
                st.subheader(f"Analyse des clusters :")
                st.write(resultat)

            except Exception as e:
                st.error(f"Erreur lors du clustering : {str(e)}")

if __name__ == '__main__':
    analyse_restaurant()