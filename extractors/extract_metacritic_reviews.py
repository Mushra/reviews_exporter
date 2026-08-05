import sys
import traceback

from core.api import fetch_reviews
from core.filesystem import save_raw_json, get_metacritic_filename
from core.logger import Logger


logger = Logger(__name__)


VALID_REVIEW_TYPES = {
    "critic",
    "user"
}



def extract_reviews(
    game: str,
    platform: str,
    review_type: str,
    progress_callback=None,
    cancel_event=None
):


    logger.info(
        f"API extraction : {game} - {platform} - {review_type}"
    )


    if review_type not in VALID_REVIEW_TYPES:

        raise ValueError(
            f"Invalid type : {review_type}. "
            f"Allowed values : {VALID_REVIEW_TYPES}"
        )



    logger.info(
        "Calling Metacritic API..."
    )


    if progress_callback:

        progress_callback(
            f"Extracting {review_type} : connecting to API...",
            ratio=0.0
        )



    data = fetch_reviews(
        game,
        platform,
        review_type,
        progress_callback=progress_callback,
        cancel_event=cancel_event
    )



    if not data:

        logger.warning(
            "No data returned by the API"
        )

        return []



    logger.info(
        "API response received"
    )


    outputs = []


    # -----------------------------------------------------------
    # All platforms mode : one raw JSON file per platform
    # -----------------------------------------------------------

    if data.get("mode") == "all":

        platforms_data = data.get(
            "platforms",
            {}
        )

        if not platforms_data:

            logger.warning(
                f"No {review_type} reviews found on any platform for '{game}'"
            )

        for platform_slug, items in platforms_data.items():

            logger.info(
                f"{platform_slug} : {len(items)} {review_type} reviews"
            )

            output = save_raw_json(
                game,
                get_metacritic_filename(
                    game,
                    review_type,
                    platform_slug,
                    "raw"
                ),
                {
                    "game": game,
                    "platform": platform_slug,
                    "review_type": review_type,
                    "totalResults": len(items),
                    "items": items,
                }
            )

            logger.info(
                f"Saved : {output}"
            )

            outputs.append(
                output
            )

        if progress_callback:

            progress_callback(
                f"Extraction {review_type} complete",
                ratio=1.0
            )

        return outputs


    # -----------------------------------------------------------
    # Single platform mode
    # -----------------------------------------------------------

    items = data.get(
        "items",
        []
    )

    total = data.get(
        "totalResults"
    )

    logger.info(
        f"Reviews received : {len(items)} / {total}"
    )

    if not items:

        logger.warning(
            f"No {review_type} reviews for platform "
            f"'{data.get('platform') or platform}' - nothing to save"
        )

        if progress_callback:

            progress_callback(
                f"No {review_type} reviews for this platform",
                ratio=1.0
            )

        return []


    if progress_callback:

        progress_callback(
            f"Extracting {review_type} : saving raw JSON...",
            ratio=0.8
        )



    output = save_raw_json(
        game,
        get_metacritic_filename(
            game,
            review_type,
            data.get("api_platform") or platform,
            "raw"
        ),
        data
    )


    logger.info(
        f"Saved : {output}"
    )


    if progress_callback:

        progress_callback(
            f"Extraction {review_type} complete",
            ratio=1.0
        )


    return [output]





def main():

    if len(sys.argv) < 4:

        print(
            "Usage : "
            "python -m extractors.extract_metacritic_reviews "
            "<game> <platform> <critic|user>"
        )

        return



    game = sys.argv[1]

    platform = sys.argv[2]

    review_type = sys.argv[3]


    try:

        extract_reviews(
            game,
            platform,
            review_type
        )


    except Exception as error:

        logger.error(
            f"Extraction error : {error}"
        )

        traceback.print_exc()





if __name__ == "__main__":

    main()
