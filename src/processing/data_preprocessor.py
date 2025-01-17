import re
import spacy
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk import download
download('stopwords')

class DataPreprocessor:
    def __init__(self):
        """
        Initialise le module de prétraitement de texte.
        Charge le modèle spaCy pour le français et définit la liste des stopwords.
        """
        self.nlp = spacy.load("fr_core_news_sm")  # Charger le modèle de langue français de spaCy
        self.stop_words = set(stopwords.words('french'))  # Définir les stopwords en français


    def preprocess_reviews(self, reviews):
        """
        Nettoie et prépare les avis pour le traitement NLP.
        Effectue les étapes suivantes :
        - Suppression des mots courts (moins de 3 caractères).
        - Suppression des chiffres et des ponctuations.
        - Conversion en minuscules.
        - Utilisation de spaCy pour la lemmatisation.
        - Suppression des stopwords et des tokens de ponctuation.

        Args:
            reviews (list): Liste de chaînes de caractères représentant les avis.

        Returns:
            list: Liste des avis nettoyés et préparés pour le traitement NLP.
        """
        processed_reviews = []

        for avis in reviews:
            # Supprimer les mots de moins de 3 caractères
            avis = re.sub(r'\b\w{1,2}\b', '', avis).strip()

            # Supprimer les chiffres
            avis = ''.join([char for char in avis if not char.isdigit()])

            # Supprimer les retours à la ligne et les espaces supplémentaires
            avis = re.sub(r'\r\n|\r|\n', ' ', avis)
            avis = re.sub(r'\s+', ' ', avis)

            # Convertir en minuscules
            avis = avis.lower()

            # Traiter le texte avec spaCy
            doc = self.nlp(avis)

            # Lemmatisation et suppression des stopwords et ponctuation
            cleaned_avis = ' '.join([
                token.lemma_ for token in doc
                if token.text.lower() not in self.stop_words and not token.is_punct
            ])

            # Ajouter l'avis nettoyé à la liste
            processed_reviews.append(cleaned_avis)

        return processed_reviews

    def preprocess_data(self, data):
        """
        Prétraiter les données en remplaçant les valeurs spécifiques, en séparant les colonnes et en transformant les types de données.

        Paramètres :
            - data (pd.DataFrame) : Le DataFrame contenant les données à prétraiter.

        Retourne :
            - pd.DataFrame : Le DataFrame prétraité.
        """

        # Remplacer les valeurs spécifiques dans la colonne fourchette_prix par None
        data['fourchette_prix'] = data['fourchette_prix'].replace(
            ['Française, Européenne, Moderne', 'Française, Européenne, Saine', 'Française'], 
            None
        )

        # Séparer les données de la colonne fourchette_prix en deux colonnes prix_min et prix_max
        data[['prix_min', 'prix_max']] = data['fourchette_prix'].str.split('€-', expand=True)

        # Nettoyer les colonnes prix_min et prix_max
        data['prix_min'] = data['prix_min'].replace('NA', np.nan).str.strip() if 'prix_min' in data.columns else np.nan
        data['prix_max'] = data['prix_max'].replace('NA', np.nan).str.strip() if 'prix_max' in data.columns else np.nan

        # Supprimer le signe € et remplacer les , par . dans les colonnes prix_min et prix_max
        data['prix_min'] = data['prix_min'].str.replace('€', '').str.replace(',', '.')
        data['prix_max'] = data['prix_max'].str.replace('€', '').str.replace(',', '.')

        # Convertir les colonnes prix_min et prix_max en float
        data['prix_min'] = pd.to_numeric(data['prix_min'], errors='coerce')
        data['prix_max'] = pd.to_numeric(data['prix_max'], errors='coerce')

        # Remplacer les , par . dans les colonnes note_moyenne_resto et note_avis et convertir en float
        if 'note_moyenne_resto' in data.columns:
            data['note_moyenne_resto'] = pd.to_numeric(data['note_moyenne_resto'].str.replace(',', '.'), errors='coerce')
        if 'note_avis' in data.columns:
            data['note_avis'] = pd.to_numeric(data['note_avis'].str.replace(',', '.'), errors='coerce')

        return data

    