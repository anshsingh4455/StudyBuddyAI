"""
utils/image_fetcher.py

Free image fetching utility for StudyBuddy AI.

Responsibilities:
- Detect if user is requesting an image
- Fetch images from free sources (Wikipedia REST API + fallback Wikipedia Search API)
- No API keys required
"""

from __future__ import annotations

import re
from typing import List
from urllib.parse import quote

import requests


# Wikipedia blocks some requests if User-Agent missing
WIKI_HEADERS = {
    "User-Agent": "StudyBuddyAI/1.0 (Educational Project; contact: none)"
}


def detect_image_request(user_text: str) -> bool:
    """
    Detect if the user is asking for an image.

    Returns True if user message contains image-related keywords.
    """
    if not user_text:
        return False

    text_lower = user_text.lower()

    image_keywords = [
        "show me an image",
        "show me a picture",
        "show me a photo",
        "give me an image",
        "give me a picture",
        "give me a photo",
        "display an image",
        "display a picture",
        "display a photo",
        "image of",
        "picture of",
        "photo of",
        "show image",
        "show picture",
        "show photo",
        "provide me image",
        "provide me a image",
        "send me image",
        "send me a image",
    ]

    return any(keyword in text_lower for keyword in image_keywords)


def extract_query(user_text: str) -> str:
    """
    Extract the search query from user's image request.

    Example: "show me an image of Isaac Newton" -> "Isaac Newton"
    """
    if not user_text:
        return ""

    text = user_text.strip()

    patterns = [
        r"image of (.+)",
        r"picture of (.+)",
        r"photo of (.+)",
        r"show me (?:an? )?(?:image|picture|photo)(?: of)? (.+)",
        r"give me (?:an? )?(?:image|picture|photo)(?: of)? (.+)",
        r"display (?:an? )?(?:image|picture|photo)(?: of)? (.+)",
        r"provide me (?:an? )?(?:image|picture|photo)(?: of)? (.+)",
        r"send me (?:an? )?(?:image|picture|photo)(?: of)? (.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"\s+(please|pls|thanks|thank you)\s*$", "", query, flags=re.IGNORECASE)
            query = query.strip("\"' ")
            return query

    # Fallback: remove common keywords
    text = re.sub(
        r"(show|give|display|provide|send)\s+(me\s+)?(an?\s+)?(image|photo|picture)\s+(of\s+)?",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    return text


def _safe_image_url(url: str) -> bool:
    """Return True only for valid http image URLs."""
    if not url or not isinstance(url, str):
        return False
    if not url.startswith("http"):
        return False
    # Usually wikipedia returns jpg/png/webp
    return True


def fetch_wikipedia_summary_image(title: str) -> List[str]:
    """
    Fetch image(s) from Wikipedia REST summary endpoint for a given title.
    Returns list of image URLs (thumbnail/originalimage if present).
    """
    if not title:
        return []

    try:
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
        response = requests.get(api_url, headers=WIKI_HEADERS, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()

        # Disambiguation pages usually have no useful image
        if data.get("type") == "disambiguation":
            return []

        urls: List[str] = []

        thumb = data.get("thumbnail")
        if isinstance(thumb, dict):
            u = thumb.get("source")
            if _safe_image_url(u):
                urls.append(u)

        orig = data.get("originalimage")
        if isinstance(orig, dict):
            u = orig.get("source")
            if _safe_image_url(u) and u not in urls:
                urls.append(u)

        return urls

    except Exception:
        return []


def wikipedia_search_titles(query: str, limit: int = 5) -> List[str]:
    """
    Search Wikipedia for a query and return candidate page titles.
    This is the KEY fallback that makes the system reliable.
    """
    if not query:
        return []

    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        }
        r = requests.get(url, params=params, headers=WIKI_HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()

        results = data.get("query", {}).get("search", [])
        titles = []
        for item in results:
            t = item.get("title")
            if t and isinstance(t, str):
                titles.append(t)

        return titles

    except Exception:
        return []


def fetch_wikipedia_images(query: str, limit: int = 3) -> List[str]:
    """
    Fetch Wikipedia images reliably:
    1) Try direct variations in summary endpoint
    2) If fails, search Wikipedia -> pick best titles -> fetch their summary images
    """
    if not query:
        return []

    images: List[str] = []

    # 1) Direct variations
    variations = [
        query.strip(),
        query.strip().replace(" ", "_"),
        query.strip().title(),
        query.strip().title().replace(" ", "_"),
    ]

    # Remove duplicates
    seen = set()
    variations_unique = []
    for v in variations:
        if v and v not in seen:
            seen.add(v)
            variations_unique.append(v)

    for v in variations_unique:
        urls = fetch_wikipedia_summary_image(v)
        for u in urls:
            if u not in images:
                images.append(u)
        if len(images) >= limit:
            return images[:limit]

    # 2) If no images, do wikipedia search for best matching page title
    titles = wikipedia_search_titles(query, limit=6)
    for title in titles:
        urls = fetch_wikipedia_summary_image(title.replace(" ", "_"))
        for u in urls:
            if u not in images:
                images.append(u)
                if len(images) >= limit:
                    return images[:limit]

    return images[:limit]


def fetch_images(query: str, limit: int = 3) -> tuple[List[str], str]:
    """
    Fetch images from Wikipedia (free, no API key required).
    Returns (images, source)
    """
    if not query:
        return [], "none"

    images = fetch_wikipedia_images(query, limit)
    if images:
        return images, "wikipedia"

    return [], "none"
