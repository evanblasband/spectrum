"""Groq AI provider implementation."""

import json
import logging
from typing import Any

from app.core.entities.analysis import (
    ArticlePoint,
    PointComparison,
    PoliticalLeaning,
    TopicAnalysis,
)
from app.services.ai.base import BaseAIProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseAIProvider):
    """Groq AI provider implementation using Llama models."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model=model,
        )

    @property
    def name(self) -> str:
        return "groq"

    @property
    def supports_streaming(self) -> bool:
        return True

    def _get_endpoint(self) -> str:
        return "/chat/completions"

    def _build_request_body(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        if kwargs.get("json_mode"):
            body["response_format"] = {"type": "json_object"}
        return body

    def _parse_response(self, response: dict[str, Any]) -> str:
        return response["choices"][0]["message"]["content"]

    async def analyze_political_leaning(
        self,
        title: str,
        content: str,
        source_name: str | None = None,
    ) -> PoliticalLeaning:
        """Analyze political leaning of article content."""
        prompt = self._get_political_leaning_prompt(title, content, source_name)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return PoliticalLeaning(
            score=data["score"],
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            economic_score=data.get("economic_score"),
            social_score=data.get("social_score"),
        )

    async def extract_topics(self, title: str, content: str) -> TopicAnalysis:
        """Extract topics and keywords from article."""
        prompt = self._get_topics_prompt(title, content)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return TopicAnalysis(
            primary_topic=data["primary_topic"],
            secondary_topics=data.get("secondary_topics", []),
            keywords=data.get("keywords", [])[:10],  # Limit to 10 keywords
            entities=data.get("entities", []),
        )

    async def extract_key_points(
        self,
        title: str,
        content: str,
        max_points: int = 5,
    ) -> list[ArticlePoint]:
        """Extract key points/claims from article."""
        prompt = self._get_key_points_prompt(title, content, max_points)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        return [ArticlePoint(**p) for p in data["points"]]

    async def compare_points(
        self,
        points_a: list[ArticlePoint],
        points_b: list[ArticlePoint],
        article_a_context: str,
        article_b_context: str,
    ) -> list[PointComparison]:
        """Compare points between two articles."""
        points_a_text = "\n".join([f"- [{p.id}] {p.statement}" for p in points_a])
        points_b_text = "\n".join([f"- [{p.id}] {p.statement}" for p in points_b])

        prompt = self._get_compare_points_prompt(
            points_a_text, points_b_text, article_a_context, article_b_context
        )
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, json_mode=True)
        data = json.loads(response)

        # Map back to full PointComparison objects
        points_a_map = {p.id: p for p in points_a}
        points_b_map = {p.id: p for p in points_b}

        comparisons = []
        for c in data.get("comparisons", []):
            point_a_id = c.get("point_a_id")
            point_b_id = c.get("point_b_id")
            if point_a_id in points_a_map and point_b_id in points_b_map:
                comparisons.append(
                    PointComparison(
                        point_a=points_a_map[point_a_id],
                        point_b=points_b_map[point_b_id],
                        article_a_id="",  # Filled in by use case
                        article_b_id="",
                        relationship=c["relationship"],
                        explanation=c["explanation"],
                    )
                )

        return comparisons

    async def health_check(self) -> bool:
        """Check if provider is available."""
        try:
            client = await self.get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")
            return False
