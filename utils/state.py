"""
utils/state.py

Session state helpers for StudyBuddy AI.

Wraps Streamlit's st.session_state to manage chat history and other
per-session data in a single, consistent place.
"""

from __future__ import annotations

from typing import List, Dict, Any

import streamlit as st


CHAT_HISTORY_KEY = "chat_history"
MESSAGES_KEY = "messages"  # ChatGPT-style message list


def init_chat_state() -> None:
    """Ensure chat history is initialized in session state."""
    if CHAT_HISTORY_KEY not in st.session_state:
        st.session_state[CHAT_HISTORY_KEY] = []
    if MESSAGES_KEY not in st.session_state:
        st.session_state[MESSAGES_KEY] = []


def get_chat_history() -> List[Dict[str, str]]:
    """Return the current chat history list (legacy format for compatibility)."""
    init_chat_state()
    return st.session_state.get(CHAT_HISTORY_KEY, [])


def get_messages() -> List[Dict[str, Any]]:
    """Return the ChatGPT-style message list."""
    init_chat_state()
    return st.session_state.get(MESSAGES_KEY, [])


def add_message(role: str, content: str, images: List[str] = None) -> None:
    """
    Add a message to the ChatGPT-style message list.
    
    Args:
        role: "user" or "assistant"
        content: Message text content
        images: Optional list of image URLs to display with the message
    """
    init_chat_state()
    message = {"role": role, "content": content}
    if images:
        message["images"] = images
    st.session_state[MESSAGES_KEY].append(message)


def add_chat_message(user_input: str, assistant_response: str) -> None:
    """Append a new exchange to the chat history (legacy format for compatibility)."""
    init_chat_state()
    st.session_state[CHAT_HISTORY_KEY].append(
        {"user": user_input, "assistant": assistant_response}
    )


def clear_chat_history() -> None:
    """Clear all chat history from the session."""
    st.session_state[CHAT_HISTORY_KEY] = []
    st.session_state[MESSAGES_KEY] = []

