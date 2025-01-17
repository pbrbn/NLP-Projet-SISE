from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.cluster import KMeans
import pandas as pd
from processing.data_preprocessor import DataPreprocessor
from processing.keyword_extractor import KeywordExtractor
from processing.sentiment_analyzer import SentimentAnalyzer

class ReviewClusterer:
    def __init__(self, vector_size=100):
        self.vector_size = vector_size
        self.data_preprocessor = DataPreprocessor()
        self.keyword_extractor = KeywordExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def cluster_reviews(self, reviews: list[str], n_clusters: int = 3, top_n: int = 5) -> pd.DataFrame:
        """Regroupe les avis en clusters et analyse chaque cluster"""
        # Prétraitement des avis
        reviews = self.data_preprocessor.preprocess_reviews(reviews)
        
        # Doc2Vec
        tagged_reviews = [TaggedDocument(review, [i]) for i, review in enumerate(reviews)]
        model = Doc2Vec(vector_size=self.vector_size, window=2, min_count=1, workers=4, epochs=10)
        model.build_vocab(tagged_reviews)
        model.train(tagged_reviews, total_examples=model.corpus_count, epochs=model.epochs)
        
        # K-Means clustering
        vectors = [model.dv[i] for i in range(len(reviews))]
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(vectors)
        labels = kmeans.labels_
        
        # Analyse des clusters
        clusters_data = []
        for i in range(n_clusters):
            cluster_reviews = [review for j, review in enumerate(reviews) if labels[j] == i]
            sentiments = self.sentiment_analyzer.analyze_sentiments(cluster_reviews, join=True)[0]
            keywords = self.keyword_extractor.aggregate_keywords(cluster_reviews, top_n=top_n)
            
            clusters_data.append({
                "Cluster": f"Cluster {i + 1}",
                "Nombres_avis": len(cluster_reviews),
                "Polarité": sentiments["Polarité"],
                "Subjectivité": sentiments["Subjectivité"],
                "Mots_Clés": ', '.join([f"{mot} ({score:.2f})" for mot, score in keywords])
            })
        
        return pd.DataFrame(clusters_data)