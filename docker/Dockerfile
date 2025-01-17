#Python 
FROM python:3.11

#Répertoire de travail 
WORKDIR /app

#Fichiers nécessaires 
COPY ../app /app/app
COPY ../data /app/data
COPY ../src /app/src
COPY ../requirements.txt .

#Maj de pip 
RUN pip install --upgrade pip

# Installer blis séparément pour isoler l'erreur
RUN pip install blis==0.7.4

#Installation des dépendances 
RUN pip install -r requirements.txt

#Port
EXPOSE 8501

#Exécution de l'application 
CMD ["streamlit", "run", "app/MyApp.py"]
