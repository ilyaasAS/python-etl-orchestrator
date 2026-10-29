#10. On importe le module datetime pour manipuler les dates et heures actuelles.
from datetime import datetime
#13. On importe notre exception temporaire depuis le fichier des exceptions du projet
from orchestrator.exceptions import TransientError

# 8. LoggedMixin
class LoggedMixin:
    """
    Mixin permettant de suivre l'exécution d'une opération en affichant des traces (logs).
    Un mixin n'est pas fait pour être instancié seul : il vient s'ajouter (par héritage multiple) 
    à une classe d'opération pour lui rajouter un comportement spécifique.
    """
    
    # Méthode utilitaire pour afficher un message formaté
    def log(self, message):
        """Affiche un message de log formaté incluant dynamiquement le nom de la classe en cours."""
        # self.__class__.__name__ récupère automatiquement le nom de l'opération concrète (ex: CSVImportOperation)
        print(f"[LOG] {self.__class__.__name__} : {message}")

    # Surcharge du hook _before_validate défini dans BaseOperation
    def _before_validate(self):
        """Exécuté avant la validation pour tracer le début de cette étape."""
        # On affiche le log correspondant
        self.log("validation")
        # 'super()' est obligatoire ici ! Il transmet l'appel au mixin suivant ou à la classe parente dans le MRO,
        # garantissant que la chaîne d'héritage multiple n'est pas cassée.
        super()._before_validate()

    # Surcharge du hook _before_do_run défini dans BaseOperation
    def _before_do_run(self):
        """Exécuté avant le traitement métier pour tracer le début de l'exécution."""
        # On affiche le log de début
        self.log("début")
        # Transmission de l'appel dans la chaîne du MRO via super()
        super()._before_do_run()

    # Surcharge du hook _after_do_run défini dans BaseOperation
    def _after_do_run(self, result):
        """Exécuté après le traitement métier pour tracer la fin de l'opération."""
        # On affiche le log de fin
        self.log("terminé")
        # Transmission de l'appel et du résultat dans la chaîne du MRO via super()
        super()._after_do_run(result)
        
# 9. AuditedMixin
class AuditedMixin:
    """
    Mixin permettant d'enregistrer l'historique (l'ordre réel) 
    des étapes du cycle de vie d'une opération dans une liste 'audit_trail'.
    """
    
    # Constructeur coopératif du mixin
    def __init__(self, *args, **kwargs):
        """Initialise la liste d'audit vide à la création de l'objet."""
        # On crée la liste qui va stocker les noms des étapes exécutées
        self.audit_trail = []
        # On fait remonter les arguments dans la chaîne du MRO via super()
        super().__init__(*args, **kwargs)

    # Surcharge du hook _before_validate
    def _before_validate(self):
        """Ajoute l'étape de pré-validation à l'audit si elle n'y est pas déjà."""
        # On vérifie pour éviter les doublons en cas d'héritage multiple
        if "before_validate" not in self.audit_trail:
            self.audit_trail.append("before_validate")
        # On transmet l'appel au parent/mixin suivant dans le MRO
        super()._before_validate()

    # Surcharge du hook _after_validate
    def _after_validate(self):
        """Ajoute l'étape de post-validation à l'audit."""
        if "after_validate" not in self.audit_trail:
            self.audit_trail.append("after_validate")
        super()._after_validate()

    # Surcharge du hook _before_do_run
    def _before_do_run(self):
        """Ajoute l'étape d'avant-exécution métier à l'audit."""
        if "before_do_run" not in self.audit_trail:
            self.audit_trail.append("before_do_run")
        super()._before_do_run()

    # Surcharge du hook _after_do_run
    def _after_do_run(self, result):
        """Ajoute l'étape de fin d'exécution à l'audit."""
        if "after_do_run" not in self.audit_trail:
            self.audit_trail.append("after_do_run")
        super()._after_do_run(result)
        

# 10. TimestampedMixin
class TimestampedMixin:
    """
    Mixin permettant d'ajouter une date de création (created_at) 
    et une date de dernière mise à jour (updated_at) après exécution.
    """
    
    def __init__(self, *args, **kwargs):
        """Constructeur coopératif initialisant la date de création."""
        # created_at stocke l'horodatage exact de la création de l'objet
        self.created_at = datetime.now()
        # updated_at est initialisé à None au départ (pas encore exécuté)
        self.updated_at = None
        # On transmet les arguments au parent/mixin suivant dans le MRO
        super().__init__(*args, **kwargs)

    def _after_do_run(self, result):
        """Actualise la date de mise à jour après une exécution réussie."""
        # On met à jour updated_at avec l'heure actuelle
        self.updated_at = datetime.now()
        # On transmet l'appel dans la chaîne du MRO via super()
        super()._after_do_run(result)
        

# 11. ValidatedMixin
class ValidatedMixin:
    """
    Mixin permettant aux opérations de participer au mécanisme de validation.
    Il s'intègre dans la chaîne d'héritage pour s'assurer que les règles 
    de validation sont bien exécutées séquentiellement.
    """
    
    # Définition de la méthode de validation du mixin
    def validate(self):
        """
        Méthode de validation de l'opération. 
        Elle fait remonter l'appel dans la chaîne du MRO via super().
        Les opérations concrètes pourront surcharger cette méthode pour ajouter 
        leurs propres règles et lever une 'ValidationError' en cas de données incorrectes.
        """
        # 'super().validate()' permet de transmettre l'appel de validation 
        # à la classe parente ou au mixin suivant dans l'ordre du MRO, 
        # garantissant ainsi que toutes les validations de la chaîne s'exécutent.
        super().validate()
        

# 12. CachedMixin
class CachedMixin:
    """
    Mixin permettant de mémoriser (mettre en cache) le résultat d'une opération 
    pour éviter de refaire un calcul coûteux si l'opération est relancée.
    """
    
    # Dictionnaire de classe partagé pour stocker les résultats en cache 
    # (clé: clé de cache fournie par l'opération, valeur: résultat stocké)
    _cache_storage = {}

    def run(self):
        """
        Surcharge de la méthode 'run' pour intercepter l'exécution,
        vérifier si le résultat est déjà en cache, ou le stocker après calcul.
        """
        # 1. On récupère la clé de cache de l'opération (définie dans l'opération, par défaut None)
        key = self.cache_key()

        # 2. Si la clé de cache est None, cela signifie que l'opération ne doit pas être mise en cache.
        # On délague simplement l'exécution normale au parent via super().run()
        if key is None:
            return super().run()

        # 3. Si la clé est présente dans notre stockage de cache, 
        # on retourne directement le résultat enregistré sans refaire le travail !
        if key in self._cache_storage:
            print(f"[CACHE] Récupération depuis le cache pour la clé : {key}")
            return self._cache_storage[key]

        # 4. Si le cache est absent, on exécute normalement le cycle de vie complet via super().run()
        result = super().run()

        # 5. On stocke le résultat obtenu dans notre dictionnaire de cache sous la clé correspondante,
        # pour pouvoir le réutiliser lors des prochains appels.
        self._cache_storage[key] = result
        print(f"[CACHE] Mise en cache du résultat pour la clé : {key}")

        # 6. On retourne le résultat
        return result
    
# 13. RetryMixin
class RetryMixin:
    """
    Mixin permettant de réessayer automatiquement l'exécution d'une opération 
    si une erreur temporaire (TransientError) se produit.
    """
    
    # Attributs configurables pour la gestion des essais
    # max_retries : nombre maximal de nouvelles tentatives autorisées
    max_retries = 3

    def run(self):
        """
        Surcharge de la méthode 'run' pour intercepter les échecs 
        et relancer l'opération en cas d'erreur transitoire.
        """
        # Compteur pour suivre le nombre de tentatives déjà effectuées
        attempt = 0

        # Boucle infinie qui s'arrêtera soit par un succès, soit si on dépasse les limites
        while True:
            try:
                # On essaie d'exécuter l'opération normale via super().run()
                return super().run()
                
            except TransientError as e:
                # Si on attrape une erreur temporaire, on incrémente le compteur de tentatives
                attempt += 1
                
                # Si on a dépassé le nombre maximal de tentatives autorisé, on abandonne et on relève l'erreur
                if attempt > self.max_retries:
                    print(f"[RETRY] Échec définitif après {attempt} tentatives.")
                    raise e
                
                # Sinon, on affiche un message de trace et on recommence la boucle (tentative suivante)
                print(f"[RETRY] Erreur temporaire détectée ({e}). Tentative {attempt}/{self.max_retries} en cours...")
                
                

# 14. SerializableMixin
class SerializableMixin:
    """
    Mixin permettant de transformer une opération en dictionnaire (to_dict) 
    pour faciliter sa sérialisation (ex: sauvegarde au format JSON).
    """

    def to_dict(self):
        """
        Convertit l'objet et ses attributs en un dictionnaire standard.
        Il intègre le nom de la classe pour identifier l'opération lors du rechargement.
        """
        # On crée un dictionnaire de base qui contient le nom de la classe concrète
        data = {
            "__class__": self.__class__.__name__
        }
        
        # On récupère tous les attributs de l'objet grâce à '__dict__' 
        # (qui est un dictionnaire natif de Python contenant les attributs et leurs valeurs)
        if hasattr(self, "__dict__"):
            data.update(self.__dict__)
            
        return data

    @classmethod
    def from_dict(cls, data):
        """
        Méthode de classe (bonus) permettant de recréer l'objet à partir d'un dictionnaire.
        """
        # On extrait la classe et on recrée une instance en passant les autres données en arguments nommés (**data)
        # (On retire "__class__" du dictionnaire pour ne garder que les attributs utiles)
        clean_data = data.copy()
        clean_data.pop("__class__", None)
        
        # On instancie la classe avec ses attributs
        return cls(**clean_data)