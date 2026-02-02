# Spectrum - Architecture Diagrams

## System Overview

```mermaid
flowchart TB
    subgraph Client["Frontend (React)"]
        UI[User Interface]
        State[State Management<br/>Zustand + TanStack Query]
    end

    subgraph Backend["Backend (FastAPI)"]
        API[API Routes]
        UC[Use Cases]

        subgraph Services["Services Layer"]
            AI[AI Provider<br/>Groq/Claude/OpenAI]
            Fetcher[Article Fetcher<br/>Web Scraper]
            News[News Aggregator<br/>NewsAPI]
            Cache[Cache Service<br/>Memory/Redis]
        end
    end

    subgraph External["External Services"]
        Groq[Groq API]
        NewsAPI[NewsAPI.org]
        Websites[News Websites]
    end

    UI --> State
    State --> API
    API --> UC
    UC --> Services

    AI --> Groq
    Fetcher --> Websites
    News --> NewsAPI

    Cache -.-> UC
```

## Article Analysis Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as API Server
    participant Cache as Cache
    participant Fetch as Article Fetcher
    participant AI as AI Provider (Groq)

    U->>FE: Paste article URL
    FE->>API: POST /articles/analyze

    API->>Cache: Check for cached analysis

    alt Cache Hit
        Cache-->>API: Return cached result
    else Cache Miss
        API->>Fetch: Fetch article content
        Fetch-->>API: Article title, content, metadata

        par Parallel AI Analysis
            API->>AI: Analyze political leaning
            API->>AI: Extract topics & keywords
        end

        AI-->>API: Leaning score + topics
        API->>Cache: Store analysis result
    end

    API-->>FE: Analysis response
    FE-->>U: Display spectrum + summary
```

## Political Analysis Dimensions

```mermaid
pie title Political Leaning Analysis Weights
    "Framing Language" : 25
    "Policy Positioning" : 25
    "Entity Sentiment" : 20
    "Source Attribution" : 15
    "Topic Emphasis" : 15
```

## AI Provider Strategy Pattern

```mermaid
classDiagram
    class AIProviderInterface {
        <<interface>>
        +name: str
        +analyze_political_leaning()
        +extract_topics()
        +extract_key_points()
        +compare_points()
        +health_check()
    }

    class BaseAIProvider {
        <<abstract>>
        -api_key: str
        -base_url: str
        -model: str
        +get_client()
        +make_request()
    }

    class GroqProvider {
        +name = "groq"
        +analyze_political_leaning()
        +extract_topics()
    }

    class ClaudeProvider {
        +name = "claude"
        +analyze_political_leaning()
        +extract_topics()
    }

    class OpenAIProvider {
        +name = "openai"
        +analyze_political_leaning()
        +extract_topics()
    }

    class AIProviderFactory {
        +create(provider_name)
        +get_default()
    }

    AIProviderInterface <|.. BaseAIProvider
    BaseAIProvider <|-- GroqProvider
    BaseAIProvider <|-- ClaudeProvider
    BaseAIProvider <|-- OpenAIProvider
    AIProviderFactory ..> AIProviderInterface : creates
```

## Caching Strategy

```mermaid
flowchart TB
    Request[Incoming Request]

    subgraph L1["L1: In-Memory Cache"]
        L1Check{Key exists?}
        L1Data[(Hot Data<br/>TTL varies)]
    end

    subgraph L2["L2: Redis Cache (Future)"]
        L2Check{Key exists?}
        L2Data[(Distributed<br/>Shared across instances)]
    end

    subgraph External["External Services"]
        AI[AI Provider<br/>$$$ per request]
        NewsAPI[News APIs<br/>Rate limited]
        Scraper[Web Scraper<br/>Slow]
    end

    Request --> L1Check
    L1Check -->|Hit| L1Data
    L1Check -->|Miss| L2Check
    L2Check -->|Hit| L2Data
    L2Check -->|Miss| External

    External --> L1Data
    External --> L2Data

    L1Data -->|Response| Request
    L2Data -->|Response| Request
```

## Frontend Component Hierarchy

```mermaid
flowchart TB
    App[App]

    subgraph Providers
        QP[QueryProvider]
        TP[ThemeProvider]
    end

    subgraph Layout
        Header
        Main[Main Content]
        Footer
    end

    subgraph Pages
        Home[HomePage]
        Analysis[AnalysisPage]
        Compare[ComparisonPage]
    end

    subgraph HomeComponents["Home Components"]
        URLInput[UrlInputForm]
        Recent[RecentAnalyses]
    end

    subgraph AnalysisComponents["Analysis Components"]
        ArticleHeader
        SpectrumViz[SpectrumVisualization]
        Summary[ArticleSummary]
        Related[RelatedArticles]
    end

    subgraph SpectrumParts["Spectrum Parts"]
        Scale[SpectrumScale]
        Marker[SpectrumMarker]
        Labels[SpectrumLabels]
        Confidence[ConfidenceIndicator]
    end

    App --> Providers
    Providers --> Layout
    Main --> Pages

    Home --> HomeComponents
    Analysis --> AnalysisComponents
    SpectrumViz --> SpectrumParts
```

## Data Flow: Full Analysis Workflow

```mermaid
flowchart LR
    subgraph Input
        URL[Article URL]
    end

    subgraph Fetch["1. Fetch"]
        Scrape[Scrape Content]
        Parse[Extract Text]
    end

    subgraph Analyze["2. Analyze"]
        Leaning[Political Leaning<br/>-1 to +1]
        Topics[Topic Extraction<br/>Keywords]
        Points[Key Points<br/>Claims]
    end

    subgraph Related["3. Find Related"]
        Search[Search NewsAPI]
        Filter[Filter & Dedupe]
    end

    subgraph Compare["4. Compare"]
        Align[Align Topics]
        Agree[Find Agreements]
        Disagree[Find Disagreements]
    end

    subgraph Output
        Result[Analysis Result<br/>+ Related Articles<br/>+ Comparison]
    end

    URL --> Fetch
    Fetch --> Analyze
    Analyze --> Related
    Related --> Compare
    Compare --> Output
```

## Political Spectrum Visualization

```mermaid
flowchart LR
    subgraph Spectrum["Political Spectrum Scale"]
        FL["-1.0<br/>Far Left"]
        L["-0.5<br/>Left"]
        C["0<br/>Center"]
        R["+0.5<br/>Right"]
        FR["+1.0<br/>Far Right"]
    end

    FL --- L --- C --- R --- FR

    style FL fill:#6366f1
    style L fill:#8b5cf6
    style C fill:#a855f7
    style R fill:#ec4899
    style FR fill:#f43f5e
```

## Comparison View Levels

```mermaid
flowchart TB
    subgraph Level1["Level 1: Summary"]
        S1[Spectrum with both markers]
        S2[Key agreements bullet list]
        S3[Key disagreements bullet list]
    end

    subgraph Level2["Level 2: Side-by-Side"]
        A1[Article A Column]
        A2[Article B Column]
        A1 --- A2
    end

    subgraph Level3["Level 3: Interactive Diff"]
        T1[Topic 1: Economic Impact]
        T2[Topic 2: Government Role]
        T3[Topic 3: Timeline]
    end

    Level1 --> Level2 --> Level3
```

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Users
        Browser[Web Browser]
        Extension[Chrome Extension<br/>Future]
    end

    subgraph Frontend["Frontend Hosting (Vercel)"]
        React[React App<br/>Static Build]
    end

    subgraph Backend["Backend Hosting (Render/Railway)"]
        FastAPI[FastAPI Server]
        MemCache[In-Memory Cache]
    end

    subgraph External
        Groq[Groq API]
        NewsAPI[NewsAPI]
    end

    Browser --> React
    Extension -.-> React
    React --> FastAPI
    FastAPI --> MemCache
    FastAPI --> Groq
    FastAPI --> NewsAPI
```
