# NLP-Projet-SISE

## Description

Le projet `NLP-Projet-SISE` est une application de traitement du langage naturel (NLP) qui permet de scraper, analyser et visualiser des données de restaurants et leurs avis. L'application utilise des techniques de NLP pour extraire des informations pertinentes à partir des avis des utilisateurs et les stocker dans une base de données SQLite. L'application est construite avec Python et utilise des bibliothèques telles que spaCy, pandas, et Streamlit pour l'analyse et la visualisation des données.
Les données sont issues du scrapping du site Tripadvisor et de l'open data de l'INSEE

## Fonctionnalités

- Scraping des informations des restaurants et des avis depuis TripAdvisor.
- Prétraitement des données textuelles avec spaCy et NLTK.
- Stockage des données dans une base de données SQLite.
- Visualisation des données avec Streamlit.


## Prérequis

- Clef Mistral

### Étapes d'Installation

1. **Cloner le Répertoire**

   Clonez le répertoire du projet depuis GitHub :

   ```sh
   git clone https://github.com/your_username/NLP-Projet-SISE.git
   cd NLP-Projet-SISE

2. **Installation des dépendances**
    ``sh
    pip install --upgrade pip
    pip install -r requirements_v2.txt

    ``sh
    python -m spacy download fr_core_news_md
3. **Lancer l'application**
    sh``
    streamlit run app/MyApp.py

## Contributeurs :
- Pierre Bourbon
- Quentin Lim
- Lansana Cisse
- Alexis Dardelet