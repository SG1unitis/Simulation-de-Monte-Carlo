import streamlit as st
import fair_core
import charts

def render(sim, n_sims, sim_seed, ale, results):
    st.subheader("💰 Calcul du ROI — Quel contrôle investir en priorité ?")
    st.markdown("> Simulez l'impact financier d'un investissement en cybersécurité. Le ROI compare la **réduction de risque obtenue** au **coût du contrôle**.")
    st.divider()

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### 🔧 Contrôle envisagé")
        controle_nom = st.text_input("Nom du contrôle", "")
        cout_controle = st.number_input("Coût annuel du contrôle (€)", 1_000, 1_000_000, 20_000, 1_000)
        st.caption("💡 Inclure : achat licence + maintenance + formation")

    with col_c2:
        st.markdown("#### 📉 Réduction estimée des paramètres FAIR")
        st.caption("Laissez à 0% les paramètres non affectés par ce contrôle.")
        reduc_vuln = st.slider("Réduction de la Vulnérabilité", 0, 80, 30, 5, format="%d%%")
        reduc_tef = st.slider("Réduction du TEF (fréquence menaces)", 0, 80, 0, 5, format="%d%%")
        reduc_lm = st.slider("Réduction de la LM (magnitude pertes)", 0, 80, 0, 5, format="%d%%")

    st.divider()

    if st.button("📊 Calculer le ROI", type="primary", use_container_width=True):
        # Récupération sécurisée des paramètres originaux
        p_apres = st.session_state["params"].copy()
        
        # Application des coefficients de réduction
        p_apres["vuln_mode"] *= (1 - reduc_vuln / 100)
        p_apres["vuln_low"] *= (1 - reduc_vuln / 100)
        p_apres["vuln_high"] *= (1 - reduc_vuln / 100)
        p_apres["tef_mode"] *= (1 - reduc_tef / 100)
        p_apres["tef_low"] *= (1 - reduc_tef / 100)
        p_apres["tef_high"] *= (1 - reduc_tef / 100)
        p_apres["lm_median"] *= (1 - reduc_lm / 100)

        with st.spinner("Simulation avant/après contrôle en cours..."):
            sim_apres = fair_core.run_fair_engine(p_apres, n=n_sims, seed=sim_seed)
            ale_apres = sim_apres["annual_loss"].mean()

        reduction_ale = ale - ale_apres
        roi_pct = ((reduction_ale - cout_controle) / cout_controle) * 100
        payback_années = cout_controle / reduction_ale if reduction_ale > 0 else float("inf")

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("ALE avant contrôle", f"{ale:,.0f} €")
        r2.metric("ALE après contrôle", f"{ale_apres:,.0f} €", delta=f"-{reduction_ale:,.0f} €", delta_color="inverse")
        r3.metric("ROI du contrôle", f"{roi_pct:,.0f} %", help="(Réduction ALE - Coût contrôle) / Coût contrôle × 100")
        r4.metric("Retour sur investissement", f"{payback_années:.1f} ans" if payback_années != float("inf") else "∞", help="Temps nécessaire pour que la réduction de risque couvre le coût")
        st.divider()

        if roi_pct > 100:
            st.success(f"✅ **Investissement très rentable** — Le contrôle *{controle_nom}* génère un ROI de **{roi_pct:,.0f}%**. Pour 1€ investi, vous économisez **{1 + roi_pct/100:.1f}€** de risque. Retour sur investissement en **{payback_années:.1f} ans**.")
        elif roi_pct > 0:
            st.warning(f"⚠️ **Investissement modérément rentable** — Le contrôle *{controle_nom}* génère un ROI de **{roi_pct:,.0f}%**. La réduction de risque (**{reduction_ale:,.0f} €/an**) couvre le coût (**{cout_controle:,.0f} €/an**) mais le retour reste limité.")
        else:
            st.error(f"❌ **Investissement non rentable** — Le coût du contrôle *{controle_nom}* (**{cout_controle:,.0f} €/an**) dépasse la réduction de risque obtenue (**{reduction_ale:,.0f} €/an**). Envisagez un contrôle moins coûteux ou ciblez un paramètre à plus fort impact.")

        st.divider()
        st.subheader("📊 Distribution du risque — Avant vs Après")
        st.plotly_chart(charts.plot_roi_comparison(results, sim_apres["annual_loss"], ale, ale_apres), use_container_width=True)
        st.caption("💡 Le décalage de la courbe **verte vers la gauche** représente la réduction du risque obtenue grâce au contrôle. Plus le décalage est important, plus le contrôle est efficace.")