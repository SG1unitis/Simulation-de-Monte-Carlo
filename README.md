# Simulateur de Risques Cyber — Méthode FAIR

Ce projet est une application web interactive développée avec Streamlit. Elle permet d'évaluer financièrement le risque cyber d'une organisation en utilisant la méthodologie FAIR (Factor Analysis of Information Risk) couplée à des simulations de Monte-Carlo.

## Architecture du Projet
Le code a été modularisé pour séparer la logique mathématique, l'interface utilisateur et la génération de graphiques :

- app.py : le point d'entrée de l'application. Gère la barre latérale, les paramètres d'entrée et le déclenchement de la simulation.
- fair_core.py : le moteur mathématique (Lois de Poisson, PERT, Log-normale) et analyse de sensibilité (Corrélation de Spearman).
- charts.py : fonctions de visualisation utilisant Plotly (Distributions, Courbe d'Exceedance, Graphiques ROI).
- excel_export.py : génération du rapport complet au format Excel.
- views: dossier contenant les vues de chaque onglet pour alléger le fichier principal :
  - tab_results.py : affichage des graphiques principaux et du tableau de fréquences.
  - tab_sensitivity.py : affichage de l'analyse de l'impact des paramètres.
  - tab_methodo.py : explications pédagogiques sur le modèle.
  - tab_roi.py : mini-simulateur pour comparer l'ALE avant/après l'application d'un contrôle de sécurité.
- tests : dossier contenant le fichier de test.
  - test_simulator.py : s'assure que le calcul des fonctions mathématiques est correct et cohérent.

## Installation & Exécution
1. Assurez-vous d'avoir Python installé (version de Python utilisée : 3.14.3, version minimale **3.11**)
2. Créez un environemment virtuel en fonction de votre OS  
3. Installez les dépendances requises ``pip install -r requirements.txt``
4. Lancez l'application : ``python -m streamlit run app.py`` (soyez dans le même dossier que app.py)
L'application mettra une dizaine de secondes à se lancer sur le port 8501.

## Tests Unitaires

Le projet inclut une suite de tests pour valider la précision des différentes fonctions mathématiques.

### Prérequis

Assurez-vous d'avoir installé `pytest`. S'il n'est pas dans votre `requirements.txt`, installez-le manuellement :
```bash
pip install pytest
```
Exécution des tests
Pour lancer l'ensemble des tests du projet, placez-vous à la racine du dossier et exécutez :

```bash
pytest
```

## Librairies utilisées
- streamlit 1.55.0 : cette librairie permet de créer l'interface web interactive (boutons, sliders, onlets) directement en Python, sans avoir besoin d'écrire du HTML/CSS/JavaScript.
- numpy 2.4.3 : librairie utilisée dans `fair_core.py` pour générer et manipuler des vecteurs de 100 000 valeurs. Il sert aussi à calculer instantanément les centiles (VaR 80%, 90%, 99%).
- scipy(scipy.stats) 1.17.1 : fournit les modèles statistiques utilisés pour la méthode FAIR (distribution log-normale pour les pertes, loi de Poisson pour la fréquence des incidents).
- pandas 2.3.3 : utilisé pour structurer les données sous forme de tableaux. Il facilite le tri des données pour l'analyse de sensibilité (corrélation de Spearman) et l'affichage des tableaux de fréquences dans l'interface.
- plotly 6.6.0 : librairie de graphiques interactifs (utilisée dans `charts.py`). plotly permet à l'utilisateur de passer sa souris sur les courbes de distribution ou d'exceedance pour lire les valeurs exactes.
- openpyxl 3.1.5 : moteur utilisé en arrière-plan par pandas pour générer, formater et exporter les résultats de la simulation dans un fichier Excel téléchargeable par l'utilisateur.
- pytest 9.0.2 : utilisé pour exécuter le script `test_simulator.py` afin de valider mathématiquement les résultats du moteur FAIR avant toute mise en production.
