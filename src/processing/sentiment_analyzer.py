from textblob import TextBlob
import pandas as pd

class SentimentAnalyzer:
    @staticmethod
    def analyze_sentiments(reviews: list[str], join: bool = True) -> list[dict]:
        """Analyse les sentiments d'une liste d'avis."""
        results = []
        
        if join:
            full_review = " ".join(reviews)
            blob = TextBlob(full_review)
            results.append({
                "Polarité": blob.sentiment.polarity,
                "Subjectivité": blob.sentiment.subjectivity
            })
        else:
            for review in reviews:
                blob = TextBlob(review)
                results.append({
                    "Polarité": blob.sentiment.polarity,
                    "Subjectivité": blob.sentiment.subjectivity
                })
        
        return results

    @staticmethod
    def analyze_by_restaurant(data: pd.DataFrame) -> list[dict]:
        """
        Analyse les sentiments des commentaires par restaurant.

        Args:
            data (pd.DataFrame): DataFrame contenant les colonnes 'id_restaurant', 'commentaire', et 'nom'.

        Returns:
            list[dict]: Résultats avec id_restaurant, nom, polarité et subjectivité.
        """
        if not {'id_restaurant', 'commentaire', 'nom'}.issubset(data.columns):
            raise ValueError("Le DataFrame doit contenir les colonnes 'id_restaurant', 'commentaire', et 'nom'.")
        
        results = []
        for _, row in data.iterrows():
            commentaire = row['commentaire']
            nom = row['nom']
            restaurant_id = row['id_restaurant']
            
            # Analyse des sentiments pour les commentaires agrégés
            sentiments = SentimentAnalyzer.analyze_sentiments([commentaire], join=True)
            results.append({
                "id_restaurant": restaurant_id,
                "nom": nom,
                "polarité": sentiments[0]['Polarité'],
                "subjectivité": sentiments[0]['Subjectivité']
            })
        
        return results
