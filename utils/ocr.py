"""
utils/ocr.py

OCR utilities for StudyBuddy AI.

Uses Tesseract via the `pytesseract` library to extract text from images.
On Windows, this module automatically tries to find Tesseract in common
installation locations if it's not on PATH.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Optional

from PIL import Image
import pytesseract


def _configure_tesseract_path() -> None:
    """
    Configure pytesseract to use Tesseract executable on Windows.
    Tries common installation paths if Tesseract is not on PATH.
    Also checks TESSERACT_CMD environment variable for manual override.
    """
    if sys.platform != "win32":
        return  # Only needed on Windows

    # Check if pytesseract already has a configured path
    try:
        current_cmd = pytesseract.pytesseract.tesseract_cmd
        if current_cmd and os.path.exists(current_cmd):
            return  # Already configured and valid
    except (AttributeError, TypeError):
        pass  # Not configured yet, continue

    # First, check for environment variable override (easiest manual configuration)
    env_path = os.getenv("TESSERACT_CMD")
    if env_path and os.path.exists(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return

    # Get username for user-specific paths
    username = os.getenv("USERNAME", "")
    userprofile = os.getenv("USERPROFILE", "")

    # Common Tesseract installation paths on Windows
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    
    # Add user-specific paths if we have the info
    if username:
        possible_paths.append(
            rf"C:\Users\{username}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        )
    if userprofile:
        possible_paths.append(
            os.path.join(userprofile, "AppData", "Local", "Programs", "Tesseract-OCR", "tesseract.exe")
        )

    # Try to find Tesseract in common locations
    for tesseract_path in possible_paths:
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            return

    # If not found, check if it's on PATH (pytesseract will handle this)
    # We don't set anything, let pytesseract try to find it naturally


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image_bytes: Raw bytes of the uploaded image.

    Returns:
        Extracted text (may be empty string if nothing is detected).

    Raises:
        RuntimeError: If the image cannot be processed or OCR fails.
    """
    if not image_bytes:
        raise RuntimeError("No image data provided for OCR.")

    # Configure Tesseract path on Windows if needed
    _configure_tesseract_path()

    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to open image: {exc}") from exc

    try:
        text: Optional[str] = pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError as exc:
        # Provide detailed installation instructions
        error_msg = (
            "Tesseract OCR engine was not found on this system.\n\n"
            "📥 INSTALLATION STEPS:\n"
            "1. Download Tesseract for Windows from:\n"
            "   https://github.com/UB-Mannheim/tesseract/wiki\n"
            "   (Look for the latest 'tesseract-ocr-w64-setup-*.exe' file)\n\n"
            "2. Run the installer and:\n"
            "   - Install to default location: C:\\Program Files\\Tesseract-OCR\n"
            "   - ✅ IMPORTANT: Check 'Add to PATH' during installation\n\n"
            "3. After installation:\n"
            "   - Close and restart your terminal/IDE completely\n"
            "   - Restart the Streamlit app\n\n"
            "💡 QUICK FIX (if Tesseract is already installed):\n"
            "Set the TESSERACT_CMD environment variable to your Tesseract path.\n"
            "In PowerShell, run:\n"
            "  $env:TESSERACT_CMD='C:\\Program Files\\Tesseract-OCR\\tesseract.exe'\n"
            "(Replace with your actual Tesseract path if different)\n\n"
            "Then restart Streamlit. This is the easiest way to configure it!"
        )
        raise RuntimeError(error_msg) from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"OCR failed: {exc}") from exc

    return text or ""

