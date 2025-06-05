import os
import json

try:
    from openai import OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key) if openai_key else None
except Exception:
    OpenAI = None
    client = None

def generate_adjacents(token, top_k=5):
    if not client:
        print("[AdjacencySeed] OpenAI client unavailable. Returning empty list.")
        return []
    try:
        prompt = f"List {top_k} semantically adjacent words or concepts to the term '{token}', in a JSON array."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You provide semantic adjacents for symbolic cognition."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )

        content = response.choices[0].message.content.strip()
        print(f"[AdjacencySeed] GPT-3.5 Response: {content}")

        try:
            # First try parsing as JSON array
            adjacents_raw = json.loads(content)
            if isinstance(adjacents_raw, list):
                return _format_adjacents(adjacents_raw[:top_k])
        except json.JSONDecodeError:
            pass

        # Fallback: parse numbered dictionary-like JSON
        try:
            adjacents_dict = json.loads(content)
            if isinstance(adjacents_dict, dict):
                return _format_adjacents(list(adjacents_dict.values())[:top_k])
        except Exception:
            pass

        # Fallback: parse numbered lines manually
        lines = content.splitlines()
        candidates = []
        for line in lines:
            parts = line.split(":", 1)
            if len(parts) == 2:
                candidates.append(parts[1].strip())
        return _format_adjacents(candidates[:top_k])

    except Exception as e:
        print(f"[AdjacencySeed] Error generating adjacents for '{token}': {e}")
        return []

def _format_adjacents(adj_list):
    return [
        {
            "glyph": f"⟁{adj}",
            "token": adj,
            "weight": 1,
            "source": "GPT-3.5"
        }
        for adj in adj_list if isinstance(adj, str)
    ]
