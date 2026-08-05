import sys
import traceback

from core.steam_api import fetch_reviews
from core.filesystem import save_raw_json, get_steam_filename
from core.logger import Logger


logger = Logger(__name__)


def extract_steam_reviews(
    game: str,
    appid,
    progress_callback=None,
    cancel_event=None,
):

    logger.info(f"Steam extraction : {game} - appid {appid}")

    if progress_callback:

        progress_callback(
            "Steam extraction : connecting to API...",
            ratio=0.0,
        )

    data = fetch_reviews(
        appid,
        progress_callback=progress_callback,
        cancel_event=cancel_event,
    )

    if not data:

        logger.warning("No data returned by the Steam API")

        return None

    logger.info(f"Steam reviews received : {data.get('totalResults')}")

    if progress_callback:

        progress_callback(
            "Steam extraction : saving raw JSON...",
            ratio=0.9,
        )

    output = save_raw_json(
        game,
        get_steam_filename(game, "raw"),
        data,
    )

    logger.info(f"Saved : {output}")

    if progress_callback:

        progress_callback(
            "Steam extraction complete",
            ratio=1.0,
        )

    return output


def main():

    if len(sys.argv) < 3:

        print(
            "Usage : "
            "python -m extractors.extract_steam_reviews "
            "<game> <appid>"
        )

        return

    game = sys.argv[1]
    appid = sys.argv[2]

    try:

        extract_steam_reviews(game, appid)

    except Exception as error:

        logger.error(f"Steam extraction error : {error}")

        traceback.print_exc()


if __name__ == "__main__":

    main()
