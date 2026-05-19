import streamlit as st
import numpy as np
import pandas as pd
import charts
import excel_export
import fair_core

def render(sim, results, lef, ale, p90, p99, scenario_name):
    colA, colB = st.columns(2)
    colA.plotly_chart(charts.plot_loss_distribution(results, ale, p90, p99), use_container_width=True)
    colA.caption("💡 Les années sans incident sont exclues pour plus de lisibilité. Ligne **noire** = ALE, ligne **orange** = VaR 90%, ligne **rouge** = VaR 99%.")
    
    colB.plotly_chart(charts.plot_exceedance_curve(results, p90, p99), use_container_width=True)
    colB.caption("💡 La courbe répond à : *'Quelle probabilité de perdre PLUS de X€ ?'* Remontez depuis l'axe horizontal jusqu'à la courbe, puis lisez la probabilité à gauche.")

    st.divider()
    st.subheader("📅 Fréquence des incidents par an")
    unique, counts = np.unique(lef, return_counts=True)
    prob_dict = dict(zip(unique, counts / len(lef) * 100))
    
    rows_freq = []
    for n_inc in range(6):
        prob = prob_dict.get(n_inc, 0)
        prob_cumul = sum(prob_dict.get(i, 0) for i in range(n_inc + 1))
        if n_inc == 0: interpretation, coul = "✅ Aucun incident — année sans impact", "🟢"
        elif n_inc == 1: interpretation, coul = "⚠️ Un incident — coût unique", "🟡"
        elif n_inc == 2: interpretation, coul = "🔶 Deux incidents — pression significative", "🟠"
        else: interpretation, coul = f"🔴 {n_inc} incidents — scénario critique", "🔴"
        
        rows_freq.append({
            "Nb incidents / an": f"{coul} {n_inc}",
            "Probabilité (%)": f"{prob:.1f}%",
            "Probabilité cumulée": f"{prob_cumul:.1f}%",
            "Interprétation": interpretation,
        })
        
    st.dataframe(pd.DataFrame(rows_freq), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📥 Télécharger le rapport")
    df_sens_export = fair_core.calculate_sensitivity(sim)
    excel_buffer = excel_export.generate_excel_report(sim, df_sens_export, scenario_name)
    st.download_button("📥 Télécharger le rapport Excel", data=excel_buffer, file_name=f"rapport_risque.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)