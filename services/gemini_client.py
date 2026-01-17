from __future__ import annotations
from PIL import Image
import io
from google import genai


def get_client(api_key: str):
    """Create Gemini client using API key."""
    return genai.Client(api_key=api_key)


def generate_text(client, prompt: str, model: str = "gemini-2.0-flash") -> str:
    """Generate text response from Gemini."""
    resp = client.models.generate_content(
        model=model,
        contents=prompt
    )
    return resp.text or ""


def generate_from_image(client, image_bytes: bytes, prompt: str, model: str = "gemini-2.0-flash") -> str:
    """Generate response from image + prompt using Gemini."""
    image = Image.open(io.BytesIO(image_bytes))

    resp = client.models.generate_content(
        model=model,
        contents=[prompt, image]
    )
    return resp.text or ""
