import requests
import config

def get_wikitext_page(page_name: str) -> str:
    """Fetch raw wikitext of a page."""
    try:
        resp = requests.get(config.WIKI_API_URL, params={
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page_name,
            "rvprop": "content",
            "rvslots": "main"
        }, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch page '{page_name}': {e}")

    pages = resp.json().get("query", {}).get("pages", {})
    if not pages:
        raise ValueError(f"No pages found for '{page_name}'")

    page = next(iter(pages.values()))
    revisions = page.get("revisions")
    if not revisions:
        raise ValueError(f"No revisions found for '{page_name}'")

    return revisions[0]["slots"]["main"]["*"]


def get_category_members(category: str) -> list[str]:
    """Fetch all pages in a category for autocomplete."""
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": 50
    }
    try:
        resp = requests.get(config.WIKI_API_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    members = resp.json().get("query", {}).get("categorymembers", [])
    return [m["title"] for m in members]
