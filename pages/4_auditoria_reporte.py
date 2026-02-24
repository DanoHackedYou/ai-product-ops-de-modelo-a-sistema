import streamlit as st
from utils.reporting import generate_sdd_markdown, markdown_to_pdf_bytes

st.title("Auditoría y Reporte")
st.caption("Genera un SDD (Markdown) y un entregable PDF básico para revisión (ITSM/SRE/Compliance).")

ss = st.session_state

col1, col2 = st.columns([1, 1])

with col1:
    with st.container(border=True):
        st.subheader("Estado actual (resumen)")
        st.write("Pipeline:", ss.get("pipeline_ordered", []))
        st.write("Roles:", {k: (v or "(pendiente)") for k, v in ss.get("roles", {}).items()})
        st.write("Métricas:", ss.get("metrics", {}))
        st.write("Guardrails:", ss.get("guardrails", {}))
        sim = ss.get("sim", {})
        if sim:
            st.write(
                "Simulación:",
                {
                    "preset": sim.get("preset"),
                    "tickets": sim.get("tickets"),
                    "tokens_total": sim.get("tokens_total"),
                    "coste_total": f"{float(sim.get('coste_total', 0)):.2f} €",
                },
            )
        else:
            st.write("Simulación: (no ejecutada)")

with col2:
    with st.container(border=True):
        st.subheader("Checklist de control (rápido)")
        pipeline = ss.get("pipeline_ordered", [])
        roles = ss.get("roles", {})
        guardrails = ss.get("guardrails", {})

        checks = [
            ("Kill switch owner", bool(roles.get("kill_switch_owner"))),
            ("Auditoría en pipeline", "Auditoría" in pipeline),
            ("HITL en pipeline", "Validación Humana" in pipeline),
            ("PII filter en pipeline", "Filtro PII" in pipeline),
            ("SLO definido", float(guardrails.get("slo_latencia_s", 0) or 0) > 0),
        ]
        for label, ok in checks:
            st.write(("✅ " if ok else "⚠️ ") + label)

st.divider()

st.subheader("SDD (Markdown)")
md = generate_sdd_markdown(ss)
st.code(md, language="markdown")

st.download_button(
    "Descargar SDD.md",
    data=md.encode("utf-8"),
    file_name="SDD_AI_Product_Ops.md",
    mime="text/markdown",
)

pdf_bytes = markdown_to_pdf_bytes(md)
st.download_button(
    "Descargar SDD.pdf",
    data=pdf_bytes,
    file_name="SDD_AI_Product_Ops.pdf",
    mime="application/pdf",
)

st.info("Para evaluación DSI/ITSM: el PDF es suficiente como entregable, aunque la conversión Markdown->PDF sea intencionalmente simple.")
