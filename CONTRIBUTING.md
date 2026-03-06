# Contributing to Aivaro

Thanks for your interest in contributing! This guide will get you up and running.

## Getting Started

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 18+** (frontend)
- **Git**

### Local Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Abelo9996/Aivaro.git
   cd Aivaro
   ```

2. **Backend**
   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Fill in your .env values (at minimum OPENAI_API_KEY)
   uvicorn app.main:app --reload --port 8000
   ```

3. **Frontend**
   ```bash
   cd web
   npm install
   cp .env.example .env.local
   npm run dev
   ```

4. **Open** `http://localhost:3000`

### Environment Variables

See `api/.env.example` and `web/.env.example` for all available config. At minimum you need:

- `OPENAI_API_KEY` — required for AI features
- `SECRET_KEY` — auto-generated in dev, **must** be set in production

## Project Structure

```
api/                    # FastAPI backend
  app/
    main.py             # App entrypoint
    config.py           # Settings (env vars)
    models/             # SQLAlchemy models
    routers/            # API endpoints
    services/           # Business logic
    mcp_servers/        # MCP tool integrations (18 providers)
web/                    # Next.js frontend
  src/
    app/                # App router pages
    components/         # React components
    lib/                # Utilities, API client
```

## Development Workflow

1. **Create a branch** off `main`:
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make your changes.** Keep commits focused and descriptive.

3. **Test locally** — make sure the app runs, your feature works end-to-end.

4. **Push and open a PR** against `main`.

## Code Guidelines

### Backend (Python / FastAPI)

- Use type hints everywhere.
- No emoji in `print()` statements (Windows cp1252 encoding breaks them).
- Settings come from env vars via `config.py` — never hardcode secrets.
- New integrations: add an MCP server in `app/mcp_servers/` — the system auto-discovers it.

### Frontend (TypeScript / Next.js)

- Functional components with hooks.
- Use the existing `api` client in `lib/api.ts` for backend calls.
- Tailwind for styling — no CSS modules.
- No markdown tables in user-facing UI (Discord/WhatsApp don't render them).

### Security

- **Never commit secrets, API keys, or credentials.** Use env vars.
- **Never commit `.env` files.** They're gitignored for a reason.
- Sensitive node types (email, payments, SMS) must default to requiring approval.
- User-supplied credentials are stripped of API keys on save.

## Adding a New Integration

1. Create `api/app/mcp_servers/your_provider.py` extending `BaseMCPServer`
2. Add the provider to the factory in `api/app/mcp_servers/registry.py`
3. Add connection config in `web/src/app/app/connections/page.tsx`
4. That's it — the agent, workflow runner, and AI generator auto-discover new tools.

## Reporting Issues

Open a GitHub issue with:
- What you expected
- What happened
- Steps to reproduce
- Screenshots if relevant

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
