import folium
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import warnings
import os


# Ignorer les avertissements
warnings.filterwarnings("ignore")

#################### Données factices pour test de l'interface ##################

# Importation des coordonnées GPS depuis les adresses dans un fichier .csv

filepath_coordonnees = 'C:/Users/Elise/Desktop/NLP/coordonnees.csv'
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
    # Folium map
    map = folium.Map(location=[45.764043, 4.850000], zoom_start=12)  # Lyon's coordinates

    for i in range (0,df_coordonnees.shape[0]):
    #   nom = df_coordonnees["Nom"][i]
      location = [df_coordonnees["Latitude"][i],df_coordonnees["Longitude"][i]]
      popup_content = f'Nom : {df_coordonnees["Nom"][i]}<br>Note moyenne : {df_coordonnees["Note_moyenne"][i]}<br>Type restaurant : {df_coordonnees["Tags"][i]}'
      popup = folium.Popup(
            popup_content,
            max_width=300
            )
      folium.Marker(location, popup=popup).add_to(map)

    # Afficher la carte avec Streamlit
    st.components.v1.html(map._repr_html_(), height=500)

####################################################################################

