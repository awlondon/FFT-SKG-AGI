import os
import requests

def fetch_images_from_serpapi(token, glyph, max_results=3):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not found.")

    query = build_symbolic_query(token, glyph)

    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",
        "ijn": "0",
        "api_key": api_key
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()

    results = []
    data = response.json()
    images = data.get("images_results", [])[:max_results]

    image_dir = "modalities/images"
    os.makedirs(image_dir, exist_ok=True)

    for i, img in enumerate(images):
        image_url = img.get("original")
        if not image_url:
            continue

        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_path = os.path.join(image_dir, f"{token}_img_{i}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            results.append(image_path)

    return results

def build_symbolic_query(token, glyph):
    base_keywords = [
        "symbol",
        "abstract"
    ]
    return f"{token} {glyph} " + " ".join(base_keywords)

