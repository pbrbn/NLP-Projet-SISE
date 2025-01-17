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
from utils import conexion_db
nlp = spacy.load('fr_core_news_md')

# Définition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))

from processing.sentiment_analyzer import SentimentAnalyzer
from processing.keyword_extractor import KeywordExtractor
from processing.resume_avis import ResumerAvis


# Chemin vers la DB
# db_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data', 'database.db'))
# df = conexion_db(db_path)



# charger les données

def load_data():
    #charger les données
    df = pd.read_csv("data/data_100.csv")
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

def get_nearby_transit(lat, lon):
    """
    Simule la récupération des arrêts de transport à proximité.
    Dans un cas réel, cette fonction appellerait une API de transport.

    Args:
        lat (float): Latitude du point central
        lon (float): Longitude du point central

    Returns:
        list: Liste des arrêts de transport simulés
    """
    import random

    # Définir des déltas aléatoires pour simuler des arrêts proches
    transit_types = ['Metro', 'Bus', 'Tramway']
    transit_lines = {
        'Metro': ['A', 'B', 'C', 'D'],
        'Bus': ['C1', 'C2', 'C3', 'C13', 'C14'],
        'Tramway': ['T1', 'T2', 'T3', 'T4']
    }

    transports = []
    for i in range(3):  # Générer 3 arrêts aléatoires
        transit_type = random.choice(transit_types)
        delta_lat = random.uniform(-0.002, 0.002)
        delta_lon = random.uniform(-0.002, 0.002)

        transport = {
            "type": transit_type,
            "name": f"Station {chr(65 + i)}",  # A, B, C...
            "line": random.choice(transit_lines[transit_type]),
            "coords": (lat + delta_lat, lon + delta_lon)
        }
        transports.append(transport)

    return transports

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

def display_comparison(restaurants_data, user_location, df):
    col1, col2 = st.columns(2)

    map_ = folium.Map(
        location=[45.75, 4.85],
        zoom_start=12,
        tiles='CartoDB positron',
        scrollWheelZoom=True
    )

    folium.WmsTileLayer(
        url='https://data.grandlyon.com/geoserver/metropole-de-lyon/wms?',
        layers='metropole-de-lyon:pvo_patrimoine_voirie.pvotrafic',
        name='Trafic routier',
        format='image/png',
        transparent=True,
    ).add_to(map_)

    transport_layer = folium.FeatureGroup(name='Transports en commun', show=True)
    restaurant_layer = folium.FeatureGroup(name='Restaurants', show=True)

    folium.Marker(
        location=user_location,
        popup="Votre position",
        tooltip="Vous êtes ici",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(map_)

    colors = ['red', 'green']

    for i, (restaurant, col, color) in enumerate(zip(restaurants_data, [col1, col2], colors)):
        col.subheader(restaurant['nom_resto'])
        col.write(f"**Type de cuisine**: {restaurant['type_cuisine']}")
        col.write(f"**Fourchette de prix**: {restaurant['fourchette_prix']}")
        col.write(f"**Note moyenne**: {restaurant['note_moyenne_resto']}")

        restaurant_coords = (restaurant['latitude'], restaurant['longitude'])
        distance_km = geodesic(user_location, restaurant_coords).kilometers
        col.write(f"**Distance estimée** : {distance_km:.2f} km")

        # Obtenir les transports à proximité
        nearby_transit = get_nearby_transit(restaurant['latitude'], restaurant['longitude'])

        # Créer le contenu du popup avec les informations sur les transports
        popup_content = f"{restaurant['nom_resto']} - {distance_km:.2f} km<br><br>Transports à proximité:<br>"
        for transit in nearby_transit:
            popup_content += f"- {transit['type']} {transit['line']} : {transit['name']}<br>"

            # Ajouter un marqueur pour chaque transport
            folium.Marker(
                location=transit['coords'],
                popup=f"{transit['type']} {transit['line']} : {transit['name']}",
                tooltip=f"{transit['type']} {transit['line']}",
                icon=folium.Icon(color="purple", icon="subway", prefix="fa")
            ).add_to(transport_layer)

        folium.Marker(
            location=restaurant_coords,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=restaurant['nom_resto'],
            icon=folium.Icon(color=color, icon="cutlery", prefix="fa")
        ).add_to(restaurant_layer)

        # Générer et afficher le nuage de mots pour ce restaurant
        reviews = df[df['nom_resto'] == restaurant['nom_resto']]['commentaire'].tolist()
        if reviews:
            all_text = " ".join(reviews)
            if all_text.strip():
                fig = generate_wordcloud(all_text, title=f"Nuage de mots pour {restaurant['nom_resto']}")
                col.plotly_chart(fig)

    transport_layer.add_to(map_)
    restaurant_layer.add_to(map_)

    folium.LayerControl().add_to(map_)

    st.write("**Carte des restaurants, transports en commun et trafic routier**")
    st_folium(map_, width=800, height=500, returned_objects=["last_active_drawing"])

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


# Initialiser la classe ResumerAvis
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
resumer_avis = ResumerAvis(api_key=MISTRAL_API_KEY)

def comparaison_deux_resto():
    st.sidebar.title("Comparer deux restaurants")
    st.markdown("""**Vous etes la parceque vous avez faim ou vous prevoyez quelque chose de speciale ?**
                Vous avez toujours rêvé de savoir quel restaurant mérite vraiment vos papilles ? Cette page est faite pour vous ! Comparez deux restaurants en fonction de leur type de cuisine, de leur fourchette de prix et de leur note moyenne. Et si vous êtes du genre à vouloir le meilleur pour moins cher, vous pouvez même filtrer les restaurants selon vos critères préférés.
                Alors, prêt à devenir un véritable critique culinaire ? C'est parti !""")

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
        display_comparison(restaurants_data, user_location, df)
        # Appel du graphique
        fig = plot_comparison_chart(restaurants_data)
        st.plotly_chart(fig)
    else:
        st.info("Veuillez sélectionner exactement deux restaurants à comparer.")


if __name__ == "__main__":
    comparaison_deux_resto()