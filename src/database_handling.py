import sqlite3

class DBHandling:
    """Class pour gérer les opérations à la base de données SQLite.(CRUD)"""

    def __init__(self, db_path:str = "data/database.db"):
        """
        Initialise la classe avec le chemin de la base de données.

        Args:
            db_path (str): Chemin vers le fichier de la base de données SQLite.
        """
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """
        Connexion à la base de données, par défaut à data/database.db.

        Exemple:
            db = DBHandling()
            db.connect()
        """
        self.conn = sqlite3.connect(self.db_path)

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
                note INTEGER,
                commentaire TEXT,
                FOREIGN KEY (id_restaurant) REFERENCES restaurants(id)
            )
            """)
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    