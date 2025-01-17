import os
import sys
import pandas as pd
import sqlite3

import folium
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling



def etude_insee():
    #############  ANALYSE INSEE  #################### -> placement temporaire
    ###################################################### 
    ###################################################### 
    # Temp create plotly graph with stacked bar chart
    # Jointure arrondissement et restaurant 
    db = DBHandling("../data/database.db")
    conn = sqlite3.connect("../data/database.db")

    db.connect()
    query = 'select * from restaurant'
    info_resto = pd.read_sql_query(query,conn)
    # info_resto contient tout les restaurants de la database
    # info arrondissement contient les arrondissements de Lyon
    query = 'select * from arrondissement'
    info_arrondissement = pd.read_sql_query(query,conn)
    # Jointure des deux tables sur arrondissement
    final_table = pd.merge(info_resto, info_arrondissement, on='arrondissement', how='inner')
    db.close()

    # Convertir les valeurs des arrondissements en entiers pour les arrondir
    final_table['arrondissement'] = final_table['arrondissement'].astype(int).astype(str)

    # Transformer les valeurs de catégories de prix
    final_table['categorie_prix'] = final_table['categorie_prix'].replace({
        '€': '€ : Pas cher et rapide',
        '€€-€€€': '€€-€€ : Intermédiaire',
        '€€€€': '€€€€ : Restaurant gourmet'
    })

    # Filtrer les données pour ne conserver que les arrondissements 69006 et 69008
    filtered_table = final_table[final_table['arrondissement'].isin(['69006', '69008'])]

    # Calculer les proportions
    proportion_table = filtered_table.groupby(['arrondissement', 'categorie_prix']).size().reset_index(name='count')
    total_counts = proportion_table.groupby('arrondissement')['count'].transform('sum')
    proportion_table['proportion'] = proportion_table['count'] / total_counts

    st.title('Analyse des restaurants par arrondissement et catégorie de prix')
    st.write(info_arrondissement) 

    # Création du graphique en barres avec les proportions
    fig = px.bar(proportion_table, x='arrondissement', y='proportion', color='categorie_prix', barmode='stack',
                title='Proportion de restaurants par arrondissement et catégorie de prix',
                labels={'arrondissement': 'Arrondissement', 'proportion': 'Proportion'})
    st.plotly_chart(fig)

    # Table qui montre les comparaisons de richesse des arrondissements
    st.write(proportion_table)
    


    ###################################################### 
    ######################################################