"""Base AI provider implementation with shared functionality."""

from abc import abstractmethod
from typing import Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.interfaces.ai_provider import AIProviderInterface


class BaseAIProvider(AIProviderInterface):
    """Base class with common functionality for AI providers."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=60.0,
            )
        return self._client

    def _get_headers(self) -> dict:
        """Get request headers. Override for provider-specific headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
    )
    async def _make_request(
        self,
        messages: list[dict],
        **kwargs,
    ) -> str:
        """Make API request with retry logic.

        Args:
            messages: Chat messages to send
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Response content string
        """
        client = await self.get_client()
        response = await client.post(
            self._get_endpoint(),
            json=self._build_request_body(messages, **kwargs),
        )
        response.raise_for_status()
        return self._parse_response(response.json())

    @abstractmethod
    def _get_endpoint(self) -> str:
        """Get API endpoint path."""
        pass

    @abstractmethod
    def _build_request_body(self, messages: list[dict], **kwargs) -> dict:
        """Build request body for API call."""
        pass

    @abstractmethod
    def _parse_response(self, response: dict) -> str:
        """Parse response and extract content."""
        pass

    def _get_political_leaning_prompt(
        self,
        title: str,
        content: str,
        source: Optional[str],
    ) -> str:
        """Get prompt for political leaning analysis."""
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

Respond ONLY with valid JSON, no additional text."""

    def _get_topics_prompt(self, title: str, content: str) -> str:
        """Get prompt for topic extraction."""
        return f"""Extract topics and keywords from this article.

Title: {title}
Content: {content[:6000]}

Respond with JSON:
{{
    "primary_topic": "<main topic>",
    "secondary_topics": ["<topic1>", "<topic2>"],
    "keywords": ["<keyword1>", "<keyword2>", ...],
    "entities": ["<person/org name>", ...]
}}

Guidelines:
- primary_topic: The main subject of the article (1-3 words)
- secondary_topics: Related but secondary topics (max 3)
- keywords: Important terms for finding related articles (max 10)
- entities: Named people, organizations, places mentioned

Respond ONLY with valid JSON, no additional text."""

    def _get_key_points_prompt(
        self,
        title: str,
        content: str,
        max_points: int,
    ) -> str:
        """Get prompt for key point extraction."""
        return f"""Extract the {max_points} most important claims or points from this article.

Title: {title}
Content: {content[:6000]}

Respond with JSON:
{{
    "points": [
        {{
            "id": "p1",
            "statement": "<clear statement of the point/claim>",
            "supporting_quote": "<direct quote from article if available, null otherwise>",
            "sentiment": "positive|negative|neutral"
        }}
    ]
}}

Guidelines:
- Focus on factual claims and arguments, not descriptive text
- Each point should be a complete, standalone statement
- Include direct quotes when they support the point
- Sentiment refers to the tone of the point

Respond ONLY with valid JSON, no additional text."""

    def _get_compare_points_prompt(
        self,
        points_a: list,
        points_b: list,
        article_a_context: str,
        article_b_context: str,
    ) -> str:
        """Get prompt for comparing points between articles."""
        points_a_text = "\n".join([f"- [{p.id}] {p.statement}" for p in points_a])
        points_b_text = "\n".join([f"- [{p.id}] {p.statement}" for p in points_b])

        return f"""Compare these points from two articles on the same topic.

Article A: {article_a_context}
Article A points:
{points_a_text}

Article B: {article_b_context}
Article B points:
{points_b_text}

Find agreements and disagreements between the articles. Respond with JSON:
{{
    "comparisons": [
        {{
            "point_a_id": "<id from article A>",
            "point_b_id": "<id from article B>",
            "relationship": "agrees|disagrees|related|unrelated",
            "explanation": "<brief explanation of why they agree/disagree>"
        }}
    ]
}}

Guidelines:
- Compare points that address similar topics
- "agrees" = both articles make the same or supporting claims
- "disagrees" = articles make contradicting claims
- "related" = points discuss same topic but different aspects
- Don't force comparisons - only include meaningful relationships

Respond ONLY with valid JSON, no additional text."""

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
