"""Response schemas for API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.core.entities.analysis import ArticleAnalysis, ArticlePoint, PoliticalLeaning, TopicAnalysis


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
    published_at: Optional[datetime] = None
    snippet: Optional[str] = None


class RelatedArticlesResponse(BaseModel):
    """Response for related articles search."""

    success: bool
    original_keywords: list[str]
    articles: list[RelatedArticlePreview]
    total_found: int
    error: Optional[str] = None


class AnalyzedRelatedArticle(BaseModel):
    """Related article with full analysis."""

    url: HttpUrl
    title: str
    source: str
    published_at: Optional[datetime] = None
    political_leaning: PoliticalLeaning
    topics: TopicAnalysis


class RelatedArticlesWithAnalysisResponse(BaseModel):
    """Response for related articles with analysis."""

    success: bool
    original_article: ArticleAnalysis
    related_articles: list[AnalyzedRelatedArticle]
    error: Optional[str] = None
    processing_time_ms: int


class ComparisonSummary(BaseModel):
    """Summary comparison between articles."""

    leaning_spread: float  # Max difference in political leaning
    common_topics: list[str]
    agreements: list[str]  # Summary statements
    disagreements: list[str]  # Summary statements


class ComparisonResponse(BaseModel):
    """Response for article comparison."""

    success: bool
    articles: list[ArticleAnalysis]
    summary: Optional[ComparisonSummary] = None
    error: Optional[str] = None
    processing_time_ms: int


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    detail: Optional[str] = None
