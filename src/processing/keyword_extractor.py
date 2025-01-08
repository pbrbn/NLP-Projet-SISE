from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import pandas as pd

class KeywordExtractor:
    def __init__(self, max_features=1000):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_features,
            lowercase=True,
            ngram_range=(1, 2)
        )
    
    def extract_keywords(self, reviews: list[str], top_n: int = 5) -> dict:
        """Extrait les mots-clés les plus significatifs"""
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(reviews)
        words = self.tfidf_vectorizer.get_feature_names_out()
        
        keywords_per_review = {}
        for index, row in enumerate(tfidf_matrix):
            scores = pd.DataFrame({
                "mot": words,
                "score": row.toarray().flatten()
            })
            top_keywords = scores.sort_values(by="score", ascending=False).head(top_n)
            keywords_per_review[f"Avis {index + 1}"] = list(zip(top_keywords["mot"], top_keywords["score"]))
        
        return keywords_per_review
    
    def aggregate_keywords(self, reviews: list[str], top_n=10) -> list:
        """Agrège les mots-clés extraits d'une liste d'avis"""
        keywords_per_review = self.extract_keywords(reviews)
        aggregation = defaultdict(float)
        
        for keywords in keywords_per_review.values():
            for word, score in keywords:
                aggregation[word] += score
        
        global_keywords = sorted(aggregation.items(), key=lambda x: x[1], reverse=True)
        return global_keywords[:top_n]
    