# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Aivaro, **please do not open a public issue.**

Email us at **security@aivaro-ai.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

We'll acknowledge your report within 48 hours and aim to resolve critical issues within 7 days.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest `main` | ✅ |
| Older commits | ❌ |

We only support the latest version on `main`. If you're self-hosting, keep up to date.

## Security Practices

### Secrets & Credentials

- All secrets are loaded from environment variables — never hardcoded.
- The app **refuses to start** in production without an explicit `SECRET_KEY`.
- User-provided integration credentials (API keys, OAuth tokens) are encrypted at rest in the database.
- Credentials are stripped from API responses — they never reach the frontend.

### Authentication

- JWT-based auth with configurable expiry (default 24h).
- Email verification required on signup.
- Password reset tokens expire after 1 hour.
- Anti-enumeration on forgot-password (same response whether email exists or not).
- OAuth tokens are auto-refreshed; expired tokens are never exposed to clients.

### Authorization

- Admin access gated by `ADMIN_EMAILS` environment variable.
- Plan-based feature gating enforced server-side.
- Workflow approval system for sensitive actions (payments, emails, SMS).

### Third-Party Integrations

- OAuth connections use standard authorization code flow with PKCE where supported.
- API key credentials are stored server-side only.
- Connection test endpoints verify credentials without exposing them.
- MCP tool execution is scoped to the user's connected providers.

### Infrastructure

- Backend: FastAPI on Railway (HTTPS enforced).
- Frontend: Next.js on Vercel (HTTPS enforced).
- Database: PostgreSQL in production with encrypted connections.
- No PII is logged. Sensitive fields are redacted in error responses.

## Responsible Disclosure

We appreciate responsible disclosure and will credit reporters (with permission) in our release notes. We do not currently offer a bug bounty program.
