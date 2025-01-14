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

# Extraction des prix

def extract_price_range(price_string):
    numbers = re.findall(r'(\d+(?:,\d+)?)', price_string)
    if len(numbers) >= 2:
        min_price = float(numbers[0].replace(',', '.'))
        max_price = float(numbers[1].replace(',', '.'))
        return min_price, max_price
    return None, None

# Filtrer les restaurants

def filter_by_price_range(df, selected_range):
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

def get_user_location():
    st.write("Nous aimerions accéder à votre position pour afficher la distance jusqu'aux restaurants.")
    location = streamlit_js_eval(js_extras="geolocation", key="user_location")
    if location and "coords" in location:
        latitude = location["coords"]["latitude"]
        longitude = location["coords"]["longitude"]
        return latitude, longitude
    return 45.7324, 4.9116

def display_comparison(restaurants_data, user_location):
    """Affiche une comparaison entre deux restaurants."""
    col1, col2 = st.columns(2)

    for i, col in enumerate([col1, col2]):
        if i < len(restaurants_data):
            restaurant = restaurants_data[i]
            col.subheader(restaurant['nom_resto'])
            col.write(f"**Type de cuisine**: {restaurant['type_cuisine']}")
            col.write(f"**Fourchette de prix**: {restaurant['fourchette_prix']}")
            col.write(f"**Note moyenne**: {restaurant['note_moyenne_resto']}")

            restaurant_coords = (restaurant['latitude'], restaurant['longitude'])
            distance_km = geodesic(user_location, restaurant_coords).kilometers
            col.write(f"**Distance estimée** : {distance_km:.2f} km")

            map_ = folium.Map(location=user_location, zoom_start=13)
            folium.Marker(
                location=restaurant_coords,
                popup=f"{restaurant['nom_resto']} ({restaurant['type_cuisine']})",
                tooltip="Restaurant",
                icon=folium.Icon(color="red", icon="cutlery", prefix="fa")
            ).add_to(map_)
            st_folium(map_, width=350, height=300, key=f"map_{i}")

def page_2_restaurants():
    st.sidebar.title("Comparer deux restaurants")

    filtered_df = filter_restaurants(df)

    if filtered_df.empty:
        st.warning("Aucun restaurant ne correspond à vos critères de sélection.")
        return

    restaurant_choices = st.sidebar.multiselect(
        "Sélectionnez deux restaurants à comparer:", 
        filtered_df['nom_resto'].unique(), 
        max_selections=2
    )

    if len(restaurant_choices) == 2:
        restaurants_data = [filtered_df[filtered_df['nom_resto'] == name].iloc[0] for name in restaurant_choices]
        user_location = get_user_location()
        display_comparison(restaurants_data, user_location)
    else:
        st.info("Veuillez sélectionner exactement deux restaurants à comparer.")

if __name__ == '__main__':
    page_2_restaurants()
