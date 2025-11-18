# WhatsApp Sales Agent - Full IntegraIA Template

**Complete Sales Qualification System with 7 External Integrations**

**Last Updated:** November 18, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [10-Step Conversation Flow](#10-step-conversation-flow)
4. [MongoDB Schemas](#mongodb-schemas)
5. [Client Integrations](#client-integrations)
6. [Environment Variables](#environment-variables)
7. [Setup Instructions](#setup-instructions)
8. [API Usage Examples](#api-usage-examples)
9. [Testing Guide](#testing-guide)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **WhatsApp Sales Agent** is a complete lead qualification and sales orchestration system that integrates 7 external services to provide:

- **Intelligent conversation management** with OpenAI structured outputs
- **Persistent lead tracking** with MongoDB
- **RAG/knowledge base** integration via Melvis
- **Real-time web search** via Tavily
- **Lead enrichment** via LinkedIn API
- **Payment checkout** via Stripe
- **Meeting scheduling** via Cal.com

### Key Features

✅ **Stateful conversations** - Tracks user progress through qualification steps  
✅ **Conditional context loading** - Only fetches RAG/web data when needed  
✅ **Automatic lead enrichment** - Enriches leads with LinkedIn data when company info available  
✅ **Payment integration** - Generates Stripe checkout URLs for qualified leads  
✅ **Booking integration** - Shares Cal.com links for qualified consultations  
✅ **Fully async** - Built with Python async/await for high performance  

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    WhatsApp Sales Agent                          │
│                     (Orchestrator Layer)                         │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │   Persistence   │      ┌──────────────┐
    │    (MongoDB)    │◄─────┤ Users        │
    │                 │      ├──────────────┤
    │  Client #1      │◄─────┤ Messages     │
    └─────────────────┘      ├──────────────┤
                             │ Leads        │
                             ├──────────────┤
                             │ Sessions     │
                             └──────────────┘

    ┌─────────────────┐
    │   LLM Brain     │      OpenAI GPT-4o-mini
    │   (OpenAI)      │      Structured JSON output
    │                 │      Context-aware responses
    │  Client #2      │
    └─────────────────┘

    ┌─────────────────┐
    │   RAG/KB        │      Vector search
    │   (Melvis)      │      Knowledge base chunks
    │                 │      Sales documentation
    │  Client #3      │
    └─────────────────┘

    ┌─────────────────┐
    │  Web Search     │      Real-time info
    │   (Tavily)      │      External context
    │                 │      News, prices, etc
    │  Client #4      │
    └─────────────────┘

    ┌─────────────────┐
    │ Lead Enrichment │      Professional data
    │  (LinkedIn)     │      Company size, role
    │                 │      Location, industry
    │  Client #5      │
    └─────────────────┘

    ┌─────────────────┐
    │    Payment      │      Checkout sessions
    │   (Stripe)      │      Payment links
    │                 │      Customer tracking
    │  Client #6      │
    └─────────────────┘

    ┌─────────────────┐
    │   Scheduling    │      Booking links
    │   (Cal.com)     │      Meeting coordination
    │                 │      Calendar integration
    │  Client #7      │
    └─────────────────┘
```

### Technology Stack

- **Language:** Python 3.11+ with async/await
- **Framework:** FastAPI for webhook handling
- **Persistence:** MongoDB (Motor async client)
- **LLM:** OpenAI GPT-4o-mini with structured outputs
- **Vector Store:** Melvis (optional)
- **Web Search:** Tavily (optional)
- **Enrichment:** LinkedIn API (optional)
- **Payments:** Stripe Checkout (optional)
- **Scheduling:** Cal.com (simple link sharing)

---

## 10-Step Conversation Flow

The orchestrator processes each incoming WhatsApp message through a structured 10-step pipeline:

### Step-by-Step Breakdown

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Webhook Receive                                          │
│ ────────────────────────────────────────────────────────────────│
│ Input:  phone="+1234567890", message="Hola"                      │
│ Action: Validate MongoDB + OpenAI configuration                  │
│ Output: Proceed to step 2 or error response                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Upsert User                                              │
│ ────────────────────────────────────────────────────────────────│
│ Action: MongoDBClient.upsert_user(phone=phone)                  │
│ Effect: Create user if new, update last_seen_at if existing     │
│ Schema: User {phone, name?, sector?, created_at, last_seen_at}  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Insert Incoming Message                                  │
│ ────────────────────────────────────────────────────────────────│
│ Action: MongoDBClient.insert_message(phone, "in", message)      │
│ Effect: Store message with timestamp for history tracking       │
│ Schema: Message {phone, direction, text, timestamp, intent?}    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Load/Create Session                                      │
│ ────────────────────────────────────────────────────────────────│
│ Action: MongoDBClient.load_or_create_session(phone)             │
│ Effect: Get current conversation state or create new session    │
│ Schema: Session {phone, current_step, answers, last_updated_at} │
│ Default: current_step = "greet"                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Get Message History                                      │
│ ────────────────────────────────────────────────────────────────│
│ Action: MongoDBClient.get_recent_messages(phone, limit=10)      │
│ Effect: Retrieve last 10 messages for conversation context      │
│ Format: [{direction: "in/out", text: "..."}]                    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: First OpenAI Call (without RAG/Web)                      │
│ ────────────────────────────────────────────────────────────────│
│ Action: OpenAISalesClient.generate_sales_response(...)          │
│ Input:  user_message, session_step, answers, history            │
│ Output: SalesAgentResponse {                                     │
│           reply: str,                                             │
│           next_step: str,                                         │
│           lead: {completed: bool, data: {...}},                  │
│           actions: ["NONE" | "CREATE_OR_UPDATE_LEAD" | ...],    │
│           context_needed: {use_melvis: bool, use_tavily: bool}  │
│         }                                                         │
└──────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │ context_needed?   │
                    └─────────┬─────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ↓ use_melvis=true                           ↓ use_tavily=true
┌───────────────────┐                       ┌───────────────────┐
│ STEP 6A: RAG      │                       │ STEP 6B: Web      │
│ Query Melvis      │                       │ Search Tavily     │
│                   │                       │                   │
│ Returns:          │                       │ Returns:          │
│ - Top 3 chunks    │                       │ - Answer + URLs   │
│ - Formatted text  │                       │ - Snippets        │
└───────┬───────────┘                       └───────┬───────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6C: Second OpenAI Call (with enriched context)             │
│ ────────────────────────────────────────────────────────────────│
│ Action: Re-call OpenAI with rag_context and/or web_context     │
│ Effect: LLM now has additional information to answer question   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: Process Actions                                          │
│ ────────────────────────────────────────────────────────────────│
│ 7A: CREATE_OR_UPDATE_LEAD                                        │
│     → Extract lead.data from OpenAI response                     │
│     → If nombre + empresa: Call LinkedInClient.enrich_lead()    │
│     → Merge enrichment data (role, company_size, location)       │
│     → MongoDBClient.upsert_lead(phone, **lead_data)             │
│                                                                  │
│ 7B: SUGGEST_CAL_LINK                                             │
│     → CalComClient.get_booking_link()                           │
│     → Inject link into reply (replace {CAL_LINK} or append)     │
│                                                                  │
│ 7C: CREATE_STRIPE_CHECKOUT                                       │
│     → Get lead for customer_email + customer_name               │
│     → StripeClient.create_checkout(email, name, metadata)       │
│     → Inject checkout URL into reply ({CHECKOUT_URL} or append) │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 8: Update Session                                           │
│ ────────────────────────────────────────────────────────────────│
│ Action: Merge session.answers with new lead.data                │
│ Action: MongoDBClient.update_session(phone, next_step, answers) │
│ Effect: Session state advances (greet → get_name → get_email)  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 9: Insert Outgoing Message                                  │
│ ────────────────────────────────────────────────────────────────│
│ Action: MongoDBClient.insert_message(phone, "out", reply)       │
│ Effect: Store agent's reply for conversation history            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 10: Send WhatsApp Reply                                     │
│ ────────────────────────────────────────────────────────────────│
│ Return: reply (str)                                               │
│ Effect: WhatsApp webhook handler sends message back to user     │
└──────────────────────────────────────────────────────────────────┘
```

### Conversation Steps (Session State Machine)

The `session.current_step` field tracks user progress:

| Step | Description | Next Action |
|------|-------------|-------------|
| `greet` | Initial greeting | Ask for name |
| `get_name` | Collecting name | Ask for email |
| `get_email` | Collecting email | Ask for company |
| `get_empresa` | Collecting company | Ask for sector |
| `get_sector` | Collecting sector/industry | Ask for company size |
| `get_tamano` | Collecting company size | Ask for budget |
| `get_presupuesto` | Collecting budget | Mark lead as qualified |
| `qualified` | Lead fully qualified | Offer Cal.com + Stripe checkout |

---

## MongoDB Schemas

All MongoDB collections use Pydantic models for validation. Fields are stored as documents with automatic timestamps.

### 1. User Schema

**Collection:** `users`

```python
{
  "phone": "+1234567890",           # Unique WhatsApp phone number (primary key)
  "name": "Juan Pérez",             # Optional: User's name
  "sector": "Technology",           # Optional: User's industry
  "created_at": "2025-11-18T10:00:00Z",  # Auto-generated on first contact
  "last_seen_at": "2025-11-18T10:15:00Z" # Updated on every message
}
```

**Indexes:**
- `phone` (unique)

### 2. Message Schema

**Collection:** `messages`

```python
{
  "phone": "+1234567890",           # Foreign key to User
  "direction": "in",                # "in" (from user) or "out" (from agent)
  "text": "Hola, me interesa",      # Message content
  "timestamp": "2025-11-18T10:05:00Z", # Message timestamp
  "intent": "greeting"              # Optional: OpenAI classified intent
}
```

**Indexes:**
- `phone` + `timestamp` (compound, for history queries)

**Example Query:**
```python
# Get last 10 messages for conversation history
messages = await db.messages.find({"phone": phone}) \
    .sort("timestamp", -1) \
    .limit(10) \
    .to_list(length=10)
```

### 3. Lead Schema

**Collection:** `leads`

```python
{
  "phone": "+1234567890",           # Unique phone (primary key)
  
  # Basic qualification data (from conversation)
  "name": "Juan Pérez",             # Optional
  "email": "juan@empresa.com",      # Optional
  "empresa": "TechCorp",            # Optional: Company name
  "sector": "Technology",           # Optional: Industry
  "tamano_empresa": "50-200",       # Optional: Company size range
  "presupuesto_aprox": "$10k-$25k", # Optional: Budget estimate
  
  # LinkedIn enrichment (added when nombre + empresa available)
  "linkedin_role": "CTO",           # Optional: Job title
  "linkedin_company_size": "51-200", # Optional: LinkedIn company size
  "linkedin_location": "San Francisco, CA", # Optional
  "linkedin_industry": "Software Development", # Optional
  
  # Lead management
  "estado": "nuevo",                # "nuevo" | "contactado" | "calificado" | "cerrado"
  "notes": "Lead cualificado para demo", # Optional: Agent notes
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:15:00Z"
}
```

**Indexes:**
- `phone` (unique)
- `estado` (for filtering)
- `created_at` (for sorting)

**Update Pattern:**
```python
# Upsert: Update existing or create new
await db.leads.find_one_and_update(
    {"phone": phone},
    {
        "$set": lead_data,
        "$setOnInsert": {"created_at": now, "estado": "nuevo"}
    },
    upsert=True,
    return_document=ReturnDocument.AFTER
)
```

### 4. Session Schema

**Collection:** `sessions`

```python
{
  "phone": "+1234567890",           # Unique phone (primary key)
  "current_step": "get_email",      # Current conversation step (state machine)
  "answers": {                       # Collected answers (merged with lead.data)
    "nombre": "Juan Pérez",
    "email": "juan@empresa.com"
  },
  "last_updated_at": "2025-11-18T10:10:00Z"
}
```

**Indexes:**
- `phone` (unique)

**State Machine:**
`greet` → `get_name` → `get_email` → `get_empresa` → `get_sector` → `get_tamano` → `get_presupuesto` → `qualified`

---

## Client Integrations

### Client #1: MongoDB (Persistence)

**File:** `app/integrations/mongodb_client.py`

**Purpose:** Store users, messages, leads, and session state.

**Configuration:**
```python
MONGODB_URI = "mongodb+srv://user:pass@cluster.mongodb.net/"
MONGODB_DB_NAME = "whatsapp_sales_agent"
```

**Initialization:**
```python
from app.integrations.mongodb_client import MongoDBClient

mongo = MongoDBClient(uri=MONGODB_URI, db_name=MONGODB_DB_NAME)
await mongo.connect()  # Call once at startup
```

**Key Methods:**

```python
# Users
user = await mongo.upsert_user(phone="+1234567890", name="Juan")
user = await mongo.get_user(phone="+1234567890")

# Messages
msg = await mongo.insert_message(phone="+1234567890", direction="in", text="Hola")
history = await mongo.get_recent_messages(phone="+1234567890", limit=10)

# Leads
lead = await mongo.upsert_lead(phone="+1234567890", nombre="Juan", email="juan@co.com")
lead = await mongo.get_lead(phone="+1234567890")

# Sessions
session = await mongo.load_or_create_session(phone="+1234567890")
session = await mongo.update_session(phone="+1234567890", current_step="get_email", answers={...})
```

**Error Handling:**
- Connection errors raise exception at startup
- Query errors return `None` or empty lists
- Upserts are atomic (no race conditions)

---

### Client #2: OpenAI (LLM Brain)

**File:** `app/integrations/openai_sales_client.py`

**Purpose:** Generate conversational responses with structured JSON output.

**Configuration:**
```python
OPENAI_API_KEY = "sk-proj-..."
OPENAI_MODEL = "gpt-4o-mini"  # Fast + cheap
```

**Initialization:**
```python
from app.integrations.openai_sales_client import OpenAISalesClient

openai = OpenAISalesClient(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini"
)
```

**Request Schema:**
```python
response = await openai.generate_sales_response(
    user_message="Hola, me interesa un autopilot",
    session_step="greet",
    session_answers={},
    message_history=[
        {"direction": "in", "text": "Hola"},
        {"direction": "out", "text": "¡Hola! ¿Cómo te llamas?"}
    ],
    rag_context="Ofrecemos autopilots para WhatsApp...",  # Optional
    web_context="TechCorp es una empresa de 100 empleados..."  # Optional
)
```

**Response Schema (Pydantic):**
```python
class SalesAgentResponse(BaseModel):
    reply: str  # "¡Genial! ¿Cuál es tu nombre completo?"
    next_step: str  # "get_name"
    lead: LeadInfo  # {completed: False, data: {nombre: None, email: None, ...}}
    actions: List[str]  # ["NONE"] or ["CREATE_OR_UPDATE_LEAD", "SUGGEST_CAL_LINK"]
    context_needed: ContextNeeded  # {use_melvis: False, use_tavily: False}
```

**Example Response JSON:**
```json
{
  "reply": "¡Perfecto! Ya tengo todos tus datos. Te comparto un link para agendar una consulta gratuita: {CAL_LINK}",
  "next_step": "qualified",
  "lead": {
    "completed": true,
    "data": {
      "nombre": "Juan Pérez",
      "email": "juan@techcorp.com",
      "empresa": "TechCorp",
      "sector": "Technology",
      "tamano_empresa": "50-200",
      "presupuesto_aprox": "$10k-$25k"
    }
  },
  "actions": ["CREATE_OR_UPDATE_LEAD", "SUGGEST_CAL_LINK"],
  "context_needed": {
    "use_melvis": false,
    "use_tavily": false
  }
}
```

**System Prompt (Sales Instructions):**

The OpenAI client sends this system prompt on every call:

```
Eres el Agente de Ventas de WhatsApp de DANIA Agency.

Tu misión es cualificar leads paso a paso, siguiendo este flujo:

1. **Saludo inicial** (step: greet) → Preguntar nombre
2. **Obtener nombre** (step: get_name) → Preguntar email
3. **Obtener email** (step: get_email) → Preguntar empresa
4. **Obtener empresa** (step: get_empresa) → Preguntar sector
5. **Obtener sector** (step: get_sector) → Preguntar tamaño empresa
6. **Obtener tamaño** (step: get_tamano) → Preguntar presupuesto aproximado
7. **Obtener presupuesto** (step: get_presupuesto) → Lead completo
8. **Lead completo** (step: qualified) → Ofrecer Cal.com link + Stripe checkout

**REGLAS IMPORTANTES**:
- Sé amable y profesional en español
- Si el usuario no responde bien, reformula con paciencia
- NO inventes datos del usuario
- Marca lead.completed = true SOLO cuando tengas todos los datos
- Usa context_needed.use_melvis = true si el usuario hace preguntas sobre servicios/productos
- Usa context_needed.use_tavily = true si el usuario pregunta info externa en tiempo real
- Cuando lead.completed = true, activa acciones: CREATE_OR_UPDATE_LEAD + SUGGEST_CAL_LINK + CREATE_STRIPE_CHECKOUT
```

**Fallback on Error:**
```python
# If OpenAI call fails, return safe fallback
return SalesAgentResponse(
    reply="Disculpa, tuve un problema técnico. ¿Puedes repetir tu mensaje?",
    next_step=session_step,  # Stay on same step
    actions=["NONE"]
)
```

---

### Client #3: Melvis (RAG/Knowledge Base)

**File:** `app/integrations/melvis_client.py`

**Purpose:** Query vector database for relevant knowledge base chunks.

**Configuration:**
```python
MELVIS_API_URL = "https://melvis.example.com/api"
MELVIS_API_KEY = "mlv_..."
MELVIS_COLLECTION = "kb_sales"
```

**Initialization:**
```python
from app.integrations.melvis_client import MelvisClient

melvis = MelvisClient(
    api_url=MELVIS_API_URL,
    api_key=MELVIS_API_KEY,
    collection="kb_sales"
)
```

**API Call:**
```python
chunks = await melvis.query_knowledge_base(
    query="¿Qué autopilots ofrecen?",
    limit=3
)
# Returns formatted string:
# - Autopilot WhatsApp: Respuestas automáticas inteligentes...
# - Autopilot Social: Publicación multi-plataforma...
# - Autopilot Lead Gen: Cualificación automática de leads...
```

**Request (HTTP POST):**
```json
POST https://melvis.example.com/api/search
Headers:
  Authorization: Bearer mlv_abc123...
  Content-Type: application/json

Body:
{
  "collection": "kb_sales",
  "query": "¿Qué autopilots ofrecen?",
  "limit": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Autopilot WhatsApp: Respuestas automáticas inteligentes...",
      "score": 0.92
    },
    {
      "text": "Autopilot Social: Publicación multi-plataforma...",
      "score": 0.88
    },
    {
      "text": "Autopilot Lead Gen: Cualificación automática de leads...",
      "score": 0.85
    }
  ]
}
```

**Error Handling:**
- Returns `None` if API call fails
- Returns `None` if no results found
- Logs errors without crashing

---

### Client #4: Tavily (Web Search)

**File:** `app/integrations/tavily_client.py`

**Purpose:** Perform real-time web searches for external context.

**Configuration:**
```python
TAVILY_API_KEY = "tvly-..."
```

**Initialization:**
```python
from app.integrations.tavily_client import TavilyClient

tavily = TavilyClient(api_key=TAVILY_API_KEY)
```

**API Call:**
```python
results = await tavily.search_web(
    query="TechCorp San Francisco funding",
    max_results=3
)
# Returns formatted string:
# Respuesta: TechCorp raised $50M Series B in 2024...
# Fuentes:
# - TechCrunch: TechCorp announces $50M...: https://techcrunch.com/...
# - Bloomberg: San Francisco startup TechCorp...: https://bloomberg.com/...
```

**Request (HTTP POST):**
```json
POST https://api.tavily.com/search
Headers:
  Content-Type: application/json

Body:
{
  "api_key": "tvly-abc123...",
  "query": "TechCorp San Francisco funding",
  "max_results": 3,
  "search_depth": "basic",
  "include_answer": true,
  "include_raw_content": false
}
```

**Response:**
```json
{
  "answer": "TechCorp raised $50M Series B in 2024...",
  "results": [
    {
      "title": "TechCorp announces $50M Series B",
      "url": "https://techcrunch.com/...",
      "content": "San Francisco-based TechCorp announced..."
    }
  ]
}
```

**Error Handling:**
- Returns `None` if API call fails
- Returns `None` if no results
- Logs errors without crashing

---

### Client #5: LinkedIn (Lead Enrichment)

**File:** `app/integrations/linkedin_client.py`

**Purpose:** Enrich lead data with professional information.

**Configuration:**
```python
LINKEDIN_API_KEY = "lin_..."
LINKEDIN_BASE_URL = "https://api.linkedin.com/v2"
```

**Initialization:**
```python
from app.integrations.linkedin_client import LinkedInClient

linkedin = LinkedInClient(
    api_key=LINKEDIN_API_KEY,
    base_url=LINKEDIN_BASE_URL
)
```

**API Call:**
```python
enriched = await linkedin.enrich_lead(
    name="Juan Pérez",
    company="TechCorp"
)
# Returns:
# {
#   "linkedin_role": "CTO",
#   "linkedin_company_size": "51-200",
#   "linkedin_location": "San Francisco, CA",
#   "linkedin_industry": "Software Development"
# }
```

**Request (HTTP GET):**
```
GET https://api.linkedin.com/v2/people/enrich?name=Juan+Pérez&company=TechCorp
Headers:
  Authorization: Bearer lin_abc123...
```

**Response:**
```json
{
  "title": "CTO",
  "company_size": "51-200",
  "location": "San Francisco, CA",
  "industry": "Software Development"
}
```

**Fallback on Error:**
```python
# If enrichment fails, return empty data (don't block lead creation)
{
  "linkedin_role": None,
  "linkedin_company_size": None,
  "linkedin_location": None,
  "linkedin_industry": None
}
```

---

### Client #6: Stripe (Payment Checkout)

**File:** `app/integrations/stripe_client.py`

**Purpose:** Create checkout sessions for payment processing.

**Configuration:**
```python
STRIPE_SECRET_KEY = "sk_live_..."
STRIPE_PRICE_ID = "price_1ABC123..."
STRIPE_SUCCESS_URL = "https://dania.agency/gracias"
STRIPE_CANCEL_URL = "https://dania.agency/cancelado"
```

**Initialization:**
```python
from app.integrations.stripe_client import StripeClient

stripe_client = StripeClient(
    secret_key=STRIPE_SECRET_KEY,
    price_id=STRIPE_PRICE_ID,
    success_url=STRIPE_SUCCESS_URL,
    cancel_url=STRIPE_CANCEL_URL
)
```

**API Call:**
```python
checkout_url = await stripe_client.create_checkout(
    customer_email="juan@techcorp.com",
    customer_name="Juan Pérez",
    metadata={"phone": "+1234567890", "source": "whatsapp_sales_agent"}
)
# Returns: "https://checkout.stripe.com/c/pay/cs_live_a1b2c3..."
```

**Stripe API Call (via SDK):**
```python
import stripe

checkout_session = stripe.checkout.Session.create(
    line_items=[{"price": "price_1ABC123...", "quantity": 1}],
    mode="payment",
    success_url="https://dania.agency/gracias",
    cancel_url="https://dania.agency/cancelado",
    customer_email="juan@techcorp.com",
    metadata={"phone": "+1234567890", "source": "whatsapp_sales_agent"}
)

return checkout_session.url  # Hosted checkout page
```

**Response:**
```
https://checkout.stripe.com/c/pay/cs_live_a1b2c3d4e5f6...
```

**Error Handling:**
- Returns `None` if checkout creation fails
- Logs Stripe errors
- Does not block message flow

---

### Client #7: Cal.com (Scheduling)

**File:** `app/integrations/calcom_client.py`

**Purpose:** Share booking links for meeting coordination.

**Configuration:**
```python
CALCOM_BOOKING_LINK = "https://cal.com/dania-agency/consulta-gratuita"
```

**Initialization:**
```python
from app.integrations.calcom_client import CalComClient

calcom = CalComClient(booking_link=CALCOM_BOOKING_LINK)
```

**API Call:**
```python
link = calcom.get_booking_link(lead_name="Juan Pérez")
# Returns: "https://cal.com/dania-agency/consulta-gratuita"
```

**Note:** This client is simple - it just returns the configured link. No external API calls are made. Future versions could add query parameters for personalization (`?name=Juan+Perez&email=juan@techcorp.com`).

---

## Environment Variables

See [`SECRETS_MATRIX.md`](./SECRETS_MATRIX.md) for the complete reference. Below is a summary of WhatsApp Sales Agent specific variables:

### Required (Core Functionality)

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DB_NAME` | MongoDB database name | `whatsapp_sales_agent` |
| `OPENAI_API_KEY` | OpenAI API key for LLM | `sk-proj-abc123...` |

### Optional (Enhanced Features)

| Variable | Description | Default |
|----------|-------------|---------|
| `MELVIS_API_URL` | Melvis API base URL | `` (disabled) |
| `MELVIS_API_KEY` | Melvis API key | `` (disabled) |
| `MELVIS_COLLECTION` | Melvis collection name | `kb_sales` |
| `TAVILY_API_KEY` | Tavily web search API key | `` (disabled) |
| `LINKEDIN_API_KEY` | LinkedIn enrichment API key | `` (disabled) |
| `LINKEDIN_BASE_URL` | LinkedIn API base URL | `https://api.linkedin.com/v2` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `` (disabled) |
| `STRIPE_PRICE_ID` | Stripe price ID for checkout | `` (disabled) |
| `STRIPE_SUCCESS_URL` | Redirect after payment | `https://dania.agency/gracias` |
| `STRIPE_CANCEL_URL` | Redirect on cancel | `https://dania.agency/cancelado` |
| `CALCOM_BOOKING_LINK` | Cal.com booking link | `https://cal.com/dania-agency/consulta-gratuita` |

### Minimum Viable Configuration

**For testing without optional integrations:**

```env
# Required
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
OPENAI_API_KEY=sk-proj-abc123...

# Optional (set to empty to disable)
MELVIS_API_KEY=
TAVILY_API_KEY=
LINKEDIN_API_KEY=
STRIPE_SECRET_KEY=
```

Agent will work but without:
- RAG/knowledge base queries (Melvis)
- Web search (Tavily)
- Lead enrichment (LinkedIn)
- Payment checkout (Stripe)

---

## Setup Instructions

### Prerequisites

1. **Python 3.11+** with pip
2. **MongoDB** (MongoDB Atlas recommended, or local MongoDB 6.0+)
3. **OpenAI API account** with API key

### Step 1: Install Dependencies

```bash
cd axon-agency/apps/api
pip install -r requirements.txt
```

**Required packages:**
- `motor` - Async MongoDB client
- `openai` - OpenAI Python SDK
- `httpx` - Async HTTP client for Melvis/Tavily/LinkedIn
- `stripe` - Stripe Python SDK
- `pydantic` - Data validation

### Step 2: Configure Environment Variables

**Create `.env` file:**

```bash
cd axon-agency/apps/api
cp .env.example .env
```

**Edit `.env` with required variables:**

```env
# MongoDB (REQUIRED)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=whatsapp_sales_agent

# OpenAI (REQUIRED)
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Optional integrations (leave empty to disable)
MELVIS_API_URL=
MELVIS_API_KEY=
TAVILY_API_KEY=
LINKEDIN_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_PRICE_ID=
CALCOM_BOOKING_LINK=https://cal.com/dania-agency/consulta-gratuita
```

### Step 3: Setup MongoDB Database

**Option A: MongoDB Atlas (Recommended)**

1. Create free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create database user with password
3. Whitelist IP: `0.0.0.0/0` (or your server IP)
4. Get connection string: `mongodb+srv://user:pass@cluster.mongodb.net/`
5. Set `MONGODB_URI` in `.env`

**Option B: Local MongoDB**

```bash
# Install MongoDB 6.0+
# macOS: brew install mongodb-community
# Ubuntu: apt install mongodb-server

# Start MongoDB
mongod --dbpath /data/db

# Connection string
MONGODB_URI=mongodb://localhost:27017/
```

**Collections are auto-created on first write** (no manual setup needed).

### Step 4: Initialize Sales Agent

**At API startup (`app/main.py`):**

```python
from app.templates.whatsapp_template_full_integraia import sales_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect MongoDB on startup
    await sales_agent.connect()
    yield
    # Disconnect on shutdown
    await sales_agent.disconnect()

app = FastAPI(lifespan=lifespan)
```

### Step 5: Test Integration

**Health check endpoint:**

```bash
curl http://localhost:8080/api/integrations/health

# Response should show MongoDB status:
{
  "overall_status": "healthy",
  "integrations": [
    {
      "name": "mongodb",
      "status": "healthy",
      "message": "MongoDB connected successfully"
    },
    {
      "name": "whatsapp_sales_agent",
      "status": "healthy",
      "message": "Core dependencies configured. 0/5 optional integrations enabled."
    }
  ]
}
```

**Test WhatsApp webhook (simulated):**

```python
from app.templates.whatsapp_template_full_integraia import handle_whatsapp_webhook

# In async context:
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Hola, me interesa un autopilot"
)

print(reply)
# "¡Hola! Encantado de ayudarte. ¿Cuál es tu nombre completo?"
```

### Step 6: Enable Optional Integrations (Production)

**Melvis (RAG/KB):**
```env
MELVIS_API_URL=https://your-melvis-instance.com/api
MELVIS_API_KEY=mlv_your_key
MELVIS_COLLECTION=kb_sales
```

**Tavily (Web Search):**
```env
TAVILY_API_KEY=tvly-your-key
```

**LinkedIn (Enrichment):**
```env
LINKEDIN_API_KEY=lin_your_key
```

**Stripe (Payments):**
```env
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PRICE_ID=price_1ABC123
STRIPE_SUCCESS_URL=https://yourdomain.com/gracias
STRIPE_CANCEL_URL=https://yourdomain.com/cancelado
```

---

## API Usage Examples

### Example 1: Simple Lead Qualification (No Optional Services)

**Setup:**
- MongoDB: ✅ Connected
- OpenAI: ✅ Configured
- Melvis: ❌ Disabled
- Tavily: ❌ Disabled
- LinkedIn: ❌ Disabled
- Stripe: ❌ Disabled

**Conversation Flow:**

```python
# Message 1: User greeting
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Hola"
)
# Reply: "¡Hola! Encantado de ayudarte. ¿Cuál es tu nombre completo?"
# MongoDB: User created, Message stored, Session created (step=greet)

# Message 2: User provides name
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Juan Pérez"
)
# Reply: "Perfecto, Juan. ¿Cuál es tu email de contacto?"
# MongoDB: Session updated (step=get_email, answers={nombre: "Juan Pérez"})

# Message 3: User provides email
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="juan@techcorp.com"
)
# Reply: "Genial. ¿Cuál es el nombre de tu empresa?"
# MongoDB: Session updated (step=get_empresa, answers={nombre, email})

# ... continues through all steps ...

# Final message: Budget provided
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Entre $10k y $25k"
)
# Reply: "¡Perfecto! Ya tengo todos tus datos. Te comparto un link para agendar una consulta: https://cal.com/..."
# MongoDB: Lead created with all data, Session updated (step=qualified)
# Actions executed: CREATE_OR_UPDATE_LEAD + SUGGEST_CAL_LINK
```

**MongoDB State After Completion:**

```python
# users collection
{
  "phone": "+1234567890",
  "name": "Juan Pérez",
  "created_at": "2025-11-18T10:00:00Z",
  "last_seen_at": "2025-11-18T10:15:00Z"
}

# leads collection
{
  "phone": "+1234567890",
  "name": "Juan Pérez",
  "email": "juan@techcorp.com",
  "empresa": "TechCorp",
  "sector": "Technology",
  "tamano_empresa": "50-200",
  "presupuesto_aprox": "$10k-$25k",
  "estado": "nuevo",
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:15:00Z"
}

# sessions collection
{
  "phone": "+1234567890",
  "current_step": "qualified",
  "answers": {
    "nombre": "Juan Pérez",
    "email": "juan@techcorp.com",
    "empresa": "TechCorp",
    "sector": "Technology",
    "tamano_empresa": "50-200",
    "presupuesto_aprox": "$10k-$25k"
  },
  "last_updated_at": "2025-11-18T10:15:00Z"
}

# messages collection (10+ documents)
[
  {"phone": "+1234567890", "direction": "in", "text": "Hola", "timestamp": "..."},
  {"phone": "+1234567890", "direction": "out", "text": "¡Hola! Encantado...", "timestamp": "..."},
  ...
]
```

### Example 2: With All Integrations Enabled

**Setup:**
- MongoDB: ✅
- OpenAI: ✅
- Melvis: ✅
- Tavily: ✅
- LinkedIn: ✅
- Stripe: ✅

**Conversation with Context Enrichment:**

```python
# User asks about services (triggers Melvis RAG)
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="¿Qué autopilots ofrecen para WhatsApp?"
)

# Flow:
# 1. OpenAI returns context_needed.use_melvis = true
# 2. Melvis query: "autopilots WhatsApp"
# 3. Returns 3 KB chunks about WhatsApp autopilots
# 4. Second OpenAI call with RAG context
# 5. Reply includes specific product details from KB

# Reply: "Ofrecemos 3 autopilots para WhatsApp:
#         1. Bot de Respuestas - $500/mes
#         2. Lead Qualifier - $1,200/mes
#         3. Customer Support - $2,000/mes
#         ¿Cuál te interesa más?"

# ---

# User provides company name (triggers LinkedIn enrichment)
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Mi empresa es TechCorp"
)

# Flow:
# 1. OpenAI extracts company name
# 2. Lead upsert with empresa="TechCorp"
# 3. Since nombre + empresa available: LinkedIn enrichment triggered
# 4. LinkedIn API call: enrich_lead(name="Juan Pérez", company="TechCorp")
# 5. Enrichment data merged into lead:
#    - linkedin_role: "CTO"
#    - linkedin_company_size: "51-200"
#    - linkedin_location: "San Francisco, CA"

# Reply: "Perfecto. ¿En qué sector opera TechCorp?"

# ---

# Final qualification (triggers Stripe + Cal.com)
reply = await handle_whatsapp_webhook(
    phone="+1234567890",
    message="Entre $10k y $25k"
)

# Flow:
# 1. OpenAI marks lead as completed
# 2. Actions: [CREATE_OR_UPDATE_LEAD, SUGGEST_CAL_LINK, CREATE_STRIPE_CHECKOUT]
# 3. Lead upserted with all data
# 4. Cal.com link injected
# 5. Stripe checkout created:
#    - customer_email: "juan@techcorp.com"
#    - customer_name: "Juan Pérez"
#    - metadata: {phone, source: "whatsapp_sales_agent"}
# 6. Checkout URL injected into reply

# Reply: "¡Genial, Juan! Ya tengo toda tu información.
#         
#         📅 Agenda una consulta gratuita aquí:
#         https://cal.com/dania-agency/consulta-gratuita
#         
#         💳 O procede directamente al pago:
#         https://checkout.stripe.com/c/pay/cs_live_a1b2c3..."
```

**MongoDB State (with enrichment):**

```python
# leads collection
{
  "phone": "+1234567890",
  "name": "Juan Pérez",
  "email": "juan@techcorp.com",
  "empresa": "TechCorp",
  "sector": "Technology",
  "tamano_empresa": "50-200",
  "presupuesto_aprox": "$10k-$25k",
  
  # LinkedIn enrichment data added
  "linkedin_role": "CTO",
  "linkedin_company_size": "51-200",
  "linkedin_location": "San Francisco, CA",
  "linkedin_industry": "Software Development",
  
  "estado": "nuevo",
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:15:00Z"
}
```

---

## Testing Guide

### Manual Testing Checklist

#### 1. MongoDB Connection Test

```bash
# Health check
curl http://localhost:8080/api/integrations/health

# Expected: MongoDB status = "healthy"
```

#### 2. Basic Conversation Flow Test

```python
import asyncio
from app.templates.whatsapp_template_full_integraia import handle_whatsapp_webhook

async def test_basic_flow():
    phone = "+1234567890"
    
    # Step 1: Greeting
    r1 = await handle_whatsapp_webhook(phone, "Hola")
    assert "nombre" in r1.lower()
    
    # Step 2: Name
    r2 = await handle_whatsapp_webhook(phone, "Juan Pérez")
    assert "email" in r2.lower()
    
    # Step 3: Email
    r3 = await handle_whatsapp_webhook(phone, "juan@test.com")
    assert "empresa" in r3.lower()
    
    print("✅ Basic flow test passed")

asyncio.run(test_basic_flow())
```

#### 3. Lead Persistence Test

```python
from app.integrations.mongodb_client import MongoDBClient
from app.core.config import settings

async def test_lead_persistence():
    mongo = MongoDBClient(settings.mongodb_uri, settings.mongodb_db_name)
    await mongo.connect()
    
    # Create test lead
    lead = await mongo.upsert_lead(
        phone="+1111111111",
        nombre="Test User",
        email="test@example.com"
    )
    
    # Retrieve lead
    retrieved = await mongo.get_lead(phone="+1111111111")
    assert retrieved.nombre == "Test User"
    assert retrieved.email == "test@example.com"
    
    await mongo.disconnect()
    print("✅ Lead persistence test passed")

asyncio.run(test_lead_persistence())
```

#### 4. Optional Integrations Test

```python
async def test_optional_integrations():
    from app.templates.whatsapp_template_full_integraia import sales_agent
    
    # Check which clients are enabled
    print(f"MongoDB: {'✅' if sales_agent.mongo else '❌'}")
    print(f"OpenAI: {'✅' if sales_agent.openai else '❌'}")
    print(f"Melvis: {'✅' if sales_agent.melvis else '❌'}")
    print(f"Tavily: {'✅' if sales_agent.tavily else '❌'}")
    print(f"LinkedIn: {'✅' if sales_agent.linkedin else '❌'}")
    print(f"Stripe: {'✅' if sales_agent.stripe else '❌'}")
    
    # Test Melvis if enabled
    if sales_agent.melvis:
        result = await sales_agent.melvis.query_knowledge_base("test query")
        print(f"Melvis test: {'✅' if result else '❌'}")

asyncio.run(test_optional_integrations())
```

### Integration Testing (Future)

**When automated tests exist, run:**

```bash
# Run WhatsApp Sales Agent tests
pytest tests/test_whatsapp_sales_agent.py -v

# Run with coverage
pytest tests/test_whatsapp_sales_agent.py --cov=app/templates --cov=app/integrations
```

**Expected test suite:**
- `test_mongodb_crud` - CRUD operations
- `test_openai_structured_output` - JSON schema validation
- `test_conversation_flow` - Full qualification flow
- `test_linkedin_enrichment` - Enrichment trigger
- `test_stripe_checkout` - Payment link generation
- `test_fallback_on_error` - Error handling
- `test_context_loading` - RAG/web context

---

## Troubleshooting

### MongoDB Connection Issues

**Error:** `MongoServerSelectionTimeoutError`

**Causes:**
1. Invalid `MONGODB_URI` format
2. Network/firewall blocking connection
3. MongoDB Atlas IP whitelist not configured
4. Invalid credentials

**Solutions:**

```bash
# 1. Verify URI format
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# 2. Test connection with mongosh
mongosh "mongodb+srv://username:password@cluster.mongodb.net/"

# 3. Check Atlas IP whitelist (allow 0.0.0.0/0 for testing)

# 4. Verify credentials in Atlas dashboard
```

**Health check:**
```bash
curl http://localhost:8080/api/integrations/health
# Look for MongoDB status: "degraded" with error message
```

---

### OpenAI API Errors

**Error:** `AuthenticationError: Incorrect API key`

**Solution:**
```bash
# Verify API key format (should start with sk-proj- or sk-)
echo $OPENAI_API_KEY

# Test API key with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Error:** `RateLimitError: You exceeded your current quota`

**Solution:**
```bash
# Check OpenAI usage: https://platform.openai.com/usage
# Add payment method or upgrade plan
```

**Error:** `Structured output parsing failed`

**Solution:**
```bash
# Check OpenAI model supports structured outputs
# gpt-4o-mini: ✅ Supported
# gpt-3.5-turbo: ❌ Not supported (use gpt-4o-mini)

OPENAI_MODEL=gpt-4o-mini  # Ensure this in .env
```

---

### Lead Not Being Created

**Symptoms:**
- Conversation progresses but lead not in `leads` collection
- OpenAI returns `lead.completed = false`

**Debug Steps:**

```python
# 1. Check OpenAI response
import logging
logging.basicConfig(level=logging.INFO)

# 2. Verify action is being triggered
# Look for log: "Message processed successfully. Actions: ['CREATE_OR_UPDATE_LEAD']"

# 3. Check MongoDB lead manually
from app.integrations.mongodb_client import MongoDBClient
mongo = MongoDBClient(uri, db_name)
await mongo.connect()
lead = await mongo.get_lead(phone="+1234567890")
print(lead)
```

**Common causes:**
- User not providing all required fields (OpenAI waits for completion)
- MongoDB write permission denied
- Phone number mismatch (check exact format)

---

### LinkedIn Enrichment Not Working

**Symptoms:**
- Lead has `nombre` + `empresa` but no `linkedin_role`, etc.
- Logs show: `LinkedIn enrichment HTTP error`

**Debug Steps:**

```bash
# 1. Check if LinkedIn client is enabled
curl http://localhost:8080/api/integrations/health
# Look for: whatsapp_sales_agent.details.optional_integrations.linkedin = true

# 2. Verify API key
echo $LINKEDIN_API_KEY

# 3. Test API endpoint directly
curl "https://api.linkedin.com/v2/people/enrich?name=Juan&company=TechCorp" \
  -H "Authorization: Bearer $LINKEDIN_API_KEY"
```

**Note:** LinkedIn enrichment is **optional** and **non-blocking**. If it fails, lead is still created without enrichment data.

---

### Stripe Checkout URL Not Generated

**Symptoms:**
- Qualified lead but no checkout URL in reply
- Action `CREATE_STRIPE_CHECKOUT` triggered but no URL

**Debug Steps:**

```python
# 1. Check Stripe client enabled
from app.templates.whatsapp_template_full_integraia import sales_agent
print(f"Stripe enabled: {bool(sales_agent.stripe)}")

# 2. Verify configuration
print(f"Secret key configured: {bool(settings.stripe_secret_key)}")
print(f"Price ID configured: {bool(settings.stripe_price_id)}")

# 3. Check Stripe logs
# Logs should show: "Stripe checkout created. Session ID: cs_live_..."
# Or error: "Stripe checkout creation failed: ..."
```

**Common issues:**
- `STRIPE_SECRET_KEY` or `STRIPE_PRICE_ID` missing
- Invalid Stripe API key (test vs live mode mismatch)
- Price ID doesn't exist in Stripe dashboard

---

### Message History Not Loading

**Symptoms:**
- OpenAI has no conversation context
- Repeats same questions

**Debug:**

```python
from app.integrations.mongodb_client import MongoDBClient
mongo = MongoDBClient(uri, db_name)
await mongo.connect()

history = await mongo.get_recent_messages(phone="+1234567890", limit=10)
print(f"Found {len(history)} messages")
for msg in history:
    print(f"{msg.direction}: {msg.text}")
```

**Causes:**
- Messages not being inserted (check logs for "Message saved: in from...")
- Phone number mismatch
- MongoDB query error

---

### General Debugging Tips

**Enable verbose logging:**

```python
# In app/main.py or relevant file
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Check health endpoint:**

```bash
# See all integration statuses
curl http://localhost:8080/api/integrations/health | jq
```

**Inspect MongoDB data:**

```python
# Connect to MongoDB with mongosh
mongosh "mongodb+srv://.../"

# Switch to database
use whatsapp_sales_agent

# Check collections
show collections

# Query data
db.users.find()
db.messages.find().sort({timestamp: -1}).limit(10)
db.leads.find()
db.sessions.find()
```

**Test webhook directly:**

```bash
# Simulate WhatsApp webhook POST
curl -X POST http://localhost:8080/api/integrations/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "message": "Hola"
  }'
```

---

## Next Steps

1. **Production Deployment:** Configure all optional integrations (Melvis, Tavily, LinkedIn, Stripe)
2. **Monitoring:** Add logging/metrics for conversation analytics
3. **Testing:** Implement automated test suite
4. **Webhook Integration:** Connect to WhatsApp Business API webhook
5. **Admin Dashboard:** Build UI to view leads (`/api/leads/list`)
6. **Multi-language:** Extend system prompt for English/Portuguese support
7. **Custom Workflows:** Add more conversation steps beyond basic qualification

---

## Related Documentation

- [`SECRETS_MATRIX.md`](./SECRETS_MATRIX.md) - Complete ENV vars reference
- [`QUICK_SETUP_GUIDE.md`](./QUICK_SETUP_GUIDE.md) - Development setup instructions
- [MongoDB Client API](../apps/api/app/integrations/mongodb_client.py) - Source code
- [OpenAI Sales Client API](../apps/api/app/integrations/openai_sales_client.py) - Source code
- [Template Orchestrator](../apps/api/app/templates/whatsapp_template_full_integraia.py) - Main implementation

---

**Last Updated:** November 18, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
