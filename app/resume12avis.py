import streamlit as st
import pandas as pd
from mistralai import Mistral
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..', 'src')))
from processing.resume_avis import ResumerAvis

def resume_les_avis():
    # Charger les variables d'environnement
    load_dotenv()

    # Charger la clé API Mistral
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    # Charger le fichier de données
    file_path = "data/data_100.csv"
    data = pd.read_csv(file_path)

    # Titre de l'application
    st.title("Analyse et Résumé des Avis Clients")

    # Sélection du type d'analyse
    type_query = st.selectbox(
        "Choisissez le type d'analyse :",
        ("Resume les avis d'un restaurant", "Resume et compare les avis de deux restaurants")
    )

    # Initialiser la classe ResumerAvis
    resumer = ResumerAvis(api_key=MISTRAL_API_KEY, type_query="analyze_1" if "Resume les avis" in type_query else "analyze_2")

    # Récupérer les noms de restaurants
    restaurant_names = data['nom_resto'].unique()

    # Sélecteur pour le premier restaurant
    selected_restaurant_1 = st.selectbox("Sélectionnez le premier restaurant :", restaurant_names)

    # Extraire les avis pour le premier restaurant
    avis_restaurant_1 = data[data['nom_resto'] == selected_restaurant_1]['commentaire'].tolist()

    if "compare" in type_query:
        # Sélecteur pour le deuxième restaurant
        selected_restaurant_2 = st.selectbox("Sélectionnez le deuxième restaurant :", restaurant_names)

        # Extraire les avis pour le deuxième restaurant
        avis_restaurant_2 = data[data['nom_resto'] == selected_restaurant_2]['commentaire'].tolist()

    # Bouton pour générer le résumé
    if st.button("Générer le résumé"):
        if "Resume les avis" in type_query:
            if avis_restaurant_1:
                resultat = resumer.generer_resume(avis_restaurant_1)
                st.subheader(f"Résumé pour {selected_restaurant_1} :")
                st.write(resultat)
            else:
                st.warning("Aucun avis disponible pour le restaurant sélectionné.")
        elif "compare" in type_query:
            if avis_restaurant_1 and avis_restaurant_2:
                resultat = resumer.generer_resume(avis_restaurant_1, avis_restaurant_2)
                st.subheader(f"Résumé comparatif entre {selected_restaurant_1} et {selected_restaurant_2} :")
                st.write(resultat)
            else:
                st.warning("Des avis sont manquants pour un ou les deux restaurants sélectionnés.")

    # Footer
    st.caption("Application développée avec l'API Mistral et Streamlit.")
if __name__ == "__main__":
    resume_les_avis()