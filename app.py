import streamlit as st


def init_state():
    ss = st.session_state
    ss.setdefault(
        "sdd_goal",
        "Diseñar un sistema IA operable, medible y gobernable, explicitando trade-offs (Coste vs Calidad, TI vs SI).",
    )
    ss.setdefault("pipeline_selected", ["Auth", "RAG", "Inferencia", "Auditoría"])
    ss.setdefault("pipeline_ordered", ss["pipeline_selected"][:])

    ss.setdefault(
        "roles",
        {
            "kill_switch_owner": "",
            "data_policy_owner": "",
            "service_owner": "",
            "sre_owner": "",
            "data_steward": "",
        },
    )

    ss.setdefault(
        "metrics",
        {
            "outcome": "FCR (First Contact Resolution)",
            "efficiency": "€/ticket",
            "safety": "Tasa de alucinación / fuga PII",
        },
    )

    ss.setdefault(
        "guardrails",
        {
            "slo_latencia_s": 2.0,
            "max_halluc_rate": 0.02,
        },
    )

    ss.setdefault("sim", {})  # resultados del simulador


st.set_page_config(
    page_title="AI Product Ops · De Modelo a Sistema",
    page_icon="🧭",
    layout="wide",
)

init_state()

pages = {
    "Producto": [
        st.Page("pages/1_home_framework.py", title="Home · Framework", icon="🧩"),
        st.Page("pages/2_simulador_ti_vs_si.py", title="Simulador · TI vs SI", icon="📉"),
        st.Page("pages/3_disenador_producto.py", title="Diseñador · Wizard", icon="🛠️"),
        st.Page("pages/4_auditoria_reporte.py", title="Auditoría · Reporte", icon="🧾"),
    ]
}

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
