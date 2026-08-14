"""Central AI provider configuration and helpers.

This module centralizes reading API keys and default models from environment
variables and exposes helpers for other modules to consume.
"""
from typing import Dict, List
import os

PROVIDERS: List[str] = [
    # Prefer providers known to be working in this environment
    "groq",
    "gemini",
    "openrouter",
    "openai",
    "pollinations",
]

def load_provider_keys() -> Dict[str, str]:
    return {
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "openrouter": os.environ.get("OPENROUTER_API_KEY", os.environ.get("API_KEY", "")),
        "groq": os.environ.get("GROQ_API_KEY", ""),
        "gemini": os.environ.get("GEMINI_API_KEY", ""),
        "pollinations": os.environ.get("POLLINATION_API_KEY", ""),
    }

def load_models() -> Dict[str, str]:
    return {
        "openai": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
        "openrouter": os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
        "groq": os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        "gemini": os.environ.get("GEMINI_MODEL", "gemma-4-26b-a4b-it"),
        "pollinations": os.environ.get("POLLINATION_MODEL", "mistral"),
    }

def configured_providers() -> List[str]:
    keys = load_provider_keys()
    # Return providers that have a non-empty key, preserving order
    return [p for p in PROVIDERS if keys.get(p)]

def any_provider_configured() -> bool:
    return any(bool(v) for v in load_provider_keys().values())
