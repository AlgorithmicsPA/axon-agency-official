# Axon 88 Workspace - Compressed Guide

## Overview

This workspace integrates **Axon Core** and **AXON Agency** to form an AI-driven ecosystem for infrastructure management and AI Agency operations.

### Public Landing Page (November 2025)

AXON Agency now features a professional public landing page accessible at the root path (`/`) with:
- **Route Groups Architecture**: Next.js 15 route groups separate public and authenticated routes
  - `(public)` route group: Landing page + legal pages (no authentication)
  - `(auth)` route group: Dashboard + admin panel (requires authentication)
- **Landing Page**: Hero section, 6 feature cards, footer with WhatsApp contact button
- **Legal Pages**: Privacy Policy, Terms of Service, Data Deletion instructions
- **WhatsApp Integration**: Contact button with ENV-configurable phone number and message **Axon Core** is a robust backend providing REST API and WebSocket interfaces for managing services, commands, files, and multi-provider LLM integrations with JWT authentication and n8n workflow automation. **AXON Agency** is a full-stack AI Agency platform focusing on campaign management, social media integrations, advanced LLM capabilities (including RAG), autopilots, and analytics, leveraging Axon Core for backend communication. The combined system aims to deliver a scalable, multi-tenant AI solution with advanced agent capabilities and automated project generation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Principles

The system utilizes a **Modular Adapter Pattern** for external services, **Environment Autodetection**, and a **Security-First Architecture** with JWT, role-based access control, and command whitelists. **Streaming and Real-Time Updates** are handled via WebSockets.

### AXON Agency Project Architecture

AXON Agency is a monorepo with a FastAPI backend and a Next.js frontend, integrated with Axon Core.
*   **UI/UX**: Professional dark-themed web application built with Next.js 15, TypeScript, Tailwind CSS, and shadcn/ui.
*   **Multi-LLM Orchestration**: Intelligent provider selection with auto-routing and streaming for various LLMs.
*   **Super Axon Agent (Chat Orchestrator)**: Production-ready conversational AI with structured responses, intent classification, autonomous delegation, session tracking, and streaming SSE integration.
*   **Auto-Builder MVP**: AI-powered project generation using multi-step LLM orchestration.
*   **Code Playground**: Monaco Editor-based environment for secure Docker-sandboxed code execution with AI assistance.
*   **RAG/Training Module**: UI for document ingestion, semantic search, and training job creation.
*   **Orders Orchestrator**: Automated order processing and structured production plan generation, integrated with Axon 88 Builder. Includes AgentBlueprint Forwarding for comprehensive agent specifications.
*   **Catalog UI**: Client-facing system for agent discovery and order creation with authentication and role-based access control.
*   **Agent Factory Dashboard**: Admin interface for monitoring factory operations and agent usage, displaying order statistics and agent catalog usage.
*   **Replit Studio Embebido**: Admin-only embedded development environment within the catalog for direct agent editing and customization.
*   **Agent Builder**: Architectural design for transforming AgentBlueprints into concrete project artifacts (specs, flows, configs, prompts, integrations) for Axon 88 Builder, aiming to sell complete agent systems.
*   **Agent Artifacts UI**: Admin-only component showing a visual checklist of Agent Builder artifacts detected in deliverables.
*   **Multi-Tenant + Client Portal**: Platform enabling isolated workspaces for multiple client organizations with backend multi-tenancy (Tenant model + tenant_id filtering), authenticated tenant context (user.tenant_id + auto-filtering), client-facing portal at `/portal/{tenantSlug}` for order management, and admin tenant management UI at `/agent/tenants` for CRUD operations. **Status**: **Phases 1-8 COMPLETE** (Backend, Auth, Portal, Admin UI, Testing & Security, Demo Data & UX). Production-ready with comprehensive deployment guide in `docs/PRODUCTION_CHECKLIST.md`. Security hardening: admin-only tenant management (`require_admin()` on /api/tenants), tenant-scoped order access (`verify_order_access()` on /orders/{id}), legacy user isolation (`tenant_id IS NULL` filter in list_orders), multi-tenant isolation verified. **Phase 8 - Demo System**: Admin-only demo data seeding endpoint (`POST /api/admin/seed-demo`) with robust idempotency via stable demo_tag identifiers. Creates 3 realistic demo tenants (Algorithmics Academy, Notaría 17, BeeSmart Delivery) + 9 demo orders (3 per tenant). Portal UX polished with Spanish copy, personalized welcome headers, elegant empty states, and zero technical jargon. Demo seeder accessible via `/agent/factory` admin dashboard with toast notifications. Full implementation plan in `docs/PHASE_8_PLAN.md`.
*   **WhatsApp Autopilot Deploy Layer (FASE 9.1)**: Production-ready deploy system for WhatsApp Autopilot orders with admin-only `POST /api/orders/{id}/deploy/whatsapp` endpoint. Features: admin auth validation, WhatsApp-compatible product type detection, estado="listo" + qa_status="ok" pre-deployment checks, n8n webhook integration (ENV: `N8N_WHATSAPP_DEPLOY_WEBHOOK_URL`), structured payload with tenant/order/agent_blueprint/deliverable artifacts, deploy_history tracking (JSON field in Order model), HTTP POST to n8n with 30s timeout, success/failed status registration, sanitized logging (no secrets/internal paths). UI: Admin-only "Deploy to WhatsApp" button in order detail page (visible only when all conditions met), MessageCircle icon, loading states with toast notifications, Deploy History card showing events with status badges (success/failed/pending), formatted timestamps, error messages. **Status**: COMPLETE. Backward compatible (nullable deploy_history field), multi-tenant aware (includes tenant in payload or null for legacy), extensible for future channels (Telegram, Email, Slack). Full technical design in `docs/WHATSAPP_DEPLOY_PLAN.md`.
*   **Social Autopilot Deploy Layer (FASE 9.S)**: Production-ready deploy system for social_autopilot orders via Ayrshare API. Admin-only `POST /api/orders/{id}/deploy/social` endpoint posts to multiple social platforms (Twitter, Facebook, Instagram) simultaneously. Features: admin auth validation, social-compatible product type detection, estado="listo" + qa_status="ok" pre-deployment checks, Ayrshare API integration (ENV: `AYRSHARE_API_KEY`, `AYRSHARE_BASE_URL`), structured payload with post text + platforms + mediaUrls + scheduleDate, deploy_history tracking (channel='social', target_system='ayrshare'), HTTP POST with Bearer auth and 30s timeout, success/failed status registration, sanitized logging (no API keys/internal paths). UI: Admin-only "Deploy to Social (Ayrshare)" button with Share2 icon, unified Deploy History card showing all channels (whatsapp + social) with channel-specific icons, platform badges for social events, loading states with toast notifications. **Status**: COMPLETE. Opt-in via AYRSHARE_API_KEY flag. Backward compatible with FASE 9.1 WhatsApp Deploy (no breaking changes). Reuses existing deploy_history model. Multi-tenant aware. Extensible for future social providers (Buffer, Hootsuite). Full technical design in `docs/SOCIAL_DEPLOY_AYRSHARE_PLAN.md`.
*   **Social Deploy Hardening & Observability (FASE 10.A)**: Production hardening for social_autopilot deploy with health monitoring, rate limiting, and granular metrics. **Health Check Endpoint**: `GET /api/integrations/social/health` returns status (disabled/misconfigured/healthy) with dual feature flag gating (ENABLE_AYRSHARE_SOCIAL + AYRSHARE_API_KEY), rate_limit info (remaining/limit/reset_at from Ayrshare headers cached to /tmp), last_deploy_success timestamp from deploy_history query, and enabled_platforms. **Rate Limit Tracking**: Ayrshare client extended to parse x-ratelimit-max/count headers (5-min sliding window, 300 req/period), cache to /tmp/ayrshare_rate_limit_cache.json, handle 429 errors gracefully. **Deploy Metrics**: platform_results per event with granular tracking (twitter/facebook/instagram: success/failed/unknown), ayrshare_post_id for tracing, partial failure detection. **Status**: BACKEND COMPLETE. Frontend health indicator pending (future).
*   **Telegram Bot Deploy Layer (FASE 10.B)**: Multi-tenant Telegram deploy system following modular pattern from WhatsApp/Social deploys. **Telegram Config**: dual feature flag gating (ENABLE_TELEGRAM_DEPLOY + TELEGRAM_BOT_TOKEN from @BotFather), telegram_base_url (default: https://api.telegram.org), default_telegram_chat_id (global fallback). **Telegram Client** (apps/api/app/integrations/telegram_client.py): httpx-based async client with complete media support - sendMessage (text-only), sendPhoto (single image + caption), sendMediaGroup (multiple images with caption on first). TelegramError exception, security (bot_token truncated in logs), 30s timeout. **Telegram Endpoint** (`POST /api/orders/{id}/deploy/telegram`): admin-only, validations (estado=listo, qa_status=ok, product type telegram/bot/messaging), 3-step multi-tenant chat_id fallback (1: deliverable_metadata.telegram_chat_id, 2: tenant.settings.telegram_chat_id, 3: settings.default_telegram_chat_id), deploy_history tracking (channel=telegram, target_system=telegram_bot_api, chat_id, telegram_message_id), datetime ISO serialization. **Status**: BACKEND COMPLETE with full media handling and multi-tenant support. Frontend UI button pending (future). Backward compatible, extensible, production-ready.
*   **WhatsApp Sales Agent Orchestrator - Template Full IntegraIA**: Complete conversational sales agent orchestrator integrating 7 clients (MongoDB, OpenAI, Melvis, Tavily, LinkedIn, Stripe, Cal.com) in 10-step conversation flow. **Architecture**: `WhatsAppSalesAgent` class in `app/templates/whatsapp_template_full_integraia.py` (293 lines). **10-Step Flow**: (1) Webhook → receive message, (2) Upsert user in MongoDB, (3) Insert incoming message, (4) Load/create session, (5) Get context conditionally (message history + optional RAG/web search), (6) OpenAI structured output call, (7) Parse actions (CREATE_OR_UPDATE_LEAD, ENRICH_LEAD, SUGGEST_CAL_LINK, CREATE_STRIPE_CHECKOUT), (8) Update session state, (9) Insert outgoing message, (10) Send reply. **7 Integrations**: MongoDB persistence (users/messages/leads/sessions collections, ENV: MONGODB_URI + MONGODB_DB_NAME), OpenAI sales client with structured JSON output (OPENAI_API_KEY), Melvis RAG/vector search (MELVIS_API_URL + MELVIS_API_KEY + MELVIS_COLLECTION - optional), Tavily web search (TAVILY_API_KEY - optional), LinkedIn lead enrichment (LINKEDIN_API_KEY + LINKEDIN_BASE_URL - optional, auto-triggered when nombre + empresa available), Stripe checkout (STRIPE_SECRET_KEY + STRIPE_PRICE_ID + STRIPE_SUCCESS_URL + STRIPE_CANCEL_URL - optional), Cal.com booking link (CALCOM_BOOKING_LINK). **Key Features**: All clients conditionally initialized (graceful degradation if ENV vars missing), context_needed flags control RAG/web search (no unnecessary API calls), silent automatic LinkedIn enrichment, placeholder replacement + smart URL injection for Cal.com/Stripe, user-friendly Spanish error messages, global singleton instance, async/await throughout, detailed logging. **Usage**: `from app.templates.whatsapp_template_full_integraia import handle_whatsapp_webhook, sales_agent` + startup: `await sales_agent.connect()` + webhook: `reply = await handle_whatsapp_webhook(phone, message)`. **Status**: COMPLETE. Production-ready orchestrator with full integration test successful, LSP clean, ready to connect to WhatsApp webhook endpoint.
*   **Self-Improvement System**: Autonomous code analysis, improvement detection, and API endpoints with an Architect Supervisor and Review Council.
*   **Meta-Agent System**: A specialized agent factory to create and manage various AI agents (e.g., SECURITY, PERFORMANCE, QA) with multi-tenancy.

### Axon Core Project Architecture

Axon Core provides a production-ready API with:
*   **RESTful Design**: Standardized API endpoints.
*   **WebSocket Architecture**: Socket.IO for real-time communication.
*   **Authentication and Authorization**: JWT tokens with role-based access control.
*   **Service Management**: Dual adapter system for systemd and Docker services.
*   **Command Execution**: Securely executes whitelisted commands.
*   **File Management**: Jail system for confined file operations.
*   **LLM Integration**: Multi-provider pattern with adapters for various LLMs.
*   **Metrics and Monitoring**: Real-time system metrics.
*   **Audit Logging**: Detailed JSONL logs for privileged actions.
*   **Configuration Management**: All configuration via environment variables.

## External Dependencies

*   **Core Frameworks & Libraries**: FastAPI, Uvicorn, Pydantic, Python-SocketIO, PyJWT, psutil, docker, httpx, loguru.
*   **Optional External Services / Integrations**: n8n, Ollama, SDXL/Automatic1111, Cloudflare Tunnel, Tailscale.
*   **Cloud LLM APIs**: OpenAI API, Google Gemini API, DeepSeek API.
*   **System Dependencies**: systemd, Docker Engine, nvidia-smi.