import os
import json
import random

# Attempt to import the OpenAI client. If unavailable the module will operate
# in offline mode using a cached adjacency dataset. This allows the
# repository to function without network access or API keys.
try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore


# Load offline adjacency data if available. Developers can augment this
# dictionary to provide meaningful adjacents without requiring an API.
OFFLINE_PATH = os.path.join(os.path.dirname(__file__), "offline_adjacency.json")
_OFFLINE_DATA: dict[str, list[str]] = {}
if os.path.exists(OFFLINE_PATH):
    try:
        with open(OFFLINE_PATH, "r", encoding="utf-8") as f:
            _OFFLINE_DATA = json.load(f)
    except Exception:
        _OFFLINE_DATA = {}

# Initialize OpenAI client if possible. If the API key is missing or
# OpenAI is unavailable the client will be None.
api_key = os.getenv("OPENAI_API_KEY")
client = None
if OpenAI is not None and api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None


def generate_adjacents(token: str, top_k: int = 5) -> list[dict]:
    """Return a list of adjacent concepts for the given token."""
    # Check offline data first
    if token in _OFFLINE_DATA:
        return _format_adjacents(_OFFLINE_DATA[token][:top_k], source="offline")
    # Try to query OpenAI if client exists
    if client is not None:
        try:
            prompt = (
                f"List {top_k} semantically adjacent words or concepts to the term "
                f"'{token}', in a JSON array."
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You provide semantic adjacents for symbolic cognition."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=150,
            )
            content = response.choices[0].message.content.strip()
            print(f"[AdjacencySeed] GPT Response: {content}")
            # Try parsing as JSON array
            try:
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
            candidates: list[str] = []
            for line in lines:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    candidates.append(parts[1].strip().strip(' ",'))
            return _format_adjacents(candidates[:top_k])
        except Exception as e:
            print(f"[AdjacencySeed] Error generating adjacents for '{token}': {e}")
    # Deterministic fallback: use simple transformations of the token
    # to create plausible adjacents (e.g. token prefixed/suffixed, reversed).
    variations = [
        token + "_1",
        token + "_2",
        token[::-1],
        token.upper(),
        token.lower(),
    ]
    # Randomize order deterministically based on token hash
    random.seed(sum(ord(c) for c in token))
    random.shuffle(variations)
    return _format_adjacents(variations[:top_k], source="fallback")


def _format_adjacents(adj_list: list[str], source: str = "GPT") -> list[dict]:
    return [
        {
            "glyph": f"⟁{adj}",
            "token": adj,
            "weight": 1,
            "source": source,
        }
        for adj in adj_list if isinstance(adj, str)
    ]
