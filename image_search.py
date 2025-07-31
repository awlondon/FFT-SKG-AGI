import os
from typing import List
try:
    import requests
except Exception:
    requests = None  # type: ignore


def fetch_images_from_serpapi(token: str, glyph: str, max_results: int = 3) -> List[str]:
    """
    Download a handful of images from SerpAPI given a token and its glyph.
    If the SERPAPI_API_KEY environment variable is not set or requests is
    unavailable an empty list is returned.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("[ImageSearch] SERPAPI_API_KEY not found; skipping image fetch")
        return []
    if requests is None:
        print("[ImageSearch] requests library not available; cannot fetch images")
        return []
    query = build_symbolic_query(token, glyph)
    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": api_key
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results: list[str] = []
        data = response.json()
        images = data.get("images_results", [])[:max_results]
        image_dir = "modalities/images"
        os.makedirs(image_dir, exist_ok=True)
        for i, img in enumerate(images):
            image_url = img.get("original")
            if not image_url:
                continue
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_path = os.path.join(image_dir, f"{token}_img_{i}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    results.append(image_path)
            except Exception:
                continue
        return results
    except Exception as e:
        print(f"[ImageSearch] Error fetching images: {e}")
        return []


def build_symbolic_query(token: str, glyph: str) -> str:
    base_keywords = ["symbol", "abstract"]
    return f"{token} {glyph} " + " ".join(base_keywords)