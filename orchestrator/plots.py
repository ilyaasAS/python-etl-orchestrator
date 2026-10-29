# Importation de Matplotlib. 
# On force le mode 'Agg' pour que Matplotlib travaille "en cachette" (en arrière-plan) 
# sans ouvrir de vraie fenêtre graphique, ce qui est obligatoire pour exécuter les tests automatisés.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import de la classe de base DataOperation (qui gère l'attribut .data)
from orchestrator.operations import DataOperation

# Import de tous les mixins demandés pour enrichir les graphiques
from orchestrator.mixins import (
    ValidatedMixin,
    LoggedMixin,
    AuditedMixin,
    TimestampedMixin
)

# Import des exceptions personnalisées pour gérer proprement les erreurs de données ou de graphiques
from orchestrator.exceptions import ValidationError, PlotError


# 21. PlotOperation (Classe intermédiaire / abstraite pour les graphiques)
class PlotOperation(
    ValidatedMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    DataOperation
):
    """
    Classe intermédiaire pour toutes les opérations de visualisation.
    Elle combine la gestion des données, les validations, les logs, l'audit et l'horodatage.
    """

    def __init__(self, data=None, x=None, y=None, title="Graphique", *args, **kwargs):
        """
        Constructeur coopératif. 
        Il initialise les données, les variables des axes (x, y) et le titre du graphique,
        puis transmet le reste des arguments aux classes parentes et mixins via super().
        """
        self.x = x
        self.y = y
        self.title = title
        # Appel du constructeur coopératif suivant dans la chaîne du MRO
        super().__init__(data=data, *args, **kwargs)
    
    # 23. Validation des graphiques
    def validate(self):
        """
        Règles de validation obligatoires avant de générer un graphique :
        - Vérifie que les données ne sont pas vides.
        - Vérifie que les axes x et y sont renseignés.
        - Vérifie que les colonnes x et y existent bien dans les dictionnaires de données.
        """
        # Appel du validate() des mixins ou classes parentes dans le MRO
        super().validate()
        
        # 1. Vérification que les données existent et ne sont pas vides
        if not self.data:
            raise ValidationError("Erreur : impossible de générer le graphique, les données sont vides.")
            
        # 2. Vérification que les noms de colonnes x et y ont bien été fournis
        if not self.x or not self.y:
            raise ValidationError("Erreur : les paramètres 'x' et 'y' sont obligatoires pour tracer un graphique.")
            
        # 3. Vérification que x et y correspondent à des clés valides dans les dictionnaires de données
        if isinstance(self.data, list) and len(self.data) > 0 and isinstance(self.data[0], dict):
            keys = self.data[0].keys()
            if self.x not in keys or self.y not in keys:
                raise ValidationError(f"Erreur de validation : la colonne '{self.x}' ou '{self.y}' est introuvable dans les données.")


# 22. BarPlotOperation (Opération concrète de diagramme en barres)
class BarPlotOperation(PlotOperation):
    """
    Opération concrète permettant de générer un diagramme en barres (bâtons) 
    à l'aide de la bibliothèque Matplotlib.
    """

    def do_run(self):
        """
        Traitement métier : crée la figure Matplotlib, extrait les données pour x et y,
        trace les barres, ajoute les labels, le titre et retourne la figure finale.
        """
        try:
            # 1. Création de la figure (la feuille) et des axes (la zone de dessin)
            fig, ax = plt.subplots()
            
            # 2. Extraction des listes de valeurs pour l'axe X et l'axe Y à partir des dictionnaires
            x_values = [item[self.x] for item in self.data]
            y_values = [item[self.y] for item in self.data]
            
            # 3. Tracé effectif du diagramme en barres
            ax.bar(x_values, y_values, label="Série de données")
            
            # 4. Ajout de la mise en forme (titre, nom des axes, légende)
            ax.set_title(self.title)
            ax.set_xlabel(self.x)
            ax.set_ylabel(self.y)
            ax.legend()
            
            # 5. On remplace self.data par la figure générée pour pouvoir l'utiliser facilement
            self.data = fig
            return fig
            
        except Exception as e:
            # Si une erreur inattendue survient pendant le dessin, on lève une PlotError personnalisée
            raise PlotError(f"Erreur lors de la création du graphique en barres : {e}")
        

# 22. LinePlotOperation (Deuxième type de graphique : diagramme en courbes)
class LinePlotOperation(PlotOperation):
    """Opération concrète pour générer un graphique en courbes (Line Plot)."""
    
    def do_run(self):
        try:
            # 1. Création de la figure et des axes
            fig, ax = plt.subplots()
            
            # 2. Extraction des valeurs x et y à partir des dictionnaires de données
            x_values = [item[self.x] for item in self.data]
            y_values = [item[self.y] for item in self.data]
            
            # 3. Tracé effectif de la courbe (avec des marqueurs pour les points)
            ax.plot(x_values, y_values, marker='o', label="Évolution")
            
            # 4. Ajout de la mise en forme demandée (titre, labels des axes, légende)
            ax.set_title(self.title)
            ax.set_xlabel(self.x)
            ax.set_ylabel(self.y)
            ax.legend()
            
            # 5. On stocke la figure finale dans self.data
            self.data = fig
            return fig
            
        except Exception as e:
            raise PlotError(f"Erreur lors de la création du graphique en courbes : {e}")
        
# 24. ScatterPlotOperation (Troisième type de graphique : nuage de points)
class ScatterPlotOperation(PlotOperation):
    """Opération concrète pour générer un nuage de points (Scatter Plot)."""
    
    def do_run(self):
        try:
            # 1. Création de la figure et des axes
            fig, ax = plt.subplots()
            
            # 2. Extraction des valeurs x et y
            x_values = [item[self.x] for item in self.data]
            y_values = [item[self.y] for item in self.data]
            
            # 3. Tracé effectif du nuage de points (scatter)
            ax.scatter(x_values, y_values, color='red', label="Observations")
            
            # 4. Ajout de la mise en forme
            ax.set_title(self.title)
            ax.set_xlabel(self.x)
            ax.set_ylabel(self.y)
            ax.legend()
            
            # 5. On stocke la figure finale
            self.data = fig
            return fig
            
        except Exception as e:
            raise PlotError(f"Erreur lors de la création du nuage de points : {e}")