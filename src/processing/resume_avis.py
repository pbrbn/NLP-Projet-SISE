from mistralai import Mistral

#Clé API Hugging Face
MISTRAL_API_KEY = "A mettre dans un fichier .env "

def resume_avis(avis : list[str]) -> str:
    """
    Génère un résumé à partir d'une liste d'avis.
    
    Args:
        avis (list of str): Liste des avis pour un restaurant.
    
    Retourne:
        str: Résumé des avis ou un message indiquant qu'aucun avis n'est disponible.
    """
    if not avis or len(avis) == 0:
        return "Aucun avis disponible."

    #Vérification de la longueur des avis combinés
    combined_avis = "\n".join(avis)
    if len(combined_avis) > 3500:  #Pour éviter de dépasser la limite de tokens (4096 pour GPT-3)
        combined_avis = combined_avis[:3500]  #Troncature
    
    #Prompt
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
    
    model = "open-mistral-nemo-2407"
    
    client = Mistral(api_key=MISTRAL_API_KEY)

    chat_response = client.chat.complete(
        model = model,
        temperature=0.5,
        messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    return chat_response.choices[0].message.content