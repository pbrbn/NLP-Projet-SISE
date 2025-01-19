import os
import sys
import pandas as pd
import sqlite3
import folium
import streamlit as st
from streamlit_folium import st_folium 
from streamlit_option_menu import option_menu
import plotly.express as px
from folium.plugins import MarkerCluster

# Ajouter le chemin des modules internes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling

# Chemin constant pour la base de données
DATABASE_PATH = "../data/database.db"

def connect_database():
    """Connecte à la base de données et retourne l'objet connexion."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erreur lors de la connexion à la base de données : {e}")
        return None

def load_data(conn):
    """Charge les données des tables restaurant et arrondissement."""
    try:
        info_resto = pd.read_sql_query('SELECT * FROM restaurant', conn)
        info_arrondissement = pd.read_sql_query('SELECT * FROM arrondissement', conn)
        return info_resto, info_arrondissement
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None, None

def process_data(info_resto, info_arrondissement):
    """Traite les données pour préparer les analyses."""
    # Jointure des deux tables
    final_table = pd.merge(info_resto, info_arrondissement, on='arrondissement', how='inner')

    # Conversion et transformation
    final_table['arrondissement'] = final_table['arrondissement'].astype(int).astype(str)
    final_table['categorie_prix'] = final_table['categorie_prix'].replace({
        '€': '€ : Pas cher et rapide',
        '€€-€€€': '€€-€€ : Intermédiaire',
        '€€€€': '€€€€ : Restaurant gourmet'
    })

    return final_table

def display_analysis(data, info_arrondissement):
    """Affiche les analyses interactives dans Streamlit."""
    st.title("Etude INSEE des restaurants")

    # **Filtres dans la sidebar**
    arrondissements = sorted(data['arrondissement'].unique())
    selected_arr = st.sidebar.multiselect(
        "Sélectionnez les arrondissements à comparer :", 
        options=['Tous les arrondissements'] + arrondissements, 
        default='Tous les arrondissements'
    )

    categories_prix = sorted(data['categorie_prix'].unique())
    selected_cat = st.sidebar.multiselect(
        "Sélectionnez les catégories de prix à analyser :", 
        options=['Toutes les catégories de prix'] + categories_prix, 
        default='Toutes les catégories de prix'
    )

    # **Logique de sélection par défaut**
    if 'Tous les arrondissements' in selected_arr:
        selected_arr = arrondissements

    if 'Toutes les catégories de prix' in selected_cat:
        selected_cat = categories_prix

    filtered_data = data[(data['arrondissement'].isin(selected_arr)) & (data['categorie_prix'].isin(selected_cat))]

    # **Analyse par arrondissement**
    arr_summary = filtered_data.groupby('arrondissement').size().reset_index(name='Nombre de restaurants')
    fig_arr = px.bar(arr_summary, x='arrondissement', y='Nombre de restaurants', color='arrondissement',
                     title="Nombre de restaurants par arrondissement")
    st.plotly_chart(fig_arr)

    # **Analyse par catégorie de prix**
    cat_summary = filtered_data.groupby('categorie_prix').size().reset_index(name='Nombre de restaurants')
    fig_cat = px.pie(cat_summary, values='Nombre de restaurants', names='categorie_prix', 
                     title="Répartition des restaurants par catégorie de prix")
    st.plotly_chart(fig_cat)

    # **Densité de restaurants vs Niveau de vie médian**
    density_life = filtered_data.groupby('arrondissement').agg({'mediane_niveau_de_vie': 'mean', 'categorie_prix': 'size'}).reset_index()
    fig_density = px.scatter(density_life, x='mediane_niveau_de_vie', y='categorie_prix', size='categorie_prix', color='arrondissement',
                             title="Densité de restaurants en fonction du niveau de vie médian",
                             labels={'categorie_prix': 'Densité de restaurants', 'mediane_niveau_de_vie': 'Niveau de vie médian'})
    st.plotly_chart(fig_density)

    # **Répartition géographique des restaurants**
    map_data = filtered_data[['latitude', 'longitude', 'arrondissement', 'categorie_prix']]

    # Création d'une carte centrée sur Lyon
    map_lyon = folium.Map(location=[45.764043, 4.835659], zoom_start=14)

    # Utilisation d'un MarkerCluster pour regrouper les marqueurs proches
    marker_cluster = MarkerCluster().add_to(map_lyon)

    # Créer une palette de couleurs en fonction des arrondissements
    color_map = {arr: px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)] 
                 for i, arr in enumerate(sorted(filtered_data['arrondissement'].unique()))}

    # Ajouter les marqueurs à la carte avec une couleur par arrondissement
    for _, row in map_data.iterrows():
        color = color_map[row['arrondissement']]
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Restaurant: {row['categorie_prix']} ({row['arrondissement']} arrondissement)",
            icon=folium.Icon(color=color)
        ).add_to(marker_cluster)

    st_folium(map_lyon, width=700, height=500)

def etude_insee():
    """Fonction principale pour l'étude INSEE."""
    conn = connect_database()
    if not conn:
        return

    info_resto, info_arrondissement = load_data(conn)
    if info_resto is None or info_arrondissement is None:
        conn.close()
        return

    data = process_data(info_resto, info_arrondissement)
    display_analysis(data, info_arrondissement)

    conn.close()

if __name__ == "__main__":
    etude_insee()
