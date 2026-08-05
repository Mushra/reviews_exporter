import sys

from models.review import Review

from core.filesystem import load_json, save_parsed, get_steam_filename
from core.normalize import (
    compute_word_count,
    steam_language_to_iso,
    timestamp_to_iso,
)
from core.paths import get_data_directory
from core.logger import Logger


logger = Logger(__name__)


# ---------------------------------------------------------
# Parsing item
# ---------------------------------------------------------

def parse_item(item, game, index):

    author = item.get("author", {})

    text = item.get("review", "")

    voted_up = item.get("voted_up")

    return Review(

        id=f"steam-{item.get('recommendationid', index)}",

        game=game,

        source="steam",

        type="user",

        platform="pc",

        author=author.get("steamid"),

        language=steam_language_to_iso(item.get("language")),

        date=timestamp_to_iso(item.get("timestamp_created")),

        score={
            "raw": voted_up,
            "scale": "boolean",
            "normalized": 1.0 if voted_up else 0.0 if voted_up is not None else None,
        },

        text=text,

        text_completeness="full",

        word_count=compute_word_count(text),

        engagement={

            "votes_up":
                item.get("votes_up"),

            "votes_down": None,

            "likes":
                item.get("votes_funny"),

            "weighted_score":
                item.get("weighted_vote_score"),

        },

        flags={

            "spoiler": None,

            "refunded":
                item.get("refunded"),

            "recommended":
                voted_up,

        },

        source_meta={

            "publication": None,

            "external_url": None,

            "primarily_steam_deck":
                item.get("primarily_steam_deck"),

        },

    )


# ---------------------------------------------------------
# Collection
# ---------------------------------------------------------

def parse_reviews(raw_data, game):

    reviews = []

    for index, item in enumerate(raw_data.get("items", [])):

        reviews.append(parse_item(item, game, index))

    return reviews


# ---------------------------------------------------------
# File-level meta
# ---------------------------------------------------------

def build_file_meta(game, reviews):

    return {

        "game": game,

        "game_title": game,

        "source": "steam",

        "type": "user",

        "platform": "pc",

        "aggregate_score": None,

        "total_items": len(reviews),

    }


# ---------------------------------------------------------
# File
# ---------------------------------------------------------

def parse_file(game):

    input_file = (
        get_data_directory()
        / game
        / "raw"
        / get_steam_filename(game, "raw")
    )

    logger.info(f"Reading : {input_file}")

    raw = load_json(input_file)

    reviews = parse_reviews(raw, game)

    meta = build_file_meta(game, reviews)

    output = save_parsed(
        game,
        get_steam_filename(game, "parsed"),
        meta,
        [review.__dict__ for review in reviews],
    )

    logger.info(f"Steam reviews parsed : {len(reviews)}")

    logger.info(f"Saved : {output}")

    return output


def main():

    if len(sys.argv) < 2:

        print(
            "Usage : "
            "python -m parsers.parse_steam_api <game>"
        )

        return

    parse_file(sys.argv[1])


if __name__ == "__main__":

    main()
