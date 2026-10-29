# Import de pytest
import pytest

# Import de l'opération API qui utilise le CachedMixin
from orchestrator.operations import APIFetchOperation


def test_cache_behavior():
    """Test 6 : Vérifie que le premier appel exécute le traitement et que le second récupère le résultat du cache."""
    # Nettoyage préalable du dictionnaire de cache de classe pour repartir d'un état vierge
    APIFetchOperation._cache_storage.clear()
    
    # Instanciation d'une opération API avec des paramètres spécifiques
    op = APIFetchOperation(endpoint="/users", params={"id": 1})
    
    # PREMIER APPEL : Le cache est vide, l'opération s'exécute réellement (calcul réel)
    res1 = op.run()
    
    # Vérification que la clé de cache générée est bien présente dans le stockage partagé
    key = op.cache_key()
    assert key in APIFetchOperation._cache_storage
    
    # DEUXIÈME APPEL : Le cache est présent, le résultat est récupéré instantanément sans recalculer
    res2 = op.run()
    
    # Assertion : le résultat du deuxième appel doit être strictement identique au premier
    assert res1 == res2