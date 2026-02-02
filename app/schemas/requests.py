"""Request schemas for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AnalyzeArticleRequest(BaseModel):
    """Request to analyze an article by URL."""

    url: HttpUrl = Field(..., description="URL of the article to analyze")
    include_points: bool = Field(
        default=True,
        description="Extract key points (slower but more detailed)",
    )
    force_refresh: bool = Field(
        default=False,
        description="Bypass cache and re-analyze",
    )

    @field_validator("url", mode="before")
    @classmethod
    def upgrade_http_to_https(cls, v):
        """Upgrade HTTP URLs to HTTPS for security."""
        if isinstance(v, str) and v.startswith("http://"):
            return v.replace("http://", "https://", 1)
        return v


class AnalyzeTextRequest(BaseModel):
    """Request to analyze raw text (no URL required)."""

    title: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Article title",
    )
    content: str = Field(
        ...,
        min_length=100,
        max_length=50000,
        description="Article body text",
    )
    source_name: Optional[str] = Field(
        default="Unknown",
        description="Name of the publication",
    )
    source_url: Optional[HttpUrl] = Field(
        default=None,
        description="Optional source URL for reference",
    )


class FindRelatedRequest(BaseModel):
    """Request to find related articles."""

    url: Optional[HttpUrl] = Field(
        default=None,
        description="Original article URL (will extract keywords)",
    )
    keywords: Optional[list[str]] = Field(
        default=None,
        description="Direct search keywords",
    )
    topic: Optional[str] = Field(
        default=None,
        description="Topic or category to search",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of results",
    )
    days_back: int = Field(
        default=7,
        ge=1,
        le=30,
        description="How many days back to search",
    )
    analyze_results: bool = Field(
        default=False,
        description="Run political analysis on results",
    )

    @field_validator("keywords", mode="after")
    @classmethod
    def validate_has_search_criteria(cls, v, info):
        """Ensure at least one search criteria is provided."""
        if v is None and info.data.get("url") is None and info.data.get("topic") is None:
            raise ValueError("Must provide url, keywords, or topic")
        return v


class CompareArticlesRequest(BaseModel):
    """Request to compare multiple articles."""

    article_urls: list[HttpUrl] = Field(
        ...,
        min_length=2,
        max_length=5,
        description="URLs of articles to compare (2-5)",
    )
    comparison_depth: str = Field(
        default="full",
        pattern="^(quick|full|deep)$",
        description="Comparison depth: quick (leaning only), full (with points), deep (detailed)",
    )


class FullAnalysisRequest(BaseModel):
    """Request for complete analysis workflow (analyze + related + compare)."""

    url: HttpUrl = Field(..., description="URL of the primary article")
    find_related: bool = Field(
        default=True,
        description="Search for related articles",
    )
    related_count: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of related articles to find",
    )
    compare_all: bool = Field(
        default=True,
        description="Compare primary with related articles",
    )
