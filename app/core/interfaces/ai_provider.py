"""Abstract interface for AI providers."""

from abc import ABC, abstractmethod
from typing import Optional

from app.core.entities.analysis import (
    ArticlePoint,
    PoliticalLeaning,
    TopicAnalysis,
)
from app.core.entities.comparison import PointComparison


class AIProviderInterface(ABC):
    """Abstract interface for AI providers.

    Implementations must handle:
    - Political leaning analysis
    - Topic/keyword extraction
    - Key point extraction
    - Point comparison between articles
    """

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
        source_name: Optional[str] = None,
    ) -> PoliticalLeaning:
        """Analyze political leaning of article content.

        Args:
            title: Article title
            content: Article body text
            source_name: Name of the publication (for context)

        Returns:
            PoliticalLeaning with score from -1 (left) to 1 (right)
        """
        pass

    @abstractmethod
    async def extract_topics(
        self,
        title: str,
        content: str,
    ) -> TopicAnalysis:
        """Extract topics and keywords from article.

        Args:
            title: Article title
            content: Article body text

        Returns:
            TopicAnalysis with primary topic, keywords, and entities
        """
        pass

    @abstractmethod
    async def extract_key_points(
        self,
        title: str,
        content: str,
        max_points: int = 5,
    ) -> list[ArticlePoint]:
        """Extract key points/claims from article.

        Args:
            title: Article title
            content: Article body text
            max_points: Maximum number of points to extract

        Returns:
            List of ArticlePoint objects
        """
        pass

    @abstractmethod
    async def compare_points(
        self,
        points_a: list[ArticlePoint],
        points_b: list[ArticlePoint],
        article_a_context: str,
        article_b_context: str,
    ) -> list[PointComparison]:
        """Compare points between two articles.

        Args:
            points_a: Key points from first article
            points_b: Key points from second article
            article_a_context: Title/summary of first article
            article_b_context: Title/summary of second article

        Returns:
            List of PointComparison showing agreements/disagreements
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available and responding."""
        pass

    async def close(self) -> None:
        """Clean up resources. Override if needed."""
        pass
