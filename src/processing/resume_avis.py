from mistralai import Mistral

#Clé API Hugging Face
MISTRAL_API_KEY = "A mettre dans un fichier .env"

class ResumerAvis:
    """
    Classe pour générer un résumé à partir d'une liste d'avis en utilisant l'API Mistral.
    """

    def __init__(self, api_key: str, model: str = "open-mistral-nemo-2407", max_length: int = 3500, type_query: str = "analyze_1"):
        """
        Initialise l'instance de la classe avec les paramètres nécessaires.

        Args:
            api_key (str): La clé API Mistral.
            model (str): Le modèle à utiliser pour la génération (par défaut: open-mistral-nemo-2407).
            max_length (int): Longueur maximale des avis combinés pour éviter de dépasser la limite de tokens.
            type_query (str): Le type de requête ('analyze_1' ou 'analyze_2'), ce paramètre permet soit d'analyser les commentaires d'un restaurant, soit de comparer 2 restaurants. 
        """
        self.api_key = api_key
        self.model = model
        self.max_length = max_length
        self.type_query = type_query
        self.client = Mistral(api_key=self.api_key)

    def _prepare_prompt(self, avis_restaurant_1: list[str], avis_restaurant_2: list[str] = None) -> str:
        """
        Prépare le prompt à envoyer au modèle à partir des avis fournis.

        Args:
            avis_restaurant_1 (list of str): Liste des avis pour un restaurant 1.
            avis_restaurant_2 (list of str): Liste des avis pour un restaurant 2.

        Retourne:
            str: Prompt formaté prêt à être envoyé au modèle.
        """
        #Analyse des commentaires d'un restaurant 
        if self.type_query == "analyze_1" :
            combined_avis = "\n".join(avis_restaurant_1)

            # Troncature si nécessaire
            if len(combined_avis) > self.max_length:
                combined_avis = combined_avis[:self.max_length]

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
        
        #Analyse de 2 restaurants 
        elif self.type_query == "analyze_2" :
            if not avis_restaurant_2 or len(avis_restaurant_2) == 0:
                raise ValueError("Pour la comparaison de deux restaurants, veuillez fournir les avis du second restaurant.")

            combined_avis_restaurant_1 = "\n".join(avis_restaurant_1)
            combined_avis_restaurant_2 = "\n".join(avis_restaurant_2)

            # Troncature si nécessaire
            if len(combined_avis_restaurant_1) + len(combined_avis_restaurant_2) > self.max_length:
                combined_avis = (combined_avis_restaurant_1 + "\n" + combined_avis_restaurant_2)[:self.max_length]
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

    def generer_resume(self, avis_restaurant_1: list[str], avis_restaurant_2: list[str] = None) -> str:
        """
        Génère un résumé à partir d'une liste d'avis.

        Args:
            avis_restaurant_1 (list of str): Liste des avis pour un restaurant 1.
            avis_restaurant_2 (list of str): Liste des avis pour un restaurant 2.

        Retourne:
            str: Résumé des avis ou un message indiquant qu'aucun avis n'est disponible.
        """
        if self.type_query == "analyze_1" and (not avis_restaurant_1 or len(avis_restaurant_1) == 0):
            return "Aucun avis disponible pour générer un résumé."

        if self.type_query == "analyze_2" and (not avis_restaurant_1 or len(avis_restaurant_1) == 0 or not avis_restaurant_2 or len(avis_restaurant_2) == 0):
            return "Les avis des deux restaurants sont nécessaires pour générer un résumé comparatif."

        prompt = self._prepare_prompt(avis_restaurant_1, avis_restaurant_2)

        try:
            chat_response = self.client.chat.complete(
                model=self.model,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ]
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            return f"Une erreur s'est produite lors de la génération du résumé : {str(e)}"