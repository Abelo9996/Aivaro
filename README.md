# Aivaro

**AI workflow automation for non-technical founders.**

Describe what you want automated in plain English. Aivaro builds the workflow, connects your tools, and runs it — with approval guardrails so nothing fires without your OK.

> "Automate bookings, payments, follow-ups in plain English."

## What It Does

1. **You describe** → "Every Tuesday, read my contacts sheet and send each person a payment reminder"
2. **AI builds** → Creates a workflow: Schedule → Read Sheet → Template Email → Send Email
3. **You review** → Approve risky steps (sending emails, charging cards) before they run
4. **It runs** → Automatic execution on your schedule, with full logs

## Key Features

- **Chat-first interface** — Describe workflows in plain English, AI generates them
- **Visual workflow editor** — Drag-and-drop React Flow canvas for manual editing
- **18 integrations** — Google, Stripe, Slack, Twilio, Brevo, HubSpot, Shopify, Discord, Airtable, Notion, Calendly, Mailchimp, SendGrid, GitHub, Jira, Linear, Monday, WhatsApp
- **212 MCP tools** — Auto-discovered by the AI generator, no hardcoding needed
- **Approval guardrails** — Sensitive actions (emails, payments, SMS) pause for review
- **For-each iteration** — Read a spreadsheet → automatically process each row
- **Knowledge base** — Store business context, auto-extracted from chat, injected into all AI
- **Free trial** — 7-day trial with usage limits, then paid plans
- **Admin dashboard** — User metrics, DAU/MAU trends, execution stats

## Architecture

```
┌─────────────┐     ┌──────────────────────┐     ┌──────────────┐
│   Vercel     │     │   Railway            │     │  PostgreSQL  │
│  Next.js 14  │────▶│   FastAPI + Python   │────▶│  (Railway)   │
│  App Router  │     │   Port 8080          │     │              │
└─────────────┘     └──────────────────────┘     └──────────────┘
                           │
                    ┌──────┴──────┐
                    │ MCP Servers │ ← 18 provider servers
                    │ (in-process)│   auto-discovered via registry
                    └─────────────┘
```

**Frontend:** Next.js 14 (App Router) + TypeScript + React Flow + Framer Motion
**Backend:** FastAPI + SQLAlchemy + OpenAI GPT-5 + MCP tool registry
**Database:** SQLite (local dev) / PostgreSQL (production)
**Deployment:** Vercel (frontend) + Railway (backend), auto-deploy from `main`

## Project Structure

```
├── api/                          # FastAPI backend
│   ├── app/
│   │   ├── models/               # SQLAlchemy models (User, Workflow, Execution, etc.)
│   │   ├── routers/              # API endpoints
│   │   │   ├── admin.py          # Admin dashboard API
│   │   │   ├── ai.py             # AI workflow generation
│   │   │   ├── approvals.py      # Approval system
│   │   │   ├── auth.py           # Auth (signup, login, OAuth, password reset)
│   │   │   ├── chat.py           # Agentic chat
│   │   │   ├── connections.py    # Integration connections + test/verify
│   │   │   ├── executions.py     # Workflow execution history
│   │   │   ├── knowledge.py      # Knowledge base CRUD + file import
│   │   │   ├── templates.py      # Workflow templates
│   │   │   ├── webhooks.py       # Webhook triggers
│   │   │   └── workflows.py      # Workflow CRUD
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── agentic_chat.py   # Chat agent with tool use
│   │   │   ├── agent_executor.py # Agent tool execution (MCP-based)
│   │   │   ├── ai_generator.py   # AI workflow generation (GPT-5)
│   │   │   ├── node_executor.py  # Node execution engine (~3000 lines)
│   │   │   ├── workflow_runner.py # Workflow orchestration + for-each iteration
│   │   │   ├── plan_limits.py    # Free trial / plan enforcement
│   │   │   └── integrations/     # 18 service-specific API wrappers
│   │   ├── mcp_servers/          # MCP tool servers (212 tools)
│   │   │   ├── base.py           # BaseMCPServer (_register pattern)
│   │   │   ├── registry.py       # MCPToolRegistry (auto-discovery)
│   │   │   └── [provider].py     # 18 provider servers
│   │   └── utils/
│   ├── requirements.txt
│   └── railway.toml
│
├── web/                          # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── (public)/         # Auth pages (login, signup, forgot-password)
│   │   │   ├── admin/            # Admin dashboard
│   │   │   ├── app/              # Main app (dashboard, workflows, connections, etc.)
│   │   │   ├── landing/          # Landing page
│   │   │   └── onboarding/       # User onboarding flow
│   │   ├── components/           # Shared React components
│   │   ├── lib/                  # API client, utilities
│   │   ├── stores/               # Zustand state stores
│   │   └── types/                # TypeScript type definitions
│   └── package.json
│
└── docker-compose.yml
```

## How Workflows Work

### Execution Pipeline

```
User prompt → AI Generator → Post-processors → Workflow JSON → Runner → Node Executor
                  │                  │                              │
                  │                  ├── Approval defaults          ├── For-each iteration
                  │                  ├── Condition edge fixing      ├── Variable interpolation
                  │                  ├── Dead branch pruning        ├── Alias resolution
                  │                  └── Template var validation    └── MCP fallback
                  │
                  └── Dynamic MCP tool injection (only connected providers)
```

### Node Types

**Triggers:** `start_manual`, `start_form`, `start_email`, `start_webhook`, `start_schedule`

**Actions (built-in):**
- `send_email` — Gmail API or SMTP fallback
- `email_template` — Deterministic template rendering (no AI). Use for reminders, confirmations, etc.
- `ai_reply` — AI-generated response (use only when you need dynamic composition)
- `read_sheet` / `append_row` — Google Sheets
- `condition` — Branch workflow based on field values
- `delay` — Wait X minutes/hours/days
- `approval` — Explicit approval gate
- Plus: Google Calendar, Stripe, Slack, Twilio, Airtable, Notion, Calendly, Mailchimp nodes

**Actions (MCP — 212 tools):** Any tool from the 18 MCP servers. The AI generator dynamically discovers tools for connected providers. The node executor routes unknown node types to MCP automatically.

### For-Each Iteration

When `read_sheet` or `airtable_list_records` runs, all downstream nodes execute **once per row**:

```
read_sheet (3 rows) → email_template → send_email
                      ↓ runs 3x        ↓ runs 3x
                      Row 1: {{name}} = "Abel", {{email}} = "abel@..."
                      Row 2: {{name}} = "Hovsep", {{email}} = "hovsep@..."
                      Row 3: {{name}} = "John", {{email}} = "john@..."
```

Sheet headers are auto-mapped to variable names: `"First Name"` → `{{first_name}}`.

### Variable System

Nodes pass data forward via a flat dictionary. Variables are referenced as `{{variable_name}}`.

**3-layer resolution:**
1. **Interpolation** — `{{name}}` → lookup in data dict
2. **Alias resolution** — 100+ aliases across 15 categories (e.g., `{{recipient}}` → `{{email}}`)
3. **Cleanup** — Remove any remaining unresolved `{{var}}` from text before sending

### Approval System

Sensitive nodes auto-flag for approval:
- Email sending (`send_email`, `brevo_send_transactional_email`, `sendgrid_send_email`)
- Payments (`stripe_create_payment_link`, `stripe_create_invoice`)
- SMS/calls (`twilio_send_sms`, `twilio_make_call`)
- Campaigns (`mailchimp_send_campaign`, `brevo_send_campaign_now`)

Workflow pauses at these nodes. User reviews in the Approvals tab, then approves/rejects.

## Integrations (18 Providers)

| Provider | Auth | Tools | Category |
|----------|------|-------|----------|
| Google (Gmail, Calendar, Sheets, Drive) | OAuth | 14 | Core |
| Stripe | API Key | 8 | Core |
| Shopify | API Key | 19 | Core |
| HubSpot | Access Token | 22 | Core |
| Slack | OAuth | 11 | Communication |
| Twilio | API Key | 9 | Communication |
| Discord | Bot Token | 15 | Communication |
| Brevo | API Key | 16 | Communication |
| SendGrid | API Key | 6 | Communication |
| Mailchimp | API Key | 14 | Communication |
| WhatsApp Business | Access Token | 4 | Communication |
| Airtable | API Key | 9 | Productivity |
| Notion | OAuth | 11 | Productivity |
| Calendly | OAuth | 8 | Productivity |
| Jira | API Token | 12 | Productivity |
| GitHub | Access Token | 15 | Productivity |
| Linear | API Key | 10 | Productivity |
| Monday.com | API Key | 9 | Productivity |

### Adding a New Integration

1. Create `api/app/mcp_servers/[provider]_server.py` using `BaseMCPServer`
2. Register tools with `_register(name, description, input_schema, handler)`
3. Add factory to `registry.py` `SERVER_FACTORIES`
4. Add connection entry to `web/src/app/app/connections/page.tsx`

The AI generator, agent executor, and workflow runner auto-discover new tools — no other code changes needed.

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Setup

```bash
# Backend
cd api
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python run.py                # Starts on port 8000

# Frontend (new terminal)
cd web
npm install
npm run dev                  # Starts on port 3000
```

**Test credentials:** `test@aivaro.com` / `test1234`

Database auto-migrates on startup via `main.py` `_run_migrations()`. No Alembic needed for local dev.

### Environment Variables

See `api/.env.example` for the full list. Key ones:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | `sqlite:///./aivaro.db` (local) or PostgreSQL URL |
| `SECRET_KEY` | ✅ | JWT signing key |
| `OPENAI_API_KEY` | ✅ | OpenAI API key (uses GPT-5 for generation, GPT-4o-mini for utilities) |
| `GOOGLE_CLIENT_ID` | For OAuth | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | For OAuth | Google OAuth client secret |
| `FRONTEND_URL` | ✅ | `http://localhost:3000` (local) or Vercel URL |
| `API_URL` | ✅ | `http://localhost:8000` (local) or Railway URL |
| `ADMIN_EMAILS` | For admin | Comma-separated admin emails |

## Production

**Frontend:** Vercel — auto-deploys from `main`, root directory `web`
**Backend:** Railway — auto-deploys from `main`, root directory `api`, port 8080
**Database:** Railway PostgreSQL

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step deployment guide.

### Production URLs

- Frontend: `https://www.aivaro-ai.com`
- Backend: `https://aivaro-production.up.railway.app`
- OAuth callbacks: `https://aivaro-production.up.railway.app/api/connections/{provider}/callback`

## Health Checks

```bash
curl https://your-api.railway.app/health
curl https://your-api.railway.app/health/db
```

## License

MIT
