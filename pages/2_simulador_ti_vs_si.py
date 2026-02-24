import pandas as pd
import plotly.express as px
import streamlit as st

from utils.economics import CostInputs, compute_costs

st.title("Simulador: TI vs SI (Coste total por ticket)")
st.caption("Optimizar solo €/tokens suele romper el sistema si baja el FCR y sube el retrabajo humano.")

preset = st.selectbox(
    "Preset (ejemplo)",
    [
        "Balanceado",
        "Barato pero peor calidad",
        "Caro pero mejor calidad",
        "Custom",
    ],
    index=0,
)

# Defaults por preset
defaults = {
    "Balanceado": dict(eur_por_1k_tokens=0.25, fcr=0.65, tokens_por_ticket=1800),
    "Barato pero peor calidad": dict(eur_por_1k_tokens=0.12, fcr=0.45, tokens_por_ticket=1600),
    "Caro pero mejor calidad": dict(eur_por_1k_tokens=0.45, fcr=0.78, tokens_por_ticket=2200),
    "Custom": dict(eur_por_1k_tokens=0.25, fcr=0.60, tokens_por_ticket=1800),
}[preset]

colA, colB, colC = st.columns(3)

with colA:
    tickets = st.number_input("Tickets / mes", min_value=100, max_value=5_000_000, value=50_000, step=1000)
    tokens_por_ticket = st.number_input(
        "Tokens por ticket", min_value=100, max_value=50_000, value=int(defaults["tokens_por_ticket"]), step=100
    )

with colB:
    eur_por_1k_tokens = st.number_input(
        "€/1k tokens", min_value=0.001, max_value=10.0, value=float(defaults["eur_por_1k_tokens"]), step=0.01
    )
    fcr = st.number_input(
        "FCR (0..1)", min_value=0.0, max_value=1.0, value=float(defaults["fcr"]), step=0.01, format="%.2f"
    )

with colC:
    coste_hora_agente = st.number_input("Coste hora agente (€)", min_value=5.0, max_value=200.0, value=22.0, step=1.0)
    aht_min = st.number_input("AHT humano (min)", min_value=1.0, max_value=120.0, value=12.0, step=1.0)

x = CostInputs(
    tickets=int(tickets),
    tokens_por_ticket=int(tokens_por_ticket),
    eur_por_1k_tokens=float(eur_por_1k_tokens),
    fcr=float(fcr),
    coste_hora_agente=float(coste_hora_agente),
    aht_min=float(aht_min),
)

res = compute_costs(x)

# Persistimos resultados en session_state para el reporte
st.session_state["sim"] = {
    "preset": preset,
    "tickets": int(tickets),
    "tokens_por_ticket": int(tokens_por_ticket),
    "eur_por_1k_tokens": float(eur_por_1k_tokens),
    "fcr": float(fcr),
    **res,
}

k1, k2, k3, k4 = st.columns(4)
k1.metric("Tokens totales", f"{res['tokens_total']:,}".replace(",", "."))
k2.metric("Coste TI", f"{res['coste_ti']:.2f} €")
k3.metric("Coste Operativo", f"{res['coste_operativo']:.2f} €")
k4.metric("Coste Total", f"{res['coste_total']:.2f} €")

st.divider()

with st.container(border=True):
    st.subheader("Lectura operativa")
    coste_ticket = res["coste_total"] / max(int(tickets), 1)
    st.write(
        f"- Coste total unitario aproximado: **{coste_ticket:.4f} €/ticket**\n"
        f"- Coste humano por ticket (si escala a agente): **{res['coste_ticket_humano']:.2f} €**\n"
        f"- Retrabajo humano esperado: **{(1.0 - fcr):.0%}** de tickets"
    )

st.divider()

# Curva de sensibilidad: FCR vs coste total
st.subheader("Sensibilidad: FCR vs Coste Total (manteniendo el resto)")
grid = []
for f in [i / 100 for i in range(10, 96, 2)]:
    xx = CostInputs(
        tickets=int(tickets),
        tokens_por_ticket=int(tokens_por_ticket),
        eur_por_1k_tokens=float(eur_por_1k_tokens),
        fcr=float(f),
        coste_hora_agente=float(coste_hora_agente),
        aht_min=float(aht_min),
    )
    rr = compute_costs(xx)
    grid.append({"FCR": f, "Coste_TI": rr["coste_ti"], "Coste_Operativo": rr["coste_operativo"], "Coste_Total": rr["coste_total"]})

df = pd.DataFrame(grid)
fig = px.line(df, x="FCR", y=["Coste_TI", "Coste_Operativo", "Coste_Total"], markers=True)
st.plotly_chart(fig, use_container_width=True)

st.info("Siguiente paso: define el flujo y ownership para operar el servicio con SLO, auditoría y control de riesgos.")
