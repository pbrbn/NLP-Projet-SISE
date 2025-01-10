import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import pandas as pd
import numpy as np
from typing import List, Optional, Union
import logging
import os

class Visualizer:
    """
    Classe pour gérer la visualisation des données textuelles et des résultats d'analyse.
    """
    
    def __init__(self, style: str = 'default'):
        """
        Initialise le visualiseur avec un style spécifique.
        
        Args:
            style: Style matplotlib à utiliser ('default', 'classic', etc.)
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        sns.set_style("whitegrid")
        
    def _setup_logging(self):
        """Configure le logging pour la classe."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def generate_wordcloud(self, 
                         text_data: str,
                         title: str = "Word Cloud",
                         output_file: Optional[str] = None,
                         width: int = 800,
                         height: int = 400,
                         background_color: str = 'white',
                         colormap: str = 'viridis',
                         max_words: int = 200) -> None:
        """
        Génère un nuage de mots à partir des données textuelles.
        
        Args:
            text_data: Texte pour générer le nuage de mots
            title: Titre du nuage de mots
            output_file: Chemin du fichier pour sauvegarder l'image
            width: Largeur de l'image
            height: Hauteur de l'image
            background_color: Couleur de fond
            colormap: Palette de couleurs à utiliser
            max_words: Nombre maximum de mots à afficher
            
        Raises:
            ValueError: Si le texte est vide
        """
        if not text_data or not isinstance(text_data, str):
            raise ValueError("Le texte fourni doit être une chaîne non vide")
            
        try:
            self.logger.info("Génération du nuage de mots...")
            
            wordcloud = WordCloud(
                width=width,
                height=height,
                background_color=background_color,
                colormap=colormap,
                max_words=max_words
            ).generate(text_data)
            
            plt.figure(figsize=(width/100, height/100))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.title(title, fontsize=16, pad=20)
            plt.axis('off') 
            plt.show()
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du nuage de mots: {str(e)}")
            raise

    def plot_confusion_matrix(self,
                            y_true: List,
                            y_pred: List,
                            labels: Optional[List[str]] = None,
                            title: str = "Matrice de confusion",
                            output_file: Optional[str] = None) -> None:
        """
        Affiche la matrice de confusion.
        
        Args:
            y_true: Labels réels
            y_pred: Prédictions
            labels: Noms des classes
            title: Titre du graphique
            output_file: Chemin pour sauvegarder l'image
        """
        try:
            cm = confusion_matrix(y_true, y_pred)
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, 
                       annot=True, 
                       fmt='d', 
                       cmap='Blues',
                       xticklabels=labels,
                       yticklabels=labels)
            
            plt.title(title)
            plt.ylabel('Vraies étiquettes')
            plt.xlabel('Prédictions')
            
            if output_file:
                plt.savefig(output_file, bbox_inches='tight')
                self.logger.info(f"Matrice de confusion sauvegardée dans {output_file}")
                
            plt.show()
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création de la matrice de confusion: {str(e)}")
            raise

    def plot_metrics_report(self,
                          y_true: List,
                          y_pred: List,
                          target_names: Optional[List[str]] = None) -> None:
        """
        Affiche un rapport complet des métriques de classification.
        
        Args:
            y_true: Labels réels
            y_pred: Prédictions
            target_names: Noms des classes
        """
        try:
            # Calcul des métriques
            report = classification_report(y_true, y_pred, 
                                        target_names=target_names, 
                                        output_dict=True)
            accuracy = accuracy_score(y_true, y_pred)
            
            # Création d'un DataFrame pour les métriques
            df_report = pd.DataFrame(report).T
            
            # Affichage des résultats
            print("\n=== Rapport de Classification ===")
            print(f"\nPrécision globale: {accuracy:.2%}")
            print("\nMétriques détaillées par classe:")
            print(df_report.round(3))
            
            # Visualisation des métriques
            plt.figure(figsize=(12, 6))
            metrics_to_plot = ['precision', 'recall', 'f1-score']
            
            df_plot = df_report.loc[target_names if target_names else df_report.index[:-3], 
                                  metrics_to_plot]
            
            df_plot.plot(kind='bar')
            plt.title('Métriques par classe')
            plt.xlabel('Classes')
            plt.ylabel('Score')
            plt.legend(title='Métriques')
            plt.tight_layout()
            plt.show()
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du rapport de métriques: {str(e)}")
            raise

    def plot_sentiment_distribution(self,
                                  sentiments: List[float],
                                  title: str = "Distribution des sentiments",
                                  output_file: Optional[str] = None) -> None:
        """
        Affiche la distribution des sentiments.
        
        Args:
            sentiments: Liste des scores de sentiment
            title: Titre du graphique
            output_file: Chemin pour sauvegarder l'image
        """
        try:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=sentiments, bins=30, kde=True)
            plt.title(title)
            plt.xlabel('Score de sentiment')
            plt.ylabel('Fréquence')
            
            if output_file:
                plt.savefig(output_file, bbox_inches='tight')
                self.logger.info(f"Distribution des sentiments sauvegardée dans {output_file}")
                
            plt.show()
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la création du graphique de distribution: {str(e)}")
            raise