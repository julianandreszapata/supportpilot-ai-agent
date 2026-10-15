"""SupportPilot: demo de agente de soporte con Gemini function calling."""
from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st
from google import genai
from dotenv import load_dotenv

from support_tools import execute_tool

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
SYSTEM_PROMPT = """
Eres SupportPilot, un asistente de soporte de una tienda ficticia llamada DemoMarket.
Responde siempre en español, de forma breve, clara, empática y profesional.

Reglas obligatorias:
- Los pedidos y políticas son datos simulados para una demostración; nunca afirmes que consultaste un sistema real.
- Cuando la pregunta requiera datos de un pedido, usa get_order_status. No inventes el estado ni los tiempos.
- Cuando respondas sobre cancelaciones, demoras, artículos faltantes o reembolsos, consulta search_support_policy.
- Si el usuario solicita una compensación, usa create_compensation_request. Esta herramienta solo crea una solicitud simulada pendiente de revisión; nunca afirmes que el dinero fue devuelto o que la compensación fue aprobada.
- Escala a un humano con transfer_to_human si el usuario lo pide, hay un posible problema de seguridad/alergia, el caso es sensible, faltan datos importantes o la política indica revisión humana.
- No solicites contraseñas, números completos de tarjetas ni datos personales sensibles.
- Si no puedes resolver el caso con las herramientas disponibles, dilo y ofrece transferirlo a un agente humano.
- No inventes políticas, acciones completadas ni resultados de herramientas.
""".strip()

TOOLS = [
    {
        "type": "function",
        "name": "get_order_status",
        "description": "Consulta el estado de un pedido ficticio de DemoMarket por su identificador.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Identificador del pedido, por ejemplo DM-1002"}
            },
            "required": ["order_id"],
        },
    },
    {
        "type": "function",
        "name": "search_support_policy",
        "description": "Busca políticas ficticias de soporte relacionadas con la consulta del usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Tema o pregunta sobre la política de soporte"}
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "create_compensation_request",
        "description": "Crea una solicitud de compensación simulada, pendiente de aprobación humana; no realiza pagos ni reembolsos.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Identificador del pedido"},
                "reason": {"type": "string", "description": "Motivo de la solicitud"},
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "type": "function",
        "name": "transfer_to_human",
        "description": "Crea un ticket ficticio para transferir el caso a una persona de soporte.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "Motivo de la transferencia"},
                "order_id": {"type": "string", "description": "Identificador del pedido si se conoce"},
            },
            "required": ["reason"],
        },
    },
]


def get_api_key() -> str | None:
    """Lee la clave de entorno local o los secretos de Streamlit Cloud."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        return None


def _field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def ask_agent(
    client: genai.Client,
    question: str,
    previous_interaction_id: str | None,
    audit_log: list[dict[str, Any]],
) -> tuple[str, str | None]:
    """Run Gemini and execute only the explicitly allow-listed demo tools."""
    if previous_interaction_id:
        interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=previous_interaction_id,
            input=question,
            tools=TOOLS,
        )
    else:
        first_prompt = f"{SYSTEM_PROMPT}\n\nConsulta del usuario: {question}"
        interaction = client.interactions.create(
            model=MODEL,
            input=first_prompt,
            tools=TOOLS,
        )

    # Limitamos las rondas para evitar bucles de llamadas a herramientas.
    for _ in range(4):
        steps = list(_field(interaction, "steps", []) or [])
        calls = [step for step in steps if _field(step, "type") == "function_call"]
        if not calls:
            break

        function_results: list[dict[str, Any]] = []
        for call in calls:
            name = str(_field(call, "name", ""))
            raw_args = _field(call, "arguments", {}) or {}
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = dict(raw_args) if isinstance(raw_args, dict) else {}

            sequence = len(audit_log) + 1
            result = execute_tool(name, args, sequence=sequence)
            audit_log.append(
                {
                    "event": sequence,
                    "tool": name,
                    "arguments": args,
                    "result_status": result.get("status", "unknown"),
                    "note": result.get("audit_note", ""),
                }
            )
            call_id = _field(call, "id")
            function_results.append(
                {
                    "type": "function_result",
                    "name": name,
                    "call_id": call_id,
                    "result": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                }
            )

        interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=_field(interaction, "id"),
            input=function_results,
            tools=TOOLS,
        )

    answer = _field(interaction, "output_text", "")
    if not answer:
        answer = "No pude generar una respuesta final. Puedes intentar de nuevo o solicitar transferencia a un agente humano."
    return str(answer), _field(interaction, "id")


st.set_page_config(page_title="SupportPilot · AI Support Agent", page_icon="🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

with st.sidebar:
    st.title("SupportPilot")
    st.caption("AI Support Agent · Demo técnica de portafolio")
    st.info("Demo educativa con pedidos y políticas ficticias. No está afiliada a Rappi ni ejecuta reembolsos reales.")
    st.markdown("**Prueba con:**")
    st.markdown("- `¿Dónde está mi pedido DM-1002?`\n- `Mi pedido llegó tarde, ¿qué política aplica?`\n- `Solicito una compensación para DM-1002`\n- `Quiero hablar con una persona`\n- `El producto me causó una reacción alérgica` ")
    if st.button("Nuevo chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.interaction_id = None
        st.session_state.audit_log = []
        st.rerun()
    st.divider()
    st.markdown("**Actividad de herramientas**")
    st.metric("Llamadas registradas", len(st.session_state.audit_log))
    with st.expander("Ver auditoría", expanded=False):
        if st.session_state.audit_log:
            st.json(st.session_state.audit_log)
        else:
            st.caption("Todavía no se han ejecutado herramientas.")

st.title("🤖 SupportPilot — Agente de soporte con IA")
st.write("Consulta pedidos de ejemplo, busca políticas de soporte y genera solicitudes simuladas con trazabilidad.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("tools"):
            with st.expander("Herramientas utilizadas"):
                st.json(message["tools"])

prompt = st.chat_input("Escribe una consulta de soporte…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_key = get_api_key()
        if not api_key:
            answer = "Falta configurar la clave GEMINI_API_KEY. Sigue las instrucciones del README y vuelve a ejecutar la aplicación."
            st.warning(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            try:
                client = genai.Client(api_key=api_key)
                starting_count = len(st.session_state.audit_log)
                with st.spinner("Analizando la consulta y consultando herramientas si hace falta…"):
                    answer, new_interaction_id = ask_agent(
                        client=client,
                        question=prompt,
                        previous_interaction_id=st.session_state.interaction_id,
                        audit_log=st.session_state.audit_log,
                    )
                st.session_state.interaction_id = new_interaction_id
                st.markdown(answer)
                new_events = st.session_state.audit_log[starting_count:]
                if new_events:
                    with st.expander("Herramientas ejecutadas en este turno"):
                        st.json(new_events)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "tools": new_events}
                )
            except Exception as exc:  # mostramos un mensaje acotado sin imprimir credenciales
                answer = (
                    "No fue posible consultar el modelo. Verifica que tu clave sea válida, "
                    "que el modelo configurado esté disponible en tu cuenta y que tengas cuota de API. "
                    f"Detalle técnico: {type(exc).__name__}."
                )
                st.error(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
