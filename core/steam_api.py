import json
import time

import requests

from core.logger import Logger
from core.paths import get_data_directory
from core.cancellation import check_cancelled


logger = Logger(__name__)


STORE_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
APP_REVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36",
    "Accept": "application/json",
}

SEARCH_CACHE_FILE = get_data_directory() / "cache" / "steam_search.json"

DEFAULT_NUM_PER_PAGE = 100


# =============================================================
# Search cache
# =============================================================

def _load_search_cache():

    if not SEARCH_CACHE_FILE.exists():
        return {}

    try:
        with open(SEARCH_CACHE_FILE, encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def _save_search_cache(cache):

    SEARCH_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SEARCH_CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)


# =============================================================
# Search
# =============================================================

def search_apps(query: str, limit: int = 10):

    if not query or len(query.strip()) < 2:
        return []

    query = query.strip()

    cache = _load_search_cache()
    cache_key = query.lower()

    if cache_key in cache:
        return cache[cache_key]

    params = {
        "term": query,
        "l": "english",
        "cc": "us",
    }

    try:

        response = requests.get(
            STORE_SEARCH_URL,
            params=params,
            headers=HEADERS,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except Exception as error:

        logger.error(f"Steam search error : {error}")

        return []

    results = []

    for item in data.get("items", []):

        appid = item.get("id")
        name = item.get("name")

        if not appid or not name:
            continue

        results.append({
            "title": name,
            "appid": appid,
            "slug": str(appid),
            "url": f"https://store.steampowered.com/app/{appid}/",
        })

    results = results[:limit]

    cache[cache_key] = results
    _save_search_cache(cache)

    return results


# =============================================================
# HTTP
# =============================================================

def _request_json(url: str, params: dict, retries: int = 3):

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except Exception as error:

            logger.warning(
                f"Steam API error, attempt {attempt + 1}/{retries} : {error}"
            )

            time.sleep(2)

    raise RuntimeError(f"Could not fetch Steam reviews for : {url}")


# =============================================================
# Reviews extraction
# =============================================================

def fetch_reviews(
    appid,
    num_per_page: int = DEFAULT_NUM_PER_PAGE,
    progress_callback=None,
    cancel_event=None,
):
    """
    Fetch every review for a Steam appid via appreviews cursor pagination.
    """

    def report(message, ratio=None):

        if progress_callback:
            progress_callback(message, ratio=ratio)

    url = APP_REVIEWS_URL.format(appid=appid)

    cursor = "*"
    reviews = []
    total = None
    fetched_count = 0
    seen_cursors = set()

    logger.info(f"Extraction Steam : appid {appid}")

    while True:

        check_cancelled(cancel_event)

        params = {
            "json": 1,
            "filter": "recent",
            "language": "all",
            "review_type": "all",
            "purchase_type": "all",
            "num_per_page": num_per_page,
            "cursor": cursor,
        }

        response = _request_json(url, params)

        if response.get("success") != 1:
            break

        query_summary = response.get("query_summary", {})

        if total is None:
            total = query_summary.get("total_reviews", 0)
            logger.info(f"Steam appid {appid} : {total} reviews")

        batch = response.get("reviews", [])

        if not batch:
            break

        fetched_count += len(batch)

        batch = [
            review for review in batch
            if review.get("review", "").strip()
        ]

        reviews.extend(batch)

        ratio = 1.0
        if total:
            ratio = min(fetched_count / total, 1.0)

        report(f"Steam : {fetched_count}/{total} ({len(reviews)} with text)", ratio=ratio)

        if total and fetched_count >= total:
            break

        next_cursor = response.get("cursor")

        if not next_cursor or next_cursor in seen_cursors:
            break

        seen_cursors.add(next_cursor)
        cursor = next_cursor

    return {
        "appid": appid,
        "source": "steam",
        "totalResults": len(reviews),
        "items": reviews,
    }
