
import sys
import os

sys.path.insert(0, os.path.abspath(".."))

import numpy as np
from fair_core import pert_sample, lognormal_from_ci


#Tests
def test_pert_dans_les_bornes():   #Les échantillons PERT ne doivent jamais dépasser low, high
    samples = pert_sample(low=2, mode=5, high=15, n=50_000)
    assert samples.min() >= 2.0, "PERT génère des valeurs sous le minimum"
    assert samples.max() <= 15.0, "PERT génère des valeurs au-dessus du maximum"


def test_pert_mode_central():     #La moyenne PERT doit être proche du mode pour une distribution symétrique
    samples = pert_sample(low=0, mode=5, high=10, n=100_000)
    assert (
        abs(samples.mean() - 5.0) < 0.1
    ), f"Moyenne trop éloignée du mode : {samples.mean():.2f}"

def test_pert_cas_degenere():  #PERT avec low=mode=high doit retourner une constante
    samples = pert_sample(low=5, mode=5, high=5, n=1_000)
    assert np.all(samples == 5.0), "PERT dégénérée ne retourne pas une constante"

#Tests distribution log-normales
def test_lognormal_positive():   #Pas de valeurs négatives (un incident ne rapport pas d'argent !)
    samples = lognormal_from_ci(median=180_000, error_factor=5, n=50_000)
    assert (samples > 0).all(), "Log-normale génère des valeurs négatives"


def test_lognormal_mediane():   #La médiane empirique doit être proche de la médiane paramétrée
    median_cible = 180_000
    samples = lognormal_from_ci(median=median_cible, error_factor=5, n=100_000)
    mediane_empirique = np.median(samples)
    ecart_relatif = abs(mediane_empirique - median_cible) / median_cible
    assert ecart_relatif < 0.05, (
        f"Médiane empirique trop éloignée : {mediane_empirique:,.0f} € "
        f"(cible : {median_cible:,.0f} €)"
    )
#Tests moteur monte-carlo
def run_simulation_test(
    tef_low=2,
    tef_mode=5,
    tef_high=15,
    vuln_low=0.08,
    vuln_mode=0.20,
    vuln_high=0.40,
    lm_median=180_000,
    lm_ef=5,
    n=50_000,
    seed=42,
):
    np.random.seed(seed)
    tef = pert_sample(tef_low, tef_mode, tef_high, n=n)
    vuln = pert_sample(vuln_low, vuln_mode, vuln_high, n=n)
    lm = lognormal_from_ci(lm_median, lm_ef, n=n)
    lef = np.random.poisson(tef * vuln)
    return lef * lm


def test_pertes_positives():  #Pertes annuelles doivent être supérieures à 0
    results = run_simulation_test()
    assert (results >= 0).all(), "Présence de pertes négatives"

def test_vulnerabilite_zero(): #Avec 0% de vulnérabilité, la perte annuelle totale doit être nulle
    results = run_simulation_test(vuln_low=0, vuln_mode=0, vuln_high=0)
    assert results.sum() == 0, "Des pertes apparaissent malgré une vulnérabilité nulle"

def test_convergence():  #L'ALE doit rester stable, avec une faible variance relative
    #Lance 5 simulations indépendantes à N=100k avec des seeds différents
    ales = [
        run_simulation_test(n=100_000, seed=s).mean() for s in [42, 123, 456, 789, 999]
    ]
    moyenne = np.mean(ales)
    ecart_type = np.std(ales)
    cv = ecart_type / moyenne  #Coefficient de variation
    assert cv < 0.05, (
        f"ALE trop instable entre simulations : CV={cv:.1%} "
        f"(valeurs : {[f'{a:,.0f}' for a in ales]})"
    )

def test_reproductibilite():   #Deux simulations avec le même seed doivent donner des résultats identiques
    r1 = run_simulation_test(seed=42)
    r2 = run_simulation_test(seed=42)
    assert np.array_equal(r1, r2), "Résultats différents avec le même seed"

def test_var_croissante():    #La VaR doit être strictement croissante avec le percentile
    results = run_simulation_test()
    p80 = np.percentile(results, 80)
    p90 = np.percentile(results, 90)
    p99 = np.percentile(results, 99)
    assert (
        p80 < p90 < p99
    ), f"VaR non croissante : P80={p80:,.0f} P90={p90:,.0f} P99={p99:,.0f}"
