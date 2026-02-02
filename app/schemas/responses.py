"""Response schemas for API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.core.entities.analysis import ArticleAnalysis
from app.core.entities.comparison import MultiArticleComparison


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class AnalysisResponse(BaseModel):
    """Response for article analysis."""

    success: bool = True
    data: Optional[ArticleAnalysis] = None
    error: Optional[str] = None
    cached: bool = False
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class RelatedArticlePreview(BaseModel):
    """Preview of a related article (before full analysis)."""

    url: HttpUrl
    title: str
    source: str
    published_at: Optional[datetime] = None
    snippet: Optional[str] = None


class RelatedArticlesResponse(BaseModel):
    """Response for related articles search."""

    success: bool = True
    original_analysis: Optional[ArticleAnalysis] = None
    search_keywords: list[str] = Field(default_factory=list)
    articles: list[RelatedArticlePreview] = Field(default_factory=list)
    analyses: list[ArticleAnalysis] = Field(
        default_factory=list,
        description="Analyses if analyze_results was True",
    )
    total_found: int = 0
    error: Optional[str] = None


class ComparisonResponse(BaseModel):
    """Response for article comparison."""

    success: bool = True
    data: Optional[MultiArticleComparison] = None
    error: Optional[str] = None
    articles_analyzed: int = 0
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class FullAnalysisResponse(BaseModel):
    """Response for complete analysis workflow."""

    success: bool = True
    primary_article: Optional[ArticleAnalysis] = None
    related_articles: list[ArticleAnalysis] = Field(default_factory=list)
    comparison: Optional[MultiArticleComparison] = None
    error: Optional[str] = None
    total_processing_time_ms: int = Field(..., description="Total processing time in milliseconds")


class HealthResponse(BaseModel):
    """Response for health check endpoints."""

    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict[str, bool] = Field(
        default_factory=dict,
        description="Status of dependent services",
    )
