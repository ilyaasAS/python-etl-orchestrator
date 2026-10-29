# Importation de la bibliothèque pytest pour écrire et exécuter les tests unitaires
import pytest
from orchestrator.operations import CSVImportOperation


# Import des classes d'opérations concrètes à tester
from orchestrator.operations import (
    CSVImportOperation,
    StatisticsOperation,
    ReportOperation
)

# Import des opérations graphiques et des exceptions personnalisées nécessaires
from orchestrator.plots import BarPlotOperation, LinePlotOperation
from orchestrator.exceptions import ValidationError


def test_csv_valid():
    """Test 1 : Vérifie qu'un contenu CSV valide est correctement parsé en liste de dictionnaires."""
    # Définition d'une chaîne de caractères représentant un faux fichier CSV valide
    csv_content = "nom,age\nAlice,30\nBob,25"
    
    # Instanciation de l'opération d'import CSV avec cette source
    op = CSVImportOperation(source=csv_content)
    
    # Exécution de l'opération
    result = op.run()
    
    # Assertion : vérifie que le résultat contient bien 2 lignes et que la première correspond à "Alice"
    assert len(result) == 2
    assert result[0]["nom"] == "Alice"


def test_csv_invalid():
    """Test 2 : Vérifie qu'une source CSV vide lève bien une ValidationError."""
    # Instanciation avec une source vide
    op = CSVImportOperation(source="")
    
    # Assertion : vérifie que l'appel de run() lève obligatoirement une exception de type ValidationError
    with pytest.raises(ValidationError):
        op.run()


def test_statistics_invalid():
    """Test 3 : Vérifie que des données non numériques transmises aux statistiques lèvent une ValidationError."""
    # Instanciation de l'opération de stats avec des lettres au lieu de nombres
    op = StatisticsOperation(data=["abc", "def"])
    
    # Assertion : la validation doit rejeter les données non numériques et lever une ValidationError
    with pytest.raises(ValidationError):
        op.run()


def test_report_empty():
    """Test 4 : Vérifie qu'un rapport généré sur des données vides déclenche une ValidationError."""
    # Instanciation d'un rapport avec une liste vide
    op = ReportOperation(data=[])
    
    # Assertion : un rapport vide est invalide et doit lever une ValidationError
    with pytest.raises(ValidationError):
        op.run()


def test_polymorphism_operations():
    """Test 5 : Vérifie que plusieurs opérations hétérogènes peuvent être exécutées par une même fonction générique."""
    # Données communes de test pour les graphiques
    data = [{"x": 1, "y": 2}, {"x": 2, "y": 4}]
    
    # Liste contenant deux types d'opérations graphiques différentes (barres et courbes)
    ops = [
        BarPlotOperation(data=data, x="x", y="y", title="Barres"),
        LinePlotOperation(data=data, x="x", y="y", title="Courbe")
    ]
    
    # Fonction d'orchestration générique et polymorphe (appelle .run() sans connaître le type exact)
    def execute_all(operations):
        return [op.run() for op in operations]

    # Exécution de la fonction générique
    res = execute_all(ops)
    
    # Assertion : les deux opérations ont bien retourné un résultat
    assert len(res) == 2
    

def test_audit_trail_order():
    """Vérifie l'ordre exact des événements d'audit enregistrés par l'AuditedMixin."""
    # Instanciation d'une opération combinant AuditedMixin
    op = CSVImportOperation(source="nom,age\nAlice,30")
    
    # Exécution de l'opération
    op.run()
    
    # Séquence exacte exigée par le sujet
    expected_trail = [
        "before_validate",
        "after_validate",
        "before_do_run",
        "after_do_run"
    ]
    
    # Assertion : vérifie que l'attribut audit_trail contient exactement la bonne séquence dans le bon ordre
    assert op.audit_trail == expected_trail