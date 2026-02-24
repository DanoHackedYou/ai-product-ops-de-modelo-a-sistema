# AI Product Ops: De Modelo a Sistema (DSI · ITSM · SRE/Compliance)

App multipágina en **Streamlit** para diseñar y justificar un sistema de IA operable en producción:
- Trade-offs **TI vs SI** (coste tokens vs retrabajo humano)
- Diseño del flujo (Process & Tech)
- Ownership (People) + guardrails (SRE/Compliance)
- Reporte tipo **SDD** exportable a **Markdown** y **PDF**

## Estructura
- `app.py`: navegación multipágina con `st.Page` + `st.navigation`
- `pages/`: 4 pantallas (framework, simulador, wizard, auditoría/reporte)
- `utils/economics.py`: modelo de costes (TI + Operativo)
- `utils/reporting.py`: generación de SDD en Markdown y export PDF (simple)

## Ejecutar local
```bash
pip install -r requirements.txt
streamlit run app.py
