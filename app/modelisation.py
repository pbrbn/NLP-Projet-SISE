import streamlit as st
import pandas as pd
import pickle
import sys
import os

# Ajouter `src` au chemin d'import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from processing.restaurant_classifier import RestaurantClassifier
from processing.text_preprocessor import TextPreprocessor


# Directory to save models
MODEL_DIR = "../models"
os.makedirs(MODEL_DIR, exist_ok=True)

# Streamlit interface
st.title("Modélisation")

sub_page = st.radio("Sélectionnez une action", ["Entraînement", "Prédiction"])

if sub_page == "Entraînement":
    st.header("Entraînement des modèles")

    # File upload
    uploaded_file = st.file_uploader("Uploader un fichier CSV contenant les données", type="csv")

    if uploaded_file:
        data = pd.read_csv(uploaded_file)

        # Check required columns
        if not {'commentaire', 'type_cuisine'} <= set(data.columns):
            st.error("Le fichier doit contenir les colonnes 'commentaire' et 'type_restaurant'.")
        else:
            classifier = RestaurantClassifier()

            # Train button
            if st.button("Lancer l'entraînement"):
                report, accuracy = classifier.train(data, 'commentaire', 'type_restaurant')

                # Save the trained model
                model_path = os.path.join(MODEL_DIR, "restaurant_classifier.pkl")
                with open(model_path, "wb") as f:
                    pickle.dump(classifier, f)

                st.success(f"Modèle entraîné et sauvegardé sous {model_path}")
                st.text(f"Accuracy: {accuracy}")
                st.json(report)

elif sub_page == "Prédiction":
    st.header("Prédiction")

    # Model upload
    model_file = st.file_uploader("Charger un modèle sauvegardé", type="pkl")
    input_text = st.text_input("Entrer un commentaire ou une description")

    if model_file and input_text:
        # Load the model
        model_path = os.path.join(MODEL_DIR, "temp_model.pkl")
        with open(model_path, "wb") as f:
            f.write(model_file.read())

        with open(model_path, "rb") as f:
            classifier = pickle.load(f)

        # Predict
        prediction = classifier.predict([input_text])
        st.success(f"Type de cuisine prédit : {prediction[0]}")
