# Spectrum - Product Requirements Document

## Overview

**Spectrum** is a web application that helps users understand where news articles fall on the political spectrum. Users can analyze articles, discover related coverage from different perspectives, and compare how different outlets cover the same story.

### Vision
Empower readers to understand media bias and seek diverse perspectives on the news they consume.

### Goals
1. **Transparency** - Show users where their news sources fall on the political spectrum
2. **Discovery** - Help users find alternative perspectives on the same story
3. **Comparison** - Reveal how different outlets agree or disagree on key points
4. **Education** - Promote media literacy without pushing any particular viewpoint

---

## Target Audience

- News consumers seeking balanced perspectives
- Students researching media bias
- Researchers studying political discourse
- Anyone wanting to escape their "filter bubble"

---

## MVP Scope

### In Scope (Phase 1)
1. **URL Analysis** - Paste an article URL, get political spectrum position (-1 to +1 scale)
2. **Related Articles** - Find articles on the same topic from other sources
3. **Basic Comparison** - See agreeing/disagreeing points between articles
4. **Spectrum Visualization** - Simple left-right scale with clear markers

### Out of Scope (Future)
- Browse/discover top stories (Phase 2)
- User accounts and saved history (Phase 2)
- Chrome browser extension (Phase 2)
- Native mobile apps (Phase 3)
- Advanced multi-axis political compass (Future)

---

## Features

### 1. Article Analysis

**User Flow:**
1. User pastes article URL
2. System fetches and parses article content
3. AI analyzes political leaning across multiple dimensions
4. Display score on spectrum with confidence indicator

**Political Spectrum Score:**
- Scale: -1.0 (far left) to +1.0 (far right), 0 = center
- Display labels: Far Left | Left | Slight Left | Center | Slight Right | Right | Far Right

**Analysis Criteria (equally weighted, averaged for final score):**
| Criterion | Description |
|-----------|-------------|
| Language & Framing | Word choice, rhetorical framing, and use of charged/loaded terms |
| Source Selection | Which experts, studies, or organizations are cited |
| Topic Emphasis | What topics are highlighted vs downplayed or omitted |
| Tone & Objectivity | Balance between factual reporting and emotional appeals |
| Source Reputation | Historical political leaning of the publication |

**Score Calculation:** The overall political leaning score is calculated as the average of the 5 criteria scores. This provides transparency - users can see exactly why an article received its score.

**Future Investigation:** Whether criteria should be weighted differently (e.g., Source Reputation having more influence than Tone) is flagged for future analysis.

**Confidence Scoring:**
- 0-100% confidence displayed to user
- Lower confidence = less certainty in the score
- Transparency about methodology and limitations

### 2. Topic Extraction & Related Articles

**Functionality:**
- Extract primary topic, subtopics, and keywords from analyzed article
- Search news APIs for related articles on the same topic
- Return 3-5 related articles from diverse sources
- Show each related article's spectrum position

**Article Sources:**
- Primary: NewsAPI.org (free tier: 100 requests/day)
- Secondary: GNews API (extensible)
- Future: RSS feeds, additional aggregators

### 3. Article Comparison

**Three Levels of Detail (Progressive Disclosure):**

**Level 1: Summary (Default)**
- Both articles on same spectrum visualization
- Bullet points of key agreements
- Bullet points of key disagreements

**Level 2: Side-by-Side**
- Two-column layout showing each article's position
- Main arguments from each
- Sources cited by each

**Level 3: Interactive Diff**
- Topic-by-topic breakdown
- Expandable sections showing exact quotes
- Visual indication of where they diverge

### 4. Spectrum Visualization

**Design Principles:**
- Neutral colors (avoid red/blue political connotations)
- Clear, accessible labels
- Touch-friendly for mobile
- Confidence range visualization (subtle blur/range indicator)

**Visual Elements:**
- Gradient track: Blue (left) → Slate (center) → Orange (right)
  - Far Left: `#1e40af` (Blue-800)
  - Left: `#2563eb` (Blue-600)
  - Slight Left: `#3b82f6` (Blue-500)
  - Center: `#64748b` (Slate-500)
  - Slight Right: `#f59e0b` (Amber-500)
  - Right: `#f97316` (Orange-500)
  - Far Right: `#ea580c` (Orange-600)
- Marker showing article position
- Labels at key positions (-1, -0.5, 0, +0.5, +1)
- Confidence indicator badge

### 5. Documentation Viewer (Implemented)

**Functionality:**
- In-app access to all project documentation via header tabs
- Documents available: README, PRD, Architecture, Diagrams, Tech Decisions
- Full markdown rendering with GitHub-flavored markdown support
- Mermaid diagram rendering for architecture visualizations
- GitHub repository link in header

**Technical Implementation:**
- Backend: `/api/v1/docs/{doc_name}` endpoint serves markdown files
- Frontend: `MarkdownViewer` component with react-markdown and remark-gfm
- Diagrams: `MermaidDiagram` component with custom light theme for readability

---

## Technical Architecture

### Stack Overview

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Backend | Python + FastAPI | Great for ML/NLP, async support, rapid development |
| Frontend | React + TypeScript | Large ecosystem, good for complex UIs |
| Styling | Tailwind CSS + shadcn/ui | Utility-first, accessible components |
| State | Zustand + TanStack Query | Minimal boilerplate, excellent caching |
| AI | Groq API (free tier) | Fast inference, generous free tier (14,400 req/day) |
| News API | NewsAPI.org | Structured data, free tier available |
| Cache | In-memory (Redis later) | Start simple, scale when needed |

### AI Provider Strategy

**Primary: Groq Free Tier**
- Model: `llama-3.3-70b-versatile`
- 14,400 requests/day free
- Fast inference (~500ms)
- No credit card required

**Swappable Architecture:**
```
AIProviderInterface (abstract)
├── GroqProvider (primary)
├── ClaudeProvider (future)
└── OpenAIProvider (future)
```

Change provider via environment variable - no code changes needed.

### Caching Strategy

**Multi-Layer Cache:**
| Layer | TTL | Purpose |
|-------|-----|---------|
| Article Content | 1 hour | Avoid re-scraping |
| Analysis Results | 24 hours | Avoid re-analyzing |
| Search Results | 15 minutes | Fresh but not spammy |
| Related Articles | 30 minutes | Balance freshness/cost |

**Cost Mitigation:**
- Cache aggressively to minimize API calls
- Semantic caching for similar articles (future)
- Pre-computed source baselines for known outlets

---

## Backend Architecture

### Project Structure
```
spectrum/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment settings
│   ├── api/
│   │   └── routes/
│   │       ├── articles.py     # Analysis endpoints
│   │       ├── comparisons.py  # Comparison endpoints
│   │       └── health.py       # Health checks
│   ├── core/
│   │   ├── entities/           # Domain models
│   │   ├── interfaces/         # Abstract interfaces
│   │   └── use_cases/          # Business logic
│   ├── services/
│   │   ├── ai/                 # AI providers (Groq, etc.)
│   │   ├── fetchers/           # Article scraping
│   │   ├── aggregators/        # News APIs
│   │   └── cache/              # Caching layer
│   └── schemas/                # Request/Response DTOs
├── tests/
├── docker/
└── pyproject.toml
```

### Core API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/articles/analyze` | POST | Analyze article from URL |
| `/api/v1/articles/related` | POST | Find related articles |
| `/api/v1/articles/sources` | GET | Get supported/blocked sources list |
| `/api/v1/comparisons` | POST | Compare 2-5 articles |
| `/api/v1/comparisons/with-related` | POST | Full workflow: analyze + find + compare |
| `/api/v1/docs/{doc_name}` | GET | Get documentation content |
| `/api/v1/health` | GET | Health check |

---

## Frontend Architecture

### Project Structure
```
spectrum-web/
├── src/
│   ├── app/                    # App setup, providers
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── layout/             # Header, Footer, etc.
│   │   └── common/             # Shared components
│   ├── features/
│   │   ├── analysis/           # URL analysis feature
│   │   ├── spectrum/           # Spectrum visualization
│   │   ├── related-articles/   # Related articles list
│   │   └── comparison/         # Comparison views
│   ├── hooks/                  # Shared hooks
│   ├── stores/                 # Zustand stores
│   └── lib/                    # Utilities
└── package.json
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `UrlInputForm` | Primary entry point for analysis |
| `SpectrumScale` | Core visualization component (blue→slate→orange gradient) |
| `ConfidenceIndicator` | Shows reliability of analysis |
| `ScoreBreakdown` | Expandable accordion showing 5 criteria scores with explanations |
| `MiniSpectrum` | Compact spectrum bar for criterion scores |
| `RelatedArticleCard` | Preview of related article with mini-spectrum |
| `ComparisonView` | Progressive disclosure comparison (3 levels) |
| `ComparisonTray` | Bottom tray for collecting articles to compare |
| `DetailLevelToggle` | Switch between Summary/Side-by-Side/Diff |
| `MarkdownViewer` | Documentation renderer with Mermaid support |
| `MermaidDiagram` | Renders Mermaid diagrams with custom theme |

### State Management

| State Type | Solution | Examples |
|------------|----------|----------|
| Server State | TanStack Query | API responses, analysis results |
| UI State | Zustand | Selected articles, detail level |
| Local State | useState | Form inputs, tooltips |

---

## Bias Mitigation & Transparency

### Approach
1. **Show your work** - Expandable "How was this score calculated?" section displays individual criterion scores with explanations. Overall score is the mathematical average of 5 criteria, so users can verify the calculation.
2. **Acknowledge uncertainty** - Clear confidence indicators
3. **Explain methodology** - Each criterion includes a brief AI-generated explanation
4. **Avoid inflammatory language** - "Left-leaning" not "biased"
5. **Neutral presentation** - No red/blue colors, balanced labels (blue→slate→orange gradient)

### Disclaimer (Always Visible)
> This analysis is generated by AI and represents one interpretation of the article's content. Political spectrum placement is inherently subjective. Use this tool as one of many resources for media literacy.

### Calibration
- Test against known articles from across the spectrum
- Monitor for drift over time
- Allow user feedback (future)

---

## Implementation Plan

### Phase 1: Foundation (MVP Core)
1. Set up Python backend with FastAPI
2. Implement article fetching/scraping
3. Integrate Groq AI provider with analysis prompts
4. Build core API endpoints (analyze, health)
5. Set up React frontend with Vite
6. Build UrlInputForm component
7. Build SpectrumScale visualization
8. Connect frontend to backend
9. Add loading states and error handling
10. Basic mobile responsiveness

### Phase 2: Related & Compare
1. Integrate NewsAPI for related articles
2. Implement topic extraction
3. Build RelatedArticleCard component
4. Implement comparison API endpoint
5. Build ComparisonSummary (Level 1)
6. Build SideBySideView (Level 2)
7. Build InteractiveDiff (Level 3)
8. Add ConfidenceIndicator component

### Phase 3: Polish & Deploy
1. Add in-memory caching layer
2. Comprehensive error handling
3. Accessibility audit
4. Performance optimization
5. Docker configuration
6. Deploy to free hosting (Render/Railway + Vercel)

### Phase 4: Extensions (Future)
1. Chrome browser extension
2. User accounts with saved history
3. Browse top stories feature
4. Redis caching for production scale

---

## Key Files to Create

### Backend (Priority Order)
1. `app/config.py` - Settings and environment config
2. `app/core/interfaces/ai_provider.py` - AI provider abstraction
3. `app/services/ai/groq_provider.py` - Groq implementation
4. `app/services/fetchers/web_scraper.py` - Article fetching
5. `app/core/use_cases/analyze_article.py` - Main analysis logic
6. `app/api/routes/articles.py` - API endpoints
7. `app/main.py` - FastAPI app setup

### Frontend (Priority Order)
1. `src/features/spectrum/components/SpectrumScale.tsx` - Core visualization
2. `src/features/analysis/components/UrlInputForm.tsx` - Main input
3. `src/features/analysis/hooks/useAnalyzeArticle.ts` - API integration
4. `src/features/spectrum/components/ConfidenceIndicator.tsx` - Trust indicator
5. `src/features/related-articles/components/RelatedArticleCard.tsx` - Related display
6. `src/features/comparison/components/ComparisonView.tsx` - Comparison UI

---

## Verification & Testing

### Manual Testing
1. Analyze article from a known left-leaning source (e.g., The Guardian - fully supported)
2. Analyze article from a known right-leaning source (e.g., Fox News - fully supported)
3. Analyze article from a known center source (e.g., BBC - fully supported)
4. Verify spectrum positions match expected ranges
5. Test related article discovery on a trending topic
6. Test comparison between two articles on same topic
7. Verify mobile responsiveness on phone viewport
8. Test error states (invalid URL, paywall, network error)

**Note on Source Compatibility:** Some news sites block automated access. For reliable testing, use fully supported sources: NPR, BBC, CNN, Fox News, Breitbart, LA Times, The Guardian. Sites like HuffPost, AP News, and Vox have partial support (JavaScript-heavy). Sites like NY Times, Washington Post, and WSJ are blocked. See README.md for the full compatibility list.

### Automated Testing
1. Unit tests for political analysis score calculation
2. Unit tests for topic extraction
3. Integration tests for API endpoints
4. Mock tests for AI provider abstraction
5. Component tests for SpectrumScale positioning

### Calibration Checks
| Source | Expected Range | Purpose | Compatibility |
|--------|----------------|---------|---------------|
| BBC | -0.15 to 0.15 | Verify center detection | Fully supported |
| The Guardian | -0.3 to 0.0 | Verify center-left detection | Fully supported |
| Fox News | 0.3 to 0.6 | Verify right detection | Fully supported |
| Breitbart | 0.5 to 0.8 | Verify far-right detection | Fully supported |

*Note: Original calibration sources (AP News, Mother Jones, National Review) have partial support due to JavaScript-heavy sites. The above alternatives provide reliable, repeatable testing.*

---

## Environment Variables

```env
# AI Providers
GROQ_API_KEY=           # Required - get free at https://console.groq.com/keys
ANTHROPIC_API_KEY=      # Optional - for Claude (future)
OPENAI_API_KEY=         # Optional - for OpenAI (future)

# News APIs
NEWSAPI_KEY=            # Required - get free at https://newsapi.org/register
GNEWS_API_KEY=          # Optional - backup news source

# App Settings
DEFAULT_AI_PROVIDER=groq
CACHE_BACKEND=memory    # memory or redis
DEBUG=true
```

---

## Success Metrics

### MVP Success Criteria
- [ ] Can analyze any news article URL in <10 seconds
- [ ] Political score aligns with expected ranges for known sources
- [ ] Can find 3+ related articles on the same topic
- [ ] Comparison clearly shows agreements and disagreements
- [ ] Works on mobile devices
- [ ] Confidence indicator shows appropriate uncertainty

### Quality Bar
- Clean, professional UI suitable for portfolio
- Code follows clean architecture principles
- Comprehensive error handling
- TypeScript types throughout frontend
- Python type hints throughout backend

---

## Open Questions & Decisions

### Resolved
- **App name**: Spectrum
- **Platform**: Web app first, Chrome extension later
- **Tech stack**: Python/FastAPI + React/TypeScript
- **AI provider**: Groq free tier (swappable)
- **Spectrum type**: Simple left-right scale
- **Auth**: None for MVP, optional accounts later
- **Gradient colors**: Blue (left) → Slate (center) → Orange (right) - chosen for neutrality
- **Color scheme**: Slate grays with blue accents (professional, neutral aesthetic)
- **Loading animation**: Spinning border animation
- **Error handling**: Structured error responses with user-friendly messages and retry options

### To Decide During Implementation
- Rate limiting strategy for API
- User feedback mechanism for analysis accuracy
