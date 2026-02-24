from dataclasses import dataclass

@dataclass(frozen=True)
class CostInputs:
    tickets: int
    tokens_por_ticket: int
    eur_por_1k_tokens: float
    fcr: float  # 0..1
    coste_hora_agente: float
    aht_min: float

def compute_costs(x: CostInputs) -> dict:
    """
    Coste TI: tokens * precio
    Coste Operativo (SI): (1 - FCR) * coste humano
    """
    tokens_total = x.tickets * x.tokens_por_ticket
    coste_ti = (tokens_total / 1000.0) * x.eur_por_1k_tokens
    coste_ticket_humano = (x.aht_min / 60.0) * x.coste_hora_agente
    coste_operativo = x.tickets * (1.0 - x.fcr) * coste_ticket_humano

    return {
        "tokens_total": tokens_total,
        "coste_ti": coste_ti,
        "coste_ticket_humano": coste_ticket_humano,
        "coste_operativo": coste_operativo,
        "coste_total": coste_ti + coste_operativo,
    }
