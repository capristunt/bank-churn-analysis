# Cadrage business — rétention bancaire

## Décision

Déterminer quels clients contacter, avec quelle offre et quel budget, afin
d'améliorer la marge nette incrémentale sur un horizon défini.

## Données reçues

Fichier : `data/raw/Churn_Modelling.csv`.
Inspection structurelle : 10 000 lignes et 14 colonnes : `RowNumber`, `CustomerId`,
`Surname`, `CreditScore`, `Geography`, `Gender`, `Age`, `Tenure`, `Balance`,
`NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`, `Exited`.
Les trois premières colonnes servent à l'audit ou à l'identification, pas à la prédiction.

**La cible `Exited` est présente et encodée 0/1.** Confirmer sa définition métier,
la signification des classes et l'horizon ; leur présence ne fournit pas à elle seule
une chronologie permettant de les vérifier. Les contrôles de qualité et de
validation restent à réaliser avant tout résultat prédictif.

## À préciser avant l'analyse

- Source, provenance et licence des données.
- Population, éligibilité et unité d'observation.
- Définition du churn, encodage de la cible et horizon de prédiction.
- Date de décision, période observée et disponibilité des variables.
- Présence de plusieurs observations par client et choix de la séparation.
- Capacité de contact, budget, coût du contact et coût de l'offre.
- Conditions de versement de l'offre et marge nette préservée sur l'horizon retenu.
- Effet de rétention : hypothèse à faire varier, sauf données de campagne probantes.

## Livrables en quatre étapes

1. `01-data-cleaning.ipynb` : qualité et nettoyage traçable, protocole de séparation.
2. `02-data-analysis.ipynb` : exploration et diagnostic des segments, sur train pour
   les relations avec la cible ; description seule si cette cible reste absente.
3. `03-prediction.ipynb` : modèles, validation, calibration et résultats finaux figés.
4. `04-business-insights.ipynb` : synthèse décisionnelle, ciblage, simulations,
   sensibilité et recommandations. Aucun nouveau réglage sur le test.

Les quatre notebooks analytiques se trouvent dans `notebooks/`. Le notebook
`bank-churn-summary.ipynb` porte la synthèse publiée sous forme d’un seul HTML.

## Analyse business attendue

Comparer les ciblages aléatoire, métier et prédictif à budget comparable, avec
l'absence de campagne comme référence. Présenter les performances, la calibration
et les simulations économiques sans assimiler un solde à une marge ni le risque de
churn à l'effet d'une offre. Figer les règles et hypothèses de référence avant
l'évaluation test ; inclure un effet nul dans la sensibilité.

Recommander un pilote randomisé avec groupe témoin et indicateur économique
préspécifié. Au moment du cadrage initial, aucun résultat analytique n'était disponible.
