# charts.py
import plotly.graph_objects as go  #Utilisé pour la création des graphiques complexes (histogrammes, courbes)
import plotly.express as px      #Utilisé pour la création des graphiques simples (diagramme en barres)
import numpy as np   #Utilisé pour manipuler mathématiquement les tableaux des résultats (tris, pourcentages)

def plot_loss_distribution(results, ale, p90, p99):   #Génération de l'histogramme des pertes annuelles (années avec incident seulement!)
    results_nonzero = results[results > 0] / 1000
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=results_nonzero,
        nbinsx=200,
        xbins=dict(start=0, end=p99 / 1000, size=(p99 / 1000) / 100),
        name="Scénarios",
        marker_color="steelblue",
        opacity=0.75,
    ))
    #Lignes verticales pour les indicateurs clés
    for val, color, name, ay in [(ale, "black", "ALE", -40), (p90, "orange", "VaR 90%", -40), (p99, "red", "VaR 99%", -40)]:
        fig.add_vline(x=val / 1000, line_color=color, line_dash="dash" if color != "black" else "solid", line_width=2)
        fig.add_annotation(x=val/1000, y=0.95 if name=="ALE" else (0.75 if "90" in name else 0.55),
                           xref="x", yref="paper", text=f"{name}<br>{val/1000:,.0f} k€",
                           showarrow=True, arrowhead=2, ax=40, ay=ay, font=dict(color=color, size=11))

    fig.update_layout(title="📊 Distribution des Pertes Annuelles", xaxis_title="Perte annuelle (k€)", 
                      yaxis_title="Nombre de scénarios", height=400, showlegend=False,
                      xaxis=dict(range=[0, p99 / 1000 * 1.2], ticksuffix=" k€"))
    return fig

def plot_exceedance_curve(results, p90, p99):  #Génère la courbe d'exceedance
    idx = np.random.choice(len(results), min(10_000, len(results)), replace=False)
    sorted_r = np.sort(results[idx]) / 1000
    exceedance = (1 - np.arange(1, len(sorted_r) + 1) / len(sorted_r)) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sorted_r, y=exceedance, mode="lines", line=dict(color="darkred", width=2),
                             fill="tozeroy", fillcolor="rgba(139,0,0,0.08)"))
    
    #Lignes de probabilité
    for p, val, color in [(10, p90, "orange"), (1, p99, "red")]:
        fig.add_hline(y=p, line_color=color, line_dash="dot", line_width=2,
                      annotation_text=f"➜ VaR {100-p}% : {val/1000:,.0f} k€", annotation_position="top right")

    fig.update_layout(title="📉 Courbe d'Exceedance", xaxis_title="Perte annuelle (k€)",
                      yaxis_title="Probabilité de dépassement (%)", height=400,
                      xaxis=dict(range=[0, p99 / 1000 * 1.2], ticksuffix=" k€"), yaxis=dict(range=[0, 100]))
    return fig

def plot_sensitivity_bar(df_sens):     #Génère le graphique de sensibilité, désignant les paramètres sur lesquels agir en priorité
    couleurs_fixes = {
        "LM - Magnitude": "#e74c3c",
        "TEF — Fréquence": "#f1c40f",   
        "Vulnérabilité": "#2ecc71"
    }
    fig = px.bar(
        df_sens,
        x="Importance (%)",
        y="Paramètre",
        orientation="h",
        color="Paramètre",
        color_discrete_map=couleurs_fixes
    )
    fig.update_layout(
        title="Contribution relative au risque",
        height=250,
        showlegend=False
    )
    return fig

def plot_roi_comparison(results_avant, results_apres, ale_avant, ale_apres):    #Compare la distribution avant et après application d'un contrôle
    x_max = np.percentile(np.concatenate([results_avant[results_avant > 0], results_apres[results_apres > 0]]) / 1000, 95)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=results_avant[results_avant > 0] / 1000, nbinsx=80, name="Avant", marker_color="salmon", opacity=0.6))
    fig.add_trace(go.Histogram(x=results_apres[results_apres > 0] / 1000, nbinsx=80, name="Après", marker_color="mediumseagreen", opacity=0.6))
    
    fig.add_vline(x=ale_avant / 1000, line_color="red", line_dash="dash", annotation_text="ALE Avant")
    fig.add_vline(x=ale_apres / 1000, line_color="green", line_dash="dash", annotation_text="ALE Après")
    
    fig.update_layout(barmode="overlay", title="Impact du contrôle sur le risque", 
                      xaxis_title="Perte (k€)", xaxis=dict(range=[0, x_max]), height=400)
    return fig