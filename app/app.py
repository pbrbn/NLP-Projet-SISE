import os
import sys
import pandas as pd
import sqlite3

import folium
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium # type: ignore
import plotly.express as px


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'scraping')))
from restaurant_scraper import RestaurantScraper
from find_url import find_url_restaurant


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'database_handling')))
from database_handling import DBHandling


from analysis2resto import comparaison_deux_resto

#################### Données factices pour test de l'interface ##################

# Importation des coordonnées GPS depuis les adresses dans un fichier .csv

# # Définition du chemin du répertoire courant (dossier 'app')
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Définition du chemin vers 'coordonnees.csv'
# filepath_coordonnees = os.path.join(current_dir, 'coordonnees.csv')
# df_coordonnees = pd.read_csv(filepath_or_buffer=filepath_coordonnees,sep=";")

# Récupération des données depuis la database
db = DBHandling("../data/database.db")
db.connect()
conn = sqlite3.connect("../data/database.db")
query = 'select * from restaurant'
info_resto = pd.read_sql_query(query,conn)
st.write(info_resto.head())

db.close()

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
        default_index=0
    )

####################################################################################
########################### Pages content ##########################################
####################################################################################

# Page to add a new restaurant in the database -------------------------------------

if page == page1_add_restaurant:
    st.title("Add a restaurant to the database")
    st.write("Type a restaurant name - the app will google-search it for you")

    # Formulaire pour ajouter une URL Tripadvisor
    with st.form(key="add_restaurant"):
        nom_resto_user = str(st.text_input("Restaurant name"))
        
        url_resto = find_url_restaurant(nom_resto_user)
        
        search_button = st.form_submit_button("Search")
        
        # Recherche d'un restaurant correspondant au nom saisi par l'utilisateur
        if search_button:
            # Lance le scraping des information du restaurant à partir de l'URL générée par 'find_url_restaurant'
            rscrap = RestaurantScraper(base_url=url_resto)
            
            df_info_resto_new = rscrap.scrape_infos_resto()
            nom_new = df_info_resto_new.iloc[0,0]
            type_cuisine_new = df_info_resto_new.iloc[0,1]
            adress_new = df_info_resto_new.iloc[0,3]

            
            # Affichage des information avant ajout à la database
            st.success(f"Restaurant found")

            st.write(f'Nom du restaurant : {nom_new}')
            st.write(f'Cuisine type : {type_cuisine_new}')
            st.write(f'Adress : {adress_new}')

        # Ajout du restaurant à la database

        add_to_db_button=st.form_submit_button("Click here to add to database",type="primary")
        
        if add_to_db_button: 
            # Scrapping complet du restaurant sut Tripadvisor
            rscrap = RestaurantScraper(base_url=url_resto)
            df_info_resto_new = rscrap.scrape_infos_resto()
            # df_description_new = rscrap.scrape_description_resto()
            df_info_avis_new = rscrap.scrape_infos_avis()

            
            nom_new = df_info_resto_new.iloc[0,0]
            type_cuisine_new = df_info_resto_new.iloc[0,1]
            fourchette_prix_new = df_info_resto_new.iloc[0,2]
            adress_new = df_info_resto_new.iloc[0,3]
            note_moy_new = df_info_resto_new.iloc[0,4]


            #Ajout à la database

            db.connect()
                # Ajout des informations du restaurant
            db.insert_restaurant(nom=nom_new,
                                 type_cuisine=type_cuisine_new,
                                 fourchette_prix=fourchette_prix_new,
                                 adresse=adress_new, 
                                 note_moyenne=note_moy_new,
                                 description = "Description non renseigner"
                                 )
                # Ajout des avis
            # db.insert_avis()
            db.close()
            
            
            st.success(f"Restaurant added to database")




            # PRINT DES RESULTATS POUR TESTS DE L'APPLI
            st.dataframe(df_info_resto_new)
            #st.write(description_new)
            st.dataframe(df_info_avis_new.head(5))

    # Temp create plotly graph with stacked bar chart
    # Jointure arrondissement et restaurant 
    db.connect()
    query = 'select * from restaurant'
    info_resto = pd.read_sql_query(query,conn)
    # info_resto contient tout les restaurants de la database
    # info arrondissement contient les arrondissements de Lyon
    query = 'select * from arrondissement'
    info_arrondissement = pd.read_sql_query(query,conn)
    # Jointure des deux tables sur arrondissement
    final_table = pd.merge(info_resto, info_arrondissement, on='arrondissement', how='inner')

    st.write(final_table.head())

    # mappage fourchette de prix

    db.close()


# Page to analyze 1 restaurant ----------------------------------------------------------

elif page == page2_analysis:
    st.title("Analysis")
    st.write("Analyze restaurant data.")
    
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
    col1_affichage, col_selectA = st.columns(2)
    
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
                padding: 7.5px;
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
            label='Analyze this restaurant',
            use_container_width=True,
            type="primary")
        
        if button_A == True :
            restaurant_A = restaurant_sélectionné

    # TEST POUR L'APPLI (valider la sélection d'un restaurant)############
    try :
        st.write(restaurant_A) 
    except :
        st.write('Select a restaurant on the map to start and launch analysis')
    ################




# Page to compare 2 restaurants ----------------------------------------------------------

elif page == page3_comparison:
    comparaison_deux_resto()


####################################################################################


