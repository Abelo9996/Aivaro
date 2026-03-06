<div align="center">

# 🚀 Aivaro

### AI Workflow Automation — Describe It, Build It, Run It

Describe what you want automated in plain English. Aivaro builds the workflow,
connects your tools, and runs it — with human-in-the-loop approval so nothing fires without your OK.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![212 MCP Tools](https://img.shields.io/badge/MCP_tools-212-purple.svg)]()
[![18 Integrations](https://img.shields.io/badge/integrations-18-orange.svg)]()

[Demo](#demo) · [Features](#-features) · [Quick Start](#-quick-start) · [Architecture](#-architecture) · [Integrations](#-integrations-18-providers) · [Contributing](#-contributing)

</div>

---

<!-- Replace with actual demo GIF/video -->
<!-- ![Aivaro Demo](docs/demo.gif) -->

## How It Works

```
💬 "Every Tuesday, read my contacts sheet and send each person a payment reminder"
```

```
   You describe it          AI builds it             You review it            It runs
┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  Plain English   │──▶│  Schedule → Read  │──▶│  Approve risky   │──▶│  Automatic with   │
│  in chat         │   │  Sheet → Template │   │  steps (emails,  │   │  full execution   │
│                  │   │  → Send Email     │   │  payments, SMS)  │   │  logs & history   │
└─────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘
```

## ✨ Features

🗣️ **Chat-First Interface** — Describe workflows in plain English, AI generates them instantly using GPT-5

🎨 **Visual Workflow Editor** — Drag-and-drop React Flow canvas for manual editing and fine-tuning

🔗 **18 Integrations, 212 Tools** — Google, Stripe, Slack, Twilio, Shopify, HubSpot, Discord, and more — auto-discovered via MCP

🛡️ **Approval Guardrails** — Sensitive actions (emails, payments, SMS) pause for human review before executing

🔄 **For-Each Iteration** — Read a spreadsheet → automatically process each row through downstream nodes

🧠 **Knowledge Base** — Store business context, auto-extracted from chat, injected into all AI systems

⚡ **Smart Variable System** — 3-layer resolution: interpolation → 100+ alias mappings → cleanup

🤖 **Agentic Chat** — AI assistant with tool use that can query your data, run actions, and answer questions

📊 **Admin Dashboard** — User metrics, DAU/MAU trends, execution stats with interactive charts

🔌 **Extensible** — Add a new integration in one file. AI generator, agent, and runner auto-discover it.

## 🎬 Demo

### Chat → Workflow Creation
> Describe what you need in plain English, AI builds the full workflow

![Chat Workflow Creation](web/public/demos/Chat_Workflow_Creation.gif)

### Visual Workflow Editor
> Drag-and-drop canvas with live execution visualization

![Workflows Visualizer](web/public/demos/Workflows_Visualizer.gif)

### Form Input & Execution
> Trigger workflows with form submissions, watch them run step-by-step

![Chat Form Input](web/public/demos/Chat_Form_Input.gif)

### Knowledge Base
> Store business context that gets injected into all AI systems

![Chat Knowledge Base](web/public/demos/Chat_Knowledge_Base.gif)

### Connect Your Tools
> One-click OAuth and API key connections for 18 providers

![Tool Connection](web/public/demos/Tool_Connection.gif)

## 🏁 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### 1. Clone & Setup Backend

```bash
git clone https://github.com/Abelo9996/aivaro.git
cd aivaro

# Backend
cd api
python -m venv venv
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|:--------:|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key (GPT-5 for generation, GPT-4o-mini for utilities) |
| `SECRET_KEY` | ✅ | JWT signing key |
| `DATABASE_URL` | ✅ | `sqlite:///./aivaro.db` (local) or PostgreSQL URL |
| `FRONTEND_URL` | ✅ | `http://localhost:3000` |
| `API_URL` | ✅ | `http://localhost:8000` |
| `GOOGLE_CLIENT_ID` | OAuth | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth | Google OAuth client secret |
| `ADMIN_EMAILS` | Admin | Comma-separated admin emails |

### 3. Run

```bash
# Terminal 1 — Backend (port 8000)
cd api
python run.py

# Terminal 2 — Frontend (port 3000)
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — test credentials: `test@aivaro.com` / `test1234`

> Database auto-migrates on startup. No Alembic needed for local dev.

## 🏗️ Architecture

```
┌─────────────────┐       ┌─────────────────────────┐       ┌──────────────┐
│    Frontend      │       │        Backend           │       │   Database    │
│                  │       │                          │       │              │
│  Next.js 14      │◀─────▶│  FastAPI + Python        │◀─────▶│  PostgreSQL   │
│  App Router      │  API  │  Port 8000/8080          │       │  (Railway)    │
│  React Flow      │       │                          │       │  SQLite (dev) │
│  Framer Motion   │       │  ┌────────────────────┐  │       └──────────────┘
│  Zustand         │       │  │   MCP Tool Registry │  │
│  TypeScript      │       │  │   18 servers        │  │
└─────────────────┘       │  │   212 tools         │  │
                          │  │   Auto-discovery     │  │
                          │  └────────────────────┘  │
                          └─────────────────────────┘
```

### Execution Pipeline

```
User prompt → AI Generator → Post-processors → Workflow JSON → Runner → Node Executor
                  │                  │                              │
                  │                  ├── Approval defaults          ├── For-each iteration
                  │                  ├── Condition edge fixing      ├── Variable interpolation
                  │                  ├── Dead branch pruning        ├── Alias resolution (100+)
                  │                  └── Template var validation    └── MCP fallback execution
                  │
                  └── Dynamic MCP tool injection (only connected providers)
```

### Project Structure

```
aivaro/
├── api/                              # FastAPI backend
│   ├── app/
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── routers/                  # API endpoints (auth, ai, chat, workflows, etc.)
│   │   ├── services/
│   │   │   ├── ai_generator.py       # AI workflow generation (GPT-5)
│   │   │   ├── agentic_chat.py       # Chat agent with tool use
│   │   │   ├── workflow_runner.py    # Workflow orchestration + for-each
│   │   │   ├── node_executor.py      # Node execution engine (~3000 lines)
│   │   │   └── integrations/         # 18 service-specific API wrappers
│   │   ├── mcp_servers/              # MCP tool servers
│   │   │   ├── base.py              # BaseMCPServer (_register pattern)
│   │   │   ├── registry.py          # Auto-discovery registry
│   │   │   └── [provider].py        # One file per provider
│   │   └── utils/
│   └── requirements.txt
│
├── web/                              # Next.js frontend
│   ├── src/
│   │   ├── app/                      # App Router pages
│   │   │   ├── app/                  # Main app (dashboard, workflows, chat)
│   │   │   ├── admin/                # Admin dashboard
│   │   │   └── (public)/             # Auth pages
│   │   ├── components/               # React components
│   │   ├── stores/                   # Zustand state stores
│   │   └── types/                    # TypeScript definitions
│   └── package.json
│
└── docker-compose.yml
```

## 🔗 Integrations (18 Providers)

<table>
<tr><th>Provider</th><th>Auth</th><th>Tools</th><th>Category</th></tr>
<tr><td>🟢 Google (Gmail, Calendar, Sheets, Drive)</td><td>OAuth</td><td>14</td><td>Core</td></tr>
<tr><td>💳 Stripe</td><td>API Key</td><td>8</td><td>Core</td></tr>
<tr><td>🛍️ Shopify</td><td>API Key</td><td>19</td><td>Core</td></tr>
<tr><td>🟠 HubSpot</td><td>Access Token</td><td>22</td><td>Core</td></tr>
<tr><td>💬 Slack</td><td>OAuth</td><td>11</td><td>Communication</td></tr>
<tr><td>📱 Twilio</td><td>API Key</td><td>9</td><td>Communication</td></tr>
<tr><td>🎮 Discord</td><td>Bot Token</td><td>15</td><td>Communication</td></tr>
<tr><td>📧 Brevo</td><td>API Key</td><td>16</td><td>Communication</td></tr>
<tr><td>✉️ SendGrid</td><td>API Key</td><td>6</td><td>Communication</td></tr>
<tr><td>🐵 Mailchimp</td><td>API Key</td><td>14</td><td>Communication</td></tr>
<tr><td>📲 WhatsApp Business</td><td>Access Token</td><td>4</td><td>Communication</td></tr>
<tr><td>📊 Airtable</td><td>API Key</td><td>9</td><td>Productivity</td></tr>
<tr><td>📝 Notion</td><td>OAuth</td><td>11</td><td>Productivity</td></tr>
<tr><td>📅 Calendly</td><td>OAuth</td><td>8</td><td>Productivity</td></tr>
<tr><td>🎯 Jira</td><td>API Token</td><td>12</td><td>Productivity</td></tr>
<tr><td>🐙 GitHub</td><td>Access Token</td><td>15</td><td>Productivity</td></tr>
<tr><td>📐 Linear</td><td>API Key</td><td>10</td><td>Productivity</td></tr>
<tr><td>📋 Monday.com</td><td>API Key</td><td>9</td><td>Productivity</td></tr>
</table>

### Adding a New Integration

Just **one file** — everything else auto-discovers it:

```python
# api/app/mcp_servers/my_provider_server.py
from .base import BaseMCPServer

class MyProviderServer(BaseMCPServer):
    def __init__(self, credentials: dict):
        super().__init__("my_provider")
        self.api_key = credentials["api_key"]
        self._register_tools()

    def _register_tools(self):
        self._register(
            name="my_provider_do_thing",
            description="Does the thing",
            input_schema={"type": "object", "properties": {"param": {"type": "string"}}},
            handler=self._do_thing
        )

    async def _do_thing(self, param: str):
        # Your API call here
        return {"result": "done"}
```

Then add the factory to `registry.py` — the AI generator, agent, and workflow runner pick it up automatically.

## 🧪 How Workflows Work

### Node Types

| Category | Nodes |
|----------|-------|
| **Triggers** | `start_manual`, `start_form`, `start_email`, `start_webhook`, `start_schedule` |
| **Email** | `send_email` (Gmail), `email_template` (deterministic, no AI) |
| **AI** | `ai_reply` (dynamic AI-generated responses) |
| **Data** | `read_sheet`, `append_row` (Google Sheets) |
| **Logic** | `condition` (branching), `delay`, `approval` (explicit gate) |
| **MCP** | Any of 212 tools from 18 providers — auto-routed |

### For-Each Iteration

```
read_sheet (3 rows) → email_template → send_email
                      ↓ runs 3x        ↓ runs 3x
                      Row 1: {{name}} = "Alice"
                      Row 2: {{name}} = "Bob"
                      Row 3: {{name}} = "Charlie"
```

### Variable Resolution (3-Layer)

1. **Interpolation** — `{{name}}` → lookup in execution data
2. **Alias mapping** — `{{recipient}}` → resolves to `{{email}}` (100+ aliases across 15 categories)
3. **Cleanup** — Strips any remaining `{{unresolved}}` before sending

### Approval System

Sensitive nodes auto-flag for human review:
- 📧 Email sends (Gmail, Brevo, SendGrid)
- 💳 Payment actions (Stripe invoices, payment links)
- 📱 SMS/calls (Twilio)
- 📢 Campaigns (Mailchimp, Brevo)

The workflow **pauses** → user reviews in the Approvals tab → approves or rejects → execution continues.

## 🚀 Production Deployment

| Service | Platform | Config |
|---------|----------|--------|
| Frontend | Vercel | Root: `web/`, auto-deploy from `main` |
| Backend | Railway | Root: `api/`, port 8080, auto-deploy from `main` |
| Database | Railway PostgreSQL | Auto-provisioned |

```bash
# Health checks
curl https://your-api.railway.app/health
curl https://your-api.railway.app/health/db
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full step-by-step guide.

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repo
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Good First Issues

- Add a new MCP integration server (see [Adding a New Integration](#adding-a-new-integration))
- Improve workflow templates
- Add more variable aliases
- UI/UX improvements

## 📄 License

[MIT](LICENSE) — use it, fork it, build on it.

---

<div align="center">

**Built by [Abel Yagubyan](https://github.com/Abelo9996)**

If Aivaro helps you, give it a ⭐

</div>
