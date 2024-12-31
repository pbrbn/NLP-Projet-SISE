import pandas as pd
from sqlalchemy import create_engine

class DataHandler:
    """
    Classe pour gérer les opérations de gestion des données, comme la combinaison, 
    l'agrégation, et la sauvegarde des données dans des fichiers ou des bases de données.
    """
    @staticmethod
    def combine_and_aggregate(infos_avis, infos_resto):
        """
        Combine les datasets des avis et des restaurants, puis agrège les commentaires par restaurant.

        Args:
            infos_avis (pd.DataFrame): DataFrame contenant les informations des avis.
            infos_resto (pd.DataFrame): DataFrame contenant les informations des restaurants.

        Returns:
            pd.DataFrame: DataFrame combiné et agrégé par restaurant.
        """
        # Combinaison des datasets
        merged_df = pd.merge(infos_avis, infos_resto, left_on='id_restaurant', right_on='id')

        # Agrégation des commentaires
        aggregated_df = merged_df.groupby(['id_x'], as_index=False).agg({
            'commentaire': lambda comments: ' | '.join(comments),  # Joindre les commentaires
            'nom': 'first',                                       # Nom unique par restaurant
            'type_cuisine': 'first',                              # Garder une seule valeur par restaurant
            'fourchette_prix': 'first',
            'description': 'first',
            'adresse': 'first',
            'note_moyenne': 'first'
        })

        # Renommer la colonne 'id_x' pour plus de clarté
        aggregated_df.rename(columns={'id_x': 'id_restaurant'}, inplace=True)
        return aggregated_df



    @staticmethod
    def save_preprocessed_data(data, filename):
        """
        Sauvegarde les données prétraitées dans un fichier CSV.

        Args:
            data (list or pd.DataFrame): Données à sauvegarder.
            filename (str): Nom du fichier CSV.

        Returns:
            None
        """
        df = pd.DataFrame(data, columns=['text']) if isinstance(data, list) else data
        df.to_csv(filename, index=False)

    @staticmethod
    def save_to_sqlite(df, db_name, table_name):
        """
        Sauvegarde un DataFrame dans une base de données SQLite.

        Args:
            df (pd.DataFrame): DataFrame à sauvegarder.
            db_name (str): Nom du fichier SQLite.
            table_name (str): Nom de la table.

        Returns:
            None
        """
        engine = create_engine(f'sqlite:///{db_name}')
        with engine.connect() as conn:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
