from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Prepare data for classification
def prepare_classification_data(data, comment_column, target_column):
    data = data.dropna(subset=[comment_column, target_column])
    data[comment_column] = preprocess_comments(data[comment_column])
    return data

# Train and evaluate a classification model
def classify_restaurants(data, comment_column, target_column):
    # Prepare the data
    data = prepare_classification_data(data, comment_column, target_column)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        data[comment_column], data[target_column], test_size=0.3, random_state=42, stratify=data[target_column]
    )
    
    # Transform comments into TF-IDF features
    # Utilisation de la méthode TfidfVectorizer pour convertir les commentaires en vecteurs TF-IDF
    
    # Train a Random Forest Classifier
    # Mise en place d'un classificateur de type RandomForestClassifier
    
    # Predict on test set
   # Prédiction sur l'ensemble de test
    # Evaluate the model
    report = classification_report(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    
    return classifier, tfidf_vectorizer, report, accuracy

# Check if the dataset contains a column for restaurant types
if 'type_restaurant' in data.columns:
    classifier, tfidf_vectorizer, report, accuracy = classify_restaurants(data, 'commentaire', 'type_restaurant')
    print("Classification Report:\n", report)
    print("Accuracy:", accuracy)
else:
    print("The dataset does not contain a column for restaurant types.")
