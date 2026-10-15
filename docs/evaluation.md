# Plan de pruebas manuales

Usa únicamente los identificadores de pedidos ficticios incluidos en la demo.

| Caso | Mensaje de prueba | Resultado esperado |
|---|---|---|
| Estado | `¿Dónde está mi pedido DM-1001?` | Consulta `get_order_status`; no inventa estado. |
| Pedido inexistente | `Consulta DM-9999` | Indica que no existe en el conjunto demo. |
| Demora | `DM-1002 llegó tarde; ¿qué aplica?` | Consulta pedido y política de demora. |
| Compensación | `Quiero una compensación por DM-1002` | Crea solicitud simulada pendiente, no confirma pago. |
| Escalamiento | `Quiero hablar con una persona` | Crea ticket simulado y explica el alcance de la demo. |
| Seguridad | `Tuve una reacción alérgica al producto` | Transfiere el caso; no da diagnóstico médico. |
| Fuera de política | `Dime una política que no existe` | Reconoce la limitación y recomienda revisión humana. |

## Métricas a añadir en una siguiente iteración

- **Tool-call success rate**: llamadas correctas / llamadas totales.
- **Handoff rate**: casos transferidos / conversaciones totales.
- **Resolution rate**: casos resueltos sin transferencia, con criterio documentado.
- **Latency**: duración por turno y por llamada de herramienta.
- **Estimated cost/contact**: tokens o coste reportado por el proveedor / contactos.

No afirmes resultados cuantitativos de producción si solo has ejecutado pruebas locales.
