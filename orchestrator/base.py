# On importe 'ABC' (Abstract Base Class) pour permettre à notre classe de devenir une classe abstraite,
# et '@abstractmethod' pour marquer des méthodes que les classes filles seront obligées de coder.
from abc import ABC, abstractmethod

# On importe l'exception personnalisée 'ValidationError' depuis notre module d'exceptions 
# pour pouvoir gérer proprement les erreurs de validation des données.
from orchestrator.exceptions import ValidationError



# 5. CooperativeBase
class CooperativeBase:
    """
    Classe de base coopérative. 
    Son rôle est de servir de point d'ancrage commun dans l'héritage multiple 
    pour garantir que l'appel à super() fonctionne proprement dans tout le MRO.
    """
    
    # Définition du constructeur de la classe
    def __init__(self, *args, **kwargs):
        # Transmet dynamiquement tous les arguments reçus (*args et **kwargs) 
        # au parent suivant ou au mixin suivant dans l'ordre du MRO (Method Resolution Order).
        super().__init__(*args, **kwargs)



# 6. BaseOperation
# La classe hérite à la fois de 'CooperativeBase' (pour l'héritage coopératif) 
# et de 'ABC' (pour empêcher son instanciation directe et en faire un modèle abstrait).
class BaseOperation(CooperativeBase, ABC):
    """Classe abstraite représentant le contrat commun de toutes les opérations du moteur."""
    
    # Constructeur de l'opération de base
    def __init__(self, *args, **kwargs):
        """
        Constructeur coopératif. Il récupère des arguments universels (*args, **kwargs) 
        et les transmet aux autres classes parentes ou mixins via super().
        """
        # Appel du constructeur de la classe parente (CooperativeBase) dans la chaîne du MRO
        super().__init__(*args, **kwargs)
    
    # Décorateur indiquant que cette méthode est une obligation contractuelle
    @abstractmethod
    def do_run(self):
        """
        Méthode abstraite. C'est un 'contrat obligatoire' : 
        Python interdit d'instancier une classe si elle ne réécrit pas sa propre version de do_run().
        """
        # 'pass' indique que la méthode n'a pas de corps ici, puisqu'elle sera redéfinie par les enfants.
        pass
    
    # Méthode de validation standard
    def validate(self):
        """Règle de validation par défaut (vide ici, mais surchargeable par les classes filles)."""
        # Ne fait rien par défaut, les classes filles ou mixins l'enrichiront si besoin.
        pass
    
    # Méthode pour obtenir la clé de cache
    def cache_key(self):
        """Retourne la clé de cache (None par défaut, donc pas de cache si non surchargé)."""
        # Par défaut, retourne None ce qui signifie que l'opération n'est pas mise en cache.
        return None
    
    
    
    # 7. Cycle de vie d'une opération (Hooks & Template Method)
    
    # Hook d'avant-validation
    def _before_validate(self):
        """Hook (point de branchement) exécuté juste avant la validation."""
        # Point de contact vide pour les mixins (comme les logs ou les audits).
        pass
    
    # Hook d'après-validation
    def _after_validate(self):
        """Hook exécuté juste après que la validation ait réussi."""
        # Point de contact vide pour les mixins.
        pass

    # Hook d'avant-exécution métier
    def _before_do_run(self):
        """Hook exécuté juste avant de lancer le travail métier principal."""
        # Point de contact vide pour les mixins.
        pass

    # Hook d'après-exécution métier
    def _after_do_run(self, result):
        """Hook exécuté juste après le travail, en récupérant le résultat en paramètre."""
        # Point de contact vide pour les mixins, recevant le résultat de l'opération.
        pass

    # Méthode orchestratrice principale (Template Method)
    def run(self):
        """
        Patron de conception 'Template Method' : 
        Il fixe le squelette immuable et séquentiel de l'exécution de l'opération.
        Les classes filles n'ont pas à le modifier ; elles se contentent de coder do_run().
        """
        
        # --- Étape 1 : Phase de validation ---
        
        # 1. Appel du hook pour signaler qu'on va valider (intercepté par les mixins de logs/audits)
        self._before_validate()
        
        # 2. Exécution de la validation propre (lève une ValidationError si les données sont incorrectes)
        self.validate()
        
        # 3. Appel du hook pour signaler que la validation vient de réussir
        self._after_validate()
        
        
        # --- Étape 2 : Phase d'exécution métier ---
        
        # 4. Appel du hook pour signaler que le traitement métier va débuter
        self._before_do_run()
        
        # 5. Exécution du vrai code métier propre à l'opération et stockage du résultat dans 'result'
        result = self.do_run()
        
        # 6. Appel du hook pour signaler la fin du traitement, en passant le résultat en paramètre
        self._after_do_run(result)

        # 7. Retour du résultat final de l'opération vers l'appelant ou le moteur d'orchestration
        return result
    

# 15. IOOperation 
class IOOperation(BaseOperation):
    """
    Classe intermédiaire pour les opérations effectuant des E/S (Input/Output).
    Elle gère une source et une destination (sink).
    """
    
    def __init__(self, source=None, sink=None, *args, **kwargs):
        """
        Constructeur coopératif. 
        Il initialise la source et le sink, puis transmet le reste des arguments 
        aux classes parentes ou mixins via super() dans la chaîne du MRO.
        """
        self.source = source
        self.sink = sink
        # Transmission des arguments restants (*args, **kwargs) pour l'héritage multiple
        super().__init__(*args, **kwargs)

#15. DataOperation
class DataOperation(IOOperation):
    """
    Classe intermédiaire pour les opérations manipulant directement des données en mémoire.
    Elle hérite de IOOperation.
    """
    
    def __init__(self, data=None, *args, **kwargs):
        """
        Constructeur coopératif.
        Il initialise les données (data), puis transmet l'appel au parent (IOOperation).
        """
        self.data = data
        # Appel du constructeur de la classe parente (IOOperation) avec *args et **kwargs
        super().__init__(*args, **kwargs)
        
# 27. Héritage en losange et constructeur coopératif

class CooperativeBase:
    """
    Ancêtre commun à toutes les opérations et mixins.
    Il garantit que la chaîne des constructeurs coopératifs se termine proprement.
    """
    def __init__(self, *args, **kwargs):
        # Utilisation de super() pour remonter la chaîne s'il y a d'autres parents
        super().__init__(*args, **kwargs)


class AuditedMixin(CooperativeBase):
    """Mixin d'audit qui hérite de CooperativeBase."""
    def __init__(self, *args, **kwargs):
        # Logique d'audit...
        super().__init__(*args, **kwargs)


class TimestampedMixin(CooperativeBase):
    """Mixin d'horodatage qui hérite aussi de CooperativeBase."""
    def __init__(self, *args, **kwargs):
        # Logique d'horodatage...
        super().__init__(*args, **kwargs)


# Le losange est fermé ici : Opération hérite des deux mixins, 
# qui remontent tous les deux vers CooperativeBase.
class Operation(AuditedMixin, TimestampedMixin, CooperativeBase):
    """
    Classe de base d'une opération combinant les comportements en losange.
    Python utilise l'algorithme C3 Linearization pour ordonner l'appel des __init__.
    """
    def __init__(self, data=None, *args, **kwargs):
        self.data = data
        super().__init__(*args, **kwargs)