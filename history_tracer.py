import os
import json

LOG_DIR = os.path.join('glyph_memory', 'logs')


def _load_log(filename: str) -> list[dict]:
    path = os.path.join(LOG_DIR, filename)
    entries: list[dict] = []
    if not os.path.exists(path):
        return entries
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def show_weight_history(token: str | None = None) -> None:
    """Print weight change history.  If token is None, all entries are shown."""
    entries = _load_log('weight_updates.log')
    for e in entries:
        if token is None or e.get('token') == token:
            print(f"{e.get('timestamp')} {e.get('token')} {e.get('old_weight')} -> {e.get('new_weight')}")


def show_adjacency_walks() -> None:
    """Print adjacency transitions in chronological order."""
    entries = _load_log('adjacency_walk.log')
    for e in entries:
        print(f"{e.get('timestamp')} {e.get('from')} -> {e.get('to')} depth={e.get('depth')}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Display logged history for SKG engine')
    parser.add_argument('--token', help='Show weight history for a specific token')
    parser.add_argument('--adjacencies', action='store_true', help='Show adjacency walk log')
    args = parser.parse_args()
    if args.adjacencies:
        show_adjacency_walks()
    if args.token:
        show_weight_history(args.token)
    if not args.token and not args.adjacencies:
        parser.print_help()