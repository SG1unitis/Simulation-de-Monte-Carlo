# fair_core.py
import numpy as np #Moteur des calculs vectoriel pour les 100 000 simulations
import pandas as pd #Structuration des résultats pour calculer les corrélations
from scipy import stats #Outils des distributions statistiques (loi de Poisson, log-normale, etc.)
from distributions import pert_sample, lognormal_from_ci 

NB_SIMULATION: int = 100_000
PLAFOND_VAL_MAX:int = 5_000_000

def run_fair_engine(params, n=NB_SIMULATION, seed=42): #Exécution de la simulation
    if seed is not None:
        np.random.seed(seed)
        
    #Tirage des paramètres TEF et Vuln selon 3 paramètres : low, mode, high
    tef = pert_sample(params['tef_low'], params['tef_mode'], params['tef_high'], n=n)
    vuln = pert_sample(params['vuln_low'], params['vuln_mode'], params['vuln_high'], n=n)
    
    #Calcul du nombre d'incidents (loi de Poisson) : TEF x Vulnérabilités
    lef = np.random.poisson(tef * vuln)
    
    #Calcul des pertes (Magnitude/LM) selon les mêmes modalités que TEF et Vulnérabilités
    total_incidents = int(lef.sum())
    lm_pool = lognormal_from_ci(params['lm_median'], params['lm_ef'], n=max(total_incidents, 1))
    
    annual_loss = np.zeros(n)
    idx = 0
    for i in range(n):
        if lef[i] > 0:
            annual_loss[i] = np.sum(lm_pool[idx : idx + lef[i]])
            idx += lef[i]
            
    #Plafonnement (modulable, selon décision) : la valeur ne pourra jamais dépasser 5 millions d'euros
    annual_loss = np.clip(annual_loss, a_min=0, a_max=PLAFOND_VAL_MAX)
    
    #Échantillon pour la sensibilité
    lm_repr = np.zeros(n)
    mask = lef > 0
    lm_repr[mask] = annual_loss[mask] / lef[mask]

    return {"annual_loss": annual_loss, "lef": lef, "tef": tef, "vuln": vuln, "lm": lm_repr}

def calculate_sensitivity(sim_data):    #Calcule l'importance de chaque paramètre selon Spearman : lequel d'entre eux agit le plus sur la réduction du risque ?
    r = sim_data["annual_loss"]
    mask = r > 0
    if not np.any(mask):
        return pd.DataFrame([{"Paramètre": "N/A", "Importance (%)": 0.0}])
        
    rows = []
    for name, arr in [
        ("TEF — Fréquence", sim_data["tef"][mask]),
        ("Vulnérabilité", sim_data["vuln"][mask]),
        ("LM — Magnitude", sim_data["lm"][mask]),
    ]:
        corr, _ = stats.spearmanr(arr, r[mask])
        rows.append({"Paramètre": name, "Importance (%)": round(abs(corr) * 100, 1)})
    
    return pd.DataFrame(rows).sort_values("Importance (%)", ascending=False)