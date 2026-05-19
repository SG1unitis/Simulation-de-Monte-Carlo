import streamlit as st

def render():
    st.subheader("📖 Méthodologie — Comment fonctionne ce simulateur ?")
    
    st.markdown(
        "### La méthode FAIR\n"
        "**Factor Analysis of Information Risk** décompose le risque en composantes quantifiables. "
        "Contrairement aux approches qualitatives, FAIR produit une distribution de pertes financières probables.\n\n"
        "La chaîne causale FAIR :\n"
        "```text\n"
        "TEF (tentatives/an)  ×  Vuln (%)  =  LEF (incidents réels)  ×  LM (coût/incident)  =  Risque (€/an)\n"
    )
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(
            "#### 📐 Distributions statistiques utilisées\n"
            "| Composante | Distribution | Pourquoi |\n"
            "|---|---|---|\n"
            "| **TEF** | PERT | Estimation min/mode/max |\n"
            "| **Vulnérabilité** | PERT | Estimation min/mode/max |\n"
            "| **LEF** | Poisson | Nb d'événements discrets/an |\n"
            "| **LM** | Log-normale | Pertes toujours positives, queue longue |"
        )
        
    with col_m2:
        st.markdown(
            "#### 📊 Indicateurs de sortie\n"
            "| Indicateur | Définition | Usage |\n"
            "|---|---|---|\n"
            "| **ALE** | Perte annuelle moyenne | Budget risque |\n"
            "| **VaR 90%** | Dépassé 1 an sur 10 | Assurance cyber |\n"
            "| **VaR 99%** | Dépassé 1 an sur 100 | PCA / PRA |\n"
            "| **P(0 incident)** | Prob. d'année sans incident | Maturité cyber |"
        )

    st.divider()
    st.markdown(
        "### 🎲 Simulation Monte-Carlo\n"
        "Pour chaque itération (×100 000) :\n"
        "1. Tire aléatoirement TEF, Vuln, LM selon leurs distributions\n"
        "2. Calcule LEF = Poisson(TEF × Vuln)\n"
        "3. Calcule Perte annuelle = LEF × LM\n"
        "4. Stocke le résultat"
    )

    st.divider()
    st.markdown(
        "### ⚠️ Limites de la simulation\n"
        "Bien que puissant, ce simulateur présente certaines limites inhérentes à la modélisation FAIR et Monte-Carlo :\n"
        "* **Précision nécessaire** : La précision des résultats dépend entièrement de la qualité des estimations fournies en entrée (TEF, Vulnérabilité, Magnitude).\n"
        "* **Interdépendance** : Le modèle actuel simule des incidents indépendants et peut sous-estimer le risque d'attaques en cascade affectant plusieurs systèmes simultanément.\n"
        "* **Pertes Intangibles** : L'impact sur la réputation ou la perte de confiance des partenaires est souvent difficile à quantifier financièrement avec précision."
    )