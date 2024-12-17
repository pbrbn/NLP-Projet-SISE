import folium
from geopy.geocoders import Nominatim

def find_coord(address:str) -> list :
    # Initialiser le géocodeur avec Nominatim
    geolocator = Nominatim(user_agent="geoapi")
    
    # Géocoder l'adresse pour obtenir les coordonnées
    location = geolocator.geocode(address)
    
    if location:
        latitude = location.latitude
        longitude = location.longitude
        coord = [latitude, longitude]
        return coord

    else:
        return None
