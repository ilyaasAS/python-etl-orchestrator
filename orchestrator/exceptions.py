# 4. Hiérarchie des exceptions personnalisées du projet

# Classe mère générale pour toutes les erreurs spécifiques du moteur d'orchestration.
# Elle hérite de la classe native 'Exception' de Python.
# Cela permet d'attraper n'importe quelle erreur propre au moteur d'un seul coup si besoin (avec except OperationError).
class OperationError(Exception):
    """Classe de base pour toutes les erreurs du moteur d'orchestration."""
    pass
    

# Levée spécifiquement lorsque les données fournies en entrée ou la source sont incorrectes.
# Elle hérite de OperationError.
class ValidationError(OperationError):
    """Levée en cas d'erreur de validation des données."""
    pass


# Levée lorsqu'une erreur (comme un souci réseau ou une API down) est temporaire.
# Elle servira pour déclencher automatiquement les réessais (mécanisme de retry).
class TransientError(OperationError):
    """Levée en cas d'erreur temporaire."""
    pass


# Levée en cas de problème lors de la sérialisation (ex: conversion de l'objet en dictionnaire).
class SerializationError(OperationError):
    """Levée en cas de problème de sérialisation."""
    pass


# Levée spécifiquement en cas de problème lors de la génération d'un graphique (avec Matplotlib).
class PlotError(OperationError):
    """Levée en cas d'erreur liée aux graphiques."""
    pass