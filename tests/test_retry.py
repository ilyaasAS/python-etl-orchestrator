# Import de pytest
import pytest

# Import des classes de base et de l'exception transitoire
from orchestrator.base import BaseOperation
from orchestrator.mixins import RetryMixin
from orchestrator.exceptions import TransientError


# Définition d'une classe de test héritant de RetryMixin et de la classe de base Operation
class FailingOperation(RetryMixin, BaseOperation):
    def __init__(self, fail_count=2, *args, **kwargs):
        # Nombre de fois que l'opération doit échouer avant de réussir
        self.fail_count = fail_count
        # Compteur du nombre de tentatives effectuées
        self.attempts = 0
        super().__init__(*args, **kwargs)

    def do_run(self):
        """Méthode métier simulant des échecs temporaires répétés."""
        self.attempts += 1
        # Si le nombre de tentatives est inférieur ou égal au seuil d'échec, on lève une TransientError
        if self.attempts <= self.fail_count:
            raise TransientError("Erreur temporaire simulée")
        # Sinon, l'opération réussit et retourne une chaîne
        return "Succès final"


def test_retry_triggers_new_attempt():
    """Test 7 : Vérifie qu'une TransientError provoque une nouvelle tentative et finit par réussir."""
    # On configure l'opération pour qu'elle échoue 2 fois avant de réussir à la 3ème tentative
    op = FailingOperation(fail_count=2)
    
    # Exécution de l'opération (le RetryMixin doit intercepter les erreurs et relancer automatiquement)
    result = op.run()
    
    # Assertions : le résultat final est un succès et le nombre total de tentatives est de 3
    assert result == "Succès final"
    assert op.attempts == 3


def test_retry_max_attempts_respected():
    """Test 8 : Vérifie que si le nombre d'échecs dépasse max_retries, l'erreur finale est bien levée."""
    # On demande 5 échecs, alors que la limite maximale de réessais (max_retries) sera fixée à 2
    op = FailingOperation(fail_count=5)
    op.max_retries = 2
    
    # Assertion : l'épuisement des tentatives doit propager l'exception TransientError vers l'extérieur
    with pytest.raises(TransientError):
        op.run()