import streamlit as st

st.title("Diseñador de Producto: Wizard TO-BE (Process + People + Policy)")
st.caption("Configura el flujo, ownership y controles. Esto alimenta el SDD y el reporte de auditoría.")

ss = st.session_state

st.subheader("1) Flujo del sistema (pipeline)")
catalog = [
    "Auth",
    "RBAC",
    "Clasificación",
    "RAG",
    "Inferencia",
    "Filtro PII",
    "Validación Humana",
    "Auditoría",
    "Feedback loop",
]

selected = st.multiselect(
    "Selecciona los pasos que existen en tu sistema",
    options=catalog,
    default=ss.get("pipeline_selected", ["Auth", "RAG", "Inferencia", "Auditoría"]),
)

ss["pipeline_selected"] = selected

# Orden manual con botones
st.markdown("Ordena el pipeline (operación real = orden real).")

if "pipeline_ordered" not in ss or set(ss["pipeline_ordered"]) != set(selected):
    ss["pipeline_ordered"] = selected[:]

ordered = ss["pipeline_ordered"]

c1, c2 = st.columns([1, 1])

with c1:
    with st.container(border=True):
        st.write("Orden actual")
        if not ordered:
            st.warning("Selecciona pasos arriba para poder ordenarlos.")
        else:
            for i, step in enumerate(ordered, 1):
                st.write(f"{i}. {step}")

with c2:
    with st.container(border=True):
        st.write("Mover elementos")
        if ordered:
            idx = st.selectbox("Elemento", list(range(len(ordered))), format_func=lambda i: ordered[i])
            up, down = st.columns(2)
            with up:
                if st.button("Subir", use_container_width=True) and idx > 0:
                    ordered[idx - 1], ordered[idx] = ordered[idx], ordered[idx - 1]
            with down:
                if st.button("Bajar", use_container_width=True) and idx < len(ordered) - 1:
                    ordered[idx + 1], ordered[idx] = ordered[idx], ordered[idx + 1]
            if st.button("Reset = orden de selección", use_container_width=True):
                ss["pipeline_ordered"] = selected[:]
        else:
            st.info("Añade pasos en la multiselección.")

ss["pipeline_ordered"] = ordered

st.divider()

st.subheader("2) Roles y ownership (mínimos para operar)")
roles = ss["roles"]

colA, colB = st.columns(2)
with colA:
    roles["service_owner"] = st.text_input("service_owner (ITSM/Product)", roles.get("service_owner", ""))
    roles["sre_owner"] = st.text_input("sre_owner (SRE/On-call)", roles.get("sre_owner", ""))
    roles["kill_switch_owner"] = st.text_input("kill_switch_owner (autoridad de parada)", roles.get("kill_switch_owner", ""))

with colB:
    roles["data_policy_owner"] = st.text_input("data_policy_owner (PII/retención/compliance)", roles.get("data_policy_owner", ""))
    roles["data_steward"] = st.text_input("data_steward (calidad de datos/KB)", roles.get("data_steward", ""))

ss["roles"] = roles

st.divider()

st.subheader("3) Guardrails operativos (SRE/Compliance)")
g = ss["guardrails"]
g["slo_latencia_s"] = st.number_input("SLO latencia p95 (s)", min_value=0.1, max_value=60.0, value=float(g.get("slo_latencia_s", 2.0)), step=0.1)
g["max_halluc_rate"] = st.number_input("Máx. alucinación", min_value=0.0, max_value=1.0, value=float(g.get("max_halluc_rate", 0.02)), step=0.01, format="%.3f")
ss["guardrails"] = g

with st.container(border=True):
    st.subheader("Checklist recomendado (interpretación)")
    st.markdown(
        """
- Kill switch con owner y runbook
- Auditoría activa (todas las decisiones trazables)
- HITL para casos de riesgo (PII, baja confianza, acciones peligrosas)
- Filtro PII antes de logs/telemetría y antes del LLM si aplica
- RBAC y mínimos privilegios (quién puede ver qué)
- SLO + error budget para decidir cambios sin romper producción
"""
    )
