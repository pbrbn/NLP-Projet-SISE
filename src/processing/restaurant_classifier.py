from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from .text_preprocessor import TextPreprocessor
from .data_handler import DataHandler

class RestaurantClassifier:
    def __init__(self):
        self.text_preprocessor = TextPreprocessor()
        self.classifier = None
        self.vectorizer = None
    
    def train(self, data, comment_column, target_column):
        """Entraîne le classificateur"""
        data = data.dropna(subset=[comment_column, target_column])
        processed_comments = self.text_preprocessor.preprocess_comments(data[comment_column])
        
        X_train, X_test, y_train, y_test = train_test_split(
            processed_comments, data[target_column], test_size=0.3, random_state=42, stratify=data[target_column]
        )
        
        self.vectorizer = TfidfVectorizer(max_features=5000)
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        self.classifier = RandomForestClassifier(random_state=42, n_estimators=100)
        self.classifier.fit(X_train_tfidf, y_train)
        
        y_pred = self.classifier.predict(X_test_tfidf)
        return classification_report(y_test, y_pred), accuracy_score(y_test, y_pred)
    
    def predict(self, comments):
        """Prédit le type de restaurant basé sur les commentaires"""
        if not self.classifier or not self.vectorizer:
            raise ValueError("Le modèle n'a pas encore été entraîné")
        
        processed_comments = self.text_preprocessor.preprocess_comments(comments)
        features = self.vectorizer.transform(processed_comments)
        return self.classifier.predict(features)
    


