# Technology Decisions

This document explains the technology choices made for Spectrum, including the reasoning, alternatives considered, and tradeoffs. Understanding these decisions helps when extending the project or applying similar patterns elsewhere.

**Living Document**: When decisions change, we document both the change and the reasoning. See [Decision History](#decision-history) for the evolution of choices over time.

---

## Decision History

This section tracks changes to technology decisions over time. Each entry includes what changed, why, and lessons learned.

### Format
```
### [Date] - [Component] - [Change Summary]
**Previous**: What we were using
**New**: What we changed to
**Trigger**: What prompted the change
**Reasoning**: Why we made this change
**Lessons**: What we learned
```

### Change Log

#### 2026-02-03 - Initial Architecture
**Status**: Baseline established

All initial technology decisions documented below. This represents the MVP architecture optimized for:
- Free-tier API usage (Groq, NewsAPI)
- Rapid development and iteration
- Single-developer workflow
- Learning and demonstration purposes

Future changes will be logged here with full context.

---

#### Template for Future Changes

<!--
Copy this template when recording a decision change:

#### [YYYY-MM-DD] - [Component] - [Brief Description]
**Previous**: [What was being used]
**New**: [What it changed to]
**Trigger**: [What prompted the evaluation - performance issue, cost, feature need, etc.]
**Reasoning**: [Why the new choice is better for current needs]
**Migration notes**: [Any steps taken to migrate, breaking changes, etc.]
**Lessons**: [What we learned that might inform future decisions]
-->

---

## Table of Contents

0. [Decision History](#decision-history)
1. [Backend Language & Framework](#1-backend-language--framework)
2. [Frontend Framework](#2-frontend-framework)
3. [Frontend Build Tool](#3-frontend-build-tool)
4. [Type Systems](#4-type-systems)
5. [Styling Approach](#5-styling-approach)
6. [State Management](#6-state-management)
7. [Server State & Data Fetching](#7-server-state--data-fetching)
8. [AI Provider](#8-ai-provider)
9. [News Data Source](#9-news-data-source)
10. [Caching Strategy](#10-caching-strategy)
11. [Web Scraping](#11-web-scraping)
12. [HTTP Client](#12-http-client)
13. [Architecture Patterns](#13-architecture-patterns)
14. [Containerization](#14-containerization)

---

## 1. Backend Language & Framework

### Decision: Python with FastAPI

### Why Python?
- **AI/ML ecosystem**: Best-in-class libraries for working with AI APIs, text processing, and data manipulation
- **Rapid development**: Quick to prototype and iterate, which suits an MVP
- **Readability**: Clean syntax makes the codebase approachable for learning

### Why FastAPI over alternatives?

| Framework | Consideration |
|-----------|---------------|
| **FastAPI** ✓ | Async-native, automatic OpenAPI docs, Pydantic integration, modern Python |
| Django | Heavier, more opinionated, includes ORM/admin we don't need for this API-focused project |
| Flask | Simpler but requires more manual setup for validation, docs, async |
| Express (Node.js) | Would work, but Python's AI ecosystem is stronger |

### Key Benefits for This Project
- **Automatic API documentation** at `/docs` - useful for testing and understanding the API
- **Pydantic integration** - request/response validation with clear error messages
- **Async support** - important since we make multiple external API calls (AI, news, scraping)
- **Type hints** - catches errors early, improves IDE support

### Tradeoffs
- **Performance**: Python is slower than Go/Rust for CPU-bound tasks, but our bottleneck is external API calls (I/O-bound), so this doesn't matter
- **Deployment**: Requires Python runtime, slightly larger container than Go binaries

### When to choose differently
- High-throughput, low-latency requirements → Consider Go or Rust
- Full-stack web app with server-side rendering → Consider Django or Next.js
- Team more familiar with JavaScript → Consider Express/Fastify with TypeScript

---

## 2. Frontend Framework

### Decision: React 18

### Why React?

| Framework | Consideration |
|-----------|---------------|
| **React** ✓ | Largest ecosystem, most job-relevant, excellent TypeScript support, flexible |
| Vue | Excellent DX, but smaller ecosystem for complex needs |
| Svelte | Great performance, less boilerplate, but smaller community and fewer libraries |
| Angular | Full framework with more structure, but heavier learning curve and more opinionated |

### Key Benefits for This Project
- **Component model** fits our UI well (SpectrumScale, AnalysisCard, etc.)
- **Hooks** provide clean state management without class complexity
- **Ecosystem** - easy to find solutions, libraries, and examples
- **Employability** - most commonly requested frontend skill

### Tradeoffs
- **Bundle size**: React is larger than Svelte/Preact, though acceptable for this app
- **Boilerplate**: More verbose than Vue's single-file components or Svelte
- **Decision fatigue**: React is "just a library" - you choose your own router, state management, etc.

### When to choose differently
- Simpler interactive pages → Svelte or Vue for less boilerplate
- Enterprise team needing enforced structure → Angular
- Maximum performance with tiny bundle → Preact or Svelte

---

## 3. Frontend Build Tool

### Decision: Vite

### Why Vite over alternatives?

| Tool | Consideration |
|------|---------------|
| **Vite** ✓ | Instant dev server, fast HMR, native ES modules, simple config |
| Create React App | Slower, webpack-based, less configurable, being phased out |
| webpack (custom) | Maximum control but complex configuration |
| Parcel | Zero-config but less ecosystem support |

### Key Benefits for This Project
- **Development speed**: Server starts in milliseconds, not seconds
- **Hot Module Replacement**: Changes appear instantly without losing state
- **Simple configuration**: Works out of the box, easy to customize when needed
- **Modern defaults**: ES modules, tree-shaking, optimized production builds

### Tradeoffs
- **Maturity**: Newer than webpack, though now widely adopted
- **Plugin ecosystem**: Smaller than webpack, but covers common needs

### When to choose differently
- Legacy browser support requirements → webpack with appropriate polyfills
- Existing webpack infrastructure → May not be worth migrating

---

## 4. Type Systems

### Decision: TypeScript (frontend) + Python Type Hints (backend)

### Why TypeScript?
- **Catch errors early**: Type mismatches caught at build time, not runtime
- **Better IDE support**: Autocomplete, refactoring, inline documentation
- **Self-documenting**: Types serve as documentation for component props and API responses
- **Refactoring confidence**: Rename a field and TypeScript shows all places to update

### Why Python Type Hints?
- **Same benefits** as TypeScript: IDE support, documentation, error catching
- **Pydantic integration**: Type hints drive request/response validation automatically
- **Gradual adoption**: Can add types incrementally without breaking existing code

### Tradeoffs
- **Learning curve**: Additional syntax to learn
- **Development overhead**: Writing types takes time upfront (saves time later)
- **Build step**: TypeScript requires compilation (handled by Vite)

### When to choose differently
- Quick prototype/throwaway code → Plain JavaScript/Python is faster initially
- Team unfamiliar with types → Gradual adoption or training needed

---

## 5. Styling Approach

### Decision: Tailwind CSS

### Why Tailwind over alternatives?

| Approach | Consideration |
|----------|---------------|
| **Tailwind CSS** ✓ | Utility-first, no context switching, small production bundle, consistent design |
| CSS Modules | Scoped styles but more files, harder to maintain consistency |
| styled-components | CSS-in-JS with good DX, but runtime overhead and bundle size |
| Plain CSS/Sass | Maximum control but harder to maintain consistency at scale |
| Component libraries (MUI, Chakra) | Pre-built components but less flexibility, larger bundles |

### Key Benefits for This Project
- **Speed**: Style directly in JSX without switching files
- **Consistency**: Design tokens (colors, spacing) enforced via config
- **Small bundle**: Only ships CSS classes actually used (via PurgeCSS)
- **Dark mode**: Built-in dark mode support with `dark:` prefix
- **Responsive**: Easy responsive design with `sm:`, `md:`, `lg:` prefixes

### Tradeoffs
- **Verbose HTML**: Class strings can get long (mitigated by extracting components)
- **Learning curve**: Need to learn utility class names
- **"Ugly" markup**: Some developers dislike inline-style-like approach

### When to choose differently
- Team prefers traditional CSS → CSS Modules or Sass
- Need pre-built, accessible components → Chakra UI or Radix + Tailwind
- Runtime theming requirements → styled-components or Emotion

---

## 6. State Management

### Decision: Zustand

### Why Zustand over alternatives?

| Library | Consideration |
|---------|---------------|
| **Zustand** ✓ | Minimal API, no boilerplate, hooks-based, built-in persistence |
| Redux Toolkit | Powerful but more boilerplate, steeper learning curve |
| React Context | Built-in but causes unnecessary re-renders, no devtools |
| Jotai | Atomic model, good for fine-grained updates, similar simplicity to Zustand |
| MobX | Observable-based, automatic tracking, more "magic" |

### Key Benefits for This Project
- **Simplicity**: Create a store in ~10 lines of code
- **No boilerplate**: No actions, reducers, or action creators to wire up
- **Persistence**: Built-in middleware for localStorage (`persist`)
- **TypeScript**: Excellent type inference
- **Performance**: Only re-renders components that use changed state

### Example: Search History Store
```typescript
// This is the entire store - no actions, reducers, or providers needed
export const useSearchHistory = create<SearchHistoryState>()(
  persist(
    (set, get) => ({
      history: [],
      addToHistory: (item) => { /* ... */ },
      clearHistory: () => set({ history: [] }),
    }),
    { name: 'spectrum-search-history' }
  )
)
```

### Tradeoffs
- **Less structure**: Freedom can lead to inconsistent patterns in large teams
- **Smaller ecosystem**: Fewer middleware options than Redux
- **Devtools**: Available but less polished than Redux DevTools

### When to choose differently
- Large team needing enforced patterns → Redux Toolkit
- Complex state with many derived values → MobX or Jotai
- Simple app with minimal global state → React Context might suffice

---

## 7. Server State & Data Fetching

### Decision: TanStack Query (React Query)

### Why TanStack Query?

| Approach | Consideration |
|----------|---------------|
| **TanStack Query** ✓ | Caching, deduplication, background refetch, loading/error states |
| SWR | Similar but fewer features, less control over cache |
| Apollo Client | GraphQL-focused, overkill for REST APIs |
| Plain fetch + useState | Works but manual handling of loading, errors, caching, race conditions |

### Key Benefits for This Project
- **Automatic caching**: Same URL analyzed twice? Returns cached result instantly
- **Loading/error states**: Built-in `isPending`, `error`, `data` - no manual state
- **Background updates**: Refetch stale data automatically
- **Mutations**: Clean API for POST requests with optimistic updates
- **DevTools**: Inspect cache, trigger refetches, see query status

### Example Usage
```typescript
// Automatically handles loading, errors, caching, and refetching
const { data, isPending, error } = useQuery({
  queryKey: ['related', url],
  queryFn: () => api.findRelated(url),
  enabled: !!url, // Only fetch when URL exists
})
```

### Tradeoffs
- **Bundle size**: ~12KB gzipped (worth it for the features)
- **Learning curve**: Concepts like query keys, stale time, cache time
- **Overkill for simple apps**: If you have one or two API calls, might be excessive

### When to choose differently
- GraphQL API → Apollo Client
- Very simple data needs → SWR or plain fetch
- No caching needed → Plain fetch with useState

---

## 8. AI Provider

### Decision: Groq (with llama-3.3-70b-versatile)

### Why Groq over alternatives?

| Provider | Consideration |
|----------|---------------|
| **Groq** ✓ | Free tier, extremely fast inference, good model quality |
| OpenAI (GPT-4) | Best quality but expensive ($30/1M tokens), rate limited |
| Anthropic (Claude) | Excellent quality, expensive, better for long context |
| Local models (Ollama) | Free, private, but requires GPU, slower, lower quality |
| Hugging Face | Many options but more setup, variable quality |

### Key Benefits for This Project
- **Free tier**: Generous limits for development and demo purposes
- **Speed**: Groq's LPU architecture is significantly faster than GPU inference
- **Model quality**: Llama 3.3 70B is competitive with GPT-4 for analysis tasks
- **OpenAI-compatible API**: Easy to swap providers if needed (same endpoint format)

### Tradeoffs
- **Rate limits**: Free tier has requests-per-minute limits (fine for MVP)
- **Model selection**: Fewer models than OpenAI
- **Reliability**: Newer service, less track record than OpenAI/Anthropic

### Provider Abstraction
The codebase uses a Strategy pattern, making it easy to swap providers:
```python
# Switch providers by changing one config value
DEFAULT_AI_PROVIDER=groq  # or "openai" or "claude"
```

### When to choose differently
- Production with high accuracy requirements → OpenAI GPT-4 or Claude
- Privacy-sensitive data → Local models via Ollama
- Cost-sensitive high volume → Fine-tuned smaller models

---

## 9. News Data Source

### Decision: NewsAPI.org

### Why NewsAPI over alternatives?

| Source | Consideration |
|--------|---------------|
| **NewsAPI** ✓ | Simple API, free tier (100 req/day), good source coverage |
| GNews | Similar but smaller source database |
| Bing News Search | More results but requires Azure account, complex pricing |
| Google News (scraping) | No official API, ToS issues, unreliable |
| Media Cloud | Academic-focused, complex setup |

### Key Benefits for This Project
- **Free tier**: 100 requests/day is sufficient for development and demos
- **Simple API**: One endpoint for searching articles
- **Source diversity**: Covers major news outlets across the political spectrum
- **Structured response**: Returns title, URL, source, publish date

### Tradeoffs
- **Free tier limitations**: Only 100 requests/day, headlines only (not full text)
- **Delayed content**: Free tier doesn't include articles < 24 hours old
- **Source coverage**: Primarily English, US-focused sources

### When to choose differently
- Real-time news requirements → Paid NewsAPI or Bing News
- International coverage → Multiple APIs or specialized regional sources
- Full article text needed → Must scrape articles anyway (which we do)

---

## 10. Caching Strategy

### Decision: In-memory cache (cachetools) for MVP

### Why in-memory over Redis?

| Approach | Consideration |
|----------|---------------|
| **In-memory (cachetools)** ✓ | Zero setup, no dependencies, sufficient for single-instance MVP |
| Redis | Distributed, persistent, but requires running another service |
| Memcached | Fast but less features than Redis, still requires setup |
| Database caching | Persistent but slower, adds complexity |

### Key Benefits for This Project
- **Zero infrastructure**: No Redis server to run locally
- **Simple**: Just import and use, no connection management
- **Fast**: In-process memory access is faster than network calls
- **Good enough**: Single server MVP doesn't need distributed cache

### Cache TTLs Used
```python
DEFAULT_TTLS = {
    "article": timedelta(hours=1),      # Scraped content
    "analysis": timedelta(hours=24),    # AI analysis results
    "search": timedelta(minutes=15),    # News search results
    "related": timedelta(minutes=30),   # Related articles
}
```

### Tradeoffs
- **Lost on restart**: Cache clears when server restarts
- **Memory bound**: Large cache consumes application memory
- **Single instance**: Can't share cache across multiple servers

### Migration Path to Redis
The cache interface is abstracted, so switching to Redis requires:
1. Add `redis` to dependencies
2. Implement `RedisCache` class (same interface)
3. Change `CACHE_BACKEND=redis` in config

### When to choose differently
- Multiple server instances → Redis required
- Cache must survive restarts → Redis or database
- Very large cache needs → Redis with separate memory

---

## 11. Web Scraping

### Decision: BeautifulSoup + lxml

### Why BeautifulSoup over alternatives?

| Library | Consideration |
|---------|---------------|
| **BeautifulSoup + lxml** ✓ | Mature, flexible, good docs, handles messy HTML |
| Scrapy | Full framework, overkill for single-page fetches |
| Playwright/Selenium | Handles JavaScript but heavy, slow, complex |
| newspaper3k | Article-specific but less maintained, extraction issues |
| trafilatura | Good extraction but less control over parsing |

### Key Benefits for This Project
- **Flexibility**: Full control over what to extract and how
- **Robust**: Handles malformed HTML gracefully
- **Speed**: lxml parser is fast for HTML parsing
- **Well-documented**: Extensive documentation and community examples

### Extraction Strategy
```python
# Priority order for finding article content:
1. <article> tag
2. Divs with class matching "article-body", "post-content", etc.
3. All <p> tags with substantial text (>50 chars)
```

### Tradeoffs
- **JavaScript content**: Can't extract content rendered by JavaScript
- **Manual selectors**: Need to handle different site structures
- **Maintenance**: Sites change their HTML, breaking extraction

### When to choose differently
- JavaScript-heavy sites → Playwright or Puppeteer
- Need structured article extraction → newspaper3k or trafilatura as starting point
- Large-scale scraping → Scrapy for better scheduling, throttling

---

## 12. HTTP Client

### Decision: httpx (async)

### Why httpx over alternatives?

| Library | Consideration |
|---------|---------------|
| **httpx** ✓ | Async support, requests-like API, HTTP/2, modern |
| requests | Synchronous only, would block async FastAPI |
| aiohttp | Async but different API, less intuitive |
| urllib3 | Low-level, more manual work |

### Key Benefits for This Project
- **Async native**: Works with FastAPI's async request handlers
- **Familiar API**: Same interface as `requests` (easy to learn)
- **Connection pooling**: Reuses connections for performance
- **Timeout handling**: Clean timeout configuration

### Usage Pattern
```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)  # Non-blocking
```

### Tradeoffs
- **Newer library**: Less battle-tested than requests (though now mature)
- **Async complexity**: Must use `await`, can't use in sync contexts

### When to choose differently
- Sync-only codebase → requests
- Need WebSocket support → aiohttp
- Maximum performance → Custom solution with connection pooling tuning

---

## 13. Architecture Patterns

### Decision: Clean Architecture + Strategy Pattern

### Why Clean Architecture?

The codebase separates into layers:
```
API Layer (routes) → Use Cases → Services → External APIs
```

**Benefits:**
- **Testability**: Mock services to test use cases in isolation
- **Flexibility**: Swap implementations without changing business logic
- **Clarity**: Each layer has clear responsibility

### Why Strategy Pattern for AI Providers?

```python
class AIProviderInterface(ABC):
    async def analyze_political_leaning(...) -> PoliticalLeaning
    async def extract_topics(...) -> TopicAnalysis
```

**Benefits:**
- **Swappable**: Change AI provider via config, not code
- **Testable**: Use mock provider in tests
- **Extensible**: Add new providers without modifying existing code

### Tradeoffs
- **More files**: Interfaces, implementations, factories add structure
- **Indirection**: Following code flow requires jumping between files
- **Overkill for simple apps**: A 100-line script doesn't need this

### When to use simpler patterns
- Prototype/hackathon → Put logic directly in routes
- Single implementation with no planned alternatives → Skip interfaces
- Small team, simple app → Reduce abstraction layers

---

## 14. Containerization

### Decision: Docker with multi-stage builds

### Why Docker?

| Approach | Consideration |
|----------|---------------|
| **Docker** ✓ | Consistent environments, easy deployment, isolated dependencies |
| Direct deployment | Simpler but "works on my machine" issues |
| Serverless (Lambda) | Auto-scaling but cold starts, 15-min timeout limits |

### Key Benefits for This Project
- **Reproducibility**: Same environment locally and in production
- **Isolation**: Dependencies don't conflict with system packages
- **Easy deployment**: Push image, pull and run anywhere
- **Development**: docker-compose for full stack locally

### Multi-stage Build
```dockerfile
# Build stage - includes dev dependencies
FROM python:3.11-slim as base
# ... install dependencies

# Production stage - minimal image
FROM base as production
# ... only runtime files
```

### Tradeoffs
- **Learning curve**: Docker concepts take time to learn
- **Build time**: Building images slower than running directly
- **Resource overhead**: Container runtime uses some memory

### When to choose differently
- Quick local development only → Virtual environment is simpler
- Auto-scaling requirements → Serverless or Kubernetes
- Edge deployment → Smaller runtimes or compiled binaries

---

## Summary: Decision Framework

When making technology decisions, we considered:

1. **Project constraints**: MVP scope, free-tier APIs, learning value
2. **Developer experience**: Fast feedback loops, good documentation
3. **Ecosystem**: Library availability, community support
4. **Scalability path**: Can we evolve this choice as the project grows?
5. **Team familiarity**: Using well-known tools reduces onboarding time

### Key Principles Applied

| Principle | Example |
|-----------|---------|
| Start simple, add complexity when needed | In-memory cache → Redis later |
| Prefer composition over inheritance | Strategy pattern for AI providers |
| Make dependencies explicit | Dependency injection in FastAPI |
| Design for change | Interfaces abstract external services |
| Optimize for developer productivity | Vite, Tailwind, Zustand all prioritize DX |

These decisions work well for Spectrum's current scope. As requirements evolve, the abstractions in place make it straightforward to swap implementations or add complexity where needed.
