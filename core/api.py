import requests
import time

from core.logger import Logger
from core.cancellation import check_cancelled, PipelineCancelled


logger = Logger(__name__)


BASE_API_URL = (
    "https://backend.metacritic.com/reviews/metacritic"
)


GAME_PAGE_API_URL = (
    "https://backend.metacritic.com/composer/metacritic/pages/games/{game}/web"
)


DEFAULT_LIMIT = 100


HEADERS = {

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36",

    "Accept":
        "application/json"

}


class NotFoundError(RuntimeError):
    """Raised for a genuine HTTP 404 - retrying is pointless."""
    pass


class GameNotFoundError(RuntimeError):
    """Raised when the requested game slug does not exist on Metacritic."""
    pass


# =============================================================
# Platform aliases (UI dropdown values -> family of real slugs)
# =============================================================


ALL_PLATFORMS_ALIASES = {

    "all platform",
    "all platforms",
    "all"

}


ALIAS_FAMILIES = {

    "pc": (
        "pc",
        ["pc"]
    ),

    "ps5": (
        "playstation-5",
        ["playstation"]
    ),

    "playstation 5": (
        "playstation-5",
        ["playstation"]
    ),

    "xbox": (
        "xbox-series-x",
        ["xbox"]
    ),

    "xbox series x": (
        "xbox-series-x",
        ["xbox"]
    ),

    "switch": (
        "nintendo-switch",
        ["switch", "nintendo"]
    ),

    "nintendo switch": (
        "nintendo-switch",
        ["switch", "nintendo"]
    ),

}


def is_all_platforms(value):

    if not value:
        return True

    return value.strip().lower() in ALL_PLATFORMS_ALIASES


def resolve_platform_slug(value, game_platforms):
    """
    Resolve a UI platform alias (pc/ps5/xbox/switch/...) against the
    real per-game platform slugs discovered from Metacritic.

    Returns the real slug, or None if the game has no matching platform.
    """

    if not value:
        return None

    normalized = value.strip().lower()

    if not game_platforms:
        return None

    slugs = {
        platform["slug"]: platform
        for platform in game_platforms
        if platform.get("slug")
    }

    # Direct slug match (e.g. value already is a real slug)
    if normalized in slugs:
        return normalized

    preferred_slug, keywords = ALIAS_FAMILIES.get(
        normalized,
        (normalized, [normalized])
    )

    if preferred_slug in slugs:
        return preferred_slug

    matches = [

        platform["slug"]

        for platform in game_platforms

        if platform.get("slug") and any(
            keyword in platform["slug"].lower()
            or keyword in (platform.get("name") or "").lower()
            for keyword in keywords
        )

    ]

    if not matches:
        return None

    if len(matches) == 1:
        return matches[0]

    # Ambiguous: prefer the lead platform, otherwise the first match
    for platform in game_platforms:

        if platform.get("slug") in matches and platform.get("is_lead"):

            return platform["slug"]

    return matches[0]


# =============================================================
# URL Builder
# =============================================================


def build_reviews_api_url(
    game: str,
    platform: str,
    review_type: str,
    offset: int = 0,
    limit: int = DEFAULT_LIMIT
):


    base = (

        f"{BASE_API_URL}/"
        f"{review_type}/"
        f"games/{game}"

    )



    if platform:

        endpoint = (

            f"{base}/"
            f"platform/{platform}/web"

        )

    else:

        endpoint = (

            f"{base}/web"

        )



    return (

        f"{endpoint}"
        f"?offset={offset}"
        f"&limit={limit}"
        f"&filterBySentiment=all"
        f"&sort=date"
        f"&componentName={review_type}-reviews"
        f"&componentDisplayName={review_type}+Reviews"
        f"&componentType=ReviewList"

    )


# =============================================================
# HTTP
# =============================================================


def request_json(
    url: str,
    params: dict = None,
    retries: int = 3
):

    last_error = None

    for attempt in range(retries):

        try:

            response = requests.get(

                url,

                params=params,

                headers=HEADERS,

                timeout=30

            )

            if response.status_code == 404:

                raise NotFoundError(
                    f"Not found (404): {url}"
                )

            response.raise_for_status()

            return response.json()

        except NotFoundError:

            # A genuine 404 will not succeed on retry - fail fast.
            raise

        except Exception as error:

            last_error = error

            logger.warning(

                f"API error, attempt {attempt+1}/{retries} : {error}"

            )

            time.sleep(
                2
            )

    raise RuntimeError(

        f"Could not fetch : {url} ({last_error})"

    )


# =============================================================
# Game platform discovery
# =============================================================


def fetch_game_platforms(game: str):
    """
    Discover the real platform slugs Metacritic has for this game,
    by reading the game's product page.
    """

    url = GAME_PAGE_API_URL.format(
        game=game
    )

    try:

        response = request_json(
            url,
            retries=2
        )

    except NotFoundError:

        raise GameNotFoundError(
            f"Game '{game}' was not found on Metacritic"
        )

    except Exception as error:

        logger.warning(
            f"Could not discover platforms for '{game}' : {error}"
        )

        return []

    item = (
        response
        .get("components", [{}])[0]
        .get("data", {})
        .get("item", {})
    )

    platforms_raw = item.get(
        "platforms",
        []
    )

    platforms = []

    for platform in platforms_raw:

        slug = platform.get("slug")

        if not slug:
            continue

        critic_summary = platform.get("criticScoreSummary") or {}

        platforms.append({

            "name":
                platform.get("name"),

            "slug":
                slug,

            "is_lead":
                bool(platform.get("isLeadPlatform")),

            "critic_review_count":
                critic_summary.get("reviewCount") or 0,

        })

    logger.info(
        f"Platforms found for '{game}' : "
        f"{', '.join(p['slug'] for p in platforms) or 'none'}"
    )

    return platforms


# =============================================================
# Extraction
# =============================================================

def fetch_platform_reviews(
    game: str,
    api_platform: str,
    review_type: str,
    limit: int,
    report,
    cancel_event=None
):

    first_url = build_reviews_api_url(
        game,
        api_platform,
        review_type,
        0,
        1
    )


    first_response = request_json(
        first_url
    )


    total = (

        first_response
        .get(
            "data",
            {}
        )
        .get(
            "totalResults",
            0
        )

    )


    if total == 0:

        logger.info(
            f"No {review_type} reviews for platform {api_platform} - skipping"
        )

        return []


    logger.info(
        f"Platform {api_platform} : {total} {review_type} reviews"
    )


    reviews = []


    offset = 0


    while offset < total:


        check_cancelled(cancel_event)


        url = build_reviews_api_url(
            game,
            api_platform,
            review_type,
            offset,
            limit
        )


        response = request_json(
            url
        )


        items = (

            response
            .get(
                "data",
                {}
            )
            .get(
                "items",
                []
            )

        )


        if not items:

            break


        reviews.extend(
            items
        )


        offset += len(items)


        ratio = 1.0
        if total:
            ratio = min(
                len(reviews) / total,
                1.0
            )


        report(
            f"{api_platform} : {len(reviews)}/{total}",
            ratio=ratio
        )


    return reviews


def fetch_reviews(
    game: str,
    platform: str,
    review_type: str,
    limit: int = DEFAULT_LIMIT,
    progress_callback=None,
    cancel_event=None
):

    requested_platform = platform

    def report(
        message,
        ratio=None
    ):

        if progress_callback:

            progress_callback(
                message,
                ratio=ratio
            )

    logger.info(
        f"API extraction : {game} - {review_type} - {platform or 'all'}"
    )

    game_platforms = fetch_game_platforms(
        game
    )

    # -----------------------------------------------------------
    # All platforms : discover the real feed, skip empty ones
    # -----------------------------------------------------------

    if is_all_platforms(requested_platform):

        logger.info(
            "All platforms mode"
        )

        report(
            "Discovering available platforms"
        )

        if not game_platforms:

            logger.warning(
                f"No platform found for '{game}' - nothing to extract"
            )

        platforms_data = {}

        for game_platform in game_platforms:

            check_cancelled(cancel_event)

            slug = game_platform["slug"]

            report(
                f"Checking {slug}..."
            )

            try:

                items = fetch_platform_reviews(
                    game,
                    slug,
                    review_type,
                    limit,
                    report,
                    cancel_event
                )

            except PipelineCancelled:

                raise

            except Exception as error:

                logger.warning(
                    f"Platform {slug} skipped ({review_type}) : {error}"
                )

                continue

            if not items:

                continue

            platforms_data[slug] = items

        total_reviews = sum(
            len(items)
            for items in platforms_data.values()
        )

        return {

            "game":
                game,

            "platform":
                requested_platform,

            "mode":
                "all",

            "review_type":
                review_type,

            "totalResults":
                total_reviews,

            "platforms":
                platforms_data,

        }

    # -----------------------------------------------------------
    # Single platform : resolve against the real feed
    # -----------------------------------------------------------

    resolved_slug = resolve_platform_slug(
        requested_platform,
        game_platforms
    )

    if resolved_slug is None:

        logger.warning(
            f"Platform '{requested_platform}' is not available for "
            f"'{game}' - skipping ({review_type})"
        )

        report(
            f"Platform {requested_platform} not available for this game",
            ratio=1.0
        )

        return {

            "game": game,
            "platform": requested_platform,
            "api_platform": None,
            "review_type": review_type,
            "totalResults": 0,
            "items": [],

        }

    try:

        reviews = fetch_platform_reviews(
            game,
            resolved_slug,
            review_type,
            limit,
            report,
            cancel_event
        )

    except PipelineCancelled:

        raise

    except Exception as error:

        logger.warning(
            f"Platform {resolved_slug} failed ({review_type}) : {error}"
        )

        reviews = []

    return {

        "game":
            game,

        "platform":
            requested_platform,

        "api_platform":
            resolved_slug,

        "review_type":
            review_type,

        "totalResults":
            len(reviews),

        "items":
            reviews

    }
