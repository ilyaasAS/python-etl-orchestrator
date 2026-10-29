# Mini-projet : Moteur d'orchestration

## 0. Se positionner dans le bon emplacement

Ouvrir un terminal dans le dossier du projet (au même niveau que le fichier README.md)

## 1. Création et activation de l'environnement virtuel

> **Note (PowerShell) :** en cas de blocage d'exécution de script, lancer au préalable :  
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

### Sur Windows :
python -m venv venv
venv\Scripts\activate

### Sur macOS et Linux :
python3 -m venv venv
source venv/bin/activate

## 2. Installation des dépendances 
pip install -r requirements.txt

## 3. Lancer le projet

### Sur Windows :
python -m orchestrator.main

### Sur macOS et Linux :
python3 -m orchestrator.main

## 4. Lancer les tests unitaires

### Sur Windows :
python -m pytest -v

### Sur macOS et Linux :
python3 -m pytest -v

## 5. Quitter l'environnement
deactivate