import { NextRequest, NextResponse } from "next/server";

const VERIFY_TOKEN =
  process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN ?? "axon88webhook";

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
 * Incoming message handler from WhatsApp Cloud API
 * Processes messages, status updates, and other webhook events
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log(
      "[WhatsApp Webhook] 📨 Message received:",
      JSON.stringify(body, null, 2)
    );

    // TODO: Add message processing logic here
    // - Extract message content
    // - Update conversation state
    // - Route to appropriate handler
    // - Send response if needed

    return NextResponse.json({ status: "ok" }, { status: 200 });
  } catch (error) {
    console.error("[WhatsApp Webhook] ❌ Error processing webhook:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to process webhook" },
      { status: 500 }
    );
  }
}
