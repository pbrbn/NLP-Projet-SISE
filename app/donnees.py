import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from processing.text_preprocessor import TextPreprocessor
from processing.data_handler import DataHandler
from scraping.restaurant_scraper import RestaurantScraper
import os

# Paths for data files
DATA_DIR = "data/dataClean"
CSV_FILE = os.path.join(DATA_DIR, "restaurants.csv")
DB_FILE = os.path.join(DATA_DIR, "restaurants.db")

# Load data
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Le fichier {file_path} n'existe pas.")
        return pd.DataFrame()

# Save data
def save_data(data, file_path):
    data.to_csv(file_path, index=False)
    handler = DataHandler()
    handler.save_to_db(data, DB_FILE)

# Streamlit interface
st.title("Chargement et exploration des données")

# Load the existing data
data = load_data(CSV_FILE)

if not data.empty:
    # Display data preview
    st.subheader("Aperçu des données")
    st.write(data.head())
    st.write("Statistiques descriptives :")
    st.write(data.describe())

    # Verify required columns
    required_columns = ["commentaire", "type_cuisine"]
    if all(col in data.columns for col in required_columns):
        st.success("Toutes les colonnes nécessaires sont présentes.")
    else:
        missing_cols = [col for col in required_columns if col not in data.columns]
        st.error(f"Colonnes manquantes : {missing_cols}")

    # Add a new restaurant
    st.subheader("Ajouter un nouveau restaurant")
    restaurant_name = st.text_input("Nom du restaurant")
    restaurant_address = st.text_input("Adresse du restaurant")

    if st.button("Ajouter le restaurant"):
        if restaurant_name and restaurant_address:
            scraper = RestaurantScraper()
            new_data = scraper.scrape_restaurant(restaurant_name, restaurant_address)

            preprocessor = TextPreprocessor()
            new_data["commentaire"] = preprocessor.preprocess_comments(new_data["commentaire"])

            # Append the new data and save
            data = pd.concat([data, pd.DataFrame([new_data])], ignore_index=True)
            save_data(data, CSV_FILE)

            st.success(f"Le restaurant '{restaurant_name}' a été ajouté et les données ont été sauvegardées.")
        else:
            st.error("Veuillez remplir le nom et l'adresse du restaurant.")

    # Refresh the data
    if st.button("Rafraîchir les données"):
        data = load_data(CSV_FILE)
        if not data.empty:
            st.success("Données rafraîchies avec succès !")
            st.write(data.head())
        else:
            st.error("Échec du chargement des données rafraîchies.")
else:
    st.error("Aucune donnée trouvée. Veuillez vérifier le fichier CSV.")
