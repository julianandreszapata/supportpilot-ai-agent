"""Herramientas de negocio simuladas para el agente SupportPilot."""
from __future__ import annotations

from typing import Any

ORDERS: dict[str, dict[str, Any]] = {
    "DM-1001": {
        "order_id": "DM-1001",
        "status": "En preparación",
        "estimated_minutes": 18,
        "details": "El comercio está preparando el pedido.",
    },
    "DM-1002": {
        "order_id": "DM-1002",
        "status": "Entregado con demora",
        "estimated_minutes": 0,
        "details": "El pedido fue entregado 22 minutos después de la hora estimada.",
    },
    "DM-1003": {
        "order_id": "DM-1003",
        "status": "Cancelado",
        "estimated_minutes": 0,
        "details": "El pedido fue cancelado antes de la entrega.",
    },
    "DM-1004": {
        "order_id": "DM-1004",
        "status": "Repartidor asignado",
        "estimated_minutes": 12,
        "details": "Hay un repartidor asignado y el pedido está pendiente de recogida.",
    },
}

POLICIES: list[dict[str, Any]] = [
    {
        "id": "POL-01",
        "title": "Demoras en la entrega",
        "keywords": ["demora", "tarde", "retraso", "retrasado", "demorado", "entrega", "late", "delay"],
        "summary": "Si un pedido llega tarde, consulta el estado y la demora registrada. Una posible compensación requiere revisión según el caso; no se aprueba automáticamente.",
        "human_review": True,
    },
    {
        "id": "POL-02",
        "title": "Cancelaciones",
        "keywords": ["cancelar", "cancelación", "cancelado", "cancelacion", "anular"],
        "summary": "La posibilidad de cancelar depende de la etapa del pedido. Si el estado no permite determinarlo, transfiere el caso a un agente humano.",
        "human_review": True,
    },
    {
        "id": "POL-03",
        "title": "Artículos faltantes o incorrectos",
        "keywords": ["faltante", "falta", "incorrecto", "equivocado", "incompleto", "producto", "artículo", "articulo"],
        "summary": "Solicita únicamente la información necesaria para identificar el artículo. La compensación requiere validación humana.",
        "human_review": True,
    },
    {
        "id": "POL-04",
        "title": "Reembolsos y compensaciones",
        "keywords": ["reembolso", "devolución", "devolver", "dinero", "compensación", "compensacion", "cobro", "pago"],
        "summary": "No se ejecutan reembolsos automáticamente en esta demo. Las solicitudes se registran como pendientes de revisión humana.",
        "human_review": True,
    },
    {
        "id": "POL-05",
        "title": "Seguridad alimentaria o reacción alérgica",
        "keywords": ["alergia", "alérgica", "alergica", "reacción", "reaccion", "intoxicación", "intoxicacion", "seguridad"],
        "summary": "Escala inmediatamente el caso a una persona. No intentes diagnosticar ni resolver automáticamente un posible riesgo de salud.",
        "human_review": True,
    },
]


def get_order_status(order_id: str) -> dict[str, Any]:
    """Returns an order from the fictitious demo dataset."""
    normalized_id = order_id.strip().upper()
    order = ORDERS.get(normalized_id)
    if not order:
        return {
            "status": "not_found",
            "order_id": normalized_id,
            "message": "No se encontró el pedido en el conjunto de datos de demostración.",
        }
    return {"status": "found", "order": order, "simulated_data": True}


def search_support_policy(query: str) -> dict[str, Any]:
    """Searches a tiny local policy catalogue by keyword; this is not vector RAG."""
    normalized = query.casefold()
    matches = []
    for policy in POLICIES:
        score = sum(1 for keyword in policy["keywords"] if keyword.casefold() in normalized)
        if score:
            matches.append({
                "id": policy["id"],
                "title": policy["title"],
                "summary": policy["summary"],
                "human_review": policy["human_review"],
                "score": score,
            })
    matches.sort(key=lambda item: item["score"], reverse=True)
    if not matches:
        return {
            "status": "no_match",
            "message": "No hay una política coincidente en la base de demostración. Se recomienda revisión humana.",
            "human_review": True,
            "matches": [],
        }
    return {"status": "matched", "matches": matches[:3], "simulated_data": True}


def create_compensation_request(order_id: str, reason: str, sequence: int = 1) -> dict[str, Any]:
    """Creates only a simulated request; never transfers money or refunds a payment."""
    normalized_id = order_id.strip().upper()
    if normalized_id not in ORDERS:
        return {
            "status": "not_created",
            "order_id": normalized_id,
            "message": "No se creó la solicitud porque el pedido no existe en la demo.",
            "financial_action_executed": False,
            "audit_note": "Compensación bloqueada: pedido no encontrado.",
        }
    return {
        "status": "pending_human_review",
        "request_id": f"COMP-{sequence:04d}",
        "order_id": normalized_id,
        "reason": reason.strip(),
        "message": "Solicitud simulada registrada. Requiere aprobación de un agente humano.",
        "financial_action_executed": False,
        "audit_note": "Solicitud simulada; no se emitió pago, crédito ni reembolso.",
    }


def transfer_to_human(reason: str, order_id: str = "", sequence: int = 1) -> dict[str, Any]:
    """Creates a fake handoff ticket for demonstration purposes."""
    normalized_id = order_id.strip().upper()
    return {
        "status": "handoff_created",
        "ticket_id": f"HUM-{sequence:04d}",
        "order_id": normalized_id or None,
        "reason": reason.strip(),
        "message": "Se creó un ticket de transferencia simulado. No se notificó a un agente real.",
        "audit_note": "Handoff ficticio para demostrar escalamiento.",
    }


def execute_tool(name: str, args: dict[str, Any], sequence: int = 1) -> dict[str, Any]:
    """Allow-listed tool dispatcher. Unknown tools are rejected."""
    try:
        if name == "get_order_status":
            return get_order_status(str(args.get("order_id", "")))
        if name == "search_support_policy":
            return search_support_policy(str(args.get("query", "")))
        if name == "create_compensation_request":
            return create_compensation_request(
                str(args.get("order_id", "")), str(args.get("reason", "")), sequence
            )
        if name == "transfer_to_human":
            return transfer_to_human(
                str(args.get("reason", "")), str(args.get("order_id", "")), sequence
            )
        return {
            "status": "rejected",
            "message": "La herramienta solicitada no está permitida.",
            "audit_note": "Intento de ejecución de una herramienta no incluida en la lista permitida.",
        }
    except (TypeError, ValueError) as exc:
        return {
            "status": "error",
            "message": "Los argumentos de la herramienta no son válidos.",
            "audit_note": type(exc).__name__,
        }
