"""Factory for creating AI provider instances."""

from typing import Type

from app.config import Settings
from app.core.interfaces.ai_provider import AIProviderInterface
from app.services.ai.claude_provider import ClaudeProvider
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.openai_provider import OpenAIProvider


class AIProviderFactory:
    """Factory for creating AI provider instances.

    Supports registration of custom providers for extensibility.
    """

    _providers: dict[str, Type[AIProviderInterface]] = {
        "groq": GroqProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        settings: Settings,
    ) -> AIProviderInterface:
        """Create an AI provider instance.

        Args:
            provider_name: Name of the provider to create
            settings: Application settings

        Returns:
            Configured AI provider instance

        Raises:
            ValueError: If provider is unknown or not configured
        """
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: {provider_name}. Available: {available}"
            )

        provider_class = cls._providers[provider_name]

        if provider_name == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY not configured")
            return provider_class(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
            )

        elif provider_name == "claude":
            if not settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            return provider_class(
                api_key=settings.anthropic_api_key,
                model=settings.claude_model,
            )

        elif provider_name == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            return provider_class(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
            )

        # For custom registered providers
        raise ValueError(f"No configuration handler for provider: {provider_name}")

    @classmethod
    def get_default(cls, settings: Settings) -> AIProviderInterface:
        """Get the default provider based on settings.

        Args:
            settings: Application settings

        Returns:
            Default AI provider instance
        """
        return cls.create(settings.default_ai_provider, settings)

    @classmethod
    def register(cls, name: str, provider_class: Type[AIProviderInterface]) -> None:
        """Register a new provider type.

        Args:
            name: Provider name for configuration
            provider_class: Provider implementation class
        """
        cls._providers[name] = provider_class

    @classmethod
    def available_providers(cls) -> list[str]:
        """Get list of available provider names."""
        return list(cls._providers.keys())
