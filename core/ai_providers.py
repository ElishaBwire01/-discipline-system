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
    # 'pollinations' intentionally excluded per project policy
]

# Task-specific provider routing. Keys are normalized task identifiers.
TASK_ROUTING = {
    # incident classification: prefer Google Gemini, fall back to Groq
    "incident_classification": ["gemini", "groq", "openrouter", "openai"],
    # report generation: Gemini first, Groq as fallback
    "report_generation": ["gemini", "groq", "openrouter", "openai"],
    # short responses: Groq first for concise replies, then Gemini
    "short_responses": ["groq", "gemini", "openrouter", "openai"],
    # long-context analysis: Gemini preferred (long-context engines), then Groq
    "long_context_analysis": ["gemini", "groq", "openrouter", "openai"],
}

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
        # Prefer the Gemma family when using Gemini
        "gemini": os.environ.get("GEMINI_MODEL", "gemma"),
        # Pollinations intentionally not used
    }

def configured_providers() -> List[str]:
    keys = load_provider_keys()
    # Return providers that have a non-empty key, preserving order
    return [p for p in PROVIDERS if keys.get(p)]


def get_providers_for_task(task_type: str) -> List[str]:
    """Return ordered list of providers for a given task_type.

    If the task_type is unknown, return the configured providers in their
    default order. The returned list only includes providers that have
    non-empty API keys (configured).
    """
    if not task_type:
        return configured_providers()

    normalized = re_normalize_task = task_type.lower().strip().replace(" ", "_")
    # If a mapping exists, pick it; otherwise, return configured providers
    mapping = TASK_ROUTING.get(normalized)
    if not mapping:
        return configured_providers()

    # Filter mapping by providers that are actually configured
    configured = configured_providers()
    ordered = [p for p in mapping if p in configured]
    # Append any remaining configured providers not already present
    for p in configured:
        if p not in ordered:
            ordered.append(p)
    return ordered

def any_provider_configured() -> bool:
    return any(bool(v) for v in load_provider_keys().values())
