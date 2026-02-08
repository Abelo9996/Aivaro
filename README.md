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

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Setup

1. **Clone and setup environment**
   ```bash
   cp .env.example .env
   ```

2. **Start the database**
   ```bash
   docker-compose up -d
   ```

3. **Setup the API**
   ```bash
   cd api
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

4. **Setup the Web App**
   ```bash
   cd web
   npm install
   npm run dev
   ```

5. **Open your browser**
   - Web App: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## Project Structure

- `/api` - FastAPI backend with workflow runner
- `/web` - Next.js 14 frontend with React Flow canvas
- `/shared` - Shared TypeScript types

## License

MIT
