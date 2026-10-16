# SupportPilot — AI Support Agent

**Demo de portafolio:** agente de soporte conversacional con Gemini function calling, herramientas backend simuladas, registro de auditoría y transferencia a una persona.

> Esta es una demostración educativa independiente. No está afiliada a ninguna compañia, no se conecta a sus sistemas y no ejecuta pagos, devoluciones ni compensaciones reales. Todos los pedidos y políticas son ficticios.

## Qué demuestra

- Integración de un LLM mediante la Gemini API.
- Function calling: el modelo puede solicitar consultas y acciones limitadas desde el backend.
- Herramientas de negocio con lista permitida y respuestas estructuradas.
- Búsqueda inicial de políticas por palabras clave.
- Solicitud de compensación simulada, pendiente de revisión humana.
- Handoff de soporte simulado con ticket y auditoría.
- Pruebas unitarias de la lógica de negocio.

## Arquitectura

Consulta [`docs/architecture.md`](docs/architecture.md) para ver componentes, límites y evolución propuesta.

## Tecnologías

- Python
- Streamlit
- Google GenAI SDK (`google-genai`)
- Gemini API
- `python-dotenv`
- `unittest`

## Requisitos

1. Python 3.11 o superior recomendado.
2. Una clave API de Google AI Studio. Revisa el modelo disponible, cuotas y condiciones de uso de tu cuenta.
3. Git y una cuenta de GitHub si vas a publicar el proyecto.

## Ejecutar en Windows

Abre una terminal de PowerShell en la carpeta del proyecto.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y reemplaza `PEGA_AQUI_TU_CLAVE` por la clave obtenida en Google AI Studio. No compartas la clave ni la subas a GitHub.

```powershell
streamlit run app.py
```

Streamlit abrirá una dirección local, normalmente `http://localhost:8501`.

### Ejecutar las pruebas

En la misma terminal:

```powershell
python -m unittest discover -s tests -v
```

## Casos de prueba sugeridos

- `¿Dónde está mi pedido DM-1002?`
- `Mi pedido llegó tarde, ¿qué política aplica?`
- `Solicito una compensación para DM-1002`
- `Quiero hablar con una persona`
- `El producto me causó una reacción alérgica`

Los casos detallados se encuentran en [`docs/evaluation.md`](docs/evaluation.md).

## Publicar en GitHub

1. Crea un repositorio público llamado `supportpilot-ai-agent`.
2. Sube todos los archivos del proyecto excepto `.env` y `.streamlit/secrets.toml`.
3. Verifica la lista de archivos publicados. El `.gitignore` evita añadir claves locales, pero revisa antes de hacer push.
4. En el README del repositorio, confirma que el nombre, las instrucciones y las limitaciones sean claros.

## Desplegar en Streamlit Community Cloud

1. Inicia sesión en [Streamlit Community Cloud](https://share.streamlit.io/) con GitHub.
2. Selecciona **Create app** y el repositorio `supportpilot-ai-agent`.
3. Define `app.py` como archivo de entrada.
4. En **Advanced settings / Secrets**, agrega, en formato TOML:

```toml
GEMINI_API_KEY = "TU_CLAVE_API"
GEMINI_MODEL = "gemini-3.8-flash"
```

5. Despliega y verifica el chat desde el enlace generado. Nunca escribas la clave API en el código o en el README.

Si el modelo predeterminado no aparece disponible para tu cuenta, consulta los modelos habilitados en la documentación de Gemini y cambia `GEMINI_MODEL` en `.env` o en los secretos del despliegue.

## Seguridad y alcance

- No introduzcas información real de clientes ni datos personales.
- En el nivel gratuito de una API, las condiciones sobre uso de datos pueden diferir de las de un plan pagado. Revisa la política vigente del proveedor antes de enviar datos.
- Nunca presentes estas funciones simuladas como integraciones productivas.
- La búsqueda de políticas usa palabras clave y **no es un sistema RAG vectorial** todavía.
- La demo no implementa MCP, WhatsApp, Amazon Connect, autenticación de usuarios ni observabilidad productiva.

## Roadmap

1. API REST con FastAPI y pruebas de integración.
2. RAG con embeddings, documentos versionados y Supabase/PostgreSQL + pgvector.
3. Evaluación automática de respuestas y un conjunto de conversaciones etiquetadas.
4. Métricas de calidad, handoff, latencia y coste.
5. MCP con herramientas explícitamente autorizadas.
6. Despliegue con controles de seguridad y monitorización.

## Autor

**Julian Zapata** — Software Engineer | Backend, APIs e Integraciones | AI-assisted development

Ajusta esta descripción si deseas reflejar exactamente tu perfil actual.
