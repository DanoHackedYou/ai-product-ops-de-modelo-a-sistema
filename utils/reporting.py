import io
import re
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import cm


def generate_sdd_markdown(state: dict) -> str:
    """Genera un SDD (System Design Doc) en Markdown desde st.session_state."""
    today = date.today().isoformat()
    pipeline = state.get("pipeline_ordered", [])
    roles = state.get("roles", {})
    metrics = state.get("metrics", {})
    guardrails = state.get("guardrails", {})
    sim = state.get("sim", {})

    checklist = [
        ("Kill Switch definido", bool(roles.get("kill_switch_owner"))),
        ("Auditoría/Logs activados", "Auditoría" in pipeline),
        ("Validación humana (HITL)", "Validación Humana" in pipeline),
        ("Filtro PII", "Filtro PII" in pipeline),
        ("RBAC/roles mínimos", bool(roles)),
        ("SLO definido", float(guardrails.get("slo_latencia_s", 0) or 0) > 0),
    ]

    md = []
    md.append("# AI Product Ops: De Modelo a Sistema — SDD\n")
    md.append(f"- Fecha: **{today}**\n")

    md.append("## 1. Objetivo\n")
    md.append(state.get("sdd_goal", "Definir un sistema IA operable, medible y gobernable, explicitando trade-offs."))
    md.append("\n")

    md.append("## 2. Trade-offs TI vs SI (simulación)\n")
    if sim:
        md.append(f"- Modelo/preset: **{sim.get('preset','(n/a)')}**\n")
        md.append(f"- Precio: **{sim.get('eur_por_1k_tokens','?')} €/1k tokens**\n")
        md.append(f"- Calidad (FCR): **{sim.get('fcr','?')}**\n")
        md.append(f"- Tickets: **{sim.get('tickets','?')}** — Tokens/ticket: **{sim.get('tokens_por_ticket','?')}**\n")
        md.append(f"- Coste TI: **{float(sim.get('coste_ti', 0)):.2f} €**\n")
        md.append(f"- Coste Operativo: **{float(sim.get('coste_operativo', 0)):.2f} €**\n")
        md.append(f"- Coste Total: **{float(sim.get('coste_total', 0)):.2f} €**\n")
    else:
        md.append("- (No se ejecutó el simulador)\n")
    md.append("\n")

    md.append("## 3. Diseño del flujo (Process & Tech)\n")
    if pipeline:
        md.append("Orden seleccionado:\n")
        for i, step in enumerate(pipeline, 1):
            md.append(f"{i}. {step}\n")
    else:
        md.append("- (No definido)\n")
    md.append("\n")

    md.append("## 4. Roles y responsabilidades (People)\n")
    if roles:
        for k, v in roles.items():
            md.append(f"- **{k}**: {v or '(pendiente)'}\n")
    else:
        md.append("- (No definidos)\n")
    md.append("\n")

    md.append("## 5. Métricas & Guardrails (Data & Policy)\n")
    md.append("### Métricas\n")
    md.append(f"- Outcome (Valor): **{metrics.get('outcome','(n/a)')}**\n")
    md.append(f"- Efficiency (Coste): **{metrics.get('efficiency','(n/a)')}**\n")
    md.append(f"- Safety (Riesgo): **{metrics.get('safety','(n/a)')}**\n")
    md.append("\n")

    md.append("### SLO / Umbrales\n")
    md.append(f"- Latencia p95 ≤ **{guardrails.get('slo_latencia_s','(n/a)')} s**\n")
    md.append(f"- Tasa alucinación máx ≤ **{guardrails.get('max_halluc_rate','(n/a)')}**\n")
    md.append("\n")

    md.append("## 6. Checklist de seguridad y gobernanza\n")
    for label, ok in checklist:
        box = "x" if ok else " "
        md.append(f"- [{box}] {label}\n")
    md.append("\n")

    md.append("## 7. Riesgos y mitigaciones (RAGA-lite)\n")
    md.append("- Riesgo: Optimización TI (€/tokens) destruye SI (retrabajo humano). Mitigación: operar por **coste total** + FCR.\n")
    md.append("- Riesgo: PII en logs/prompts. Mitigación: filtro PII + minimización + auditoría.\n")
    md.append("- Riesgo: Sin kill switch / sin HITL. Mitigación: control operativo (SRE/Owner) y escalado.\n")

    return "\n".join(md)


def _md_inline_to_html(text: str) -> str:
    # **bold** -> <b>bold</b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # escapado mínimo
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # re-inyecta <b> tras el escape
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    return text


def markdown_to_pdf_bytes(md: str) -> bytes:
    """
    Conversión básica Markdown->PDF (headings, bullets y párrafos).
    No pretende ser un render completo, pero sirve como entregable.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="SDD - AI Product Ops",
    )
    styles = getSampleStyleSheet()
    story = []
    bullet_acc = []

    def flush_bullets():
        nonlocal bullet_acc
        if bullet_acc:
            lf = ListFlowable(
                [ListItem(Paragraph(_md_inline_to_html(x), styles["BodyText"])) for x in bullet_acc],
                bulletType="bullet",
                leftIndent=14,
            )
            story.append(lf)
            story.append(Spacer(1, 8))
            bullet_acc = []

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line:
            flush_bullets()
            story.append(Spacer(1, 8))
            continue

        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_md_inline_to_html(line[2:]), styles["Title"]))
            story.append(Spacer(1, 10))
            continue

        if line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_md_inline_to_html(line[3:]), styles["Heading2"]))
            story.append(Spacer(1, 8))
            continue

        if line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(_md_inline_to_html(line[4:]), styles["Heading3"]))
            story.append(Spacer(1, 6))
            continue

        if line.startswith("- "):
            bullet_acc.append(line[2:])
            continue

        flush_bullets()
        story.append(Paragraph(_md_inline_to_html(line), styles["BodyText"]))
        story.append(Spacer(1, 6))

    flush_bullets()
    doc.build(story)
    return buf.getvalue()
