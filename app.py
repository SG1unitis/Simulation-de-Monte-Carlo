import sys
import os
import streamlit as st #Création de l'interface web interactive
import numpy as np #Calculs des centiles
import base64

import fair_core #Import du moteur mathématique

#Détection du dossier views
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
if dossier_actuel not in sys.path:
    sys.path.append(dossier_actuel)

#Configuration de la page
st.set_page_config(page_title="Simulateur Risques Cyber — FAIR", page_icon="🛡️", layout="wide")

#Création de la sidebar
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "Logo_Valabre.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <div style='text-align: center; padding: 10px 0 20px 0;'>
                <img src='data:image/png;base64,{logo_b64}' style='width: 140px; border-radius: 8px;'><br><br>
                <span style='font-size: 11px; color: #666;'>Pôle Innovation & Nouvelles Technologies</span>
            </div>
            <hr style='margin: 0 0 15px 0; border-color: #2980B9;'>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style='text-align: center; padding: 10px 0 20px 0;'>
                <span style='font-size: 20px; font-weight: bold; color: #2980B9;'>
                    Entente Valabre
                </span><br><br>
                <span style='font-size: 12px; color: #666;'>
                    Pôle Innovation & Nouvelles Technologies
                </span>
            </div>
            <hr style='margin: 0 0 15px 0; border-color: #2980B9; border-width: 2px;'>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("⚙️ Paramètres")
    scenario_name = st.text_input("Nom du scénario", "Ransomware")

    st.subheader("🔴 TEF — Fréquence des menaces")
    tef_low = st.slider("Minimum", 0.1, 5.0, 2.0, 0.1, help="Nb minimum de tentatives/an")
    tef_mode = st.slider("Mode", 0.5, 15.0, 5.0, 0.5, help="Nb le plus probable de tentatives/an")
    tef_high = st.slider("Maximum", 1.0, 30.0, 15.0, 0.5, help="Nb maximum de tentatives/an")

    st.subheader("🟠 Vulnérabilité")
    vuln_low = st.slider("Minimum", 0.01, 0.30, 0.08, 0.01, format="%.2f", help="Probabilité min qu'une attaque aboutisse")
    vuln_mode = st.slider("Mode", 0.05, 0.60, 0.20, 0.01, format="%.2f", help="Probabilité la plus probable")
    vuln_high = st.slider("Maximum", 0.10, 1.00, 0.40, 0.01, format="%.2f", help="Probabilité max")

    st.subheader("🟡 LM — Magnitude des pertes")
    lm_median = st.number_input("Perte médiane (€)", 10_000, 5_000_000, 180_000, 10_000)
    lm_ef = st.slider("Facteur d'incertitude (EF)", 1.5, 20.0, 5.0, 0.5, help="Marge d'erreur de l'estimation. Ex : avec un facteur de 5 et une médiane à 180 000, on est sûrs à 90 % que la perte réelle d'un seul incident se situera entre 36 000 (180 divisé par 5) et 900 000 euros (180 multiplié par 5)")

    st.subheader("⚙️ Simulation")
    n_sims = st.select_slider("Nb de simulations", [10_000, 50_000, 100_000], 100_000)
    use_fixed_seed = st.checkbox("Mode démonstration", value=True, help="Verrouille le moteur pour garantir exactement les mêmes résultats à chaque lancement.")
    sim_seed = 42 if use_fixed_seed else None

    tef_valide = round(tef_low, 4) <= round(tef_mode, 4) <= round(tef_high, 4)
    vuln_valide = round(vuln_low, 4) <= round(vuln_mode, 4) <= round(vuln_high, 4)

    if not tef_valide:
        st.error("🚨 **TEF** : L'ordre Minimum ≤ Mode ≤ Maximum n'est pas respecté.")
    if not vuln_valide:
        st.error("🚨 **Vulnérabilité** : L'ordre Minimum ≤ Mode ≤ Maximum n'est pas respecté.")

    run = st.button("🚀 Lancer la simulation", type="primary", use_container_width=True, disabled=not (tef_valide and vuln_valide))

#Titres et paramètres
st.title("Simulateur de Risques Cyber — Méthode FAIR")
st.caption("Entente Valabre — Pôle Innovation & Nouvelles Technologies")
st.divider()

if not run and "sim" not in st.session_state:
    st.info("👈 Configurez les paramètres dans la sidebar puis cliquez sur **Lancer la simulation**")
else:
    params = {
        "tef_low": tef_low, "tef_mode": tef_mode, "tef_high": tef_high,
        "vuln_low": vuln_low, "vuln_mode": vuln_mode, "vuln_high": vuln_high,
        "lm_median": lm_median, "lm_ef": lm_ef
    }

    if run:
        with st.spinner(f"⏳ Simulation de {n_sims:,} scénarios en cours..."):
            sim = fair_core.run_fair_engine(params, n=n_sims, seed=sim_seed)
            st.session_state["sim"] = sim
            st.session_state["params"] = params
            st.session_state["scenario"] = scenario_name

    sim = st.session_state["sim"]
    results = sim["annual_loss"]
    lef = sim["lef"]
    ale = results.mean()
    p80, p90, p99 = np.percentile(results, 80), np.percentile(results, 90), np.percentile(results, 99)
    prob_zero = (lef == 0).mean()

    #Explication des différentes métriques
    st.subheader(f"📊 Résultats — {st.session_state['scenario']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("ALE moyen", f"{ale:,.0f} €", help="Perte financière moyenne attendue sur une année.")
    c2.metric("VaR 80%", f"{p80:,.0f} €", help="Dans 8 années sur 10, la perte restera EN DESSOUS de ce montant.")
    c3.metric("VaR 90%", f"{p90:,.0f} €", help="Dans 9 années sur 10, la perte restera EN DESSOUS de ce montant.")
    c4.metric("VaR 99%", f"{p99:,.0f} €", help="Scénario catastrophe (1 an sur 100). Seuil pour le PCA.")
    c5.metric("P(0 incident)", f"{prob_zero:.1%}", help="Probabilité qu'aucune attaque n'aboutisse dans l'année.")
    st.divider()

    #Bandeau d'alerte adaptatif selon le risque
    if p80 == 0:
        explication_var = f"Dans {prob_zero:.0%} des années simulées, aucun incident ne se produit. Dans le pire scénario (1 an sur 100), elle pourrait atteindre {p99/1000:,.0f} k€ (VaR 99%)."
    else:
        explication_var = f"Dans 9 années sur 10, la perte restera sous {p90/1000:,.0f} k€ (VaR 90%). Dans le pire scénario (1 an sur 100), elle pourrait atteindre {p99/1000:,.0f} k€ (VaR 99%)."

    if prob_zero > 0.80:
        st.success(f"🟢 Risque faible — L'ALE moyen est de {ale/1000:,.0f} k€/an. {explication_var}")
    elif prob_zero > 0.50:
        st.warning(f"🟡 Risque modéré — L'ALE moyen est de {ale/1000:,.0f} k€/an. {explication_var}")
    else:
        st.error(f"🔴 Risque élevé — L'ALE moyen est de {ale/1000:,.0f} k€/an. {explication_var}")
    
    st.divider()
    #Création et import des 4 onglets
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Résultats", "🔍 Analyse de sensibilité", "📖 Méthodologie", "💰 ROI Contrôles"])

    with tab1:
        from views import tab_results
        tab_results.render(sim, results, lef, ale, p90, p99, st.session_state["scenario"])

    with tab2:
        from views import tab_sensitivity
        tab_sensitivity.render(sim)

    with tab3:
        from views import tab_methodo
        tab_methodo.render()

    with tab4:
        from views import tab_roi
        tab_roi.render(sim, n_sims, sim_seed, ale, results)