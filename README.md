# credit_scoring

#  Prédiction d'octroi de crédit avec LightGBM

## Présentation

Ce projet consiste à développer un modèle de Machine Learning permettant
d'aider à la décision d'octroi de crédit.

L'objectif est de prédire si une demande de crédit doit être considérée
comme favorable ou défavorable à partir des caractéristiques du demandeur
et des caractéristiques du crédit.

Le modèle final retenu est *LightGBM*.

Le projet suit une démarche complète de Data Science allant de la préparation
des données jusqu'à l'évaluation finale du modèle sur un jeu de test
totalement indépendant.

il est testable sur ce lien : https://credit-scoring-7rro.onrender.com

----------------------------------------------------------------------------------------------

# Objectifs

Le système doit permettre de :

- analyser les caractéristiques des demandeurs de crédit ;
- prédire la classe d'une demande ;
- estimer la probabilité associée à la prédiction ;
- aider à identifier les demandes présentant un risque ;
- fournir une base de décision pour l'octroi ou le refus du crédit.

Une attention particulière est portée aux erreurs de classification pouvant
conduire à accorder un crédit à un mauvais profil.

---------------------------------------------------------------------------------------------------

# Approche Machine Learning

Le projet a suivi les principales étapes  :

1. Exploration des données
2. Nettoyage des données
3. Séparation des variables explicatives et de la cible
4. Séparation Train/Test
5. Preprocessing
6. Encodage des variables catégorielles
7. Feature Engineering
8. Benchmarking des modèles
9. Sélection du modèle
10. Validation croisée
11. Optimisation des hyperparamètres
12. Contrôle de l'overfitting
13. Entraînement du modèle final
14. Évaluation finale sur le jeu de test
15. Déploiement

-------------------------------------------------------------------------------------------

# Séparation des données

Les données ont été séparées en deux ensembles avec stratification sur la variable cible:

- *80 % : données d'entraînement*
- *20 % : données de test*

Le jeu de test a été conservé séparément pendant toute la phase de
sélection et d'optimisation du modèle.

Toutes les opérations de sélection du modèle, de validation croisée et
d'ajustement des hyperparamètres ont été réalisées uniquement à partir
des données d'entraînement.

Le jeu de test n'a été utilisé qu'à la fin pour obtenir une estimation
finale des performances du modèle.

---------------------------------------------------------------------------------------------------------------

# Le Preprocessing

Les variables catégorielles ont été encodées à l'aide d'un preprocessing pour rester a l'abri d'un data leakage

Le preprocessing a été ajusté (fit) uniquement sur les données
d'entraînement.

Les données de test ont ensuite été transformées à l'aide du même
preprocessing (transform).

--------------------------------------------------------------------------------------------------------------------

# Feature selection et Feature Engineering

Après le preprocessing, les données ont fait l'objet d'une étape de feature selection et de feature engineering.
Le jeu final utilisé pour l'entraînement du modèle comporte 11 variables explicatives.
La même transformation est appliquée aux nouvelles données lors de l'utilisation du modèle.

----------------------------------------------------------------------------------------------------------------------

# Sélection du modèle

Plusieurs modèles de classification ont été comparés dans le cadre du benchmarking.
Les principaux modèles étudiés comprennent notamment :
LightGBM
AdaBoost
Naives Bayes
CatBoost

Le choix du modèle n'a pas été effectué uniquement sur l'accuracy.
Les critères considérés comprennent notamment :
ROC-AUC / Precision / Recall / F1-score
stabilité des performances

Compte tenu du contexte de scoring crédit, une attention particulière a été portée au rappel et à la précision ainsi qu'à la capacité du modèle à distinguer les profils favorables et défavorables.
Le modèle final retenu est :
LightGBM

---------------------------------------------------------------------------------------------------------------------------------------
# Optimisation des hyperparamètres

Les hyperparamètres du modèle LightGBM ont été optimisés à partir des données d'entraînement.
La validation croisée a permis d'évaluer la stabilité du modèle sur plusieurs folds.
L'objectif était notamment de rechercher un compromis entre :
 - performance ;
 - généralisation ;
 - stabilité ;
 - limitation de l'overfitting.

----------------------------------------------------------------------------------------------------------------------------------------

# Contrôle de l'overfitting

Une comparaison entre les performances d'entraînement et celles obtenues en validation croisée a été réalisée.
La ROC-AUC a notamment été utilisée pour comparer :
   ***** Train AUC vs Cross-Validation AUC
L'objectif était de détecter un éventuel écart excessif entre la performance sur les données d'entraînement et la performance sur des données non utilisées pour l'apprentissage.
Après ajustement des paramètres de régularisation et des hyperparamètres, le modèle final a été retenu avant l'évaluation sur le jeu de test.

--------------------------------------------------------------------------------------------------------------------------------------

# Évaluation finale

Après la fin de toutes les étapes d'entraînement et d'optimisation, le modèle final a été évalué une seule fois sur le jeu de test indépendant.
Résultats obtenus : Métrique  Test
Accuracy  ROC-AUC   Precision – Accord   Recall – Accord    F1-score – Accord    Precision – Refus     Recall – Refus
0.7967    0.7511      0.84                 0.87                  0.86              0.69                  0.63

F1-score – Refus
  0.66

*******Matrice de confusion**********
                    Prédiction
                 Refus    Accord

Réel Refus         24       14
Réel Accord        11       74

Le modèle a correctement identifié :
   - 74 demandes réellement favorables ,
   - 24 demandes réellement défavorables, 
Il a également produit :
   - 14 faux positifs, 
   - 11 faux négatifs.

Le modèle présente une bonne capacité à identifier les demandes classées comme favorables.
Sur le jeu de test :
    le recall de la classe Accord est de 0.87 ;
    la precision de la classe Accord est de 0.84 ;
    le F1-score de la classe Accord est de 0.86.
La classe Refus reste plus difficile à identifier :
    recall = 0.63 ;
    precision = 0.69.
Cette différence constitue un point important dans l'interprétation métier du modèle.
Dans un contexte d'octroi de crédit, les faux positifs peuvent représenter un risque important lorsqu'un crédit est accordé à un profil qui aurait dû être refusé.

---------------------------------------------------------------------------------------------------------------------------
# Principe d'intégrité du jeu de test

Le jeu de test de 20 % a été conservé comme un jeu de données indépendant.
Il n'a pas été utilisé pour :
   - sélectionner le modèle ;
   - optimiser les hyperparamètres ;
   - ajuster le preprocessing ;
   - régler le modèle contre l'overfitting ;
   - choisir les paramètres du modèle.
L'évaluation finale sur le test constitue donc une mesure indépendante des performances du modèle final.
Aucune modification supplémentaire du modèle n'est effectuée à partir de cette évaluation finale.

----------------------------------------------------------------------------------------------------------------------------------

# Modèle sauvegardé

Le modèle final est sauvegardé afin de pouvoir être utilisé sans réentraînement.
Les composants nécessaires à la prédiction sont notamment : 
    - lightgbm_model.pkl
    - preprocessor.pkl
    - label_encoder.pkl
Le serveur charge ces objets au démarrage de l'application.
Aucun fit() n'est effectué lors d'une prédiction.
Le pipeline de prédiction utilise uniquement les transformations déjà apprises lors de l'entraînement.

# Déploiement

L'application est exposée sous forme d'API REST avec FastAPI et passera par une conteneurisation Docker et sera déployé sur heroku ou render
