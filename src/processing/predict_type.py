# Combine descriptions and comments, predict type of cuisine
def predict_cuisine_type(data, comment_column, description_column, type_column):
    # Check for required columns
    if type_column not in data.columns:
        return "The dataset does not contain a column for the type of cuisine."
    
    # Combine descriptions and comments into a single text feature
    data['combined_text'] = data[comment_column].fillna('') + ' ' + data[description_column].fillna('')
    
    # Drop rows with missing type information
    data = data.dropna(subset=[type_column])
    
    # Preprocess the combined text
    data['combined_text'] = preprocess_comments(data['combined_text'])
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        data['combined_text'], data[type_column], test_size=0.3, random_state=42, stratify=data[type_column]
    )
    
    # Vectorize the combined text using TF-IDF
    tfidf = TfidfVectorizer(max_features=5000)
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    
    # Train a Random Forest Classifier
    classifier = RandomForestClassifier(random_state=42, n_estimators=100)
    classifier.fit(X_train_tfidf, y_train)
    
    # Make predictions
    y_pred = classifier.predict(X_test_tfidf)
    
    # Evaluate the model
    report = classification_report(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    
    return classifier, tfidf, report, accuracy

# Check if dataset contains necessary columns
if {'type_restaurant', 'commentaire', 'description'} <= set(data.columns):
    classifier, tfidf_vectorizer, report, accuracy = predict_cuisine_type(
        data, 'commentaire', 'description', 'type_restaurant'
    )
    print("Classification Report:\n", report)
    print("Accuracy:", accuracy)
else:
    print("The dataset does not contain all the required columns for this task.")
