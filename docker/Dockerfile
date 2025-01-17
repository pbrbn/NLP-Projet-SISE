#Python 
FROM python:3.11-slim

#Répertoire de travail 
WORKDIR /app

#Fichiers nécessaires 
COPY ./app ./app
COPY ./data ./data
COPY ./src ./src

#requirements
COPY requirements.txt requirements.txt

#Installation des dépendances 
RUN pip install -r requirements.txt

#Port
EXPOSE 8501

#Exécution de l'application 
CMD ["streamlit", "run", "app/app.py"]
