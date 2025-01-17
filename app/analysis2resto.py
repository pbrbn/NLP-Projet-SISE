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
from folium import plugins
from geopy.distance import geodesic
from utils import conexion_db
nlp = spacy.load('fr_core_news_md')

# Définition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))
from processing.sentiment_analyzer import SentimentAnalyzer
from processing.keyword_extractor import KeywordExtractor
from processing.resume_avis import ResumerAvis

@st.cache_data
def get_data_from_db(db_path):
    """Charge les données depuis la base de données et les met en cache."""
    return conexion_db(db_path)

# Chemin vers la DB
db_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'database.db'))
df = get_data_from_db(db_path)



# charger les données

#def load_data():
    #charger les données
  
#   df = pd.read_csv("data/data_100.csv")
#   return df


# df = load_data()


# Extraction des prix
def extract_price_range(price_string):
    """Extrait les valeurs min et max d'une fourchette de prix"""
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
    # Remplacer les valeurs manquantes par une chaîne vide avant de traiter les types de cuisine
    df['type_cuisine'] = df['type_cuisine'].fillna('')

    # Diviser les cuisines et obtenir une liste unique triée
    cuisines = df['type_cuisine'].str.split(', ').explode()
    types_uniques = ["Toutes les cuisines"] + sorted(cuisine for cuisine in cuisines.unique() if cuisine)

    # Gérer les fourchettes de prix
    fourchettes_prix = ["Toutes les fourchettes"]
    valid_fourchettes = sorted(df['fourchette_prix'].dropna().unique().tolist())
    fourchettes_prix.extend([f for f in valid_fourchettes if f != ""])

    # Widgets Streamlit pour les sélections
    selected_cuisine = st.sidebar.selectbox("Type de cuisine", types_uniques, index=0)
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



def get_user_location():
    st.write("Nous aimerions accéder à votre position pour afficher la distance jusqu'aux restaurants.")
    location = streamlit_js_eval(js_extras="geolocation", key="user_location")
    if location and "coords" in location:
        latitude = location["coords"]["latitude"]
        longitude = location["coords"]["longitude"]
        return latitude, longitude
    return 45.7324, 4.9116


def generate_wordcloud(text_data: str, title: str = "Word Cloud", width: int = 800, height: int = 400, background_color: str = 'white', colormap: str = 'plasma', max_words: int = 200) -> go.Figure:
    """
    Génère un nuage de mots à partir des données textuelles.

    Args:
        text_data: Texte pour générer le nuage de mots
        title: Titre du nuage de mots
        width: Largeur de l'image
        height: Hauteur de l'image
        background_color: Couleur de fond
        colormap: Palette de couleurs à utiliser
        max_words: Nombre maximum de mots à afficher

    Returns:
        go.Figure: Figure Plotly du nuage de mots
    """
    if not text_data or not isinstance(text_data, str):
        raise ValueError("Le texte fourni doit être une chaîne non vide")

    try:
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=max_words
        ).generate(text_data)

        fig = px.imshow(wordcloud.to_array(), title=title)
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        return fig

    except Exception as e:
        st.error(f"Erreur lors de la génération du nuage de mots: {str(e)}")
        raise

def comparaison_deux_resto():
    st.title("Comparaison de deux restaurants")
    st.sidebar.title("Sélection des restaurants")
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

        col1, col2 = st.columns(2)

        # Créer une carte unique pour les deux restaurants
        map_center = user_location if user_location else (45.75, 4.85)  # Centre par défaut sur Lyon
        map_ = folium.Map(location=map_center, zoom_start=12)

        colors = ['red', 'green']
        for i, (restaurant, col, color) in enumerate(zip(restaurants_data, [col1, col2], colors)):
            col.subheader(restaurant['nom_resto'])
            col.write(f"**Type de cuisine**: {restaurant['type_cuisine']}")
            col.write(f"**Fourchette de prix**: {restaurant['fourchette_prix']}")
            col.write(f"**Note moyenne**: {restaurant['note_moyenne_resto']}")

            restaurant_coords = (restaurant['latitude'], restaurant['longitude'])

            # Distance et temps estimés
            if user_location:
                distance_km = geodesic(user_location, restaurant_coords).kilometers
                estimated_time = distance_km / 50 * 60  # 50 km/h en moyenne
                col.write(f"**Distance estimée** : {distance_km:.2f} km")
                col.write(f"**Temps estimé** : {estimated_time:.0f} minutes")

            # Marqueur restaurant
            folium.Marker(
                location=restaurant_coords,
                popup=f"{restaurant['nom_resto']} ({restaurant['type_cuisine']})",
                tooltip=restaurant['nom_resto'],
                icon=folium.Icon(color=color, icon="cutlery", prefix="fa")
            ).add_to(map_)

            # Générer et afficher le nuage de mots pour ce restaurant
            reviews = df[df['nom_resto'] == restaurant['nom_resto']]['commentaire'].tolist()
            if reviews:
                all_text = " ".join(reviews)
                if all_text.strip():
                    fig = generate_wordcloud(all_text, title=f"Nuage de mots pour {restaurant['nom_resto']}")
                    col.plotly_chart(fig)

        # Marqueur utilisateur (si localisation disponible)
        if user_location:
            folium.Marker(
                location=user_location,
                popup="Votre position",
                tooltip="Vous êtes ici",
                icon=folium.Icon(color="blue", icon="cutlery", prefix="fa")
            ).add_to(map_)

        # Afficher la carte
        st.subheader("Carte des restaurants")
        st_folium(map_, width=700, height=500)

        # Appel du graphique de comparaison
        fig = plot_comparison_chart(restaurants_data)
        st.plotly_chart(fig)
    else:
        st.info("Veuillez sélectionner exactement deux restaurants à comparer.")



def plot_comparison_chart(restaurant_data):
    """
    Crée un graphique comparant les restaurants sélectionnés.
    """
    fig = go.Figure()

    # Ajout des restaurants dans le graphique
    for i, restaurant in enumerate(restaurant_data):
        fig.add_trace(go.Bar(
            x=[restaurant['nom_resto']],
            y=[restaurant['note_moyenne_resto']],
            name=restaurant['nom_resto'],
            marker_color='blue' if i == 0 else 'green'
        ))

    fig.update_layout(
        title="Comparaison des Notes des Restaurants",
        xaxis_title="Restaurant",
        yaxis_title="Note moyenne",
        barmode='group'
    )

    return fig



def comparaison_deux_resto():
    st.title("Comparaison de deux restaurants")
    st.sidebar.title("Sélection des restaurants")
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

        # Créer une carte Folium centrée sur Lyon
        m = folium.Map(location=[45.75, 4.85], zoom_start=12)

        colors = ['red', 'green']
        col1, col2 = st.columns(2)

        for i, (restaurant, col, color) in enumerate(zip(restaurants_data, [col1, col2], colors)):
            col.subheader(restaurant['nom_resto'])
            col.write(f"**Type de cuisine**: {restaurant['type_cuisine']}")
            col.write(f"**Fourchette de prix**: {restaurant['fourchette_prix']}")
            col.write(f"**Note moyenne**: {restaurant['note_moyenne_resto']}")

            restaurant_coords = (restaurant['latitude'], restaurant['longitude'])

            # Calculer la distance si la localisation de l'utilisateur est disponible
            if user_location:
                distance_km = geodesic(user_location, restaurant_coords).kilometers
                col.write(f"**Distance estimée** : {distance_km:.2f} km")

            # Ajouter un marqueur pour le restaurant
            folium.Marker(
                location=restaurant_coords,
                popup=restaurant['nom_resto'],
                tooltip=restaurant['nom_resto'],
                icon=folium.Icon(color=color, icon="cutlery", prefix="fa")
            ).add_to(m)

            # Générer et afficher le nuage de mots pour ce restaurant
            reviews = df[df['nom_resto'] == restaurant['nom_resto']]['commentaire'].tolist()
            if reviews:
                all_text = " ".join(reviews)
                if all_text.strip():
                    fig = generate_wordcloud(all_text, title=f"Nuage de mots pour {restaurant['nom_resto']}")
                    col.plotly_chart(fig)

        # Ajouter un marqueur pour la position de l'utilisateur si disponible
        if user_location:
            folium.Marker(
                location=user_location,
                popup="Votre position",
                tooltip="Vous êtes ici",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)

        # Afficher la carte
        st.subheader("Carte des restaurants")
        st_folium(m, width=700, height=500)

        # Appel du graphique de comparaison
        fig = plot_comparison_chart(restaurants_data)
        st.plotly_chart(fig)
    else:
        st.info("Veuillez sélectionner exactement deux restaurants à comparer.")


if __name__ == "__main__":
    comparaison_deux_resto()