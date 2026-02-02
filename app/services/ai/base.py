"""Base AI provider with common functionality."""

from abc import ABC, abstractmethod
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.interfaces.ai_provider import AIProviderInterface


class BaseAIProvider(AIProviderInterface, ABC):
    """Base class with common functionality for AI providers."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._client: httpx.AsyncClient | None = None

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests. Override in subclass if needed."""
        return {"Authorization": f"Bearer {self.api_key}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def _make_request(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Make API request with retry logic."""
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
    def _build_request_body(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        """Build request body for API call."""
        pass

    @abstractmethod
    def _parse_response(self, response: dict[str, Any]) -> str:
        """Parse response from API."""
        pass

    def _get_political_leaning_prompt(
        self, title: str, content: str, source: str | None
    ) -> str:
        """Generate prompt for political leaning analysis."""
        return f"""Analyze the political leaning of this news article.

Title: {title}
Source: {source or 'Unknown'}
Content: {content[:8000]}

Provide your analysis as JSON with this exact structure:
{{
    "score": <float from -1.0 (far left) to 1.0 (far right), 0 is center>,
    "confidence": <float from 0.0 to 1.0>,
    "reasoning": "<brief explanation of why you assigned this score>",
    "economic_score": <float from -1.0 to 1.0 for economic policy stance, or null if not applicable>,
    "social_score": <float from -1.0 to 1.0 for social policy stance, or null if not applicable>
}}

Consider:
- Word choice and framing
- Sources cited
- Topics emphasized or omitted
- Emotional vs factual tone
- Known bias of the source (if any)

Be objective and avoid imposing your own biases. Focus on language patterns and framing.

Respond ONLY with valid JSON."""

    def _get_topics_prompt(self, title: str, content: str) -> str:
        """Generate prompt for topic extraction."""
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

Keywords should be specific enough to find related articles. Include no more than 10 keywords.
Entities should be named entities (people, organizations, places).

Respond ONLY with valid JSON."""

    def _get_key_points_prompt(self, title: str, content: str, max_points: int) -> str:
        """Generate prompt for key points extraction."""
        return f"""Extract the {max_points} most important claims or points from this article.

Title: {title}
Content: {content[:6000]}

Respond with JSON:
{{
    "points": [
        {{
            "id": "p1",
            "statement": "<clear statement of the point/claim>",
            "supporting_quote": "<direct quote from article if available, or null>",
            "sentiment": "positive" | "negative" | "neutral"
        }}
    ]
}}

Focus on:
- Key factual claims
- Opinions or positions taken
- Conclusions drawn
- Important statistics or data points

Respond ONLY with valid JSON."""

    def _get_compare_points_prompt(
        self,
        points_a_text: str,
        points_b_text: str,
        article_a_context: str,
        article_b_context: str,
    ) -> str:
        """Generate prompt for comparing points between articles."""
        return f"""Compare these points from two articles on the same topic.

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
            "relationship": "agrees" | "disagrees" | "related" | "unrelated",
            "explanation": "<why they agree/disagree>"
        }}
    ]
}}

Only include comparisons where there is a meaningful relationship.

Respond ONLY with valid JSON."""
