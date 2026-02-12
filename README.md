# Aivaro

**n8n, but built for non-technical founders.**

Aivaro is a visual workflow automation tool designed for founders who want to automate their business without needing to understand APIs, webhooks, or technical jargon.

## Features

- 🎨 **Visual Workflow Builder** - Drag-and-drop interface powered by React Flow
- 📝 **Plain English Generation** - Describe what you want, and AI creates the workflow
- 🚀 **Templates** - Start from proven templates in under 2 minutes
- ✅ **Approval Guardrails** - Review risky actions before they happen
- 🧪 **Test Runs** - Safely test workflows with mock data
- 📊 **Run History** - Track every execution with detailed logs

## 🚀 Production Deployment

### Frontend (Vercel)

1. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com) and import your GitHub repo
   - Set root directory to `web`
   
2. **Configure Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com
   ```

3. **Deploy!** Vercel handles the rest automatically.

### Backend (Railway / Render)

#### Option A: Railway
1. Connect your GitHub repo to [Railway](https://railway.app)
2. Set root directory to `api`
3. Add a PostgreSQL database
4. Set environment variables (see `api/.env.example`)
5. Railway will auto-deploy using `railway.toml`

#### Option B: Render
1. Connect your GitHub repo to [Render](https://render.com)
2. Use the Blueprint in `api/render.yaml` for one-click setup
3. Set environment variables in the dashboard

### Required Environment Variables (API)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (generate a secure random string) |
| `OPENAI_API_KEY` | OpenAI API key for AI features |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `FRONTEND_URL` | Your Vercel frontend URL |
| `API_URL` | Your Railway/Render backend URL |

---

## 🛠 Local Development

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Option 1: Docker (Full Stack)

```bash
# Clone and configure environment
cp api/.env.example api/.env
# Edit api/.env with your API keys

# Start all services (PostgreSQL + API + Web)
docker-compose up -d

# Open your browser
# Web App: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

1. **Start PostgreSQL (or use SQLite for dev)**
   ```bash
   docker-compose up -d postgres
   ```

2. **Setup the API**
   ```bash
   cd api
   cp .env.example .env
   # Edit .env with your API keys
   
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Run migrations
   alembic upgrade head
   
   # Seed templates
   python -c "from app.seed.templates import seed_templates; seed_templates()"
   
   # Start the API
   python run.py
   ```

3. **Setup the Web App**
   ```bash
   cd web
   cp .env.example .env.local
   npm install
   npm run dev
   ```

4. **Open your browser**
   - Web App: http://localhost:3000
   - API Docs: http://localhost:8000/docs

---

## 📁 Project Structure

```
├── api/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   └── requirements.txt
│
├── web/                 # Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js app router
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities
│   └── package.json
│
└── docker-compose.yml   # Local development stack
```

---

## 🔧 Database Configuration

### Local Development (SQLite)
```env
DATABASE_URL=sqlite:///./aivaro.db
```

### Production (PostgreSQL)
```env
# Supabase
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Neon.tech
DATABASE_URL=postgresql://user:[password]@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Railway (auto-configured)
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

---

## 🏥 Health Checks

- Basic: `GET /health`
- Database: `GET /health/db`

---

## 📄 License

MIT

## Environment Variables

See `api/.env.example` and `web/.env.example` for all required configuration.

## Health Checks

- Basic: `GET /health`
- With DB: `GET /health/db`

## License

MIT
