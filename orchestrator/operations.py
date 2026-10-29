# Import des modules Python natifs pour parser le CSV et manipuler du texte en mémoire
import csv
import io

# Import de notre classe intermédiaire et des exceptions
from orchestrator.base import DataOperation, IOOperation
from orchestrator.exceptions import ValidationError

# Import de tous nos mixins
from orchestrator.mixins import (
    SerializableMixin,
    ValidatedMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    CachedMixin,
    RetryMixin
)

# 16. CSVImportOperation
class CSVImportOperation(
    ValidatedMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    DataOperation
):
    """
    Opération concrète permettant d'importer et de parser un contenu CSV 
    présent dans la source, tout en combinant validation, audit, logs et horodatage.
    """

    def validate(self):
        """
        Règle de validation propre à l'import CSV : 
        On vérifie que la source est bien renseignée et qu'elle n'est pas vide.
        """
        # Appel du validate() des mixins/parents dans la chaîne du MRO via super()
        super().validate()
        
        # Si la source est vide ou absente, on lève une erreur de validation
        if not self.source or not self.source.strip():
            raise ValidationError("La source CSV est vide ou invalide.")

    def do_run(self):
        """
        Traitement métier : lit la chaîne de caractères de la source au format CSV 
        et la convertit en une liste de dictionnaires.
        """
        # Utilisation de io.StringIO pour transformer le texte brut de la source 
        # en un flux lisible par le module 'csv' standard de Python
        f = io.StringIO(self.source.strip())
        
        # csv.DictReader lit le CSV en prenant la première ligne comme clés (en-têtes) 
        # et crée un dictionnaire pour chaque ligne suivante.
        reader = csv.DictReader(f)
        
        # On convertit le lecteur en une liste classique de dictionnaires
        parsed_data = list(reader)
        
        # On stocke le résultat dans l'attribut 'data' hérité de DataOperation
        self.data = parsed_data
        
        return parsed_data
    

# 17. APIFetchOperation
class APIFetchOperation(
    CachedMixin,
    RetryMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    IOOperation
):
    """
    Opération concrète simulant un appel API avec gestion du cache, 
    des réessais automatiques en cas d'erreur temporaire, des logs, de l'audit et de l'horodatage.
    """

    def __init__(self, endpoint=None, params=None, *args, **kwargs):
        """Constructeur coopératif initialisant l'endpoint et les paramètres de l'API."""
        self.endpoint = endpoint
        self.params = params or {}  # Dictionnaire vide par défaut si params est None
        # Appel du constructeur coopératif des parents/mixins via super()
        super().__init__(*args, **kwargs)

    def cache_key(self):
        """
        Définit la clé unique de cache basée sur l'endpoint et les paramètres.
        Transforme les paramètres en tuple trié pour qu'ils soient immuables (hashable).
        """
        if not self.endpoint:
            return None
        # On convertit le dictionnaire de params en une représentation immuable (tuple de paires triées)
        params_tuple = tuple(sorted(self.params.items())) if self.params else ()
        return (self.endpoint, params_tuple)

    def do_run(self):
        """
        Traitement métier : simule l'appel à une API distante.
        Pour l'exercice, on peut simuler un comportement ou retourner un dictionnaire standard.
        """
        # Résultat simulé de l'appel API réussi
        result = {
            "endpoint": self.endpoint,
            "params": self.params,
            "status": 200
        }
        
        return result
    
# 18. StatisticsOperation
class StatisticsOperation(
    ValidatedMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    DataOperation
):
    """
    Opération concrète permettant de calculer des statistiques de base 
    (count, min, max, mean) sur une série de valeurs numériques.
    """

    def validate(self):
        """
        Règle de validation : Vérifie que les données sont présentes, 
        qu'elles forment une liste valide, et qu'elles contiennent uniquement des nombres.
        Lève une ValidationError si les données ne sont pas exploitables.
        """
        # Appel de la chaîne de validation via super()
        super().validate()
        
        # 1. Vérification que les données existent
        if self.data is None:
            raise ValidationError("Aucune donnée fournie pour le calcul statistique.")
        
        # 2. Vérification que les données sont itérables (ex: liste, tuple)
        try:
            values = list(self.data)
        except (TypeError, ValueError):
            raise ValidationError("Les données fournies ne peuvent pas être converties en liste.")
        
        # 3. Vérification que la liste n'est pas vide
        if not values:
            raise ValidationError("La liste de données est vide.")
            
        # 4. Vérification que chaque élément de la liste est bien un nombre (int ou float)
        for item in values:
            if not isinstance(item, (int, float)):
                raise ValidationError(f"Valeur non numérique non exploitable détectée : {item}")

    def do_run(self):
        """
        Traitement métier : calcule le count, le min, le max et la moyenne de la série.
        """
        values = list(self.data)
        
        count = len(values)
        minimum = min(values)
        maximum = max(values)
        mean = sum(values) / count  # Calcul de la moyenne arithmétique
        
        # Constitution du dictionnaire de résultats
        result = {
            "count": count,
            "min": minimum,
            "max": maximum,
            "mean": mean
        }
        
        # On met à jour self.data avec le résultat final
        self.data = result
        
        return result
    

# 19. ReportOperation
class ReportOperation(
    ValidatedMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    DataOperation
):
    """
    Opération concrète permettant de générer un résumé textuel (rapport) 
    à partir des données fournies en entrée.
    """

    def validate(self):
        """
        Règle de validation : Vérifie que les données sont bien présentes 
        et qu'elles ne sont pas vides. Lève une ValidationError sinon.
        """
        # Appel de la chaîne de validation via super()
        super().validate()
        
        # Si les données sont absentes ou vides, on lève une erreur
        if not self.data:
            raise ValidationError("Impossible de générer un rapport : les données sont vides ou absentes.")

    def do_run(self):
        """
        Traitement métier : analyse la structure des données et génère un résumé textuel.
        """
        # On convertit les données en liste pour analyser leur taille
        records = list(self.data)
        lignes = len(records)
        
        # Détermination du nombre de colonnes (si chaque ligne est un dictionnaire)
        colonnes = 0
        if lignes > 0 and isinstance(records[0], dict):
            colonnes = len(records[0].keys())

        # Génération du texte du rapport demandé
        rapport_texte = f"Rapport : Lignes={lignes}, Colonnes={colonnes}"
        
        # On met à jour l'attribut data avec le rapport textuel final
        self.data = rapport_texte
        
        return rapport_texte
    
# 25. ComplexOperation (Opération Composite)
class ComplexOperation(
    SerializableMixin,
    CachedMixin,
    RetryMixin,
    AuditedMixin,
    LoggedMixin,
    TimestampedMixin,
    DataOperation
):
    """
    Classe représentant une opération composée de plusieurs sous-opérations.
    Elle permet de lancer une séquence d'opérations de manière polymorphe.
    """

    def __init__(self, steps=None, *args, **kwargs):
        """
        Constructeur coopératif.
        Initialise la liste des étapes (steps) et transmet le reste via super().
        """
        self.steps = steps if steps is not None else []
        super().__init__(*args, **kwargs)

    def do_run(self):
        """
        Traitement métier : parcourt la liste des étapes et exécute 
        la méthode .run() de chaque sous-opération de façon polymorphe.
        """
        results = []
        for operation in self.steps:
            # Exécution de chaque opération sans connaître son type exact
            result = operation.run()
            results.append(result)
        
        # On met à jour self.data avec les résultats de la chaîne
        self.data = results
        return results