import folium
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import warnings
import os
from streamlit_folium import st_folium # type: ignore

from tools_functions_app import *


# Ignorer les avertissements
warnings.filterwarnings("ignore")

#################### Données factices pour test de l'interface ##################

# Importation des coordonnées GPS depuis les adresses dans un fichier .csv

filepath_coordonnees = 'app/coordonnees.csv'
df_coordonnees = pd.read_csv(filepath_or_buffer=filepath_coordonnees,sep=";")



####################################################################################
############################# Sidebar menu #########################################
####################################################################################

# Names of the pages
page1_add_restaurant = str('Add a new restaurant')
page2_analysis = str('Analysis of 1 restaurant')
page3_comparison = str('Compare 2 restaurants')

# Sidebar parameters
with st.sidebar:
    page = option_menu(
        "Menu", 
        [page1_add_restaurant,page2_analysis,page3_comparison], 
        icons=['plus', 'bar-chart-fill', 'calculator'], 
        menu_icon="house",
        default_index=1
    )

####################################################################################
########################### Pages content ##########################################
####################################################################################

# Page to add a new restaurant in the database -------------------------------------

if page == page1_add_restaurant:
    st.title("Add a Restaurant")
    st.write("Use this page to add a new restaurant.")
    # Exemple de formulaire pour ajouter un restaurant
    with st.form(key="add_restaurant"):
        name = st.text_input("Restaurant Name")
        rating = st.slider("Rating", 0.0, 5.0, step=0.1)
        reviews = st.number_input("Number of Reviews", min_value=0, step=1)
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            st.success(f"Restaurant {name} with rating {rating} added!")


# Page to analyze 1 restaurant ----------------------------------------------------------

elif page == page2_analysis:
    st.title("Analysis")
    st.write("Analyze restaurant data.")
    




# Page to compare 2 restaurants ----------------------------------------------------------

elif page == page3_comparison:
    st.title("Comparison")
    st.write("Compare restaurants on a map.")
    
    # Folium map initiation
    map = folium.Map(location=[45.764043, 4.850000], zoom_start=12)  # Lyon's coordinates

    # Generating the restaurant markers on the map
    for i in range (0,df_coordonnees.shape[0]):
      location = [df_coordonnees["Latitude"][i],df_coordonnees["Longitude"][i]]
      popup_content = f'Nom : {df_coordonnees["Nom"][i]}<br>Note moyenne : {df_coordonnees["Note_moyenne"][i]}<br>Type restaurant : {df_coordonnees["Tags"][i]}'
      popup = folium.Popup(
            popup_content,
            max_width=300
            )
      folium.Marker(location, popup=popup).add_to(map)

    # Affichage de la carte dans Streamlit
    st_folium_output = st_folium(map, width=700, height=500)

    # Diviser l'espace en deux colonnes
    col1_affichage, col_selectA, col_selectB = st.columns(3)
    
    # Initialisation de la ligne "Sélection de restaurant"

    
    if not st_folium_output.get("last_object_clicked") :
        restaurant_sélectionné = str('Sélectionner un restaurant')


    # Gestion de la sélection d'un marker
    if st_folium_output and st_folium_output.get("last_object_clicked"):
        clicked_object = st_folium_output["last_object_clicked"]
        lat, lon = clicked_object["lat"], clicked_object["lng"]

        # Trouver la ligne correspondante dans le DataFrame
        mask = (df_coordonnees['Latitude'] == lat) & (df_coordonnees['Longitude'] == lon)
        if mask.any():
            restaurant_sélectionné = df_coordonnees[mask].iloc[0,1]

        else:
            st.warning("Aucun individu trouvé pour ces coordonnées.")

    # Ligne de sélection d'un restaurant - 3 widgets
    with col1_affichage :
        st.markdown(body = f"""
            <div style="
                background-color: lightblue;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
                color: black;
                font-weight: bold;
            ">
                {restaurant_sélectionné}
            </div>
        """, unsafe_allow_html=True)

    with col_selectA :
        button_A = st.button(
            label='Définir comme restaurant A',
            use_container_width=True,
            args=
            on_click=lambda )
        
        if button_A == True :
            restaurant_A = restaurant_sélectionné

        try :
            markdown_A = st.markdown(body=f'Restaurant A : {restaurant_A}')
        except :
            markdown_A = st.markdown(body=f'sélectionner un restaurant')

    with col_selectB :
        button_B = st.button(label='Définir comme restaurant B',use_container_width=True)
        
        if button_B == True :
            restaurant_B = restaurant_sélectionné

        try :
            markdown_B = st.markdown(body=f'Restaurant B : {restaurant_B}')
        except :
            markdown_B = st.markdown(body=f'sélectionner un restaurant')



####################################################################################


