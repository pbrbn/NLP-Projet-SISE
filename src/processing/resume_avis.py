from mistralai import Mistral
import os
from dotenv import load_dotenv
import logging

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class ResumerAvis:
    """
    Classe pour générer un résumé à partir d'une liste d'avis en utilisant l'API Mistral.
    """

    def __init__(self, api_key=MISTRAL_API_KEY, model: str = "open-mistral-nemo-2407", max_length: int = 130000, type_query: str = "analyze_1"):
        """
        Initialise l'instance de la classe avec les paramètres nécessaires.

        Args:
            api_key (str): La clé API Mistral.
            model (str): Le modèle à utiliser pour la génération (par défaut: open-mistral-nemo-2407).
            max_length (int): Longueur maximale des avis combinés pour éviter de dépasser la limite de tokens.
            type_query (str): Le type de requête ('analyze_1', 'analyze_2', 'analyze_clusters'), ce paramètre permet soit d'analyser les commentaires d'un restaurant, soit de comparer 2 restaurants.
        """
        self.api_key = api_key
        self.model = model
        self.max_length = max_length
        self.type_query = type_query
        self.client = Mistral(api_key=self.api_key)
        logging.basicConfig(level=logging.INFO)

    def _prepare_prompt(self, avis_restaurant_1: list[str]=None, avis_restaurant_2: list[str] = None, avis_clusters : list[list[str]] = None) -> str:
        """
        Prépare le prompt à envoyer au modèle à partir des avis fournis.

        Args:
            avis_restaurant_1 (list of str): Liste des avis pour un restaurant 1.
            avis_restaurant_2 (list of str): Liste des avis pour un restaurant 2.
            avis_clusters list(list of str) : Liste des avis par clusters

        Retourne:
            str: Prompt formaté prêt à être envoyé au modèle.
        """
        if avis_restaurant_1 and not isinstance(avis_restaurant_1, list) or not all(isinstance(avis, str) for avis in avis_restaurant_1):
            raise ValueError("avis_restaurant_1 doit être une liste de chaînes de caractères.")

        if avis_restaurant_2 and (not isinstance(avis_restaurant_2, list) or not all(isinstance(avis, str) for avis in avis_restaurant_2)):
            raise ValueError("avis_restaurant_2 doit être une liste de chaînes de caractères.")

        # Analyse des commentaires d'un restaurant
        if self.type_query == "analyze_1":
            combined_avis = "\n".join(avis_restaurant_1)

            # Troncature si nécessaire
            if len(combined_avis) > self.max_length:
                combined_avis = combined_avis[:(self.max_length)]

            prompt = (
                "Vous êtes un expert en synthèse de données. "
                "Voici une liste d'avis clients pour un restaurant. Chaque avis peut inclure des commentaires "
                "sur la nourriture, le service, l'ambiance, le prix, ou d'autres aspects.\n\n"
                "Avis des clients :\n"
                f"{combined_avis}\n\n"
                "Votre tâche est de fournir un résumé clair et précis. "
                "Incluez les points suivants dans votre résumé :\n"
                "1. Les aspects positifs les plus fréquemment mentionnés.\n"
                "2. Les aspects négatifs ou critiques s'il y en a.\n"
                "3. Une conclusion générale sur la satisfaction des clients.\n"
                "4. Est ce que vous nous recommandez d'aller manger dans ce restaurant.\n\n"
                "Résumé :"
            )
            return prompt

        # Analyse de 2 restaurants
        elif self.type_query == "analyze_2":
            if not avis_restaurant_2 or len(avis_restaurant_2) == 0:
                raise ValueError("Pour la comparaison de deux restaurants, veuillez fournir les avis du second restaurant.")

            combined_avis_restaurant_1 = "\n".join(avis_restaurant_1)
            combined_avis_restaurant_2 = "\n".join(avis_restaurant_2)

            # Troncature si nécessaire
            if len(combined_avis_restaurant_1) + len(combined_avis_restaurant_2) > (self.max_length):
                combined_avis = (combined_avis_restaurant_1 + "\n" + combined_avis_restaurant_2)[:(self.max_length)]
            else:
                combined_avis = combined_avis_restaurant_1 + "\n" + combined_avis_restaurant_2

            prompt = (
                "Vous êtes un expert en comparaison d'avis clients. "
                "Voici les avis de deux restaurants différents. Comparez les points suivants entre les deux restaurants :\n\n"
                "Restaurant 1 - Avis des clients :\n"
                f"{combined_avis_restaurant_1}\n\n"
                "Restaurant 2 - Avis des clients :\n"
                f"{combined_avis_restaurant_2}\n\n"
                "Votre tâche est de comparer les deux restaurants sur les aspects suivants :\n"
                "1. Les aspects positifs les plus fréquemment mentionnés pour chaque restaurant.\n"
                "2. Les aspects négatifs ou critiques pour chaque restaurant.\n"
                "3. Une conclusion générale sur la satisfaction des clients pour chaque restaurant.\n"
                "4. Faire une recommandation sur le restaurant qu'il faut choisir entre les deux."
                "Résumé comparatif :"
            )
            return prompt
        
        #Analyse des clusters 
        elif self.type_query == "analyze_clusters":
            if not avis_clusters or avis_clusters == 0:
                raise ValueError("Pour l'analyse des clusters, veuillez fournir les avis pour chaque clusters.")

            combined_avis_clusters = ["\n".join(cluster) for cluster in avis_clusters]

            # # Troncature si nécessaire
            # if len(combined_avis_clusters[0]) + len(combined_avis_clusters[1]+len(combined_avis_clusters[2])) > (self.max_length - 200):
            #     combined_avis = (combined_avis_clusters[0])[:((self.max_length-200)/3)] + "\n" + (combined_avis_clusters[1][:((self.max_length-200)/3)]) + "\n" + (combined_avis_clusters[2][:((self.max_length-200)/3)])

            prompt = (
                "Vous êtes un analyste d'avis de restaurant. Vous avez reçu trois clusters d'avis provenant du même restaurant. Chaque cluster représente un groupe d'avis avec des caractéristiques similaires. Votre tâche est de comparer ces clusters pour mettre en lumière les thématiques principales de chaque cluster et leurs différences.\n"
                "Voici les avis pour chaque cluster :\n"
                "Cluster 1 :\n"
                f"{combined_avis_clusters[0]}\n\n"
                "Cluster 2 :\n" 
                f"{combined_avis_clusters[1]}\n\n"
                "Cluster 3 :\n" 
                f"{combined_avis_clusters[2]}\n\n"
                "Pour chaque cluster, identifiez les thématiques principales en analysant les avis. Ensuite, comparez les thématiques entre les clusters et mettez en lumière les différences. Fournissez une analyse détaillée en répondant aux questions suivantes :\n"
                "1. Quelles sont les différences majeures entre les thématiques des clusters ?\n"
                "2. Quelles sont les impressions générales des clients pour chaque cluster ?\n"
                "Fournissez une analyse détaillée en répondant à ces questions.\n"
            )

            return prompt

    def generer_resume(self, avis_restaurant_1: list[str]=None, avis_restaurant_2: list[str] = None, avis_clusters : list[list[str]] = None) -> str:
        """
        Génère un résumé à partir d'une liste d'avis.

        Args:
            avis_restaurant_1 (list of str): Liste des avis pour un restaurant 1.
            avis_restaurant_2 (list of str): Liste des avis pour un restaurant 2.
            avis_clusters list(list of str): Liste des listes des avis par clusters

        Retourne:
            str: Résumé des avis ou un message indiquant qu'aucun avis n'est disponible.
        """
        if self.type_query == "analyze_1" and (not avis_restaurant_1 or len(avis_restaurant_1) == 0):
            return "Aucun avis disponible pour générer un résumé."

        if self.type_query == "analyze_2" and (not avis_restaurant_1 or len(avis_restaurant_1) == 0 or not avis_restaurant_2 or len(avis_restaurant_2) == 0):
            return "Les avis des deux restaurants sont nécessaires pour générer un résumé comparatif."
        
        if self.type_query == "analyze_clusters" and (not avis_clusters or len(avis_clusters)==0):
            return "Les avis des clusters sont nécessaires pour générer un résumé comparatif."

        prompt = self._prepare_prompt(avis_restaurant_1, avis_restaurant_2, avis_clusters)

        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "min_length" : 300,
                        "max_tokens" : 2000,
                    },
                ]
            )
            return chat_response.choices[0].message.content
        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            return f"Une erreur de valeur s'est produite : {str(ve)}"
        except ConnectionError as ce:
            logging.error(f"ConnectionError: {ce}")
            return f"Une erreur de connexion s'est produite : {str(ce)}"
        except Exception as e:
            logging.error(f"Exception: {e}")
            return f"Une erreur s'est produite lors de la génération du résumé : {str(e)}"
