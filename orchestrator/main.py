# Importation de toutes nos opérations concrètes depuis le module operations
from orchestrator.mixins import CachedMixin, RetryMixin
from orchestrator.base import DataOperation
from orchestrator.operations import ComplexOperation
from orchestrator.plots import BarPlotOperation
from orchestrator.operations import (
    CSVImportOperation,
    APIFetchOperation,
    StatisticsOperation,
    ReportOperation
)

#26. Pipeline complet
from orchestrator.operations import (
    CSVImportOperation,
    APIFetchOperation,
    StatisticsOperation,
    ReportOperation,
    ComplexOperation
)
from orchestrator.plots import BarPlotOperation

# 20. Démonstration du Polymorphisme

# On crée une liste contenant des instances de différentes opérations
operations = [
    CSVImportOperation(source="nom,age\nAlice,25\nBob,31"),
    APIFetchOperation(endpoint="/users", params={"active": True}),
    StatisticsOperation(data=[120, 170, 150, 210]),
    ReportOperation(data=[{"nom": "Alice"}, {"nom": "Bob"}])
]

# Grâce au polymorphisme, une simple boucle suffit. 
# On appelle .run() sur chaque objet sans se soucier de sa classe exacte.
for operation in operations:
    resultat = operation.run()
    print(f"Type : {type(operation).__name__} | Résultat : {resultat}")

# RÉPONSES AUX QUESTIONS SUR LE POLYMORPHISME

# 1. Où se trouve le polymorphisme ?
# - Il se trouve dans la capacité à appeler la méthode .run() sur n'importe quel objet 
#   de la liste sans se préoccuper de sa classe d'origine. Chaque objet exécute sa propre 
#   logique interne (via do_run()) tout en répondant au même contrat externe.

# 2. Pourquoi la boucle ne connaît-elle pas la classe exacte ?
# - Parce qu'elle manipule les objets à travers leur type abstrait commun (BaseOperation). 
#   Python utilise le typage dynamique : il vérifie juste que l'objet possède la méthode run().

# 3. Quelle différence existe-t-il entre héritage et polymorphisme ?
# - L'héritage permet de transmettre et partager du code/des attributs entre une classe mère et une classe fille.
# - Le polymorphisme permet d'utiliser de manière unifiée des objets de classes différentes partageant un même contrat.

# 4. Quel est l'intérêt d'une classe abstraite dans cette architecture ?
# - Elle sert de contrat in-négociable : elle empêche l'instanciation de la classe de base 
#   et force toutes les classes filles à réécrire leur propre méthode do_run(), garantissant 
#   que le polymorphisme fonctionnera toujours.



#26. Pipeline complet
# PIPELINE 1 : CSV -> Stats -> (Rapport & Graphique)
print("--- Exécution du Pipeline 1 (CSV) ---")

csv_data = """mois,ventes
Janvier,120
Février,170
Mars,150
Avril,210"""

# 1. Importation du CSV
csv_op = CSVImportOperation(source=csv_data)
csv_op.run()

# 2. Calcul des statistiques sur les ventes
# On extrait les valeurs numériques de la colonne "ventes"
ventes_values = [int(row["ventes"]) for row in csv_op.data]
stats_op = StatisticsOperation(data=ventes_values)
stats_op.run()

# 3. Branchement : Génération du rapport textuel ET du graphique en barres
report_op = ReportOperation(data=csv_op.data)
report_op.run()

bar_plot = BarPlotOperation(
    data=csv_op.data,
    x="mois",
    y="ventes",
    title="Évolution des ventes"
)
bar_plot.run()

print("Pipeline 1 exécuté avec succès !")


# PIPELINE 2 : API -> Traitement -> (Rapport & Graphique)
print("\n--- Exécution du Pipeline 2 (API) ---")

# 1. Appel API
api_op = APIFetchOperation(
    endpoint="/api/v1/metrics",
    params={"region": "FR"}
)
api_op.run()

# Simulation de données reçues de l'API prêtes à être traitées
api_results = [
    {"trimestre": "Q1", "performance": 300},
    {"trimestre": "Q2", "performance": 450},
    {"trimestre": "Q3", "performance": 400},
    {"trimestre": "Q4", "performance": 600}
]

# 2. Branchement : Rapport ET Graphique basés sur les données API
api_report = ReportOperation(data=api_results)
api_report.run()

api_plot = BarPlotOperation(
    data=api_results,
    x="trimestre",
    y="performance",
    title="Performance Trimestrielle (API)"
)
api_plot.run()

print("Pipeline 2 exécuté avec succès !")



# 28 : Étude du MRO (Method Resolution Order)
print("=== MRO de ComplexOperation ===")
# La méthode .mro() renvoie la liste ordonnée des classes et mixins 
# que Python va parcourir pour résoudre les méthodes et les appels super().
print(ComplexOperation.mro())

# Affichage propre, classe par classe, dans l'ordre de résolution linéaire (C3 Linearization)
for classe in ComplexOperation.mro():
    print(classe.__name__)

print("\n=== MRO d'une opération graphique (BarPlotOperation) ===")
print(BarPlotOperation.mro())

for classe in BarPlotOperation.mro():
    print(classe.__name__)


# 29 : Expérience sur l'ordre des mixins et analyse du MRO

# Définition de OperationA (CachedMixin en premier)
class OperationA(CachedMixin, RetryMixin, DataOperation):
    pass

# Définition de OperationB (RetryMixin en premier)
class OperationB(RetryMixin, CachedMixin, DataOperation):
    pass

print("=== MRO de OperationA (CachedMixin avant RetryMixin) ===")
# Affiche l'ordre de résolution : CachedMixin s'exécute en premier, puis RetryMixin
for cls in OperationA.mro():
    print(cls.__name__)

print("\n=== MRO de OperationB (RetryMixin avant CachedMixin) ===")
# Affiche l'ordre de résolution inversé : RetryMixin s'exécute en premier, puis CachedMixin
for cls in OperationB.mro():
    print(cls.__name__)
    

from orchestrator.operations import CSVImportOperation
from orchestrator.exceptions import (
    ValidationError,
    PlotError,
    TransientError,
    OperationError
)

# 30 : Gestion structurée des exceptions
print("=== Test de gestion des exceptions ===")

try:
    # On simule une erreur de validation (source vide)
    bad_op = CSVImportOperation(source="")
    bad_op.run()

except ValidationError as e:
    print("Validation :", e)

except PlotError as e:
    print("Graphique :", e)

except TransientError as e:
    print("Erreur temporaire :", e)

except OperationError as e:
    print("Erreur opération :", e)

except Exception as e:
    print("Erreur inattendue :", e)
    
    
# 32 : Fonction générique d'orchestration

def executer_operations(liste_operations):
    """
    Fonction générique d'orchestration.
    Elle prend une collection (liste) d'opérations et exécute leur méthode .run() 
    de manière totalement polymorphe, sans tester leur type concret (sans isinstance).
    """
    # Initialise une liste vide pour stocker les résultats
    resultats = []
    
    # Parcourt chaque opération dans la liste fournie
    for operation in liste_operations:
        # Appel polymorphe : chaque objet exécute sa propre méthode run()
        res = operation.run()
        # Ajoute le résultat à la liste
        resultats.append(res)
        
    # Retourne la liste complète des résultats
    return resultats


# Petit test pour vérifier que la fonction marche (optionnel)
print("\n=== Test de la fonction générique d'orchestration (Etape 32) ===")
mes_ops = [
    CSVImportOperation(source="nom,age\nMarc,40"),
    StatisticsOperation(data=[10, 20, 30])
]
res_finaux = executer_operations(mes_ops)
print("Résultats :", res_finaux)