import sqlite3
import os
import pandas as pd
import numpy as np
import re
from geopy.geocoders import Nominatim


class DBHandling:
    """Class pour gérer les opérations à la base de données SQLite (Singleton)."""
    
    _instance = None  # Instance unique de la classe
    
    def __new__(cls, db_path: str = "data/database.db"):
        """Crée une instance unique ou renvoie l'instance existante."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "data/database.db"):
        """
        Initialise la classe avec le chemin de la base de données.
        Cette méthode est appelée uniquement lors de la première création de l'instance.
        
        Args:
            db_path (str): Chemin vers le fichier de la base de données SQLite.
        """
        if not self.__initialized:  # Vérifie si l'instance a déjà été initialisée
            self.db_path = db_path
            self.conn = None
            self.__initialized = True  # Marque l'instance comme initialisée

    def connect(self):
        """
        Connexion à la base de données, par défaut à data/database.db.

        Exemple:
            db = DBHandling()
            db.connect()
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Connexion à la base de données réussie : {self.db_path}")
        except sqlite3.Error as e:
            print(f"Erreur de connexion : {e}")
            print(f"Chemin : {self.db_path}")
        

    def close(self):
        """
        Ferme la connexion à la base de données.

        Exemple:
            db = DBHandling()
            db.connect()
            db.close()
        """
        if self.conn:
            self.conn.close()

    def execute_query(self, query:str, params=None):
        """
        Exécute une requête SQL.

        Args:
            query (str): La requête SQL à exécuter.
            params (tuple, optional): Les paramètres de la requête SQL.

        Returns:
            sqlite3.Cursor: Le curseur de la base de données après exécution de la requête.

        Exemple:
            db = DBHandling()
            db.connect()
            db.execute_query("CREATE TABLE IF NOT EXISTS restaurant (id INTEGER PRIMARY KEY, nom TEXT, type_cuisine TEXT, fourchette_prix TEXT, adresse TEXT, note_moyenne REAL)")
            db.close()
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor

    def fetch_all(self, query:str, params=None):
        """
        Récupère toutes les lignes à partir d'une requête.

        Args:
            query (str): La requête SQL à exécuter.
            params (tuple, optional): Les paramètres de la requête SQL.

        Returns:
            list: Une liste de toutes les lignes récupérées.

        Exemple:
            db = DBHandling()
            db.connect()
            rows = db.fetch_all("SELECT * FROM restaurant")
            db.close()
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def fetch_one(self, query:str, params=None):
        """
        Récupère une seule ligne à partir d'une requête.

        Args:
            query (str): La requête SQL à exécuter.
            params (tuple, optional): Les paramètres de la requête SQL.

        Returns:
            tuple: Une seule ligne récupérée.

        Exemple:
            db = DBHandling()
            db.connect()
            row = db.fetch_one("SELECT * FROM restaurant WHERE id = ?", (1,))
            db.close()
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def create_tables(self):
        """
        Crée les tables 'restaurant' et 'avis' dans la base de données.

        Exemple:
            db = DBHandling()
            db.connect()
            db.create_tables()
            db.close()
        """
        try:
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS arrondissement (
                arrondissement INTEGER PRIMARY KEY,
                taux_menage_imposable INTEGER,
                mediane_niveau_de_vie INTEGER,
                taux_pauvrete INTEGER
            )
            """)
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS restaurant (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type_cuisine TEXT,
                fourchette_prix TEXT,
                adresse TEXT,
                note_moyenne REAL,
                description TEXT,
                arrondissement INTEGER,
                categorie_prix TEXT,
                latitude REAL,
                longitude REAL,
                FOREIGN KEY (arrondissement) REFERENCES arrondissement(arrondissement)
            )
            """)
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS avis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_restaurant INTEGER,
                date DATE,
                note REAL,
                commentaire TEXT,
                FOREIGN KEY (id_restaurant) REFERENCES restaurant(id)
            )
            """)
            print("Tables créées avec succès.")
        except sqlite3.Error as e:
            print("Erreur lors de la création des tables.")
            print(f"An error occurred: {e}")
    
    def insert_restaurant(self, nom: str, type_cuisine: str, fourchette_prix: str, adresse: str, note_moyenne: float, description: str = "Description non renseigner", categorie_prix: str = None):
        """
        Insère un restaurant dans la table 'restaurant'.

        Args:
            nom (str): Nom du restaurant.
            type_cuisine (str): Type de cuisine du restaurant.
            fourchette_prix (str): Fourchette de prix du restaurant.
            adresse (str): Adresse du restaurant.
            note_moyenne (float): Note moyenne du restaurant.
            description (str, optional): Description du restaurant. Par défaut "Description non renseigner".

        Exemple:
            db = DBHandling()
            db.connect()
            db.insert_restaurant("Le Petit Paris", "Français", "€€", "1 rue de Paris, 75001 Paris", 4.5, "Petit restaurant français sympa.")
            db.close()
        """
        # Gestion arrondissement
        arrondissement = self._extract_postal_code(adresse)

        # Get the lat and long from the address
        # Enlever la virgule dans adresse car erreur d'argument
        adresse = adresse.replace(",", "")
        coords = self._find_coord(str(adresse)) # Use Nominatim to get the coordinates
        if coords is None:
            # Quelques fois geopy a du mal avec l'adresse mais peut fonctionner avec le resto + ville
            print(nom)
            coords = self._find_coord(str(nom + ", Lyon"))
        if coords is None:
            print(f"Impossible de trouver les coordonnées pour l'adresse : {adresse}")
        
        latitude, longitude = coords
        
        try:
            self.execute_query("INSERT INTO restaurant (nom, type_cuisine, fourchette_prix, adresse, note_moyenne, description, arrondissement, categorie_prix, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                               , (nom, type_cuisine, fourchette_prix, adresse, note_moyenne, description, arrondissement, categorie_prix, latitude, longitude))
            print("Insertion réussie.")
        except sqlite3.Error as e:
            print("Erreur lors de l'insertion.")
            print(f"An error occurred: {e}")

    def insert_avis(self, id_restaurant: int, date: str, note: int, commentaire: str):
        """
        Insère un avis dans la table 'avis'.

        Args:
            id_restaurant (int): ID du restaurant.
            date (str): Date de l'avis.
            note (int): Note de l'avis.
            commentaire (str): Commentaire de l'avis.

        Exemple:
            db = DBHandling()
            db.connect()
            db.insert_avis(1, "déc. 2024", 5, "Super restaurant, je recommande !")
            db.close()
        """
        try:
            self.execute_query("INSERT INTO avis (id_restaurant, date, note, commentaire) VALUES (?, ?, ?, ?)", (id_restaurant, date, note, commentaire))
            print("Insertion réussie.")
        except sqlite3.Error as e:
            print("Erreur lors de l'insertion.")
            print(f"An error occurred: {e}")
    
    def insert_arrondissement(self, arrondissement: int, taux_menage_imposable: int, mediane_niveau_de_vie: int, taux_pauvrete: int):
        """
        Insère un arrondissement dans la table 'arrondissement'.

        Args:
            arrondissement (int): Code de l'arrondissement.
            taux_menage_imposable (int): Taux de ménage imposable.
            mediane_niveau_de_vie (int): Médiane du niveau de vie.
            taux_pauvrete (int): Taux de pauvreté.

        Exemple:
            db = DBHandling()
            db.connect()
            db.insert_arrondissement(69001, 60, 25980, 15)
            db.close()
        """
        try:
            self.execute_query(
                "INSERT INTO arrondissement (arrondissement, taux_menage_imposable, mediane_niveau_de_vie, taux_pauvrete) VALUES (?, ?, ?, ?)",
                (arrondissement, taux_menage_imposable, mediane_niveau_de_vie, taux_pauvrete)
            )
            print(f"Arrondissement {arrondissement} inséré avec succès.")
        except sqlite3.Error as e:
            print("Erreur lors de l'insertion de l'arrondissement.")
            print(f"An error occurred: {e}")

    def _find_coord(self, address: str) -> list:
        """
        Trouve les coordonnées (latitude, longitude) pour une adresse donnée.
        
        Args:
            address (str): L'adresse pour laquelle trouver les coordonnées.
        
        Returns:
            list: [latitude, longitude] ou None si l'adresse n'est pas trouvée.
        """
        geolocator = Nominatim(user_agent="geoapi")
        location = None

        location = geolocator.geocode(address)
        print(location)
        if location!=None:
            latitude = location.latitude
            longitude = location.longitude
            return [latitude, longitude]
        return None
    
    def _extract_postal_code(self, address: str) -> int:
        """
        Extrait le code postal d'une adresse.

        Args:
            address (str): L'adresse complète.

        Returns:
            int: Le code postal extrait ou None si non trouvé.
        """
        # Regex pattern to match French postal codes (5 digits)
        pattern = r'\b\d{5}\b'
        match = re.search(pattern, address)
        if match:
            return int(match.group(0))
        return None
    
    def combine_tables(self, avis: pd.DataFrame, infos_resto: pd.DataFrame, arrondissement: pd.DataFrame) -> pd.DataFrame:
        """
        Combine les tables avis, infos_resto et arrondissement en effectuant des jointures successives.

        Args:
            avis (pd.DataFrame): Table contenant les avis.
            infos_resto (pd.DataFrame): Table contenant les informations des restaurants.
            arrondissement (pd.DataFrame): Table contenant les informations des arrondissements.

        Returns:
            pd.DataFrame: Table finale combinée avec les informations des avis,
                        des restaurants et des arrondissements.

        Exemple:
            db = DBHandling()
            avis_df = pd.DataFrame(...)
            resto_df = pd.DataFrame(...)
            arrond_df = pd.DataFrame(...)
            combined_df = db.combine_tables(avis_df, resto_df, arrond_df)
        """
        # Jointure entre avis et infos_resto
        combined = pd.merge(
            avis,
            infos_resto,
            left_on='id_restaurant',
            right_on='id',
            how='left',
            suffixes=('_avis', '_resto')
        )

        # Jointure avec arrondissement
        final_table = pd.merge(
            combined,
            arrondissement,
            on='arrondissement',
            how='inner'
        )

        # Supprimer la colonne id_restaurant pour éviter les doublons
        final_table = final_table.drop(columns=['id_restaurant'])

        # Renommer les colonnes pour plus de clarté
        final_table = final_table.rename(columns={
            'note': 'note_avis',
            'note_moyenne': 'note_moyenne_resto',
            'nom': 'nom_resto',
        })

        return final_table