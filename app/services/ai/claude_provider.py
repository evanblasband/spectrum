"""Claude (Anthropic) AI provider implementation."""

import json
from typing import Optional

from app.core.entities.analysis import (
    ArticlePoint,
    PoliticalLeaning,
    TopicAnalysis,
)
from app.core.entities.comparison import PointComparison
from app.services.ai.base import BaseAIProvider


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude AI provider implementation."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        super().__init__(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
            model=model,
        )

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_streaming(self) -> bool:
        return True

    def _get_headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _get_endpoint(self) -> str:
        return "/messages"

    def _build_request_body(self, messages: list[dict], **kwargs) -> dict:
        # Convert OpenAI-style messages to Anthropic format
        anthropic_messages = []
        system_message = None

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

        body = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.1),
        }

        if system_message:
            body["system"] = system_message

        return body

    def _parse_response(self, response: dict) -> str:
        return response["content"][0]["text"]

    async def analyze_political_leaning(
        self,
        title: str,
        content: str,
        source_name: Optional[str] = None,
    ) -> PoliticalLeaning:
        """Analyze political leaning of article content."""
        prompt = self._get_political_leaning_prompt(title, content, source_name)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages)

        # Extract JSON from response (Claude may include markdown)
        json_str = self._extract_json(response)
        data = json.loads(json_str)

        return PoliticalLeaning(
            score=float(data["score"]),
            confidence=float(data["confidence"]),
            reasoning=data["reasoning"],
            economic_score=data.get("economic_score"),
            social_score=data.get("social_score"),
            criteria_scores=data.get("criteria_scores"),
        )

    async def extract_topics(
        self,
        title: str,
        content: str,
    ) -> TopicAnalysis:
        """Extract topics and keywords from article."""
        prompt = self._get_topics_prompt(title, content)
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages)
        json_str = self._extract_json(response)
        data = json.loads(json_str)

        return TopicAnalysis(
            primary_topic=data["primary_topic"],
            secondary_topics=data.get("secondary_topics", []),
            keywords=data.get("keywords", [])[:10],
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

        response = await self._make_request(messages)
        json_str = self._extract_json(response)
        data = json.loads(json_str)

        return [
            ArticlePoint(
                id=p["id"],
                statement=p["statement"],
                supporting_quote=p.get("supporting_quote"),
                sentiment=p.get("sentiment", "neutral"),
            )
            for p in data.get("points", [])
        ]

    async def compare_points(
        self,
        points_a: list[ArticlePoint],
        points_b: list[ArticlePoint],
        article_a_context: str,
        article_b_context: str,
    ) -> list[PointComparison]:
        """Compare points between two articles."""
        if not points_a or not points_b:
            return []

        prompt = self._get_compare_points_prompt(
            points_a,
            points_b,
            article_a_context,
            article_b_context,
        )
        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages)
        json_str = self._extract_json(response)
        data = json.loads(json_str)

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
                        article_a_id="",
                        article_b_id="",
                        relationship=c.get("relationship", "related"),
                        explanation=c.get("explanation", ""),
                    )
                )

        return comparisons

    async def health_check(self) -> bool:
        """Check if Claude API is available."""
        try:
            # Simple health check - send minimal request
            messages = [{"role": "user", "content": "Hi"}]
            await self._make_request(messages, max_tokens=10)
            return True
        except Exception:
            return False

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from text that may contain markdown code blocks."""
        # Try to find JSON in code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # Try to find raw JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return text[start:end]

        return text
