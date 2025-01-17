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

# Menu de navigation
with st.sidebar:
    page = option_menu(
        menu_title="Navigation",
        options=["Accueil", "Ajouter un restaurant", "Analyser un restaurant", "Comparer deux restaurants", "Résumé IA"],
        icons=["house", "plus", "search", "arrows-angle-expand", "robot"],
        menu_icon="list",
        default_index=0,
    )

# Chargement des pages
if page == "Accueil":
    acceuil()
elif page == "Ajouter un restaurant":
    ajouter_restaurant()
elif page == "Analyser un restaurant":
    analyse_restaurant()
elif page == "Comparer deux restaurants":
    comparaison_deux_resto()
elif page == "Résumé IA":
    resume_les_avis()

