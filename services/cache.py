import json
import os

CACHE_FILE = "category_cache.json"

def load_cache(category: str):
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(category)

def save_cache(category: str, data: list[str]):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    else:
        cache = {}
    cache[category] = data
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)
