import { NextRequest, NextResponse } from "next/server";

const VERIFY_TOKEN =
  process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN ?? "axon88webhook";

/**
 * ============================================================
 * WHATSAPP WEBHOOK BRAIN
 * ============================================================
 * 
 * Recibe mensajes desde WhatsApp Cloud API (Meta).
 * Llama a OpenAI (gpt-4o-mini) para generar respuesta inteligente.
 * Envía la respuesta de vuelta al usuario usando WHATSAPP_CLOUD_ACCESS_TOKEN.
 * 
 * El token se obtiene desde process.env y puede definirse en:
 * - Replit Secrets (recomendado para producción)
 * - apps/web/.env.local (desarrollo local)
 * 
 * Configuración de variables:
 * 1. OPENAI_API_KEY → para generar respuestas
 * 2. WHATSAPP_CLOUD_ACCESS_TOKEN → para enviar mensajes
 * 3. WHATSAPP_WEBHOOK_VERIFY_TOKEN → para verificar webhook (por defecto: "axon88webhook")
 * 
 * ============================================================
 */

/**
 * Generate AI reply using OpenAI Chat Completions
 */
async function generateReply(userMessage: string): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    console.error("[WhatsApp Brain] ❌ OPENAI_API_KEY not set");
    return "Lo siento, en este momento no puedo responder. Inténtalo más tarde.";
  }

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content:
              "Eres el asistente oficial de AXON AGENCY. Hablas en un tono cercano y profesional, en español latinoamericano. Ayudas a prospectos y clientes a entender qué hace la agencia (automatización con IA, agentes, WhatsApp sales agent, etc.) y a reservar una llamada o dejar sus datos. Sé breve, claro y útil. No inventes datos técnicos específicos (precios, URLs) si no te los dan.",
          },
          {
            role: "user",
            content: userMessage,
          },
        ],
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[WhatsApp Brain] ❌ OpenAI API error:", errorText);
      return "Lo siento, tuve un problema para procesar tu mensaje. ¿Podrías intentarlo de nuevo?";
    }

    const data = await response.json();
    const reply =
      data.choices?.[0]?.message?.content?.trim() ??
      "Gracias por tu mensaje. En un momento te responderemos.";

    console.log("[WhatsApp Brain] 🧠 OpenAI reply generated:", reply);
    return reply;
  } catch (error) {
    console.error("[WhatsApp Brain] ❌ OpenAI request error:", error);
    return "Lo siento, en este momento no puedo responder. Inténtalo más tarde.";
  }
}

/**
 * Send message via WhatsApp Cloud API
 */
async function sendWhatsAppMessage(
  phoneNumberId: string,
  to: string,
  text: string
): Promise<void> {
  const token = process.env.WHATSAPP_CLOUD_ACCESS_TOKEN;
  
  // DEBUG: Log token availability (length only, for security)
  console.log(
    "[ENV DEBUG] WHATSAPP_CLOUD_ACCESS_TOKEN length:",
    token ? token.length : "NONE"
  );
  
  if (!token) {
    console.error("[WhatsApp Brain] ❌ WHATSAPP_CLOUD_ACCESS_TOKEN not set");
    console.error(
      "[WhatsApp Brain] ⚠️ Configure WHATSAPP_CLOUD_ACCESS_TOKEN in Replit Secrets or apps/web/.env.local"
    );
    return;
  }

  try {
    const url = `https://graph.facebook.com/v20.0/${phoneNumberId}/messages`;

    const payload = {
      messaging_product: "whatsapp",
      to,
      type: "text",
      text: {
        body: text,
      },
    };

    // DEBUG: Log exact payload being sent to WhatsApp
    console.log(
      "[WhatsApp Brain] 🔍 Payload to WhatsApp:",
      JSON.stringify(payload, null, 2)
    );

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(
        "[WhatsApp Brain] ❌ Error sending message to WhatsApp:",
        errorText
      );
    } else {
      const responseData = await res.json();
      console.log(
        "[WhatsApp Brain] ✅ WhatsApp message sent successfully:",
        responseData
      );
    }
  } catch (error) {
    console.error("[WhatsApp Brain] ❌ WhatsApp API request error:", error);
  }
}

/**
 * GET /api/webhooks/whatsapp
 * Webhook verification endpoint for WhatsApp Cloud API
 * Meta sends this request to verify the webhook URL during setup
 */
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const mode = searchParams.get("hub.mode");
  const token = searchParams.get("hub.verify_token");
  const challenge = searchParams.get("hub.challenge");

  if (mode === "subscribe" && token === VERIFY_TOKEN && challenge) {
    console.log("[WhatsApp Webhook] ✅ Verification successful");
    return new NextResponse(challenge, { status: 200 });
  }

  console.warn(
    "[WhatsApp Webhook] ❌ Verification failed",
    {
      mode,
      tokenValid: token === VERIFY_TOKEN,
      hasChallenge: !!challenge,
    }
  );

  return new NextResponse("Verification failed", { status: 403 });
}

/**
 * POST /api/webhooks/whatsapp
 * 
 * Main message processing handler
 * - Receives webhook payload from Meta WhatsApp Cloud API
 * - Extracts message content
 * - Generates AI reply via OpenAI
 * - Sends response back to user via WhatsApp
 * - Always returns 200 (failures logged internally)
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log(
      "[WhatsApp Webhook] 📨 Raw payload received:",
      JSON.stringify(body, null, 2)
    );

    // Extract webhook payload structure
    const entry = body.entry?.[0];
    const change = entry?.changes?.[0];
    const value = change?.value;
    const messages = value?.messages;
    const message = messages?.[0];
    const metadata = value?.metadata;

    // Extract message details
    const from = message?.from;
    const msgId = message?.id;
    const text = message?.text?.body || "";
    const phoneNumberId = metadata?.phone_number_id;

    // Validate required fields
    if (!from || !text) {
      console.warn(
        "[WhatsApp Webhook] ⚠️ Ignoring webhook - missing from or text",
        { from, hasText: !!text }
      );
      return NextResponse.json(
        { status: "ignored", reason: "missing_from_or_text" },
        { status: 200 }
      );
    }

    if (!phoneNumberId) {
      console.warn(
        "[WhatsApp Webhook] ⚠️ Ignoring webhook - missing phoneNumberId"
      );
      return NextResponse.json(
        { status: "ignored", reason: "missing_phoneNumberId" },
        { status: 200 }
      );
    }

    console.log(
      "[WhatsApp Webhook] 🎯 Processing message",
      { from, msgId, textLength: text.length, phoneNumberId }
    );

    // Generate AI reply
    const replyText = await generateReply(text);

    // Send response back to user
    await sendWhatsAppMessage(phoneNumberId, from, replyText);

    console.log(
      "[WhatsApp Webhook] ✅ Message processed successfully",
      { from, msgId }
    );

    return NextResponse.json(
      { status: "ok", processed: true, messageId: msgId },
      { status: 200 }
    );
  } catch (error) {
    console.error("[WhatsApp Webhook] ❌ Error processing webhook:", error);
    // Always return 200 to Meta even on errors
    return NextResponse.json(
      { status: "ok", processed: false, error: "internal_error" },
      { status: 200 }
    );
  }
}

/**
 * ============================================================
 * PASOS PARA ACTIVAR EL CEREBRO DE WHATSAPP
 * ============================================================
 * 
 * 1) Obtener tokens:
 *    - OPENAI_API_KEY: https://platform.openai.com/account/api-keys
 *    - WHATSAPP_CLOUD_ACCESS_TOKEN: https://developers.facebook.com/apps
 *      → Selecciona tu app → WhatsApp → Configuration → Permanent Access Token
 * 
 * 2) Opción A - Desarrollo local:
 *    - Abre apps/web/.env.local
 *    - Sustituye "PEGAR_AQUI_MI_API_KEY_DE_OPENAI" por tu OpenAI key
 *    - Sustituye "PEGAR_AQUI_MI_TOKEN_DE_WHATSAPP_CLOUD" por tu WhatsApp token
 *    - Guarda el archivo
 * 
 * 3) Opción B - Producción (Replit):
 *    - Ve a Secrets de Replit (panel derecho del IDE)
 *    - Crea las variables OPENAI_API_KEY y WHATSAPP_CLOUD_ACCESS_TOKEN
 *    - Reinicia el proyecto (Ctrl+Shift+P → "Restart project")
 * 
 * 4) Prueba:
 *    - Envía un mensaje de prueba por WhatsApp
 *    - Revisa la consola del servidor:
 *      "[ENV DEBUG] WHATSAPP_CLOUD_ACCESS_TOKEN length: XXX" (debe mostrar un número)
 *      "[WhatsApp Brain] 🧠 OpenAI reply generated: ..." (respuesta de OpenAI)
 *      "[WhatsApp Brain] ✅ WhatsApp message sent successfully: ..." (confirmación de envío)
 * 
 * ============================================================
 */
