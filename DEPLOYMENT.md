# Deployment Guide

## Current Production Setup

| Service | Platform | Domain |
|---------|----------|--------|
| Frontend | Vercel | `www.aivaro-ai.com` |
| Backend | Railway | `aivaro-production.up.railway.app` |
| Database | Railway PostgreSQL | Auto-configured |

Both auto-deploy from `main` branch on push.

## Initial Setup

### 1. Database (Railway PostgreSQL)

Railway provisions PostgreSQL automatically. The `DATABASE_URL` is injected as an env var.

The backend auto-migrates on startup — `_run_migrations()` in `main.py` uses `ALTER TABLE` statements with column existence checks. No Alembic needed.

### 2. Backend (Railway)

1. Connect GitHub repo at [railway.app](https://railway.app)
2. Set root directory: `api`
3. Railway uses `railway.toml` for build/start config
4. Add environment variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (auto from Railway) |
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `OPENAI_API_KEY` | Your OpenAI key |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `FRONTEND_URL` | `https://www.aivaro-ai.com` |
| `API_URL` | `https://aivaro-production.up.railway.app` |
| `ALLOWED_ORIGINS` | `https://www.aivaro-ai.com,https://aivaro-ai.com,http://localhost:3000` |
| `ADMIN_EMAILS` | Comma-separated admin email addresses |
| `SMTP_HOST` | SMTP server for email verification (optional) |
| `SMTP_PORT` | SMTP port (optional) |
| `SMTP_USER` | SMTP username (optional) |
| `SMTP_PASS` | SMTP password (optional) |

### 3. Frontend (Vercel)

1. Import GitHub repo at [vercel.com](https://vercel.com)
2. Framework: Next.js, root directory: `web`
3. Environment variable:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://aivaro-production.up.railway.app` |

### 4. OAuth Configuration

In [Google Cloud Console](https://console.cloud.google.com/apis/credentials):

**Authorized redirect URIs:**
```
https://aivaro-production.up.railway.app/api/connections/google/callback
```

**Authorized JavaScript origins:**
```
https://www.aivaro-ai.com
https://aivaro-ai.com
```

Other OAuth providers (Slack, Notion, Calendly) follow the same pattern:
```
https://aivaro-production.up.railway.app/api/connections/{provider}/callback
```

### 5. Admin Access

1. Set `ADMIN_EMAILS=your@email.com` on Railway
2. Log in to the app
3. Visit `/admin` and click "Activate Admin Access"

## Connection Auth Types

| Type | Providers | How Users Connect |
|------|-----------|-------------------|
| OAuth | Google, Slack, Notion, Calendly | Click Connect → OAuth redirect flow |
| API Key | Stripe, Brevo, SendGrid, Airtable, Mailchimp, Linear, Monday | Paste key in modal |
| Access Token | HubSpot, GitHub, WhatsApp | Paste token in modal |
| Bot Token | Discord | Paste bot token (+ optional guild ID) |
| Multi-field | Twilio (SID + token), Shopify (domain + token), Jira (domain + email + token) | Comma-separated in modal |

All API keys are stripped of whitespace on save. Each connection has a **Test** button that verifies credentials against the provider's API.

## Monitoring

### Health Checks
```bash
curl https://aivaro-production.up.railway.app/health
curl https://aivaro-production.up.railway.app/health/db
```

### Railway Logs
Check Railway dashboard for:
- Startup logs (migrations, template seeding)
- Email/schedule trigger polling (every 60s)
- Workflow execution logs
- MCP routing logs (`Routing to MCP server (brevo)`)

### Admin Dashboard
Visit `/admin` for:
- Total users, DAU, MAU
- Workflow and execution counts
- 30-day trend charts
- Per-user breakdown

## Troubleshooting

### CORS Errors
Ensure `ALLOWED_ORIGINS` includes your frontend domain(s). The backend also auto-allows `FRONTEND_URL`.

### OAuth Token Expired
Google OAuth tokens auto-refresh via `_request()` interceptor in `google_service.py`. Requires `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` env vars on Railway.

### Connection Test Fails
- **401**: API key is invalid or expired. Disconnect and reconnect with a fresh key.
- **Timeout**: Provider API is slow. Retry.
- **Empty key warning in logs**: Credentials stored under wrong field name.

### Workflows Not Triggering
- **Email triggers**: Check Railway logs for `[Email Trigger]` lines. "plan limit reached" means user exceeded free trial.
- **Schedule triggers**: Check `[Schedule Trigger]` logs. Time is in user's timezone (default Pacific).

### MCP Tool Not Found
If a workflow uses an MCP node type and gets "No MCP tool found":
1. Check the connection exists and is active for that provider
2. Verify the MCP server file has the tool registered via `_register()`
3. Check `registry.py` `SERVER_FACTORIES` includes the provider

## Database

### Migrations
Auto-run on startup. New columns are added via `_run_migrations()` in `main.py`:
```python
columns = [c["name"] for c in inspect(engine).get_columns("table_name")]
if "new_column" not in columns:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE table_name ADD COLUMN new_column TYPE DEFAULT value"))
```

### Models
- `User` — email, password, plan, trial, admin flag, onboarding status
- `Workflow` — name, nodes/edges JSON, triggers, owner
- `Execution` — status, trigger data, execution nodes, timing
- `ExecutionNode` — per-node results within an execution
- `Connection` — provider type, encrypted credentials, user
- `Conversation` / `Message` — chat history
- `KnowledgeEntry` — business context entries
- `Approval` — pending/approved/rejected actions
- `AuditLog` — system event log
