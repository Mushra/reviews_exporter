import requests
import time

from core.logger import Logger


logger = Logger(__name__)


BASE_API_URL = (
    "https://backend.metacritic.com/reviews/metacritic"
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



# =============================================================
# Platform mapping
# =============================================================


PLATFORM_MAPPING = {

    "pc":
        "pc",

    "ps5":
        "playstation-5",

    "playstation 5":
        "playstation-5",

    "xbox":
        "xbox-series-x",

    "xbox series x":
        "xbox-series-x",

    "switch":
        "nintendo-switch",

    "nintendo switch":
        "nintendo-switch"

}

# =============================================================
# All platforms extraction
# =============================================================


ALL_API_PLATFORMS = [

    "pc",

    "playstation-5",

    "playstation-4",

    "xbox-series-x",

    "xbox-one",

    "nintendo-switch"

]



def normalize_platform(
    platform
):

    """
    Convert UI platform names into Metacritic API values.
    """

    if not platform:

        return None



    value = (
        platform
        .strip()
        .lower()
    )



    if value in (

        "all platform",
        "all platforms",
        "all"

    ):

        return None



    return PLATFORM_MAPPING.get(
        value,
        value
    )





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
    retries: int = 3
):


    for attempt in range(retries):

        try:


            response = requests.get(

                url,

                headers=HEADERS,

                timeout=30

            )


            response.raise_for_status()


            return response.json()



        except Exception as error:


            logger.warning(

                f"Erreur API tentative {attempt+1}/{retries} : {error}"

            )


            time.sleep(
                2
            )



    raise RuntimeError(

        f"Impossible de récupérer : {url}"

    )





# =============================================================
# Extraction
# =============================================================

def fetch_platform_reviews(
    game: str,
    api_platform: str | None,
    review_type: str,
    limit: int,
    report
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


    logger.info(
        f"Plateforme {api_platform or 'all'} : {total} reviews"
    )


    reviews = []


    offset = 0


    while offset < total:


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
            f"{api_platform or 'all'} : {len(reviews)}/{total}",
            ratio=ratio
        )


    return reviews

def fetch_reviews(
    game: str,
    platform: str,
    review_type: str,
    limit: int = DEFAULT_LIMIT,
    progress_callback=None
):

    requested_platform = platform

    platform = normalize_platform(
        platform
    )

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
        f"Extraction API : {game} - {review_type} - {platform or 'all'}"
    )

    reviews = []

    if platform is None:

        logger.info(
            "Mode toutes plateformes"
        )

        report(
            "Extraction toutes plateformes"
        )

        for api_platform in ALL_API_PLATFORMS:

            try:

                logger.info(
                    f"Extraction plateforme : {api_platform}"
                )

                report(
                    f"Extraction {api_platform}"
                )

                reviews.extend(
                    fetch_platform_reviews(
                        game,
                        api_platform,
                        review_type,
                        limit,
                        report
                    )
                )

            except Exception as error:

                logger.warning(
                    f"Plateforme ignorée {api_platform} : {error}"
                )

    else:

        try:

            reviews = fetch_platform_reviews(
                game,
                platform,
                review_type,
                limit,
                report
            )

        except Exception:

            logger.warning(
                f"Plateforme {platform} indisponible, fallback global"
            )

            reviews = fetch_platform_reviews(
                game,
                None,
                review_type,
                limit,
                report
            )

    unique_reviews = {}

    for review in reviews:

        key = (
            review.get("id")
            or review.get("url")
            or (
                review.get("publicationSlug"),
                review.get("date"),
                review.get("quote")
            )
        )

        unique_reviews[key] = review

    reviews = list(
        unique_reviews.values()
    )

    return {
        "game":
            game,

        "platform":
            requested_platform,

        "api_platform":
            platform or "all",

        "review_type":
            review_type,

        "totalResults":
            len(reviews),

        "items":
            reviews
    }