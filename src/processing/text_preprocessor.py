import re
import spacy
from nltk.corpus import stopwords

class TextPreprocessor:
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
                if token.text not in self.stop_words and not token.is_punct
            ])

            # Ajouter l'avis nettoyé à la liste
            processed_reviews.append(cleaned_avis)

        return processed_reviews
