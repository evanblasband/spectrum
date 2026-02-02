"""Factory for creating AI provider instances."""

from typing import Type

from app.config import Settings
from app.core.interfaces.ai_provider import AIProviderInterface
from app.services.ai.groq_provider import GroqProvider


class AIProviderFactory:
    """Factory for creating AI provider instances."""

    _providers: dict[str, Type[AIProviderInterface]] = {
        "groq": GroqProvider,
    }

    @classmethod
    def create(cls, provider_name: str, settings: Settings) -> AIProviderInterface:
        """Create an AI provider instance."""
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. Available: {available}"
            )

        provider_class = cls._providers[provider_name]

        if provider_name == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is required for Groq provider")
            return provider_class(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
            )

        raise ValueError(f"Provider {provider_name} not configured")

    @classmethod
    def get_default(cls, settings: Settings) -> AIProviderInterface:
        """Get the default provider based on settings."""
        return cls.create(settings.default_ai_provider, settings)

    @classmethod
    def register(cls, name: str, provider_class: Type[AIProviderInterface]) -> None:
        """Register a new provider type."""
        cls._providers[name] = provider_class

    @classmethod
    def available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())
