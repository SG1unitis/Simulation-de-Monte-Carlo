"""
distributions.py
----------------
Fonctions de génération des distributions statistiques
utilisées dans le modèle FAIR.

Distributions disponibles :
  - pert_sample         : distribution PERT (estimations expertes)
  - lognormal_from_ci   : log-normale depuis médiane + facteur d'incertitude
"""

import numpy as np
import scipy.stats as stats
NB_ECHANTILLON: int = 10_000

def pert_sample(low, mode, high, n=NB_ECHANTILLON, lam=4):
    """
    Génère n échantillons selon une distribution PERT.

    Paramètres
    ----------
    low  : valeur minimale plausible
    mode : valeur la plus probable (mode)
    high : valeur maximale plausible
    lam  : poids du mode (4 par défaut, standard PERT)
    n    : nombre d'échantillons

    Retourne
    --------
    np.ndarray de n valeurs dans [low, high]

    Exemple
    -------
    >>> tef = pert_sample(low=2, mode=5, high=15, n=100_000)
    """
    if not (low <= mode <= high):
        raise ValueError(
            f"Ordre invalide : low={low} <= mode={mode} <= high={high} requis"
        )
    if low == high:
        return np.full(n, low)

    mu = (low + lam * mode + high) / (lam + 2)

    if abs(mode - mu) < 1e-10:
        return np.full(n, mode)

    alpha = (mu - low) * (2 * mode - low - high) / ((mode - mu) * (high - low))
    beta = alpha * (high - mu) / (mu - low)

    samples = stats.beta.rvs(alpha, beta, size=n)
    return low + samples * (high - low)


def lognormal_from_ci(median, error_factor, n=NB_ECHANTILLON, max_value=None):
    """
    Génère n échantillons log-normaux depuis des paramètres intuitifs.

    Paramètres
    ----------
    median       : valeur centrale (ex: 180_000 €)
    error_factor : facteur multiplicatif pour l'intervalle à 90%
                   ex: 5 → plage [median/5 ; median×5] à 90%
    n            : nombre d'échantillons

    Retourne
    --------
    np.ndarray de n valeurs positives

    Exemple
    -------
    >>> lm = lognormal_from_ci(median=180_000, error_factor=5, n=100_000)
    """
    mu = np.log(median)
    sigma = np.log(error_factor) / 1.645
    samples = np.random.lognormal(mu, sigma, n)
    if max_value is not None:
        samples = np.clip(samples, 0, max_value)
    return samples
