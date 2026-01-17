"""
model/llm_client.py

Model / AI layer for StudyBuddy AI.

Responsibilities:
- Talk to OpenRouter API
- Provide a simple, robust function to generate text from prompts
- Hide all networking details from the rest of the app
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from services.openrouter_client import generate_llm_response as _openrouter_generate, LLMError


# Re-export LLMError for backward compatibility
__all__ = ["generate_llm_response", "LLMError"]


def generate_llm_response(
    prompt: str,
    api_key: str,
    model: str,
    chat_history: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Generate a text response from OpenRouter model.

    Args:
        prompt: The prompt string to send
        api_key: OpenRouter API key
        model: Model identifier to use
        chat_history: Optional chat history in format [{"role": "user", "content": "..."}, ...]

    Returns:
        Formatted assistant response text

    Raises:
        LLMError: If API call fails or response is invalid
    """
    return _openrouter_generate(
        prompt=prompt,
        api_key=api_key,
        model=model,
        chat_history=chat_history,
    )
