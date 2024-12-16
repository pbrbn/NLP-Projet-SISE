import sqlite3
import os

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
            db.execute_query("CREATE TABLE IF NOT EXISTS restaurants (id INTEGER PRIMARY KEY, nom TEXT, type_cuisine TEXT, fourchette_prix TEXT, adresse TEXT, note_moyenne REAL)")
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
            rows = db.fetch_all("SELECT * FROM restaurants")
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
            row = db.fetch_one("SELECT * FROM restaurants WHERE id = ?", (1,))
            db.close()
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def create_tables(self):
        """
        Crée les tables 'restaurants' et 'avis' dans la base de données.

        Exemple:
            db = DBHandling()
            db.connect()
            db.create_tables()
            db.close()
        """
        try:
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type_cuisine TEXT,
                fourchette_prix TEXT,
                adresse TEXT,
                note_moyenne REAL
            )
            """)
            self.execute_query("""
            CREATE TABLE IF NOT EXISTS avis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_restaurant INTEGER,
                date DATE,
                note REAL,
                commentaire TEXT,
                FOREIGN KEY (id_restaurant) REFERENCES restaurants(id)
            )
            """)
            print("Tables créées avec succès.")
        except sqlite3.Error as e:
            print("Erreur lors de la création des tables.")
            print(f"An error occurred: {e}")
    
    def insert_restaurant(self, nom: str, type_cuisine: str, fourchette_prix: str, adresse: str, note_moyenne: float):
        """
        Insère un restaurant dans la table 'restaurants'.

        Args:
            nom (str): Nom du restaurant.
            type_cuisine (str): Type de cuisine du restaurant.
            fourchette_prix (str): Fourchette de prix du restaurant.
            adresse (str): Adresse du restaurant.
            note_moyenne (float): Note moyenne du restaurant.

        Exemple:
            db = DBHandling()
            db.connect()
            db.insert_restaurant("Le Petit Paris", "Français", "€€", "1 rue de Paris, 75001 Paris", 4.5)
            db.close()
        """
        try:
            self.execute_query("INSERT INTO restaurants (nom, type_cuisine, fourchette_prix, adresse, note_moyenne) VALUES (?, ?, ?, ?, ?)", (nom, type_cuisine, fourchette_prix, adresse, note_moyenne))
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
    
    