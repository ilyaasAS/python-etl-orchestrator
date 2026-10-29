# Import de pytest
import pytest

# Import de matplotlib et configuration obligatoire en mode 'Agg' (sans interface graphique)
import matplotlib
matplotlib.use("Agg")

# Import de l'opération graphique et de l'exception de validation
from orchestrator.plots import BarPlotOperation
from orchestrator.exceptions import ValidationError


def test_matplotlib_valid_generation():
    """Test 9 : Vérifie la création réussie d'un graphique en mode 'Agg'."""
    # Données valides comportant les clés "mois" et "ventes"
    data = [{"mois": "Jan", "ventes": 100}, {"mois": "Fev", "ventes": 200}]
    
    # Instanciation de l'opération de diagramme en barres
    op = BarPlotOperation(data=data, x="mois", y="ventes", title="Test Barres")
    
    # Exécution de la génération du graphique
    fig = op.run()
    
    # Assertion : la figure Matplotlib générée ne doit pas être nulle
    assert fig is not None


def test_matplotlib_missing_column():
    """Test 10 : Vérifie qu'une colonne 'x' ou 'y' inexistante déclenche une ValidationError."""
    data = [{"mois": "Jan", "ventes": 100}]
    
    # On fournit un nom de colonne 'x' qui n'existe pas dans le dictionnaire des données
    op = BarPlotOperation(data=data, x="colonne_fausse", y="ventes")
    
    # Assertion : la méthode validate() doit intercepter l'anomalie et lever une ValidationError
    with pytest.raises(ValidationError):
        op.run()


def test_matplotlib_empty_data():
    """Test 11 : Vérifie qu'un graphique avec des données vides lève une ValidationError."""
    # Données vides transmises à l'opération graphique
    op = BarPlotOperation(data=[], x="mois", y="ventes")
    
    # Assertion : l'absence de données provoque une ValidationError
    with pytest.raises(ValidationError):
        op.run()