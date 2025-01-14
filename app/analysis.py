import streamlit as st
import pandas as pd
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
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Charger le modèle de langue française de spaCy
nlp = spacy.load('fr_core_news_md')

# Définition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))

from processing.data_handler import DataHandler
from processing.text_preprocessor import TextPreprocessor
from processing.restaurant_classifier import RestaurantClassifier
from processing.review_clusterer import ReviewClusterer
from processing.sentiment_analyzer import SentimentAnalyzer
from processing.visualizer import Visualizer
from processing.keyword_extractor import KeywordExtractor

data_path = "../data/DataClean/restaurants_data.csv"

def load_data():
    """Charge les données depuis le CSV et convertit la note en float."""
    df = pd.read_csv(data_path)
    return df

df = load_data()

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
    cuisines = df['type_cuisine'].str.split(', ').explode()
    types_uniques = sorted(cuisines.unique())

    fourchettes_prix = ["Toutes les fourchettes"]
    valid_fourchettes = sorted(df['fourchette_prix'].dropna().unique().tolist())
    fourchettes_prix.extend([f for f in valid_fourchettes if f != ""])

    selected_cuisine = st.sidebar.selectbox("Type de cuisine", types_uniques, index=2)
    selected_prix = st.sidebar.selectbox("Fourchette de prix", fourchettes_prix)

    note_min = st.sidebar.number_input("Note minimum", min_value=0.0, max_value=5.0, value=0.0)

    filtered_df = df[df['type_cuisine'].str.contains(selected_cuisine)]
    filtered_df = filter_by_price_range(filtered_df, selected_prix)
    filtered_df = filtered_df[filtered_df['note_moyenne_resto'].astype(float) >= note_min]

    return filtered_df

# Coordonnées par défaut : Université Lumière Lyon 2, Campus de Bron
DEFAULT_LATITUDE = 45.7324
DEFAULT_LONGITUDE = 4.9116

def get_user_location():
    """Utilise JavaScript pour récupérer la position géographique de l'utilisateur."""
    st.write(
        "Nous aimerions accéder à votre position pour afficher la distance jusqu'aux restaurants. "
        "Vous pouvez accepter ou refuser cette demande. Si vous refusez, des coordonnées par défaut seront utilisées."
    )
    location = streamlit_js_eval(js_extras="geolocation", key="user_location")
    if location and "coords" in location:
        latitude = location["coords"]["latitude"]
        longitude = location["coords"]["longitude"]
        return latitude, longitude
    return DEFAULT_LATITUDE, DEFAULT_LONGITUDE

def display_restaurant_information(restaurant_data, user_location):
    """Affiche les informations sur le restaurant et une carte avec la localisation."""
    st.title('Restaurant Review Analysis')
    st.subheader('Restaurant Information')
    st.write(f"**Nom du restaurant**: {restaurant_data['nom_resto']}")
    st.write(f"**Type de cuisine**: {restaurant_data['type_cuisine']}")
    st.write(f"**Fourchette de prix**: {restaurant_data['fourchette_prix']}")
    st.write(f"**Note moyenne**: {restaurant_data['note_moyenne_resto']}")

    restaurant_coords = (restaurant_data['latitude'], restaurant_data['longitude'])

    # Distance et temps estimés
    if user_location:
        distance_km = geodesic(user_location, restaurant_coords).kilometers
        estimated_time = distance_km / 50 * 60  # 50 km/h en moyenne
        st.write(f"**Distance estimée** : {distance_km:.2f} km")
        st.write(f"**Temps estimé** : {estimated_time:.0f} minutes")
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
    st.subheader('Sentiment Analysis')
    st.write(f"Average Polarity: {average_polarity}")
    st.write(f"Average Subjectivity: {average_subjectivity}")

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
                colormap='viridis',
                max_words=200
            ).generate(all_text)
            
            # Récupérer les mots et leurs fréquences
            word_list = list(wordcloud.words_.keys())
            freq_list = list(wordcloud.words_.values())
            
            # Définir les couleurs pour les mots
            colors = [f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.7)" for _ in range(len(word_list))]
            
            # Créer une disposition aléatoire des mots
            x_coords = np.random.uniform(low=-1, high=1, size=len(word_list))
            y_coords = np.random.uniform(low=-1, high=1, size=len(word_list))
            
            # Créer la figure Plotly
            fig = go.Figure(data=[go.Scatter(
                x=x_coords,
                y=y_coords,
                mode="text",
                text=word_list,
                hoverinfo="text",
                textfont=dict(
                    size=[f * 70 for f in freq_list],
                    color=colors
                )
            )])
            
            # Personnaliser l'apparence de la figure
            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                margin=dict(l=0, r=0, t=0, b=0),
                hovermode='closest'
            )
            
            # Afficher la figure dans Streamlit
            st.plotly_chart(fig)
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

def page_analyse_restaurant():
    st.sidebar.title("Restaurant Review Analysis")
    st.sidebar.write("Welcome to the Restaurant Review Analysis app!")
    st.sidebar.write("Select a restaurant from the dropdown menu to view detailed information and sentiment analysis.")
    
    filtered_df = filter_restaurants(df)
    
    if filtered_df.empty:
        st.warning("Aucun restaurant ne correspond à vos critères de sélection.")
        return
    
    selected_restaurant = st.sidebar.selectbox("Choose a restaurant:", filtered_df["nom_resto"].unique())
    
    restaurant_data = filtered_df[filtered_df['nom_resto'] == selected_restaurant].iloc[0]
    user_location = get_user_location()
    display_restaurant_information(restaurant_data, user_location)
    analyze_restaurant(df, selected_restaurant)

if __name__ == '__main__':
   page_analyse_restaurant()

