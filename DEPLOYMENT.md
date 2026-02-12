# Aivaro Deployment Guide

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Vercel       │     │  Railway/Render │     │   PostgreSQL    │
│   (Frontend)    │────▶│     (API)       │────▶│   (Database)    │
│   Next.js 14    │     │    FastAPI      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Step-by-Step Deployment

### 1. Set up PostgreSQL Database

**Option A: Supabase (Free tier available)**
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings > Database > Connection string
4. Copy the URI (starts with `postgresql://`)

**Option B: Neon.tech (Serverless PostgreSQL)**
1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string

### 2. Deploy API to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" > "Deploy from GitHub repo"
3. Select your Aivaro repository
4. Set root directory: `api`
5. Add environment variables:
   ```
   DATABASE_URL=<your-postgresql-url>
   SECRET_KEY=<generate-a-random-32-char-string>
   OPENAI_API_KEY=<your-openai-key>
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   FRONTEND_URL=https://your-app.vercel.app
   API_URL=https://your-api.railway.app
   ```
6. Deploy! Railway will use `railway.toml` for configuration

### 3. Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project" > Import your GitHub repo
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `web`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-api.railway.app
   ```
5. Deploy!

### 4. Update OAuth Redirect URIs

In Google Cloud Console:
1. Go to APIs & Services > Credentials
2. Edit your OAuth 2.0 Client
3. Add Authorized redirect URIs:
   - `https://your-api.railway.app/api/connections/google/callback`
4. Add Authorized JavaScript origins:
   - `https://your-app.vercel.app`

## Environment Variables Reference

### API (Railway/Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key (32+ random chars) |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for AI features |
| `GOOGLE_CLIENT_ID` | ✅ | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | Google OAuth client secret |
| `FRONTEND_URL` | ✅ | Your Vercel frontend URL |
| `API_URL` | ✅ | Your Railway/Render API URL |
| `ALLOWED_ORIGINS` | ❌ | Additional CORS origins (comma-separated) |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | Your API URL (Railway/Render) |

## Post-Deployment Checklist

- [ ] Database migrations ran successfully (check Railway logs)
- [ ] Health check passes: `curl https://your-api.railway.app/health/db`
- [ ] Frontend loads correctly
- [ ] User signup/login works
- [ ] Google OAuth connection works
- [ ] AI workflow generation works
- [ ] Workflows can be created and saved

## Troubleshooting

### API won't start
- Check DATABASE_URL format (must start with `postgresql://`)
- Verify all required environment variables are set
- Check Railway/Render logs for migration errors

### CORS errors
- Ensure FRONTEND_URL matches your Vercel domain exactly
- Add additional domains to ALLOWED_ORIGINS if needed

### OAuth not working
- Verify redirect URIs in Google Cloud Console
- Ensure API_URL matches the actual deployed URL
- Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct

## Useful Commands

```bash
# Check API health
curl https://your-api.railway.app/health
curl https://your-api.railway.app/health/db

# View API docs
open https://your-api.railway.app/docs
```
