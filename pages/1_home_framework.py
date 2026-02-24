import streamlit as st

st.title("AI Product Ops: De Modelo a Sistema")
st.caption("DSI · ITSM · SRE/Compliance: operar IA como un servicio medible y gobernable.")

with st.container(border=True):
    st.subheader("Mapa mental: de modelo a sistema")
    st.markdown(
        """
Un asistente en producción no se gestiona como un “modelo”, sino como un **servicio**:

- **People**: ownership, on-call, kill switch, stewardship de datos
- **Process**: intake → clasificación → RAG → inferencia → HITL → auditoría → mejora continua
- **Tech**: auth, RBAC, logs, trazabilidad, versionado, feature flags
- **Policy**: PII, retención, minimización, DPIA, control de cambios
- **SRE**: SLO, error budget, runbooks, incident response
- **ITSM**: catálogo, SLAs, escalado, problemas, cambios, conocimiento
"""
    )

with st.container(border=True):
    st.subheader("Objetivo del SDD")
    st.session_state["sdd_goal"] = st.text_area(
        "Define el objetivo (1-3 frases)",
        st.session_state.get("sdd_goal", ""),
        height=120,
    )

col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.subheader("Métricas (Outcome / Efficiency / Safety)")
        m = st.session_state["metrics"]
        m["outcome"] = st.text_input("Outcome (valor)", m.get("outcome", ""))
        m["efficiency"] = st.text_input("Efficiency (coste)", m.get("efficiency", ""))
        m["safety"] = st.text_input("Safety (riesgo)", m.get("safety", ""))

with col2:
    with st.container(border=True):
        st.subheader("Guardrails (SLO/umbrales)")
        g = st.session_state["guardrails"]
        g["slo_latencia_s"] = st.number_input(
            "Latencia p95 (segundos)",
            min_value=0.1,
            max_value=60.0,
            value=float(g.get("slo_latencia_s", 2.0)),
            step=0.1,
        )
        g["max_halluc_rate"] = st.number_input(
            "Tasa alucinación máxima",
            min_value=0.0,
            max_value=1.0,
            value=float(g.get("max_halluc_rate", 0.02)),
            step=0.01,
            format="%.3f",
        )

st.info("Siguiente paso: usa el simulador para ver el trade-off TI vs SI y luego diseña el flujo con ownership.")
