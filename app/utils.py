# Importation des modules nécessaires
import os
import sys
import streamlit as st
import pandas as pd
import sqlite3

# Definition du chemin du répertoire courant
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from scraping.restaurant_scraper import RestaurantScraper
from scraping.find_url import find_url_restaurant
from processing.data_preprocessor import DataPreprocessor

# classe de données
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling

# Conexion à la base de données
def conexion_db(db_path):
    db = DBHandling(db_path)
    db.connect()
    info_resto = pd.read_sql_query('select * from restaurant', db.conn)
    avis = pd.read_sql_query('select * from avis', db.conn)
    arrondissement = pd.read_sql_query('select * from arrondissement', db.conn)
    data = db.combine_tables(avis, info_resto, arrondissement)
    db.close()
    data["commentaire"] = DataPreprocessor().preprocess_reviews(data["commentaire"])
    return DataPreprocessor().preprocess_data(data)


