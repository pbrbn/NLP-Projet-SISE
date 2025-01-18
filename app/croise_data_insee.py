# Importation des packages
import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling


def analyse_croisee_insee():

    # Importation des données depuis la database dans un dataframe 'df'
    query ="""SELECT 
    restaurant.id, 
    restaurant.fourchette_prix, 
    restaurant.note_moyenne,
    restaurant.arrondissement, 
    arrondissement.mediane_niveau_de_vie
    FROM 
    restaurant
    JOIN 
    arrondissement 
    ON 
    restaurant.arrondissement = arrondissement.arrondissement;
    """
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'database.db'))
    db = DBHandling(db_path=db_path)
    db.connect()
    requete = db.fetch_all(query=query)
    db.close()
    df = pd.DataFrame(requete)

    # Preprocessing des données
    df = df[df[1] != 'NA']
    df.rename(columns={0:'id',1:'fourchette_prix',2:'note_moyenne',3:'arrondissement',4:'mediane_niveau_de_vie'},inplace=True)
    df['note_moyenne'] = df['note_moyenne'] \
    .str.replace(",", ".") \
    .astype(float)

    # Conversion en variable numérique du prix à partir de 'fourchette_pruix' 
    df['prix_min'] = df['fourchette_prix'] \
    .str.split('-').str[0] \
    .str.replace(" €", "") \
    .str.replace(",", ".") \
    .str.replace("\xa0", "") \
    .str.replace("€", "").astype(float)
    df['prix_max'] = df['fourchette_prix'] \
    .str.split('-').str[1] \
    .str.replace(" €", "") \
    .str.replace(",", ".") \
    .str.replace("\xa0", "") \
    .str.replace("€", "").astype(float)
    df['mean_prix'] = (df["prix_max"]+df["prix_min"])/2

    # # Isolement des variables quantitatives (pour ACP)
    # df_lite = df.drop(labels=['fourchette_prix','arrondissement','id'],axis=1)
    # # ACP
    # acp = PCA(n_components=2)
    # principal_components = acp.fit_transform(df_lite)
    # pc1 = principal_components[:, 0]  # Premier facteur
    # pc2 = principal_components[:, 1]  # Deuxième facteur

    # Création d'un scatter plot
    fig = px.scatter(
        data_frame=df,
        x='mediane_niveau_de_vie',
        y='mean_prix',
        color='note_moyenne',
        color_continuous_scale='RdYlGn',
        labels={'mediane_niveau_de_vie':'Revenu médian/foyer',
                'mean_prix':'Prix moyen du restaurant',
                'note_moyenne':'Note moyenne'
        },
        title="Note des restaurants selon le revenu médian de l'arrondissement et le prix moyen"
    )
    st.plotly_chart(fig)


