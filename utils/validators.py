"""
utils/validators.py

Input validation helpers for StudyBuddy AI.
These functions perform simple checks and return (is_valid, error_message).
"""

from __future__ import annotations

from typing import Tuple, Any


def validate_text_input(text: str, field_name: str = "input") -> Tuple[bool, str]:
    """
    Validate a text input field.

    Args:
        text: The text to validate.
        field_name: Human-readable name of the field for error messages.

    Returns:
        (is_valid, error_message)
    """
    if text is None:
        return False, f"Please provide {field_name}."
    if not isinstance(text, str):
        return False, f"The {field_name} must be text."
    if not text.strip():
        return False, f"Please enter some {field_name}."
    if len(text) > 8000:
        return False, f"The {field_name} is too long. Please shorten it a bit."
    return True, ""


def validate_image_file(file_obj: Any) -> Tuple[bool, str]:
    """
    Validate an uploaded image file-like object from Streamlit.

    Args:
        file_obj: The uploaded file returned by st.file_uploader.

    Returns:
        (is_valid, error_message)
    """
    if file_obj is None:
        return False, "Please upload an image first."

    filename = getattr(file_obj, "name", "") or ""
    allowed_ext = (".jpg", ".jpeg", ".png")
    if not filename.lower().endswith(allowed_ext):
        return False, "Unsupported file type. Please upload a JPG or PNG image."

    return True, ""

