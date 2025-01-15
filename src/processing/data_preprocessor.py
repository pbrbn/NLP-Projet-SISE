import re
import spacy
import pandas as pd
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

        # Séparer les données de la colonne fourchette_prix en deux colonnes min_prix et max_prix
        data[['min_prix', 'max_prix']] = data['fourchette_prix'].str.split('€-', expand=True)

        # Supprimer le signe € dans les colonnes min_prix et max_prix
        data['min_prix'] = data['min_prix'].str.replace('€', '')
        data['max_prix'] = data['max_prix'].str.replace('€', '')

        # Remplacer la , par . dans les colonnes min_prix et max_prix
        data['min_prix'] = data['min_prix'].str.replace(',', '.')
        data['max_prix'] = data['max_prix'].str.replace(',', '.')

        # Transformer le type des colonnes min_prix et max_prix en float
        data['min_prix'] = data['min_prix'].astype(float)
        data['max_prix'] = data['max_prix'].astype(float)

        # Remplacer les , par . dans les colonnes note_moyenne_resto et note_avis
        data['note_moyenne_resto'] = data['note_moyenne_resto'].str.replace(',', '.')
        data['note_avis'] = data['note_avis'].str.replace(',', '.')
        data['note_moyenne_resto'] = data['note_moyenne_resto'].astype(float)
        data['note_avis'] = data['note_avis'].astype(float)

        return data
    