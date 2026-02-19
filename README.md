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
├── TECH_DECISIONS.md       # Technology Decision Rationale
└── diagrams.md             # Mermaid diagrams
```

## Documentation

### TECH_DECISIONS.md - Technology Decisions

Explains why each technology was chosen over alternatives:

- **Language & Framework choices** - Python/FastAPI over Node/Django, React over Vue/Svelte
- **Tooling decisions** - Vite, TypeScript, Tailwind, Zustand, TanStack Query
- **External services** - Groq AI, NewsAPI, caching strategy
- **Architecture patterns** - Clean Architecture, Strategy pattern, dependency injection
- **Tradeoffs** - What we gain and lose with each choice, when to choose differently

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

## Features

### Implemented (MVP)

- **Article Analysis**: Paste any news article URL to get political spectrum analysis
  - Score from -1 (far left) to +1 (far right)
  - Confidence indicator with info tooltip explaining methodology
  - Brief article summary generated from topics and key points
  - AI-generated reasoning for the political score
  - Topic and keyword extraction
  - Key points identification

- **Related Articles**: Automatically finds related coverage from other sources
  - Uses NewsAPI to search by extracted keywords
  - One-click analyze for any related article

- **Search History**: Quick access to previously analyzed articles
  - Shows last 10 articles searched (persisted in localStorage)
  - Visual success/failure indicators
  - Click to re-analyze, or remove individual entries
  - Clear all history option

- **Article Comparison**: Compare multiple articles side-by-side
  - Add analyzed articles to comparison list
  - Visual spectrum showing all articles' positions
  - Summary of political spread
  - Shared topics identification

### Not Yet Implemented

- User accounts and saved history
- Chrome browser extension
- Redis caching (uses in-memory cache)
- Advanced comparison (agreements/disagreements extraction)

### Roadmap / Planned Work

- [ ] **Better error handling** - Improve error messages and user notifications throughout the app (network errors, API failures, scraping issues)
- [ ] **Fix comparison feature** - Investigate and fix issues with the article comparison functionality
- [ ] **Security audit** - Review input validation, XSS prevention, API key handling, dependency vulnerabilities
- [ ] **Hosting setup** - Deploy to a hosting platform (Railway, Render, Vercel) for portfolio demonstration

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **AI**: Groq API (llama-3.3-70b-versatile)
- **News Data**: NewsAPI.org
- **State Management**: Zustand + TanStack Query
- **Caching**: In-memory with TTL (cachetools)
