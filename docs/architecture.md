# Arquitectura técnica

```text
Usuario
  |
  v
Interfaz de chat (Streamlit)
  |
  v
Orquestador del agente (app.py)
  |-- Gemini API: interpreta la solicitud y elige una herramienta
  |-- get_order_status: consulta pedidos ficticios
  |-- search_support_policy: búsqueda por palabras clave en políticas locales
  |-- create_compensation_request: registra una solicitud pendiente (sin dinero real)
  |-- transfer_to_human: genera un ticket ficticio
  |
  v
Registro de auditoría visible en la interfaz
```

## Decisiones y límites

- Las llamadas a herramientas se ejecutan en backend con una lista permitida.
- La demo no se conecta a Rappi, WhatsApp, un contact center ni servicios de pagos.
- Las compensaciones no mueven dinero y requieren revisión humana.
- Los datos de pedidos y políticas son sintéticos.
- La búsqueda inicial es por palabras clave; no debe describirse como RAG vectorial.
- La aplicación limita el número de rondas de llamada a herramientas para evitar bucles.

## Siguiente evolución

1. Extraer herramientas del prototipo hacia una API REST con FastAPI.
2. Implementar RAG real con embeddings y PostgreSQL + pgvector/Supabase.
3. Añadir autenticación, autorización por usuario, límites de tasa y validación de entradas.
4. Agregar evaluación de conversaciones y métricas: resolución, transferencia, latencia, coste y calidad.
5. Exponer herramientas mediante un servidor MCP local o remoto, con autorización explícita.
6. Integrar un proveedor de chat/WhatsApp únicamente cuando se disponga de credenciales y consentimiento apropiados.
