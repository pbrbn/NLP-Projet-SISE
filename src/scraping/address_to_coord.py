import folium
from geopy.geocoders import Nominatim

def find_coord(address):
    # Initialiser le géocodeur avec Nominatim
    geolocator = Nominatim(user_agent="geoapi")
    
    # Géocoder l'adresse pour obtenir les coordonnées
    location = geolocator.geocode(address)
    
    if location:
        latitude = location.latitude
        longitude = location.longitude
        print(f"Adresse trouvée : {location.address}")
        print(f"Coordonnées : Latitude = {latitude}, Longitude = {longitude}")
        coord = [latitude, longitude]

        return coord

    else:
        print("Adresse non trouvée.")
        return None


adresse = "1 Quai du Commerce, 69009 Lyon France"
print(find_coord(adresse))