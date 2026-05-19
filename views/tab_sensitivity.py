import streamlit as st
import fair_core
import charts

def render(sim):
    st.subheader("🔍 Analyse de Sensibilité — Sur quels paramètres agir en priorité ?")
    df_sens = fair_core.calculate_sensitivity(sim)
    col_s1, col_s2 = st.columns([1, 2])
    col_s1.dataframe(df_sens, use_container_width=True, hide_index=True)
    col_s2.plotly_chart(charts.plot_sensitivity_bar(df_sens), use_container_width=True)

    st.caption(
        "#### 💡 Aide à la décision\n\n"
        "**Priorisation des investissements** : Ce graphique identifie les leviers qui dictent le niveau de risque financier. "
        "Plus la barre est longue, plus une action sur ce paramètre sera efficace pour réduire l'ALE.\n\n"
        "**Note sur la répartition** : Le total est inférieur ou supérieur à 100 % car les facteurs de risque ne s'additionnent pas : ils se multiplient et s'amplifient mutuellement. "
        "Ce score mesure l'**influence individuelle** de chaque facteur sur le résultat final, et non une simple part de gâteau comptable."
    )

    st.markdown("""
| Paramètre | Définition | Levier d'action |
|---|---|---|
| 🔴 **LM — Magnitude des pertes** | Coût financier d'un seul incident | Assurance cyber, PCA/PRA, sauvegardes |
| 🟡 **TEF — Fréquence des menaces** | Nb de tentatives d'attaque par an | Filtrage mail, threat intelligence |
| 🟢 **Vulnérabilité** | Probabilité qu'une tentative aboutisse | EDR, MFA, segmentation réseau |
    """)