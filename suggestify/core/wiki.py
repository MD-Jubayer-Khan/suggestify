# suggestify/core/wiki.py
from typing import List
import wikipediaapi
from functools import lru_cache

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='suggestify/0.1 (https://github.com/MD-Jubayer-Khan/suggestify`)'
)

@lru_cache(maxsize=1024)
def _get_page(title: str):
    try:
        return wiki.page(title)
    except Exception:
        return None

def wiki_expand(query: str, top_k: int = 5) -> List[str]:
    """
    Use Wikipedia to expand a short query into several human-friendly suggestions.
    Strategy:
      1. Try to fetch a Wikipedia page for the exact query.
         - If exists, return the top-level section titles and the first sentence summary snippets.
      2. If no exact page, perform wiki.search to get related page titles.
      3. Always return up to top_k suggestions.
    """
    if not query or not query.strip():
        return []

    suggestions = []
    q = query.strip()

    # 1) Try exact page match
    page = _get_page(q)
    if page and page.exists():
        # Add summary short phrases (first sentence or first 120 chars)
        try:
            summary = page.summary.split('\n')[0]
            if summary:
                # keep only first sentence or 120 chars
                first_sentence = summary.split('. ')[0].strip()
                suggestions.append(f"{q} — {first_sentence}")
        except Exception:
            pass

        # Add top-level section titles
        try:
            for s in page.sections[: top_k * 2]:
                title = s.title.strip()
                if title and title.lower() not in (q.lower(),):
                    suggestions.append(f"{q}: {title}")
                    if len(suggestions) >= top_k:
                        break
        except Exception:
            pass

    # 2) If not enough suggestions, perform a search for related pages
    if len(suggestions) < top_k:
        try:
            search_results = wiki.search(q, results=top_k * 3)
            for title in search_results:
                if title.lower() == q.lower():
                    continue
                suggestions.append(f"{title}")
                if len(suggestions) >= top_k:
                    break
        except Exception:
            pass

    # 3) De-duplicate and trim
    unique = []
    for s in suggestions:
        if s not in unique:
            unique.append(s)
        if len(unique) >= top_k:
            break

    return unique
