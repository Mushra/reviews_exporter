import re
import sys

from models.review import Review

from core.filesystem import (
    load_json,
    save_parsed,
    get_raw_folder,
    get_parsed_folder,
    get_enriched_folder,
    get_metacritic_filename,
    get_metacritic_combined_filename,
    load_parsed_merged,
    slugify_segment
)
from core.normalize import (
    compute_word_count,
    detect_language,
    date_only_to_iso,
)
from core.paths import get_data_directory
from core.logger import Logger
from core.api import fetch_game_platforms


logger = Logger(__name__)


# ---------------------------------------------------------
# ID
# ---------------------------------------------------------

def build_review_id(
    item,
    index,
    review_type,
    platform_slug
):

    original_id = item.get(
        "id"
    )


    if original_id:

        return (
            f"metacritic-{review_type}-{original_id}"
        )


    if review_type == "critic":

        publication = (
            item.get(
                "publicationSlug"
            )
            or
            "unknown"
        )


        return (
            f"metacritic-critic-{platform_slug}-{publication}-{index}"
        )


    return (
        f"metacritic-user-{platform_slug}-{index}"
    )



# ---------------------------------------------------------
# Platform extraction
# ---------------------------------------------------------

def extract_platform(
    item,
    fallback=None
):


    platform = item.get(
        "platform"
    )


    if platform:

        return platform



    product = item.get(
        "reviewedProduct",
        {}
    )


    platform_data = product.get(
        "platform",
        {}
    )


    if isinstance(
        platform_data,
        dict
    ):


        platform = platform_data.get(
            "name"
        )


        if platform:

            return platform



    return fallback or "unknown"



# ---------------------------------------------------------
# Score normalization
#
# Critic reviews are scored 0-100, user reviews 0-10. Both are
# normalized to a common 0.0-1.0 scale so cross-source filtering
# ("only positive reviews") does not need to know the source scale.
# ---------------------------------------------------------

def normalize_score(raw_score, review_type):

    if raw_score is None:

        return {
            "raw": None,
            "scale": "0-100" if review_type == "critic" else "0-10",
            "normalized": None,
        }

    if review_type == "critic":

        return {
            "raw": raw_score,
            "scale": "0-100",
            "normalized": round(raw_score / 100, 4),
        }

    return {
        "raw": raw_score,
        "scale": "0-10",
        "normalized": round(raw_score / 10, 4),
    }



# ---------------------------------------------------------
# Parsing item
# ---------------------------------------------------------

def parse_item(
    item,
    game,
    platform_slug,
    review_type,
    index
):


    author = item.get(
        "author"
    ) or None


    real_platform = extract_platform(
        item,
        platform_slug
    )


    text = item.get(
        "quote",
        ""
    )


    if review_type == "user":


        # User reviews are the full text submitted by the reviewer.
        text_completeness = "full"


        engagement = {

            "votes_up":
                item.get("thumbsUp"),

            "votes_down":
                item.get("thumbsDown"),

            "likes": None,

            "weighted_score": None,

        }


        flags = {

            "spoiler":
                item.get("spoiler", False),

            "refunded": None,

            "recommended": None,

        }


        source_meta = {

            "publication": None,

            "external_url": None,

            "primarily_steam_deck": None,

        }



    else:

        # Critic reviews returned by the Metacritic API are pull-quote
        # excerpts, NOT the full review text - a missing topic mention
        # here is not a reliable negative signal.
        text_completeness = "excerpt"


        engagement = {

            "votes_up": None,
            "votes_down": None,
            "likes": None,
            "weighted_score": None,

        }


        flags = {

            "spoiler": None,
            "refunded": None,
            "recommended": None,

        }


        source_meta = {

            "publication":
                item.get("publicationName"),

            "external_url":
                item.get("url") or None,

            "primarily_steam_deck": None,

        }


    language = detect_language(text)


    return Review(

        id=build_review_id(
            item,
            index,
            review_type,
            platform_slug
        ),

        game=game,

        source="metacritic",

        type=review_type,

        platform=platform_slug,

        author=author,

        language=language,

        date=date_only_to_iso(
            item.get("date", "")
        ),

        score=normalize_score(
            item.get("score"),
            review_type
        ),

        text=text,

        text_completeness=text_completeness,

        word_count=compute_word_count(text),

        engagement=engagement,

        flags=flags,

        source_meta=source_meta,

    )



# ---------------------------------------------------------
# Collection
# ---------------------------------------------------------

def parse_reviews(
    raw_data,
    game,
    platform_slug,
    review_type
):


    reviews = []


    for index, item in enumerate(
        raw_data.get(
            "items",
            []
        )
    ):


        reviews.append(

            parse_item(
                item,
                game,
                platform_slug,
                review_type,
                index
            )

        )


    return reviews



# ---------------------------------------------------------
# File-level meta
# ---------------------------------------------------------

def build_file_meta(
    game,
    platform_slug,
    review_type,
    raw_data,
    reviews
):

    items = raw_data.get("items", [])

    product = (items[0].get("reviewedProduct") if items else {}) or {}

    game_title = product.get("title") or game

    aggregate_score = None

    critic_summary = product.get("criticScoreSummary") or {}

    if review_type == "critic":
        aggregate_score = critic_summary.get("score")

    return {

        "game": game,

        "game_title": game_title,

        "source": "metacritic",

        "type": review_type,

        "platform": platform_slug,

        "aggregate_score": aggregate_score,

        "total_items": len(reviews),

    }



# ---------------------------------------------------------
# File
# ---------------------------------------------------------

def parse_file(
    game,
    platform,
    review_type
):


    # The raw file must keep exactly
    # the name produced by the extractor

    platform_slug = slugify_segment(platform) or "unknown"

    input_file = (

        get_data_directory()
        /
        game
        /
        "raw"
        /
        get_metacritic_filename(
            game,
            review_type,
            platform,
            "raw"
        )

    )



    logger.info(
        f"Reading : {input_file}"
    )



    raw = load_json(
        input_file
    )



    reviews = parse_reviews(
        raw,
        game,
        platform_slug,
        review_type
    )


    meta = build_file_meta(
        game,
        platform_slug,
        review_type,
        raw,
        reviews
    )



    output = save_parsed(

        game,

        get_metacritic_filename(
            game,
            review_type,
            platform,
            "parsed"
        ),

        meta,

        [
            review.__dict__
            for review in reviews
        ],

    )



    logger.info(
        f"Reviews parsed : {len(reviews)}"
    )


    for path in output:
        logger.info(f"Saved : {path}")


    return output



# ---------------------------------------------------------
# All platforms : parse every per-platform raw file found
# ---------------------------------------------------------

def discover_raw_platforms(
    game,
    review_type
):

    """
    Only consider raw files whose platform slug matches one of the
    game's real, current platform slugs. This avoids picking up stale
    raw files left over from earlier runs under a different alias
    (e.g. "switch" vs "nintendo-switch-2") or from single-platform runs.
    """

    raw_folder = get_raw_folder(
        game
    )

    prefix = f"{game}_metacritic_{review_type}_"
    suffix = "_raw.json"

    real_slugs = {
        entry["slug"]
        for entry in fetch_game_platforms(game)
    }

    slug_lookup = {
        slugify_segment(slug): slug
        for slug in real_slugs
    }

    platforms = []

    for file in raw_folder.glob(f"{prefix}*{suffix}"):

        stem = file.stem

        if not stem.startswith(prefix) or not stem.endswith("_raw"):
            continue

        platform_slug = stem[len(prefix):-len("_raw")]

        if platform_slug in ALL_PLATFORMS_TOKENS:
            continue

        real_platform = slug_lookup.get(platform_slug)

        if not real_platform:
            continue

        platforms.append(real_platform)

    return platforms


ALL_PLATFORMS_TOKENS = {
    "all",
    "all_platform",
    "all platform",
    "all_platforms",
    "all platforms",
}


def parse_all_platforms(
    game,
    review_type
):

    platforms = discover_raw_platforms(
        game,
        review_type
    )

    if not platforms:

        logger.warning(
            f"No per-platform raw file found for '{game}' ({review_type})"
        )

        return []

    outputs = []

    for platform in platforms:

        try:

            outputs.append(
                parse_file(
                    game,
                    platform,
                    review_type
                )
            )

        except FileNotFoundError:

            logger.warning(
                f"Raw file missing for platform '{platform}' ({review_type})"
            )

    return outputs



# ---------------------------------------------------------
# Combine : merge every processed (parsed) file for this game - both
# review types, every platform - into a single JSON. Still goes through
# save_parsed, so the combined output follows the same 60MB split rule
# (see MAX_PART_BYTES in core/filesystem.py) as any other processed file.
# ---------------------------------------------------------

def _parsed_base_pattern(game):

    return re.compile(
        rf"^{re.escape(game)}_metacritic_(user|critic)_(.+)_parsed(?:_\d{{3}})?$"
    )


def discover_parsed_bases(game):
    """Every individual (non-combined) Metacritic parsed file base for this
    game - one entry per (review_type, platform). Files split across
    multiple parts (`_001`, `_002`, ...) collapse to the base they were
    split from."""

    folder = get_parsed_folder(game)

    pattern = _parsed_base_pattern(game)

    bases = set()

    for file in (
        list(folder.glob(f"{game}_metacritic_*_parsed*.json"))
        + list(folder.glob(f"{game}_metacritic_*_parsed*.jsonl"))
    ):

        match = pattern.match(file.stem)

        if not match:
            continue

        review_type, platform_slug = match.groups()

        bases.add(f"{game}_metacritic_{review_type}_{platform_slug}_parsed")

    return sorted(bases)


def combine_processed_reviews(game):

    parsed_folder = get_parsed_folder(game)
    enriched_folder = get_enriched_folder(game)

    bases = discover_parsed_bases(game)

    if not bases:

        raise FileNotFoundError(
            f"No processed Metacritic reviews found for '{game}'"
        )

    all_items = []
    sources = []
    game_title = None

    for base in bases:

        # Critic reviews may have been enriched (full press article
        # scraped from the journalist's site) into a separate enriched/
        # file - prefer that over the plain excerpt in parsed/ when it
        # exists, so the combined JSON carries the full text too.
        enriched_base = base[:-len("_parsed")] + "_enriched"

        merged = load_parsed_merged(enriched_folder, enriched_base)
        stage = "enriched"

        if merged is None:
            merged = load_parsed_merged(parsed_folder, base)
            stage = "parsed"

        if merged is None:
            continue

        meta = merged.get("meta") or {}
        items = merged.get("items", [])

        if game_title is None:
            game_title = meta.get("game_title")

        all_items.extend(items)

        sources.append({
            "type": meta.get("type"),
            "platform": meta.get("platform"),
            "aggregate_score": meta.get("aggregate_score"),
            "item_count": len(items),
            "stage": stage,
        })

    combined_meta = {

        "game": game,

        "game_title": game_title or game,

        "source": "metacritic",

        "type": "combined",

        "platform": "all",

        "aggregate_score": None,

        "total_items": len(all_items),

        "sources": sources,

    }

    output = save_parsed(
        game,
        get_metacritic_combined_filename(game, "parsed"),
        combined_meta,
        all_items,
    )

    logger.info(
        f"Combined Metacritic reviews : {len(all_items)} "
        f"(from {len(sources)} source file(s))"
    )

    for path in output:
        logger.info(f"Saved : {path}")

    return output


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():


    if len(sys.argv) < 4:

        print(
            "Usage : "
            "python -m parsers.parse_metacritic_api "
            "<game> <platform> <critic|user>"
        )

        return



    parse_file(

        sys.argv[1],

        sys.argv[2],

        sys.argv[3]

    )



if __name__ == "__main__":

    main()
