from mistralai import Mistral

#Clé API Hugging Face
MISTRAL_API_KEY = "A mettre dans un fichier .env"

class ResumerAvis:
    """
    Classe pour générer un résumé à partir d'une liste d'avis en utilisant l'API Mistral.
    """

    def __init__(self, api_key: str, model: str = "open-mistral-nemo-2407", max_length: int = 3500):
        """
        Initialise l'instance de la classe avec les paramètres nécessaires.

        Args:
            api_key (str): La clé API Mistral.
            model (str): Le modèle à utiliser pour la génération (par défaut: open-mistral-nemo-2407).
            max_length (int): Longueur maximale des avis combinés pour éviter de dépasser la limite de tokens.
        """
        self.api_key = api_key
        self.model = model
        self.max_length = max_length
        self.client = Mistral(api_key=self.api_key)

    def _prepare_prompt(self, avis: list[str]) -> str:
        """
        Prépare le prompt à envoyer au modèle à partir des avis fournis.

        Args:
            avis (list of str): Liste des avis pour un restaurant.

        Retourne:
            str: Prompt formaté prêt à être envoyé au modèle.
        """
        combined_avis = "\n".join(avis)

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
            "3. Une conclusion générale sur la satisfaction des clients.\n\n"
            "Résumé :"
        )
        return prompt

    def generer_resume(self, avis: list[str]) -> str:
        """
        Génère un résumé à partir d'une liste d'avis.

        Args:
            avis (list of str): Liste des avis pour un restaurant.

        Retourne:
            str: Résumé des avis ou un message indiquant qu'aucun avis n'est disponible.
        """
        if not avis or len(avis) == 0:
            return "Aucun avis disponible."

        prompt = self._prepare_prompt(avis)

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