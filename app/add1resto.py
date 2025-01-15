# Importation des modules nécessaires
import os
import sys
import streamlit as st
import pandas as pd
import sqlite3

# Definition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from scraping.restaurant_scraper import RestaurantScraper
from scraping.find_url import find_url_restaurant
from processing.data_preprocessor import DataPreprocessor

# classe de données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling

# Récupération des données depuis la database
db = DBHandling("../data/database.db")
db.connect()


def ajouter_restaurant():
    st.title("Ajouter un restaurant")
    st.write("Type a restaurant name - the app will google-search it for you")

    # Formulaire pour ajouter une URL Tripadvisor
    with st.form(key="add_restaurant"):
        nom_resto_user = st.text_input("Restaurant name")

        # Recherche de l'URL du restaurant à partir du nom
        url_resto = find_url_restaurant(nom_resto_user)

        search_button = st.form_submit_button("Search")

        if search_button:
            # Scraping des informations du restaurant à partir de l'URL
            rscrap = RestaurantScraper(base_url=url_resto)
            df_info_resto_new = rscrap.scrape_infos_resto()
            
            nom_new = df_info_resto_new.iloc[0, 0]
            type_cuisine_new = df_info_resto_new.iloc[0, 1]
            adress_new = df_info_resto_new.iloc[0, 3]
            categorie_prix_new = df_info_resto_new.iloc[0, 5]

            # Affichage des informations avant ajout à la base de données
            st.success("Restaurant found")
            st.write(f"Nom du restaurant : {nom_new}")
            st.write(f"Cuisine type : {type_cuisine_new}")
            st.write(f"Adress : {adress_new}")

        # Ajout du restaurant à la base de données
        add_to_db_button = st.form_submit_button("Click here to add to database", type="primary")

        if add_to_db_button:
            # Scraping complet du restaurant sur Tripadvisor
            rscrap = RestaurantScraper(base_url=url_resto)
            df_info_resto_new = rscrap.scrape_infos_resto()
            df_info_avis_new = rscrap.scrape_infos_avis()

            nom_new = df_info_resto_new.iloc[0, 0]
            type_cuisine_new = df_info_resto_new.iloc[0, 1]
            fourchette_prix_new = df_info_resto_new.iloc[0, 2]
            adress_new = df_info_resto_new.iloc[0, 3]
            note_moy_new = df_info_resto_new.iloc[0, 4]
            categorie_prix_new = df_info_resto_new.iloc[0, 5]

            # Connexion à la base de données et insertion des données
            db.connect()
            db.insert_restaurant(
                nom=nom_new,
                type_cuisine=type_cuisine_new,
                fourchette_prix=fourchette_prix_new,
                adresse=adress_new,
                note_moyenne=note_moy_new,
                description="Description non renseignée",
                categorie_prix=categorie_prix_new
            )
            # db.insert_avis()  # Ajout des avis si nécessaire
            db.close()

            st.success("Restaurant added to database")

            # Affichage des résultats pour les tests
            st.dataframe(df_info_resto_new)
            st.dataframe(df_info_avis_new.head(5))

        # Bouton pour réinitialiser le formulaire
        reset_button = st.form_submit_button("Reset")