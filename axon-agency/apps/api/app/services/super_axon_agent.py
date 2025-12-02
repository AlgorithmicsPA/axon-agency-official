"""Super Axon Agent - Servicio centralizado para el agente principal de AXON Agency.

Este servicio maneja:
- Prompt de sistema especializado
- Detección de modos de trabajo (estratega/implementador/tutor)
- Preparación de mensajes con contexto
"""

import logging
import re
from typing import Literal, Optional
from typing import AsyncIterator

logger = logging.getLogger(__name__)

# ============================================================================
# PROMPT DE SISTEMA DEL SUPER AXON AGENT
# ============================================================================

SUPER_AXON_SYSTEM_PROMPT = """Eres el **Super Axon Agent**, el agente principal de la plataforma AXON Agency.

**TU ROL:**
- Trabajas para Federico, fundador de la agencia, que usa Axon 88 como cerebro local.
- Tu misión es ayudar a construir, operar y mejorar agencias de IA para:
  - Escuelas (6–18 años)
  - Notarías
  - Inmobiliarias
  - Otros negocios que usan automatizaciones (WhatsApp, n8n, Telegram, etc.)

**TU ESTILO:**
- Hablas en español neutro, profesional y cercano.
- Puedes usar tono amigable, pero NUNCA romántico ni demasiado informal.
- Explicas las cosas con claridad, con pasos y bullets.
- Cuando das planes o estrategias, eres concreto: quién, qué, cuándo, cómo.

**TU CONOCIMIENTO DEL CONTEXTO:**
- Sabes que Axon Agency es un panel con módulos:
  - Campañas, Publicaciones, Autopilots IA, Conversaciones, Analíticas, Redes Conectadas, etc.
- Axon 88 es el servidor local (Jetson AGX Orin) donde corre este backend.
- Hay integraciones con:
  - WhatsApp (via autopilots), Telegram, n8n, RAG interno, etc. (algunas pueden estar en modo stub).
- No inventas integraciones que no existan; hablas en futuro ("podemos conectar…") si algo aún no está implementado.

**ESTRUCTURA DE TUS RESPUESTAS:**
Siempre que sea posible, contesta con esta estructura:
1) **Contexto breve** - Resumen de lo que entiendes
2) **Plan o respuesta principal** - En bullets o pasos numerados
3) **Siguientes acciones concretas** - 1–3 acciones muy claras

**TUS LÍMITES:**
- No das consejos legales o médicos definitivos; marcas que son orientativos.
- No inventas datos específicos de terceros; usas ejemplos genéricos.

**MODOS DE TRABAJO:**
- **ESTRATEGA**: Piensas en planes, estrategias, visión de negocio, objetivos a largo plazo.
- **IMPLEMENTADOR**: Piensas en pasos técnicos, código, flujos, integraciones concretas.
- **TUTOR**: Explicas conceptos, enseñas paso a paso, aclaras dudas conceptuales.

Responde siempre en español, con claridad y estructura."""


# ============================================================================
# PROMPTS ADICIONALES POR MODO
# ============================================================================

MODE_PROMPTS = {
    "estratega": """
En este mensaje, actúa como **ESTRATEGA DE AGENCIA**:
- Piensa en planes de negocio, estrategias de mercado, objetivos a largo plazo.
- Considera el contexto del cliente (escuela, notaría, inmobiliaria, etc.).
- Propón estrategias concretas con pasos claros y métricas de éxito.
- Enfócate en el "qué" y el "por qué", no tanto en el "cómo técnico".
""",
    "implementador": """
En este mensaje, actúa como **IMPLEMENTADOR TÉCNICO**:
- Piensa en pasos técnicos concretos, código, flujos, integraciones.
- Sé específico: qué archivos, qué endpoints, qué configuraciones.
- Proporciona código o pseudocódigo cuando sea relevante.
- Enfócate en el "cómo técnico" paso a paso.
""",
    "tutor": """
En este mensaje, actúa como **TUTOR / MAESTRO**:
- Explica conceptos de forma clara y didáctica.
- Usa ejemplos concretos relacionados con AXON Agency.
- Desglosa conceptos complejos en pasos simples.
- Responde preguntas de forma educativa y comprensiva.
"""
}


# ============================================================================
# DETECCIÓN DE MODO
# ============================================================================

def detect_mode(user_message: str) -> Literal["estratega", "implementador", "tutor", "auto"]:
    """Detecta el modo de trabajo basado en tags o contenido del mensaje.
    
    Tags reconocidos:
    - #estratega, #plan, #ideas, #estrategia → estratega
    - #implementador, #pasos, #codigo, #flujo, #tecnico → implementador
    - #tutor, #explica, #pasoapaso, #enseña → tutor
    
    Si no hay tags, infiere del contenido:
    - Palabras como "estrategia", "plan", "objetivo" → estratega
    - Palabras como "código", "pasos", "implementar", "configurar" → implementador
    - Palabras como "explica", "qué es", "cómo funciona" → tutor
    """
    message_lower = user_message.lower()
    
    # Detección por tags
    if re.search(r'#(estratega|plan|ideas|estrategia)', message_lower):
        return "estratega"
    if re.search(r'#(implementador|pasos|codigo|flujo|tecnico)', message_lower):
        return "implementador"
    if re.search(r'#(tutor|explica|pasoapaso|enseña)', message_lower):
        return "tutor"
    
    # Inferencia por contenido
    estratega_keywords = ["estrategia", "plan", "objetivo", "visión", "negocio", "mercado", "cliente"]
    implementador_keywords = ["código", "codigo", "pasos", "implementar", "configurar", "instalar", "conectar", "endpoint", "api"]
    tutor_keywords = ["explica", "qué es", "que es", "cómo funciona", "como funciona", "enseña", "aprende"]
    
    estratega_score = sum(1 for kw in estratega_keywords if kw in message_lower)
    implementador_score = sum(1 for kw in implementador_keywords if kw in message_lower)
    tutor_score = sum(1 for kw in tutor_keywords if kw in message_lower)
    
    if estratega_score > implementador_score and estratega_score > tutor_score:
        return "estratega"
    if implementador_score > tutor_score:
        return "implementador"
    if tutor_score > 0:
        return "tutor"
    
    return "auto"


# ============================================================================
# PREPARACIÓN DE MENSAJES
# ============================================================================

def prepare_messages(
    user_messages: list[dict],
    mode: Optional[Literal["estratega", "implementador", "tutor", "auto"]] = None
) -> list[dict]:
    """Prepara los mensajes para el LLM con el prompt de sistema y modo.
    
    Args:
        user_messages: Lista de mensajes del usuario (formato OpenAI)
        mode: Modo de trabajo. Si es None o "auto", se detecta automáticamente.
    
    Returns:
        Lista de mensajes con el prompt de sistema y modo aplicado.
    """
    # Detectar modo si no se especifica
    if mode is None or mode == "auto":
        # Tomar el último mensaje del usuario para detectar el modo
        last_user_message = None
        for msg in reversed(user_messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        if last_user_message:
            mode = detect_mode(last_user_message)
        else:
            mode = "auto"
    
    # Construir mensajes con prompt de sistema
    messages = [
        {
            "role": "system",
            "content": SUPER_AXON_SYSTEM_PROMPT
        }
    ]
    
    # Añadir prompt de modo si no es "auto"
    if mode != "auto" and mode in MODE_PROMPTS:
        messages.append({
            "role": "system",
            "content": MODE_PROMPTS[mode]
        })
        logger.info(f"Super Axon Agent: Modo '{mode}' detectado/aplicado")
    
    # Añadir mensajes del usuario (limpiar tags si existen)
    for msg in user_messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            # Remover tags del contenido para que no aparezcan en la respuesta
            content = re.sub(r'#\w+\s*', '', content).strip()
            messages.append({
                "role": "user",
                "content": content
            })
        else:
            # Mantener otros mensajes (assistant, etc.) tal cual
            messages.append(msg)
    
    return messages


# ============================================================================
# FUNCIÓN PRINCIPAL PARA STREAMING
# ============================================================================

async def super_axon_chat_stream(
    user_messages: list[dict],
    provider_func: callable,
    mode: Optional[Literal["estratega", "implementador", "tutor", "auto"]] = None,
    model: Optional[str] = None,
    images: Optional[list] = None
) -> AsyncIterator[str]:
    """Stream de chat del Super Axon Agent con prompt de sistema y modo aplicado.
    
    Args:
        user_messages: Lista de mensajes del usuario
        provider_func: Función del provider (openai_chat_stream, gemini_chat_stream, etc.)
        mode: Modo de trabajo (opcional, se detecta automáticamente si no se especifica)
        model: Modelo a usar (se pasa al provider)
        images: Imágenes para Gemini (se pasa al provider)
    
    Yields:
        Chunks de texto del stream
    """
    # Preparar mensajes con prompt de sistema y modo
    prepared_messages = prepare_messages(user_messages, mode)
    
    # Llamar al provider con los mensajes preparados
    # Construir kwargs según el provider
    kwargs = {}
    if model:
        kwargs["model"] = model
    if images is not None:
        kwargs["images"] = images
    
    async for chunk in provider_func(prepared_messages, **kwargs):
        yield chunk

