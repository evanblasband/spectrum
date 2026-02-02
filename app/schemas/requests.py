"""Request schemas for API endpoints."""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AnalyzeArticleRequest(BaseModel):
    """Request to analyze an article by URL."""

    url: HttpUrl
    include_points: bool = True
    force_refresh: bool = False  # Bypass cache

    @field_validator("url", mode="before")
    @classmethod
    def validate_url_protocol(cls, v: str) -> str:
        """Upgrade HTTP to HTTPS."""
        if isinstance(v, str) and v.startswith("http://"):
            return v.replace("http://", "https://", 1)
        return v


class AnalyzeTextRequest(BaseModel):
    """Request to analyze raw text."""

    title: str = Field(..., min_length=5, max_length=500)
    content: str = Field(..., min_length=100, max_length=50000)
    source_name: str = "Unknown"
    source_url: Optional[HttpUrl] = None


class FindRelatedRequest(BaseModel):
    """Request to find related articles."""

    url: Optional[HttpUrl] = None
    keywords: Optional[list[str]] = None
    topic: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    days_back: int = Field(default=7, ge=1, le=30)

    @field_validator("keywords", mode="after")
    @classmethod
    def validate_has_search_criteria(
        cls, v: Optional[list[str]], info
    ) -> Optional[list[str]]:
        """Ensure at least one search criteria is provided."""
        if v is None and info.data.get("url") is None and info.data.get("topic") is None:
            raise ValueError("Must provide url, keywords, or topic")
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
