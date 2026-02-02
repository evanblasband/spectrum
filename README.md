# Spectrum

A web application that analyzes news articles to show where they fall on the political spectrum, finds related coverage from other sources, and compares how different outlets cover the same story.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys (free):
  - [Groq API Key](https://console.groq.com/keys) - for AI analysis
  - [NewsAPI Key](https://newsapi.org/register) - for finding related articles

### Backend Setup

```bash
# From the project root directory

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Run the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/v1/health`

### Frontend Setup

```bash
# From the project root directory
cd spectrum-web

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
spectrum/
├── app/                    # Python backend (FastAPI)
│   ├── api/                # API routes
│   ├── core/               # Business logic
│   ├── services/           # External integrations
│   └── schemas/            # Data models
├── spectrum-web/           # React frontend
│   └── src/
│       ├── features/       # Feature modules
│       └── components/     # Shared components
├── docker/                 # Docker configuration
├── prd.md                  # Product Requirements Document
├── ARCHITECTURE.md         # Backend Architecture Guide
└── diagrams.md             # Mermaid diagrams
```

## Documentation

### prd.md - Product Requirements Document

The PRD contains the complete product specification:

- **Overview & Vision** - What Spectrum does and why
- **MVP Scope** - Features for initial release (URL analysis, related articles, comparison)
- **Feature Specifications** - Detailed user flows and functionality
- **Political Spectrum Analysis** - How the AI determines political leaning (5 weighted dimensions)
- **Technical Stack** - Python/FastAPI backend, React/TypeScript frontend, Groq AI
- **Implementation Plan** - Step-by-step build guide in 4 phases
- **Verification Plan** - How to test the application works correctly
- **Bias Mitigation** - Strategies for transparent, fair analysis

### ARCHITECTURE.md - Backend Architecture Guide

The architecture document provides detailed technical design:

- **Architecture Principles** - Clean architecture, dependency injection, strategy pattern
- **Project Structure** - Directory layout and file organization
- **API Endpoints** - All REST endpoints with request/response schemas
- **Service Layer** - How components interact (fetchers, AI providers, aggregators, cache)
- **Data Models** - Pydantic schemas for articles, analysis, comparisons
- **AI Provider Abstraction** - Swappable AI providers (Groq, Claude, OpenAI)
- **Caching Strategy** - Multi-layer caching to minimize API costs
- **Configuration** - Environment variables and settings
- **Docker Setup** - Containerization for deployment

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/articles/analyze` | POST | Analyze article political leaning |
| `/api/v1/articles/related` | POST | Find related articles |
| `/api/v1/comparisons` | POST | Compare multiple articles |

## Environment Variables

```env
# Required
GROQ_API_KEY=your_groq_key
NEWSAPI_KEY=your_newsapi_key

# Optional
DEFAULT_AI_PROVIDER=groq
CACHE_BACKEND=memory
DEBUG=true
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: React 18, TypeScript, Tailwind CSS, shadcn/ui
- **AI**: Groq API (llama-3.3-70b-versatile)
- **News Data**: NewsAPI.org
- **State Management**: Zustand + TanStack Query
