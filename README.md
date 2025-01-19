# NLP-Projet-SISE

## Description

Le projet `NLP-Projet-SISE` est une application de traitement du langage naturel (NLP) dédiée à l'extraction, l'analyse et la visualisation des données des restaurants et de leurs avis. L'application exploite des techniques de NLP pour extraire des informations pertinentes à partir des avis utilisateurs et les stocke dans une base de données SQLite. Elle est développée en Python et utilise des bibliothèques telles que spaCy, pandas, et Streamlit pour l'analyse et la visualisation des données. Les données proviennent du scraping du site TripAdvisor et de l'open data de l'INSEE.

## Fonctionnalités

- **Scraping** : Extraction des informations des restaurants et des avis depuis TripAdvisor.
- **Prétraitement des données** : Analyse textuelle avec spaCy et NLTK.
- **Stockage des données** : Gestion des données dans une base SQLite.
- **Visualisation des données** : Tableaux et graphiques interactifs via Streamlit.

## Structure du Projet

```
project/
│
├── app/                    # Fichiers de l'application Streamlit
├── data/                   # Données brutes et prétraitées
│
├── src/                    # Code source
│   ├── scraping/           # Scripts pour l'extraction des données
│   │
│   ├── processing/         # Scripts pour le prétraitement et l'analyse des données
│   │
│   ├── database_handling/  # Gestion de la base de données
│
├── docker/                 # Configuration et fichiers pour Docker
│
├── notebooks/              # Notebooks Jupyter pour les analyses exploratoires
│
├── requirements.txt        # Liste des dépendances Python
├── README.md               # Documentation principale du projet
```

## Prérequis

- Clé Mistral (pour l'utilisation avec Docker).

## Étapes d'Installation

1. **Cloner le Répertoire**

   Clonez le dépôt GitHub du projet :

   ```bash
   git clone https://github.com/your_username/NLP-Projet-SISE.git
   cd NLP-Projet-SISE
   ```

2. **Installer les dépendances**

   Avec Python et pip :  

   ```bash
   pip install --upgrade pip
   pip install -r requirements_v2.txt
   python -m spacy download fr_core_news_md
   ```

   Avec Docker et un fichier `.env` contenant une clé Mistral :  

   ```bash
   docker pull ql2111/projet_nlp:latest
   docker run --env-file <chemin/vers/le/.env> -p 8501:8501 ql2111/projet_nlp:latest
   ```

3. **Lancer l'application**

   Avec Streamlit :  

   ```bash
   streamlit run app/MyApp.py
   ```

## Contributeurs

- **Pierre Bourbon**  
- **Quentin Lim**  
- **Lansana Cisse**  
- **Alexis Dardelet**

---
