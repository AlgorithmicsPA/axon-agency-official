"""WhatsApp Sales Agent Orchestrator - Full IntegraIA Template.

Complete orchestrator integrating 7 clients (MongoDB, OpenAI, Melvis, Tavily, 
LinkedIn, Stripe, Cal.com) in 10-step conversation flow.

10-Step Flow:
1. Webhook WhatsApp → receive message
2. Upsert user in MongoDB
3. Insert incoming message in messages collection
4. Load/create session from sessions collection
5. Get context conditionally (message history, RAG chunks, web search)
6. OpenAI call with structured output → JSON response
7. Parse actions (CREATE_OR_UPDATE_LEAD, ENRICH_LEAD, SUGGEST_CAL_LINK, CREATE_STRIPE_CHECKOUT)
8. Update session (currentStep, answers)
9. Insert outgoing message in messages collection
10. Send reply via WhatsApp

Usage:
    from app.templates.whatsapp_template_full_integraia import handle_whatsapp_webhook, sales_agent
    
    # At startup:
    await sales_agent.connect()
    
    # In webhook:
    reply = await handle_whatsapp_webhook(phone="+1234567890", message="Hola")
    
    # At shutdown:
    await sales_agent.disconnect()
"""

from typing import Optional, Dict
from loguru import logger

from app.integrations.mongodb_client import MongoDBClient, User, Message, Lead, Session
from app.integrations.openai_sales_client import OpenAISalesClient, SalesAgentResponse
from app.integrations.melvis_client import MelvisClient
from app.integrations.tavily_client import TavilyClient
from app.integrations.linkedin_client import LinkedInClient
from app.integrations.stripe_client import StripeClient
from app.integrations.calcom_client import CalComClient
from app.core.config import settings


class WhatsAppSalesAgent:
    """
    WhatsApp Sales Agent orchestrator integrating 7 clients for lead qualification,
    RAG/web context, enrichment, and payment checkout.
    """
    
    def __init__(self):
        """Initialize all clients with settings."""
        # MongoDB persistence
        self.mongo = MongoDBClient(
            uri=settings.mongodb_uri,
            db_name=settings.mongodb_db_name
        ) if settings.mongodb_uri else None
        
        # OpenAI sales agent
        self.openai = OpenAISalesClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        ) if settings.openai_api_key else None
        
        # Melvis RAG (optional - only if configured)
        self.melvis = MelvisClient(
            api_url=settings.melvis_api_url,
            api_key=settings.melvis_api_key,
            collection=settings.melvis_collection
        ) if settings.melvis_api_url and settings.melvis_api_key else None
        
        # Tavily web search (optional)
        self.tavily = TavilyClient(
            api_key=settings.tavily_api_key
        ) if settings.tavily_api_key else None
        
        # LinkedIn enrichment (optional)
        self.linkedin = LinkedInClient(
            api_key=settings.linkedin_api_key,
            base_url=settings.linkedin_base_url
        ) if settings.linkedin_api_key else None
        
        # Stripe checkout (optional)
        self.stripe = StripeClient(
            secret_key=settings.stripe_secret_key,
            price_id=settings.stripe_price_id,
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url
        ) if settings.stripe_secret_key and settings.stripe_price_id else None
        
        # Cal.com booking
        self.calcom = CalComClient(
            booking_link=settings.calcom_booking_link
        )
        
        logger.info(
            f"WhatsApp Sales Agent initialized. "
            f"MongoDB: {bool(self.mongo)}, OpenAI: {bool(self.openai)}, "
            f"Melvis: {bool(self.melvis)}, Tavily: {bool(self.tavily)}, "
            f"LinkedIn: {bool(self.linkedin)}, Stripe: {bool(self.stripe)}"
        )
    
    async def connect(self):
        """Connect to MongoDB. Call once at startup."""
        if self.mongo:
            await self.mongo.connect()
    
    async def disconnect(self):
        """Disconnect from MongoDB. Call at shutdown."""
        if self.mongo:
            await self.mongo.disconnect()
    
    async def process_message(
        self,
        phone: str,
        message_text: str
    ) -> str:
        """
        Process incoming WhatsApp message through full sales agent flow.
        
        Args:
            phone: WhatsApp phone number (e.g. "+1234567890")
            message_text: Incoming message text from user
        
        Returns:
            Reply message to send back to WhatsApp user
        """
        try:
            # STEP 1: Validate MongoDB connection
            if not self.mongo:
                logger.error("MongoDB not configured - cannot process message")
                return "Sistema temporalmente no disponible. Por favor intenta más tarde."
            
            if not self.openai:
                logger.error("OpenAI not configured - cannot process message")
                return "Sistema temporalmente no disponible. Por favor intenta más tarde."
            
            # STEP 2: Upsert user
            await self.mongo.upsert_user(phone=phone)
            logger.info(f"User upserted: {phone[:10]}...")
            
            # STEP 3: Insert incoming message
            await self.mongo.insert_message(
                phone=phone,
                direction="in",
                text=message_text
            )
            
            # STEP 4: Load/create session
            session = await self.mongo.load_or_create_session(phone=phone)
            logger.info(f"Session loaded: {phone[:10]}... step={session.current_step}")
            
            # STEP 5: Get message history for context
            message_history = await self.mongo.get_recent_messages(phone=phone, limit=10)
            history_dict = [
                {"direction": msg.direction, "text": msg.text}
                for msg in message_history
            ]
            
            # STEP 6: Call OpenAI (without RAG/web context initially)
            # OpenAI will tell us if it needs RAG or web search via context_needed flags
            ai_response = await self.openai.generate_sales_response(
                user_message=message_text,
                session_step=session.current_step,
                session_answers=session.answers,
                message_history=history_dict,
                rag_context=None,
                web_context=None
            )
            
            # STEP 7: Check if OpenAI needs additional context
            rag_context = None
            web_context = None
            
            if ai_response.context_needed.use_melvis and self.melvis:
                logger.info("OpenAI requested Melvis RAG context")
                rag_context = await self.melvis.query_knowledge_base(query=message_text)
            
            if ai_response.context_needed.use_tavily and self.tavily:
                logger.info("OpenAI requested Tavily web search")
                web_context = await self.tavily.search_web(query=message_text)
            
            # If we got new context, re-call OpenAI with enriched context
            if rag_context or web_context:
                logger.info("Re-calling OpenAI with enriched context")
                ai_response = await self.openai.generate_sales_response(
                    user_message=message_text,
                    session_step=session.current_step,
                    session_answers=session.answers,
                    message_history=history_dict,
                    rag_context=rag_context,
                    web_context=web_context
                )
            
            # STEP 8: Process actions
            reply = ai_response.reply
            
            # Action: CREATE_OR_UPDATE_LEAD
            if "CREATE_OR_UPDATE_LEAD" in ai_response.actions and ai_response.lead.data:
                lead_data = ai_response.lead.data.model_dump(exclude_none=True)
                
                # Check if lead has nombre + empresa for LinkedIn enrichment
                if (self.linkedin and 
                    lead_data.get("nombre") and 
                    lead_data.get("empresa")):
                    logger.info("Lead has nombre + empresa, calling LinkedIn enrichment")
                    enriched = await self.linkedin.enrich_lead(
                        name=lead_data["nombre"],
                        company=lead_data["empresa"]
                    )
                    # Merge enrichment data into lead
                    lead_data.update(enriched)
                
                # Upsert lead with enrichment
                await self.mongo.upsert_lead(phone=phone, **lead_data)
                logger.info(f"Lead upserted with {len(lead_data)} fields")
            
            # Action: SUGGEST_CAL_LINK
            if "SUGGEST_CAL_LINK" in ai_response.actions:
                cal_link = self.calcom.get_booking_link()
                # Inject link into reply (replace placeholder if exists, else append)
                if "{CAL_LINK}" in reply:
                    reply = reply.replace("{CAL_LINK}", cal_link)
                else:
                    reply += f"\n\n📅 Agenda una consulta gratuita: {cal_link}"
                logger.info("Cal.com link injected into reply")
            
            # Action: CREATE_STRIPE_CHECKOUT
            if "CREATE_STRIPE_CHECKOUT" in ai_response.actions and self.stripe:
                # Get lead data for customer_email
                lead = await self.mongo.get_lead(phone=phone)
                customer_email = lead.email if lead else None
                customer_name = lead.name if lead else None
                
                checkout_url = await self.stripe.create_checkout(
                    customer_email=customer_email,
                    customer_name=customer_name,
                    metadata={"phone": phone, "source": "whatsapp_sales_agent"}
                )
                
                if checkout_url:
                    # Inject checkout URL into reply
                    if "{CHECKOUT_URL}" in reply:
                        reply = reply.replace("{CHECKOUT_URL}", checkout_url)
                    else:
                        reply += f"\n\n💳 Procede al pago: {checkout_url}"
                    logger.info("Stripe checkout URL injected into reply")
                else:
                    logger.warning("Stripe checkout creation failed")
            
            # STEP 9: Update session with merged answers
            if ai_response.lead.data:
                lead_data_dict = ai_response.lead.data.model_dump(exclude_none=True)
                updated_answers = {**session.answers, **lead_data_dict}
            else:
                updated_answers = session.answers
            
            await self.mongo.update_session(
                phone=phone,
                current_step=ai_response.next_step,
                answers=updated_answers
            )
            
            # STEP 10: Insert outgoing message
            await self.mongo.insert_message(
                phone=phone,
                direction="out",
                text=reply
            )
            
            logger.info(
                f"Message processed successfully. "
                f"Step: {session.current_step} → {ai_response.next_step}, "
                f"Actions: {ai_response.actions}"
            )
            
            return reply
            
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"WhatsApp Sales Agent error: {error_msg}")
            return "Disculpa, tuve un problema técnico. Por favor intenta de nuevo."


# Global singleton instance
sales_agent = WhatsAppSalesAgent()


async def handle_whatsapp_webhook(phone: str, message: str) -> str:
    """
    Main entry point for WhatsApp webhook.
    
    Args:
        phone: WhatsApp phone number
        message: Incoming message text
    
    Returns:
        Reply message to send back
    """
    return await sales_agent.process_message(phone=phone, message_text=message)
