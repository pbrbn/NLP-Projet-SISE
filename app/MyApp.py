import os
import sys
import pandas as pd
import sqlite3
import folium
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium # type: ignore
import plotly.express as px

# Importation des pages de l'application
from analysis2resto import comparaison_deux_resto
from analysis1resto import analyse_restaurant
from acceuil import acceuil
from add1resto import ajouter_restaurant
from resume12avis import resume_les_avis

from streamlit_option_menu import option_menu
import streamlit as st

# Configuration de la page Streamlit
st.set_page_config(page_title="Application de Gestion de Restaurants", page_icon="🍴")

# Titre principal
st.title("🍴 streaApplication de Gestion de Restaurants")

# Menu de navigation avec option_menu
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",  # Titre du menu
        options=["Acceuil","Ajouter un restaurant","Analyser un restaurant", "Comparer deux restaurants", "Resumé avec L'IA"],  # Options du menu
        icons=["house", "search", "bar-chart-line"],  # Icônes pour chaque option
        menu_icon="list",  # Icône du menu principal
        default_index=0,  # Option sélectionnée par défaut
    )

# Chargement des pages
if page == "Acceuil":
    acceuil()
elif page == "Ajouter un restaurant":
    ajouter_restaurant()
elif page == "Analyser un restaurant":
    analyse_restaurant()
elif page == "Comparer deux restaurants":
    comparaison_deux_resto()
elif page == "Resumé avec L'IA":
    resume_les_avis()

