#Python 
FROM python:3.11.11-slim

#Répertoire de travail 
WORKDIR /app

#Fichiers nécessaires 
COPY ../app /app/app
COPY ../data /app/data
COPY ../src /app/src
COPY ../.env /app/src/processing
COPY ../requirements_v2.txt .

#Maj de pip 
RUN pip install --upgrade pip

#Installation des dépendances 
RUN pip install -r requirements_v2.txt

# Installer le modèle spaCy pour le français
RUN python -m spacy download fr_core_news_md

#Port
EXPOSE 8501

#Exécution de l'application 
CMD ["streamlit", "run", "app/MyApp.py"]
