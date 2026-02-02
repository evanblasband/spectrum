"""Abstract interface for AI providers."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.entities.analysis import (
        ArticlePoint,
        PointComparison,
        PoliticalLeaning,
        TopicAnalysis,
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
        source_name: str | None = None,
    ) -> "PoliticalLeaning":
        """Analyze political leaning of article content."""
        pass

    @abstractmethod
    async def extract_topics(
        self,
        title: str,
        content: str,
    ) -> "TopicAnalysis":
        """Extract topics and keywords from article."""
        pass

    @abstractmethod
    async def extract_key_points(
        self,
        title: str,
        content: str,
        max_points: int = 5,
    ) -> list["ArticlePoint"]:
        """Extract key points/claims from article."""
        pass

    @abstractmethod
    async def compare_points(
        self,
        points_a: list["ArticlePoint"],
        points_b: list["ArticlePoint"],
        article_a_context: str,
        article_b_context: str,
    ) -> list["PointComparison"]:
        """Compare points between two articles."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available."""
        pass
