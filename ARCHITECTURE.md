# Spectrum - Political News Analyzer Backend Architecture

## Overview

Spectrum is a political spectrum analyzer for news articles. This document describes the backend architecture designed for clean separation of concerns, extensibility, and production-quality code.

## Architecture Principles

1. **Clean Architecture**: Domain logic independent of frameworks and external services
2. **Dependency Injection**: All services receive dependencies, enabling testing and swapping
3. **Strategy Pattern**: Swappable AI providers without code changes
4. **Repository Pattern**: Abstract data access for future database integration
5. **CQRS-lite**: Separate read/write operations where beneficial
6. **Fail-Safe Design**: Graceful degradation when external services fail

---

## 1. Project Structure

### Backend (Python/FastAPI)

```
spectrum/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Settings and configuration
│   │
│   ├── api/                       # API Layer (Controllers)
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection for routes
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── articles.py        # Article analysis + related endpoints
│   │   │   ├── comparisons.py     # Article comparison endpoints
│   │   │   └── health.py          # Health check endpoints
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── error_handler.py   # Global error handling
│   │       └── logging.py         # Request/response logging
│   │
│   ├── core/                      # Core Business Logic
│   │   ├── __init__.py
│   │   ├── entities/              # Domain entities
│   │   │   ├── __init__.py
│   │   │   ├── article.py         # Article domain model
│   │   │   ├── analysis.py        # Analysis result model
│   │   │   └── comparison.py      # Comparison result model
│   │   ├── interfaces/            # Abstract interfaces (ports)
│   │   │   ├── __init__.py
│   │   │   ├── ai_provider.py     # AI provider interface
│   │   │   ├── article_fetcher.py # Article fetching interface
│   │   │   ├── news_aggregator.py # News API interface
│   │   │   └── cache.py           # Cache interface
│   │   └── use_cases/             # Application use cases
│   │       ├── __init__.py
│   │       ├── analyze_article.py # Core analysis orchestration
│   │       ├── find_related.py    # Related article discovery
│   │       └── compare_articles.py # Multi-article comparison
│   │
│   ├── services/                  # Service Implementations (Adapters)
│   │   ├── __init__.py
│   │   ├── ai/                    # AI Provider implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base AI provider with prompts
│   │   │   ├── groq_provider.py   # Groq implementation (primary)
│   │   │   └── factory.py         # Provider factory
│   │   ├── fetchers/
│   │   │   ├── __init__.py
│   │   │   └── web_scraper.py     # Web scraping with BeautifulSoup
│   │   ├── aggregators/
│   │   │   ├── __init__.py
│   │   │   └── newsapi.py         # NewsAPI.org integration
│   │   └── cache/
│   │       ├── __init__.py
│   │       ├── memory_cache.py    # In-memory TTL cache
│   │       └── cache_keys.py      # Cache key generation
│   │
│   └── schemas/                   # Pydantic Schemas (DTOs)
│       ├── __init__.py
│       ├── requests.py            # Request schemas
│       └── responses.py           # Response schemas
│
├── docker/
│   ├── Dockerfile                 # Production Docker image
│   ├── Dockerfile.web             # Frontend Docker image
│   └── docker-compose.yml         # Local development stack
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Frontend (React/TypeScript)

```
spectrum-web/
├── src/
│   ├── main.tsx                   # Entry point
│   ├── index.css                  # Global styles (Tailwind)
│   │
│   ├── app/
│   │   ├── App.tsx                # Root component with main UI
│   │   └── providers/
│   │       └── index.tsx          # React Query provider setup
│   │
│   ├── features/                  # Feature-based modules
│   │   ├── spectrum/              # Political spectrum visualization
│   │   │   ├── components/
│   │   │   │   ├── SpectrumScale.tsx
│   │   │   │   ├── SpectrumMarker.tsx
│   │   │   │   ├── SpectrumLabels.tsx
│   │   │   │   ├── ConfidenceIndicator.tsx
│   │   │   │   └── MiniSpectrum.tsx
│   │   │   ├── utils/
│   │   │   │   └── spectrumColors.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── analysis/              # Article analysis feature
│   │   │   ├── components/
│   │   │   │   ├── UrlInputForm.tsx
│   │   │   │   ├── AnalysisCard.tsx
│   │   │   │   └── ArticleSummary.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAnalyzeArticle.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── related-articles/      # Related articles feature
│   │   │   ├── components/
│   │   │   │   ├── RelatedArticlesList.tsx
│   │   │   │   └── RelatedArticleCard.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useFindRelated.ts
│   │   │   └── index.ts
│   │   │
│   │   └── comparison/            # Article comparison feature
│   │       ├── components/
│   │       │   ├── ComparisonView.tsx
│   │       │   ├── ComparisonSummary.tsx
│   │       │   └── ComparisonSpectrum.tsx
│   │       └── index.ts
│   │
│   ├── components/
│   │   └── common/                # Shared UI components
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorMessage.tsx
│   │       └── Disclaimer.tsx
│   │
│   ├── stores/
│   │   ├── useComparisonStore.ts  # Zustand store for article comparison
│   │   └── useSearchHistory.ts    # Zustand store for search history (localStorage persisted)
│   │
│   └── lib/
│       └── api/
│           └── client.ts          # API client with types
│
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── index.html
```

---

## 2. Core API Endpoints Design

### Base URL: `/api/v1`

### Health & Status

```
GET  /health                    # Basic health check
GET  /health/ready              # Readiness (all dependencies up)
```

### Article Analysis

```
POST /articles/analyze          # Analyze single article
     Body: { "url": "string", "options": {...} }
     Response: ArticleAnalysis

GET  /articles/{analysis_id}    # Get cached analysis by ID
     Response: ArticleAnalysis

POST /articles/analyze/text     # Analyze raw text (no URL)
     Body: { "title": "string", "content": "string", "source": "string" }
     Response: ArticleAnalysis
```

### Related Articles

```
POST /articles/related          # Find related articles
     Body: { "url": "string" } or { "keywords": ["string"], "topic": "string" }
     Response: RelatedArticlesResponse

POST /articles/related/analyze  # Find and analyze related articles
     Body: { "url": "string", "limit": 5 }
     Response: RelatedArticlesWithAnalysis
```

### Article Comparison

```
POST /comparisons               # Compare multiple articles
     Body: { "article_urls": ["string"], "comparison_type": "full|points_only" }
     Response: ComparisonResult

POST /comparisons/with-related  # Analyze article + find related + compare
     Body: { "url": "string", "related_count": 3 }
     Response: FullComparisonResult
```

### OpenAPI Schema

```yaml
openapi: 3.1.0
info:
  title: Spectrum - Political News Analyzer
  version: 1.0.0
  description: API for analyzing political leaning of news articles

paths:
  /api/v1/articles/analyze:
    post:
      summary: Analyze article political leaning
      operationId: analyzeArticle
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnalyzeRequest'
      responses:
        '200':
          description: Analysis complete
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ArticleAnalysis'
        '422':
          description: Validation error
        '503':
          description: External service unavailable
```

---

## 3. Service Layer Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           API Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │   /articles  │  │ /comparisons │  │   /health    │               │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘               │
└─────────┼─────────────────┼─────────────────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Use Cases Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  AnalyzeArticle  │  │   FindRelated    │  │ CompareArticles  │   │
│  │                  │  │                  │  │                  │   │
│  │  - Orchestrates  │  │  - Searches news │  │  - Multi-article │   │
│  │    fetching &    │  │    APIs          │  │    analysis      │   │
│  │    analysis      │  │  - Deduplicates  │  │  - Point extract │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘   │
└───────────┼─────────────────────┼─────────────────────┼─────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Services Layer                                │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  AI Provider│  │Article      │  │   News      │  │    Cache    │ │
│  │  (Strategy) │  │Fetcher      │  │ Aggregator  │  │   Service   │ │
│  │             │  │             │  │             │  │             │ │
│  │ - Groq      │  │ - Scraper   │  │ - NewsAPI   │  │ - Memory    │ │
│  │ - Claude    │  │ - Reader    │  │ - GNews     │  │ - Redis     │ │
│  │ - OpenAI    │  │             │  │             │  │             │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Service Responsibilities

#### ArticleFetcher Service
- Fetches article content from URL using HTTP/2 (required by many news sites)
- Extracts title, content, author, and publication date
- Uses multiple content extraction strategies (`<article>`, `<main>`, class patterns)
- Maintains lists of supported, partially supported, and blocked news sources
- Provides clear error messages for known blocked sites (e.g., NY Times, Washington Post)
- See README.md for full source compatibility list

#### AIProvider Service (Strategy Pattern)
- Political leaning analysis (-1 to 1 score)
- Topic/keyword extraction
- Point extraction for comparison
- Agreement/disagreement identification

#### NewsAggregator Service
- Searches for related articles by keywords
- Filters by date range, source diversity
- Deduplicates results
- Returns normalized article metadata

#### Cache Service
- Caches fetched articles (1 hour TTL)
- Caches analysis results (24 hour TTL)
- Caches news search results (15 min TTL)
- Provides cache key generation

---

## 4. Data Models (Pydantic Schemas)

### Domain Entities

```python
# app/core/entities/article.py
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum

class ArticleSource(BaseModel):
    """Metadata about article source."""
    name: str
    domain: str
    known_bias: Optional[float] = None  # Pre-known bias if available

class Article(BaseModel):
    """Core article entity."""
    id: str = Field(..., description="Unique identifier (hash of URL)")
    url: HttpUrl
    title: str
    content: str
    source: ArticleSource
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    word_count: int
    fetched_at: datetime

# app/core/entities/analysis.py
class PoliticalLeaning(BaseModel):
    """Political leaning analysis result."""
    score: float = Field(..., ge=-1.0, le=1.0, description="-1=far left, 0=center, 1=far right")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Explanation of the score")

    # Detailed breakdown
    economic_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    social_score: Optional[float] = Field(None, ge=-1.0, le=1.0)

class TopicAnalysis(BaseModel):
    """Topic and keyword extraction."""
    primary_topic: str
    secondary_topics: list[str] = []
    keywords: list[str] = Field(..., max_length=10)
    entities: list[str] = []  # Named entities (people, organizations)

class ArticlePoint(BaseModel):
    """A key point/claim made in an article."""
    id: str
    statement: str
    supporting_quote: Optional[str] = None
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")

class ArticleAnalysis(BaseModel):
    """Complete analysis result for an article."""
    article_id: str
    article_url: HttpUrl
    article_title: str
    source_name: str

    political_leaning: PoliticalLeaning
    topics: TopicAnalysis
    key_points: list[ArticlePoint]

    analyzed_at: datetime
    ai_provider: str
    cached: bool = False

# app/core/entities/comparison.py
class PointComparison(BaseModel):
    """Comparison between points from different articles."""
    point_a: ArticlePoint
    point_b: ArticlePoint
    article_a_id: str
    article_b_id: str
    relationship: str = Field(..., pattern="^(agrees|disagrees|related|unrelated)$")
    explanation: str

class ArticleComparison(BaseModel):
    """Full comparison between two articles."""
    article_a_id: str
    article_b_id: str

    # Leaning comparison
    leaning_difference: float  # Absolute difference
    leaning_summary: str

    # Topic overlap
    shared_topics: list[str]
    unique_topics_a: list[str]
    unique_topics_b: list[str]

    # Point comparisons
    agreements: list[PointComparison]
    disagreements: list[PointComparison]

    overall_summary: str

class MultiArticleComparison(BaseModel):
    """Comparison across multiple articles."""
    articles: list[ArticleAnalysis]
    pairwise_comparisons: list[ArticleComparison]

    # Aggregate insights
    leaning_spectrum: dict[str, float]  # article_id -> score
    consensus_points: list[str]
    contested_points: list[str]
    overall_summary: str
```

### Request/Response Schemas

```python
# app/schemas/requests.py
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional

class AnalyzeArticleRequest(BaseModel):
    """Request to analyze an article by URL."""
    url: HttpUrl
    include_points: bool = True
    force_refresh: bool = False  # Bypass cache

    @field_validator('url')
    @classmethod
    def validate_url_protocol(cls, v):
        if str(v).startswith('http://'):
            # Upgrade to HTTPS
            return HttpUrl(str(v).replace('http://', 'https://'))
        return v

class AnalyzeTextRequest(BaseModel):
    """Request to analyze raw text."""
    title: str = Field(..., min_length=5, max_length=500)
    content: str = Field(..., min_length=100, max_length=50000)
    source_name: Optional[str] = "Unknown"
    source_url: Optional[HttpUrl] = None

class FindRelatedRequest(BaseModel):
    """Request to find related articles."""
    url: Optional[HttpUrl] = None
    keywords: Optional[list[str]] = None
    topic: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    days_back: int = Field(default=7, ge=1, le=30)

    @field_validator('keywords')
    @classmethod
    def validate_keywords_or_url(cls, v, info):
        if v is None and info.data.get('url') is None and info.data.get('topic') is None:
            raise ValueError('Must provide url, keywords, or topic')
        return v

class CompareArticlesRequest(BaseModel):
    """Request to compare multiple articles."""
    article_urls: list[HttpUrl] = Field(..., min_length=2, max_length=5)
    comparison_depth: str = Field(default="full", pattern="^(quick|full|deep)$")

class FullAnalysisRequest(BaseModel):
    """Request for complete analysis workflow."""
    url: HttpUrl
    find_related: bool = True
    related_count: int = Field(default=3, ge=1, le=5)
    compare_all: bool = True

# app/schemas/responses.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnalysisResponse(BaseModel):
    """Response for article analysis."""
    success: bool
    data: Optional[ArticleAnalysis] = None
    error: Optional[str] = None
    cached: bool = False
    processing_time_ms: int

class RelatedArticlePreview(BaseModel):
    """Preview of a related article (before full analysis)."""
    url: HttpUrl
    title: str
    source: str
    published_at: Optional[datetime]
    snippet: Optional[str]

class RelatedArticlesResponse(BaseModel):
    """Response for related articles search."""
    success: bool
    original_keywords: list[str]
    articles: list[RelatedArticlePreview]
    total_found: int

class ComparisonResponse(BaseModel):
    """Response for article comparison."""
    success: bool
    data: Optional[MultiArticleComparison] = None
    error: Optional[str] = None
    articles_analyzed: int
    processing_time_ms: int

class FullAnalysisResponse(BaseModel):
    """Response for complete analysis workflow."""
    primary_article: ArticleAnalysis
    related_articles: list[ArticleAnalysis]
    comparison: Optional[MultiArticleComparison]
    total_processing_time_ms: int
```

---

## 5. AI Provider Abstraction (Strategy Pattern)

### Interface Definition

```python
# app/core/interfaces/ai_provider.py
from abc import ABC, abstractmethod
from typing import Optional
from app.core.entities.analysis import (
    PoliticalLeaning,
    TopicAnalysis,
    ArticlePoint,
    PointComparison
)

class AIProviderInterface(ABC):
    """Abstract interface for AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging/tracking."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether provider supports streaming responses."""
        pass

    @abstractmethod
    async def analyze_political_leaning(
        self,
        title: str,
        content: str,
        source_name: Optional[str] = None
    ) -> PoliticalLeaning:
        """Analyze political leaning of article content."""
        pass

    @abstractmethod
    async def extract_topics(
        self,
        title: str,
        content: str
    ) -> TopicAnalysis:
        """Extract topics and keywords from article."""
        pass

    @abstractmethod
    async def extract_key_points(
        self,
        title: str,
        content: str,
        max_points: int = 5
    ) -> list[ArticlePoint]:
        """Extract key points/claims from article."""
        pass

    @abstractmethod
    async def compare_points(
        self,
        points_a: list[ArticlePoint],
        points_b: list[ArticlePoint],
        article_a_context: str,
        article_b_context: str
    ) -> list[PointComparison]:
        """Compare points between two articles."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available."""
        pass
```

### Base Implementation

```python
# app/services/ai/base.py
from abc import ABC
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.entities.analysis import PoliticalLeaning, TopicAnalysis, ArticlePoint

class BaseAIProvider(AIProviderInterface, ABC):
    """Base class with common functionality."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=60.0
            )
        return self._client

    def _get_headers(self) -> dict:
        """Override in subclass for provider-specific headers."""
        return {"Authorization": f"Bearer {self.api_key}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def _make_request(self, messages: list[dict], **kwargs) -> str:
        """Make API request with retry logic."""
        client = await self.get_client()
        response = await client.post(
            self._get_endpoint(),
            json=self._build_request_body(messages, **kwargs)
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    @abstractmethod
    def _get_endpoint(self) -> str:
        pass

    @abstractmethod
    def _build_request_body(self, messages: list[dict], **kwargs) -> dict:
        pass

    @abstractmethod
    def _parse_response(self, response: dict) -> str:
        pass

    def _get_political_leaning_prompt(self, title: str, content: str, source: Optional[str]) -> str:
        return f"""Analyze the political leaning of this news article.

Title: {title}
Source: {source or 'Unknown'}
Content: {content[:8000]}

Provide your analysis as JSON with this exact structure:
{{
    "score": <float from -1.0 (far left) to 1.0 (far right), 0 is center>,
    "confidence": <float from 0.0 to 1.0>,
    "reasoning": "<brief explanation of why you assigned this score>",
    "economic_score": <float from -1.0 to 1.0 for economic policy stance, null if not applicable>,
    "social_score": <float from -1.0 to 1.0 for social policy stance, null if not applicable>
}}

Consider:
- Word choice and framing
- Sources cited
- Topics emphasized or omitted
- Emotional vs factual tone
- Known bias of the source (if any)

Respond ONLY with valid JSON."""
```

### Groq Implementation

```python
# app/services/ai/groq_provider.py
import json
from typing import Optional
from app.services.ai.base import BaseAIProvider
from app.core.entities.analysis import (
    PoliticalLeaning,
    TopicAnalysis,
    ArticlePoint,
    PointComparison
)

class GroqProvider(BaseAIProvider):
    """Groq AI provider implementation."""

    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model=model
        )

    @property
    def name(self) -> str:
        return "groq"

    @property
    def supports_streaming(self) -> bool:
        return True

    def _get_endpoint(self) -> str:
        return "/chat/completions"

    def _build_request_body(self, messages: list[dict], **kwargs) -> dict:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "response_format": {"type": "json_object"} if kwargs.get("json_mode") else None
        }

    def _parse_response(self, response: dict) -> str:
        return response["choices"][0]["message"]["content"]

    async def analyze_political_leaning(
        self,
        title: str,
        content: str,
        source_name: Optional[str] = None
    ) -> PoliticalLeaning:
        prompt = self._get_political_leaning_prompt(title, content, source_name)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return PoliticalLeaning(
            score=data["score"],
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            economic_score=data.get("economic_score"),
            social_score=data.get("social_score")
        )

    async def extract_topics(self, title: str, content: str) -> TopicAnalysis:
        prompt = f"""Extract topics and keywords from this article.

Title: {title}
Content: {content[:6000]}

Respond with JSON:
{{
    "primary_topic": "<main topic>",
    "secondary_topics": ["<topic1>", "<topic2>"],
    "keywords": ["<keyword1>", "<keyword2>", ...],  // max 10
    "entities": ["<person/org name>", ...]  // named entities
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return TopicAnalysis(**data)

    async def extract_key_points(
        self,
        title: str,
        content: str,
        max_points: int = 5
    ) -> list[ArticlePoint]:
        prompt = f"""Extract the {max_points} most important claims or points from this article.

Title: {title}
Content: {content[:6000]}

Respond with JSON:
{{
    "points": [
        {{
            "id": "p1",
            "statement": "<clear statement of the point/claim>",
            "supporting_quote": "<direct quote from article if available>",
            "sentiment": "positive|negative|neutral"
        }}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return [ArticlePoint(**p) for p in data["points"]]

    async def compare_points(
        self,
        points_a: list[ArticlePoint],
        points_b: list[ArticlePoint],
        article_a_context: str,
        article_b_context: str
    ) -> list[PointComparison]:
        points_a_text = "\n".join([f"- {p.statement}" for p in points_a])
        points_b_text = "\n".join([f"- {p.statement}" for p in points_b])

        prompt = f"""Compare these points from two articles on the same topic.

Article A context: {article_a_context}
Article A points:
{points_a_text}

Article B context: {article_b_context}
Article B points:
{points_b_text}

Find agreements and disagreements. Respond with JSON:
{{
    "comparisons": [
        {{
            "point_a_id": "<id>",
            "point_b_id": "<id>",
            "relationship": "agrees|disagrees|related|unrelated",
            "explanation": "<why they agree/disagree>"
        }}
    ]
}}"""

        messages = [{"role": "user", "content": prompt}]
        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        # Map back to full PointComparison objects
        points_a_map = {p.id: p for p in points_a}
        points_b_map = {p.id: p for p in points_b}

        comparisons = []
        for c in data["comparisons"]:
            if c["point_a_id"] in points_a_map and c["point_b_id"] in points_b_map:
                comparisons.append(PointComparison(
                    point_a=points_a_map[c["point_a_id"]],
                    point_b=points_b_map[c["point_b_id"]],
                    article_a_id="",  # Filled in by use case
                    article_b_id="",
                    relationship=c["relationship"],
                    explanation=c["explanation"]
                ))

        return comparisons

    async def health_check(self) -> bool:
        try:
            client = await self.get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
```

### Provider Factory

```python
# app/services/ai/factory.py
from typing import Optional
from app.core.interfaces.ai_provider import AIProviderInterface
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.claude_provider import ClaudeProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.config import Settings

class AIProviderFactory:
    """Factory for creating AI provider instances."""

    _providers = {
        "groq": GroqProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        settings: Settings
    ) -> AIProviderInterface:
        """Create an AI provider instance."""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider_class = cls._providers[provider_name]

        if provider_name == "groq":
            return provider_class(
                api_key=settings.groq_api_key,
                model=settings.groq_model
            )
        elif provider_name == "claude":
            return provider_class(
                api_key=settings.anthropic_api_key,
                model=settings.claude_model
            )
        elif provider_name == "openai":
            return provider_class(
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

    @classmethod
    def get_default(cls, settings: Settings) -> AIProviderInterface:
        """Get the default provider based on settings."""
        return cls.create(settings.default_ai_provider, settings)

    @classmethod
    def register(cls, name: str, provider_class: type):
        """Register a new provider type."""
        cls._providers[name] = provider_class
```

---

## 6. Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Request Flow                                  │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  L1: In-Memory Cache (TTLCache)                                     │
│  - Hot data only                                                     │
│  - 100-500 items max                                                 │
│  - Sub-millisecond access                                            │
│  TTLs: Analysis=1hr, Articles=30min, Search=5min                    │
└─────────────────────────────────────────────────────────────────────┘
                               │ miss
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  L2: Redis Cache (Optional - for production)                        │
│  - Distributed cache                                                 │
│  - Survives restarts                                                 │
│  - Shared across instances                                           │
│  TTLs: Analysis=24hr, Articles=6hr, Search=15min                    │
└─────────────────────────────────────────────────────────────────────┘
                               │ miss
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  External Services (Expensive)                                       │
│  - News APIs (rate limited)                                          │
│  - AI Providers (paid per token)                                     │
│  - Web Scrapers (slow)                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Cache Interface & Implementation

```python
# app/core/interfaces/cache.py
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from datetime import timedelta

T = TypeVar('T')

class CacheInterface(ABC, Generic[T]):
    """Abstract cache interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: T, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        pass


# app/services/cache/memory_cache.py
from datetime import datetime, timedelta
from typing import Optional, Any
from cachetools import TTLCache
import asyncio
from app.core.interfaces.cache import CacheInterface

class MemoryCache(CacheInterface[Any]):
    """Thread-safe in-memory cache with TTL support."""

    # Default TTLs for different data types
    DEFAULT_TTLS = {
        "article": timedelta(hours=1),
        "analysis": timedelta(hours=24),
        "search": timedelta(minutes=15),
        "related": timedelta(minutes=30),
    }

    def __init__(self, maxsize: int = 500):
        self._caches: dict[str, TTLCache] = {}
        self._lock = asyncio.Lock()
        self._maxsize = maxsize

    def _get_cache_for_type(self, key: str) -> TTLCache:
        """Get or create cache for key type."""
        # Extract type from key prefix (e.g., "article:xxx" -> "article")
        key_type = key.split(":")[0] if ":" in key else "default"
        ttl_seconds = self.DEFAULT_TTLS.get(key_type, timedelta(hours=1)).total_seconds()

        if key_type not in self._caches:
            self._caches[key_type] = TTLCache(
                maxsize=self._maxsize,
                ttl=ttl_seconds
            )
        return self._caches[key_type]

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            cache = self._get_cache_for_type(key)
            return cache.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        async with self._lock:
            cache = self._get_cache_for_type(key)
            cache[key] = value

    async def delete(self, key: str) -> None:
        async with self._lock:
            cache = self._get_cache_for_type(key)
            cache.pop(key, None)

    async def exists(self, key: str) -> bool:
        async with self._lock:
            cache = self._get_cache_for_type(key)
            return key in cache

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern (simple prefix matching)."""
        count = 0
        async with self._lock:
            for cache in self._caches.values():
                keys_to_delete = [k for k in cache.keys() if k.startswith(pattern.rstrip("*"))]
                for key in keys_to_delete:
                    del cache[key]
                    count += 1
        return count


# app/services/cache/cache_keys.py
import hashlib
from urllib.parse import urlparse

class CacheKeys:
    """Cache key generation utilities."""

    @staticmethod
    def article(url: str) -> str:
        """Generate cache key for article content."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"article:{url_hash}"

    @staticmethod
    def analysis(url: str, provider: str) -> str:
        """Generate cache key for analysis result."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"analysis:{provider}:{url_hash}"

    @staticmethod
    def search(keywords: list[str], source: str) -> str:
        """Generate cache key for search results."""
        keywords_str = "|".join(sorted(keywords))
        kw_hash = hashlib.md5(keywords_str.encode()).hexdigest()[:12]
        return f"search:{source}:{kw_hash}"

    @staticmethod
    def related(url: str) -> str:
        """Generate cache key for related articles."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        return f"related:{url_hash}"
```

### Caching Decorator

```python
# app/utils/cache_decorator.py
from functools import wraps
from typing import Callable, Optional
from datetime import timedelta
from app.core.interfaces.cache import CacheInterface

def cached(
    key_func: Callable[..., str],
    ttl: Optional[timedelta] = None
):
    """Decorator for caching async function results."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, cache: CacheInterface, **kwargs):
            # Generate cache key
            cache_key = key_func(*args, **kwargs)

            # Check cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                # Mark as cached if result has that attribute
                if hasattr(cached_result, 'cached'):
                    cached_result.cached = True
                return cached_result

            # Execute function
            result = await func(self, *args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
```

---

## 7. Key Libraries

### Core Dependencies

```toml
# pyproject.toml
[project]
name = "spectrum"
version = "0.1.0"
description = "Political spectrum analyzer for news articles"
requires-python = ">=3.11"

dependencies = [
    # Web Framework
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.6",

    # HTTP Client
    "httpx>=0.26.0",

    # Validation & Settings
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",

    # Web Scraping
    "beautifulsoup4>=4.12.0",
    "lxml>=5.1.0",
    "readability-lxml>=0.8.1",
    "newspaper3k>=0.2.8",         # Article extraction

    # Caching
    "cachetools>=5.3.0",
    "redis>=5.0.0",               # Optional, for production

    # Resilience
    "tenacity>=8.2.0",            # Retry logic

    # Utilities
    "python-dateutil>=2.8.0",
    "structlog>=24.1.0",          # Structured logging
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",              # For test client
    "respx>=0.20.0",              # HTTP mocking
    "ruff>=0.1.0",                # Linting
    "mypy>=1.8.0",                # Type checking
]
```

### Library Purposes

| Library | Purpose |
|---------|---------|
| `fastapi` | Async web framework with automatic OpenAPI docs |
| `uvicorn` | ASGI server for running FastAPI |
| `httpx` | Async HTTP client for API calls |
| `pydantic` | Data validation and serialization |
| `pydantic-settings` | Environment-based configuration |
| `beautifulsoup4` | HTML parsing for web scraping |
| `readability-lxml` | Article content extraction |
| `newspaper3k` | Alternative article extraction with NLP |
| `cachetools` | In-memory caching with TTL |
| `redis` | Distributed caching (production) |
| `tenacity` | Retry logic with backoff strategies |
| `structlog` | Structured JSON logging |
| `pytest-asyncio` | Async test support |
| `respx` | HTTP request mocking for tests |

---

## 8. Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    app_name: str = "Spectrum"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # AI Providers
    default_ai_provider: str = "groq"

    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_model: str = "llama-3.1-70b-versatile"

    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    claude_model: str = "claude-3-5-sonnet-20241022"

    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_model: str = "gpt-4-turbo-preview"

    # News APIs
    newsapi_key: Optional[str] = Field(None, env="NEWSAPI_KEY")
    gnews_api_key: Optional[str] = Field(None, env="GNEWS_API_KEY")

    # Cache
    cache_backend: str = "memory"  # "memory" or "redis"
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    cache_max_size: int = 500

    # Rate Limiting (prepared for auth)
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Scraping
    scraper_timeout_seconds: int = 30
    scraper_user_agent: str = "Spectrum/1.0 (News Analysis Bot)"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## 9. Use Case Implementation Example

```python
# app/core/use_cases/analyze_article.py
from datetime import datetime
import hashlib
from typing import Optional
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.article_fetcher import ArticleFetcherInterface
from app.core.interfaces.cache import CacheInterface
from app.core.entities.article import Article
from app.core.entities.analysis import ArticleAnalysis
from app.services.cache.cache_keys import CacheKeys
import structlog

logger = structlog.get_logger()

class AnalyzeArticleUseCase:
    """Use case for analyzing a single article."""

    def __init__(
        self,
        ai_provider: AIProviderInterface,
        article_fetcher: ArticleFetcherInterface,
        cache: CacheInterface
    ):
        self.ai = ai_provider
        self.fetcher = article_fetcher
        self.cache = cache

    async def execute(
        self,
        url: str,
        force_refresh: bool = False,
        include_points: bool = True
    ) -> ArticleAnalysis:
        """
        Analyze an article's political leaning.

        1. Check cache for existing analysis
        2. Fetch article content (cached)
        3. Run AI analysis
        4. Cache and return results
        """
        log = logger.bind(url=url, provider=self.ai.name)

        # Check for cached analysis
        if not force_refresh:
            cache_key = CacheKeys.analysis(url, self.ai.name)
            cached = await self.cache.get(cache_key)
            if cached:
                log.info("cache_hit", cache_key=cache_key)
                cached.cached = True
                return cached

        # Fetch article
        log.info("fetching_article")
        article = await self._fetch_article(url)

        # Run AI analysis in parallel
        log.info("running_analysis")
        leaning, topics = await asyncio.gather(
            self.ai.analyze_political_leaning(
                article.title,
                article.content,
                article.source.name
            ),
            self.ai.extract_topics(article.title, article.content)
        )

        # Extract points if requested
        points = []
        if include_points:
            points = await self.ai.extract_key_points(
                article.title,
                article.content
            )

        # Build result
        analysis = ArticleAnalysis(
            article_id=article.id,
            article_url=url,
            article_title=article.title,
            source_name=article.source.name,
            political_leaning=leaning,
            topics=topics,
            key_points=points,
            analyzed_at=datetime.utcnow(),
            ai_provider=self.ai.name,
            cached=False
        )

        # Cache result
        cache_key = CacheKeys.analysis(url, self.ai.name)
        await self.cache.set(cache_key, analysis)

        log.info("analysis_complete", score=leaning.score)
        return analysis

    async def _fetch_article(self, url: str) -> Article:
        """Fetch article with caching."""
        cache_key = CacheKeys.article(url)

        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        article = await self.fetcher.fetch(url)
        await self.cache.set(cache_key, article)

        return article
```

---

## 10. API Route Implementation

```python
# app/api/routes/articles.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.schemas.requests import AnalyzeArticleRequest, AnalyzeTextRequest
from app.schemas.responses import AnalysisResponse
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.api.deps import get_analyze_use_case
import structlog

router = APIRouter(prefix="/articles", tags=["Articles"])
logger = structlog.get_logger()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_article(
    request: AnalyzeArticleRequest,
    use_case: AnalyzeArticleUseCase = Depends(get_analyze_use_case)
) -> AnalysisResponse:
    """
    Analyze the political leaning of an article.

    - Fetches article content from URL
    - Analyzes political bias on -1 (left) to 1 (right) spectrum
    - Extracts topics, keywords, and key points
    - Results are cached for 24 hours
    """
    start_time = datetime.utcnow()

    try:
        analysis = await use_case.execute(
            url=str(request.url),
            force_refresh=request.force_refresh,
            include_points=request.include_points
        )

        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return AnalysisResponse(
            success=True,
            data=analysis,
            cached=analysis.cached,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error("analysis_failed", error=str(e), url=str(request.url))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Analysis failed: {str(e)}"
        )
```

---

## 11. Dependency Injection Setup

```python
# app/dependencies.py
from functools import lru_cache
from typing import Generator
from app.config import Settings, get_settings
from app.core.interfaces.ai_provider import AIProviderInterface
from app.core.interfaces.cache import CacheInterface
from app.services.ai.factory import AIProviderFactory
from app.services.cache.memory_cache import MemoryCache
from app.services.cache.redis_cache import RedisCache
from app.services.fetchers.web_scraper import WebScraper
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase

# Singleton instances
_cache_instance: CacheInterface | None = None
_ai_provider_instance: AIProviderInterface | None = None

def get_cache(settings: Settings = Depends(get_settings)) -> CacheInterface:
    """Get or create cache instance."""
    global _cache_instance
    if _cache_instance is None:
        if settings.cache_backend == "redis" and settings.redis_url:
            _cache_instance = RedisCache(settings.redis_url)
        else:
            _cache_instance = MemoryCache(maxsize=settings.cache_max_size)
    return _cache_instance

def get_ai_provider(settings: Settings = Depends(get_settings)) -> AIProviderInterface:
    """Get or create AI provider instance."""
    global _ai_provider_instance
    if _ai_provider_instance is None:
        _ai_provider_instance = AIProviderFactory.get_default(settings)
    return _ai_provider_instance

def get_article_fetcher(settings: Settings = Depends(get_settings)) -> WebScraper:
    """Get article fetcher instance."""
    return WebScraper(
        timeout=settings.scraper_timeout_seconds,
        user_agent=settings.scraper_user_agent
    )

# app/api/deps.py
from fastapi import Depends
from app.dependencies import get_cache, get_ai_provider, get_article_fetcher
from app.core.use_cases.analyze_article import AnalyzeArticleUseCase
from app.core.use_cases.find_related import FindRelatedUseCase
from app.core.use_cases.compare_articles import CompareArticlesUseCase

def get_analyze_use_case(
    ai_provider = Depends(get_ai_provider),
    fetcher = Depends(get_article_fetcher),
    cache = Depends(get_cache)
) -> AnalyzeArticleUseCase:
    """Assemble analyze article use case with dependencies."""
    return AnalyzeArticleUseCase(
        ai_provider=ai_provider,
        article_fetcher=fetcher,
        cache=cache
    )
```

---

## 12. Main Application

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import articles, comparisons, health
from app.api.middleware.error_handler import error_handler_middleware
from app.api.middleware.logging import logging_middleware
import structlog

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger = structlog.get_logger()
    logger.info("starting_application", version=settings.app_version)
    yield
    logger.info("shutting_down_application")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Political spectrum analyzer for news articles",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Routes
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(articles.router, prefix=settings.api_prefix)
app.include_router(comparisons.router, prefix=settings.api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
```

---

## 13. Docker Configuration

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Production stage
FROM base as production
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM base as development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - NEWSAPI_KEY=${NEWSAPI_KEY}
      - CACHE_BACKEND=redis
      - REDIS_URL=redis://redis:6379
      - DEBUG=true
    volumes:
      - ../app:/app/app
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

---

## 14. Future Auth Integration Points

The architecture is designed to easily add authentication:

```python
# app/api/middleware/auth.py (future)
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

class AuthMiddleware:
    """Authentication middleware - currently pass-through."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.bearer = HTTPBearer(auto_error=False)

    async def __call__(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> Optional[dict]:
        if not self.enabled:
            return {"user_id": "anonymous", "tier": "free"}

        if not credentials:
            raise HTTPException(status_code=401, detail="Missing authentication")

        # Validate JWT token here
        # Return user context
        return await self._validate_token(credentials.credentials)

# Usage in routes:
# @router.post("/analyze", dependencies=[Depends(auth_middleware)])
```

---

## Architecture Decisions Record (ADR)

### ADR-001: Strategy Pattern for AI Providers
**Decision**: Use Strategy pattern with factory for AI providers
**Rationale**: Allows swapping providers without code changes, facilitates testing with mocks, enables A/B testing of providers
**Trade-offs**: Slight added complexity vs direct API calls

### ADR-002: In-Memory Cache for MVP
**Decision**: Start with in-memory cache, design for Redis migration
**Rationale**: Simpler local development, no external dependencies for MVP
**Trade-offs**: Cache lost on restart, not suitable for multiple instances

### ADR-003: Use Cases as Orchestrators
**Decision**: Implement business logic in use case classes
**Rationale**: Clean separation from API layer, easier to test, reusable across different entry points
**Trade-offs**: More files/classes than putting logic in routes

### ADR-004: Async-First Design
**Decision**: All I/O operations are async
**Rationale**: Better performance for I/O-bound operations (API calls, scraping)
**Trade-offs**: Requires async testing, slightly more complex code

---

## Summary

This architecture provides:

1. **Clean separation** - API, Use Cases, Services, and Entities are isolated
2. **Testability** - All dependencies are injected, enabling easy mocking
3. **Extensibility** - New AI providers, news sources, or features plug in easily
4. **Production readiness** - Caching, error handling, logging, and observability built in
5. **Simplicity** - MVP-focused with clear paths for enhancement
6. **Learning value** - Demonstrates real-world patterns in a practical context

Start with the core flow (analyze single article), then build out related articles and comparison features incrementally.
