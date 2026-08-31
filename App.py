
from typing import Any

from fastapi import FastAPI, HTTPException
import uvicorn
import numpy as np
import pandas as pd
import pickle
import os
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse




# initialisation de l'application
app = FastAPI(
    title="Scoring Credit API",
    description="API pour predire la solvabilite d'un demandeur de credit a notre banque",
    version="1.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def accueil():
    return FileResponse("static/index.html")



# definition du chemins adaptes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# chargement du pipeline
pipeline_path = os.path.join(BASE_DIR, "models", "pipeline_complet.pkl")

try:
    with open(pipeline_path, "rb") as f:
        pipeline = pickle.load(f)

    modele = pipeline['modele']
    preprocesseur= pipeline['preprocessor']
    features_finales = pipeline['features_final']
    params_finaux = pipeline['params_finaux']
    seuil_optimal = pipeline['seuil']

    print(f"Pipeline charge")
    print(f"seuil : {seuil_optimal}")
    print(f"Nombre de features:{len(features_finales)}")

except FileNotFoundError as e:
    print(f"erreur: {e}")
    print(f"verifiez que les fichiers sont dans les dossiers")

    raise

class CreditData(BaseModel):
    genre : str
    marrie : str
    travailleur_indep: str

    revenu_demandeur : float
    revenu_codemmandeur : float
    montant_pret :float

    pers_en_charge : int
    credit_historique: str
    zone_residence: str

    duree_pret : float
    Education: str



'''
Nous allons definir notre endpoint en y incluant les règles metiers. voici l'architecture de decision:
Donnees brut ---> valeurs financiere --->Regles Metiers (capacite de remboursement) ----> Non respecté ==> Refus de credit

Regles Metiers (capacite de remboursement) ---> respecté ---> Modele ML de decider ----> probabilité_defaut --->seuil(0.64)

probabilité_defaut --->seuil(0.64) >=0.64 ==> Refus .  si probabilité_defaut --->seuil(0.64) <= 0.64 ===> Accordé

Donc les 02 conditions(Regle metier + seuil du Modele ) doivent etre satisfaite pour un accord de credit

'''
@app.post("/predict")
async def predict(data:CreditData):

    df = pd.DataFrame([data.model_dump()])
    print("colonnes recues par l'API :", df.columns.tolist())

    # CONTEXTE METIER A DEFINIR

    # 1. taux d'effort maximal : 30 % du revenu mensuel peut etre consacré au remboursement du credit
    taux_effort_max = 0.30

    montant_pret = float(df['montant_pret'].iloc[0])
    revenu_demandeur = float(df['revenu_demandeur'].iloc[0])
    revenu_codemmandeur = float(df['revenu_codemmandeur'].iloc[0])
    duree_pret = float(df['duree_pret'].iloc[0])

    # 2. validation metier
    if montant_pret < 0:
        raise HTTPException(
            status_code = 400,
            detail = "le montant du prêt ne peut pas etre negatif" )
    if revenu_demandeur < 0:
        raise HTTPException(
            status_code = 400,
            detail = "le revenu du demandeur ne peut pas etre negatif")
    if revenu_codemmandeur < 0:
        raise HTTPException(
            status_code = 400,
            detail = "le revenu du codemandeur ne peut pas etre negatif")
    if duree_pret < 0:
        raise HTTPException(
            status_code = 400,
            detail = "la durée du prêt ne peut pas etre negatif" )

    # 3. Calcul des differents indicateurs
    revenu_menage = revenu_demandeur + revenu_codemmandeur
    duree_mois = duree_pret / 30

    if revenu_menage < 0:
        raise HTTPException(
                    status_code = 400,
                    detail = " Le revenu du menage doit etre supérieur a zero"
                )
    ratio_endett = ( montant_pret / revenu_demandeur if revenu_demandeur > 0 else float("inf") )
    ratio_endett_menage = (montant_pret/revenu_menage)

    # 4. Calcul capacité de remboursement sur la duree du pret
    capacite_totale_remb = (revenu_menage * taux_effort_max) * duree_mois

    # 5. condition metier
    if (montant_pret >= capacite_totale_remb):
        decision_metier = "Refusé"
    else:
        decision_metier = "Accordé"


    print("------Politique Metier---------")
    print("ratio endettement brut:",ratio_endett)
    print("ratio endettement menage brut:", ratio_endett_menage)
    print("duree du pret en mois: ",duree_mois)
    print("montant du pret: ",montant_pret)
    print("capacité de remboursement sur la duree: ",capacite_totale_remb)
    print("Peut rembourser(True/False) ?:" ,capacite_totale_remb > montant_pret)

    # Donnees brutes a transformer dans le pipeline
    df_transforme = preprocesseur.transform(df)
    noms_colonnes = preprocesseur.get_feature_names_out()
    df_transforme = pd.DataFrame(df_transforme, columns=noms_colonnes)

    df_transforme['ratio_endettement'] = df_transforme['num__montant_pret'] / df_transforme['num__revenu_demandeur'] 
    df_transforme['ratio_endettement_menage'] = df_transforme['num__montant_pret'] / (df_transforme['num__revenu_demandeur'] + df_transforme['num__revenu_codemmandeur'])
    print("ratio d'endettement", df_transforme['ratio_endettement'] )
    print("ratio d'endettementdu menage:", df_transforme['ratio_endettement_menage'] )

    df_transforme = df_transforme[features_finales]
    proba_defaut = modele.predict_proba(df_transforme)[0][1]  #[0][1] signifie 1er client car renvoie la probabilite d'un seul client/ [1] choisit la probabilite de la 2eme classe. exp: [0.35 , 0.65] :0.35 est la 1ere classe et 0.65 est la 2eme classe
    decision_modele = "Refusé" if proba_defaut >= seuil_optimal else "Accordé"

    
    # 5. condition de decision : le montant du pret ne doit pas depasser la capacité de remboursement du menage sur toute la duree du pret
     

    if (decision_metier == "Accordé") & (decision_modele =="Accordé"):
        decision_finale ="Accordé"
        motif = ("selon le modèle : Accordé " 
                 " ET selon la politique metier")
    elif (decision_metier == "Accordé") & (decision_modele =="Refusé"):
        decision_finale = "Refusé"
        motif = (" selon le modèle : Refusé car le risque est élevé")
    elif (decision_metier == "Refusé") & (decision_modele =="Accordé"):
            decision_finale = "Refusé"
            motif = (" selon le la politique metier : Refusé ")
    else:
        decision_finale = "Refusé"
        motif = ("selon le modèle: Refusé "
                 "ET selon la politique metier : Refusé")


    return {
        "decision" : decision_finale,
        "decision_modele" : decision_modele,
        "decision_metier" : decision_metier,
        "motif" : motif,
        "probabilite" : round(proba_defaut, 4),
        "ratio_endettement" : round(ratio_endett, 4),
        "ratio_endettement_menage" : round(ratio_endett_menage, 4)
        }


if __name__ =="__main__" :
    uvicorn.run(app)