"""
services/openrouter_client.py

OpenRouter API client for StudyBuddy AI.

Responsibilities:
- Call OpenRouter Chat Completions API
- Handle API errors gracefully
- Support model fallback
- Return assistant text responses
"""

from __future__ import annotations

from typing import List, Dict, Optional, Any

import requests
from utils.formatters import ensure_markdown_headings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model options with fallback order
DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free"
FALLBACK_MODELS = [
    "xiaomi/mimo-v2-flash:free",
    "mistralai/devstral-2-2512:free",
    "tngtech/deepseek-r1t2-chimera:free",
]


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    
    def __init__(self, message: str, is_model_error: bool = False):
        super().__init__(message)
        self.is_model_error = is_model_error


def openrouter_chat(
    messages: List[Dict[str, str]],
    api_key: str,
    model: str,
    temperature: float = 0.5,
    max_tokens: int = 700,
) -> str:
    """
    Call OpenRouter Chat Completions API and return assistant response.
    
    Args:
        messages: List of message dicts with "role" and "content" keys
        api_key: OpenRouter API key
        model: Model identifier (e.g., "xiaomi/mimo-v2-flash:free")
        temperature: Sampling temperature (default: 0.5)
        max_tokens: Maximum tokens to generate (default: 700)
    
    Returns:
        Assistant response text
    
    Raises:
        LLMError: If API call fails or response is invalid
    """
    if not api_key or not api_key.strip():
        raise LLMError("OpenRouter API key is required. Please set it in the .env file or environment variables.")
    
    # Validate API key format (should start with sk-or-v1- or sk-or-v1)
    api_key_clean = api_key.strip()
    # Allow both sk-or-v1- and sk-or-v1 formats, and also check for common variations
    valid_prefixes = ["sk-or-v1-", "sk-or-v1", "sk-"]
    if not any(api_key_clean.startswith(prefix) for prefix in valid_prefixes):
        raise LLMError(
            "Invalid API key format. OpenRouter API keys should start with 'sk-or-v1-' or 'sk-'. "
            "Please check your .env file and get a valid key from https://openrouter.ai/keys"
        )
    
    if not messages:
        raise LLMError("Messages list is empty. Cannot generate a response.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "StudyBuddy AI",
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.exceptions.ConnectionError as exc:
        raise LLMError(
            "Could not connect to OpenRouter API. Please check your internet connection."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise LLMError("The request to OpenRouter timed out. Please try again.") from exc
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"Unexpected error while calling OpenRouter: {exc}") from exc
    
    if response.status_code != 200:
        try:
            data = response.json()
            error_msg = data.get("error", {}).get("message", "") or data.get("message", "") or response.text
        except Exception:  # noqa: BLE001
            error_msg = response.text
        
        # Handle specific error codes with user-friendly messages
        if response.status_code == 401:
            # 401 = Unauthorized - API key is invalid or expired
            raise LLMError(
                "Authentication failed. Your OpenRouter API key is invalid or expired. "
                "Please check your `.env` file and ensure the key starts with 'sk-or-v1-'. "
                "Get a new key at: https://openrouter.ai/keys",
                is_model_error=False,
            )
        elif response.status_code == 429:
            # 429 = Rate limit exceeded
            raise LLMError(
                "Rate limit exceeded. Please wait a moment and try again.",
                is_model_error=False,
            )
        
        # Check if it's a model error that might be fixed by fallback
        error_lower = error_msg.lower()
        is_model_error = (
            "model" in error_lower and ("not found" in error_lower or "invalid" in error_lower)
        )
        
        # Don't expose full error details for security
        user_friendly_msg = error_msg
        if "key" in error_lower or "api" in error_lower or "auth" in error_lower:
            user_friendly_msg = "API authentication error. Please check your API key in the .env file."
        
        raise LLMError(
            f"OpenRouter API error (status {response.status_code}): {user_friendly_msg}",
            is_model_error=is_model_error,
        )
    
    try:
        data = response.json()
    except Exception as exc:  # noqa: BLE001
        raise LLMError(f"Failed to parse response from OpenRouter: {exc}") from exc
    
    # Extract assistant message from response
    choices = data.get("choices", [])
    if not choices:
        raise LLMError("Received an empty response from OpenRouter.")
    
    message = choices[0].get("message", {})
    text: Optional[str] = message.get("content")
    
    if not text:
        raise LLMError("Received an empty response from the LLM.")
    
    return text


def generate_llm_response(
    prompt: str,
    api_key: str,
    model: str,
    chat_history: Optional[List[Dict[str, Any]]] = None,
    system_message: str = "You are StudyBuddy AI, a friendly and patient tutor helping students learn.",
) -> str:
    """
    Generate a text response from OpenRouter model.
    
    Converts a prompt string to OpenRouter messages format and calls the API.
    Tries fallback models if the primary model fails.
    
    Args:
        prompt: The prompt string to send
        api_key: OpenRouter API key
        model: Primary model to use
        chat_history: Optional chat history in format [{"role": "user", "content": "..."}, ...]
        system_message: System message to prepend
    
    Returns:
        Formatted assistant response text
    """
    if not prompt or not prompt.strip():
        raise LLMError("Prompt is empty. Cannot generate a response.")
    
    # Build messages array
    messages = []
    
    # Add system message
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    # Add chat history if provided
    if chat_history:
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
    
    # Add current prompt as user message
    messages.append({"role": "user", "content": prompt})
    
    # Determine which models to try
    models_to_try = [model]
    if model not in FALLBACK_MODELS:
        models_to_try.extend(FALLBACK_MODELS)
    else:
        # If model is in fallback list, try other fallbacks after it
        current_idx = FALLBACK_MODELS.index(model) if model in FALLBACK_MODELS else -1
        for fallback in FALLBACK_MODELS:
            if fallback != model and fallback not in models_to_try:
                models_to_try.append(fallback)
    
    # Try models in order
    last_error = None
    for model_to_try in models_to_try:
        try:
            raw = openrouter_chat(
                messages=messages,
                api_key=api_key,
                model=model_to_try,
                temperature=0.5,
                max_tokens=700,
            )
            return ensure_markdown_headings(raw)
        except LLMError as exc:
            last_error = exc
            # Check if it's a model error and we have more models to try
            is_model_error = getattr(exc, "is_model_error", False)
            if is_model_error and model_to_try != models_to_try[-1]:
                continue  # Try next model
            # If it's not a model error or it's the last model, break
            if not is_model_error:
                break
    
    # All models failed
    if last_error:
        raise LLMError(
            f"Failed to generate response after trying {len(models_to_try)} model(s). "
            f"Last error: {last_error}"
        )
    raise LLMError("Failed to generate response from OpenRouter.")
