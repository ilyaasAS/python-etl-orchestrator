# Import de pytest
import pytest

# Import des classes dont on souhaite analyser l'ordre de résolution
from orchestrator.plots import BarPlotOperation
from orchestrator.operations import ComplexOperation


def test_mro_bar_plot_order():
    """Test 12 : Vérifie l'ordre relatif des classes dans le MRO de BarPlotOperation."""
    # Récupération de la liste des noms des classes dans l'ordre du MRO (C3 Linearization)
    mro_names = [cls.__name__ for cls in BarPlotOperation.mro()]
    
    # Assertions : vérifie la présence des classes fondamentales de la hiérarchie
    assert "BarPlotOperation" in mro_names
    assert "PlotOperation" in mro_names
    assert "DataOperation" in mro_names
    
    # Assertion d'ordre hiérarchique : l'enfant direct doit apparaître avant son parent dans l'indice du MRO
    assert mro_names.index("BarPlotOperation") < mro_names.index("PlotOperation")
    assert mro_names.index("PlotOperation") < mro_names.index("DataOperation")


def test_mro_complex_operation_order():
    """Test 13 : Vérifie la présence de ComplexOperation dans son propre MRO."""
    # Récupération du MRO de la classe ComplexOperation sous forme de liste de noms
    mro_names = [cls.__name__ for cls in ComplexOperation.mro()]
    
    # Assertions : vérifie que la classe composite et la classe de base de données y figurent bien
    assert "ComplexOperation" in mro_names
    assert "DataOperation" in mro_names