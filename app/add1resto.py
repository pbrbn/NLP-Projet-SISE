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

    # Formulaire pour ajouter une URL Tripadvisor
    with st.form(key="add_restaurant"):
        nom_resto_user = st.text_input("Saisir le nom du restaurant")


        # Recherche de l'URL du restaurant à partir du nom
        url_resto = find_url_restaurant(nom_resto_user)

        search_button = st.form_submit_button("Chercher le restaurant", type="primary")
        
        if search_button:
            # Scraping des informations du restaurant à partir de l'URL
            # st.write(f"L'URL du restaurant {nom_resto_user} a été trouvé !")
            # st.write(f"URL : {url_resto}") # Débugging , à enlever plus tard !!!!!
            rscrap = RestaurantScraper(base_url=url_resto)
            df_info_resto_new = rscrap.scrape_infos_resto()
            
            nom_new = df_info_resto_new.iloc[0, 0]
            type_cuisine_new = df_info_resto_new.iloc[0, 1]
            adress_new = df_info_resto_new.iloc[0, 3]

            # Affichage des informations avant ajout à la base de données
            st.success("Restaurant trouvé")
            st.write(f"Nom du restaurant : {nom_new}")
            st.write(f"Cuisine type : {type_cuisine_new}")
            st.write(f"Adress : {adress_new}")

        # Ajout du restaurant à la base de données
        add_to_db_button = st.form_submit_button("Cliquez ici pour ajouter le restaurant à la base de données", type="primary")

        if add_to_db_button:
            # Scraping complet du restaurant sur Tripadvisor
            # st.write(url_resto) # Débugging 
            rscrap = RestaurantScraper(base_url=url_resto)
            df_info_resto_new = rscrap.scrape_infos_resto()
            df_info_avis_new = rscrap.scrape_infos_avis()
            try:
                df_description_new = rscrap.scrape_description_resto()
            except:
                descrtiption_new = "Description non renseignée"

            nom_new = df_info_resto_new.iloc[0, 0]
            type_cuisine_new = df_info_resto_new.iloc[0, 1]
            fourchette_prix_new = df_info_resto_new.iloc[0, 2]
            adress_new = df_info_resto_new.iloc[0, 3]
            note_moy_new = df_info_resto_new.iloc[0, 4]
            categorie_prix_new = df_info_resto_new.iloc[0, 5]

            descrtiption_new = df_description_new.iloc[0, 1]
            # st.write(f"Description : {descrtiption_new}")


            # Connexion à la base de données et insertion des données
            db.connect()
            db.insert_restaurant(
                nom=nom_new,
                type_cuisine=type_cuisine_new,
                fourchette_prix=fourchette_prix_new,
                adresse=adress_new,
                note_moyenne=note_moy_new,
                description=descrtiption_new,
                categorie_prix=categorie_prix_new

            )
            # Ajout des avis si nécessaire
            # st.write(df_info_avis_new)
            # def insert_avis(self, nom_restaurant: str, date: str, note: int, commentaire: str):

            for index, row in df_info_avis_new.iterrows():
                db.insert_avis(
                    note=row['Notes'],
                    commentaire=row['Commentaires'],
                    date=row['Date'],
                    nom_restaurant=nom_new
                )

            st.success("Restaurant ajouté à la base de données")
            # Affichage des informations ajoutées avec sqlite
            conn = sqlite3.connect("../data/database.db")
            query_resto = 'select * from restaurant where nom = "{}"'.format(nom_new)
            info_resto = pd.read_sql_query(query_resto, conn)
            query_avis = 'select * from avis where nom_restaurant = "{}"'.format(nom_new)
            info_avis = pd.read_sql_query(query_avis, conn)
            st.write(info_resto.head())
            st.write(info_avis.head())

            db.close()

            

        # Bouton pour réinitialiser le formulaire
        reset_button = st.form_submit_button("Réinitialiser le formulaire", type="secondary")