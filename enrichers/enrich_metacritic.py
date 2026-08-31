"""Optional enrichment step: follows each Metacritic critic review's
source_meta.external_url and scrapes the full press article, replacing the
excerpt with the complete text when scraping succeeds. Writes to a separate
enriched/ folder so parsed/ stays a faithful, always-safe-to-regenerate
copy of the raw API data.

Only critic reviews are targeted - user/Steam/YouTube reviews are already
full text (text_completeness == "full")."""

import re
import sys

from core.filesystem import (
    get_parsed_folder,
    get_metacritic_filename,
    load_parsed_merged,
    save_enriched,
    slugify_segment,
)
from core.normalize import compute_word_count
from core.scraper import fetch_article_text
from core.cancellation import check_cancelled
from core.logger import Logger

from parsers.parse_metacritic_api import discover_raw_platforms


logger = Logger(__name__)


ALL_PLATFORMS_TOKENS = {
    "all",
    "all_platform",
    "all platform",
    "all_platforms",
    "all platforms",
}

# Some critic entries point to a video review (YouTube, Vimeo...) rather than
# a press article. Trafilatura will happily "succeed" on the video page's
# boilerplate (footer links, cookie notices) - that's not review text, so
# these must be skipped rather than treated as a scrape attempt.
VIDEO_URL_PATTERN = re.compile(
    r"(youtube\.com|youtu\.be|vimeo\.com|dailymotion\.com|twitch\.tv)",
    re.IGNORECASE,
)


# ---------------------------------------------------------
# Item enrichment
# ---------------------------------------------------------

def enrich_item(item):

    url = (item.get("source_meta") or {}).get("external_url")

    if not url:

        item["enrichment"] = {"status": "no_url"}

        return item

    if VIDEO_URL_PATTERN.search(url):

        item["enrichment"] = {"status": "video_url"}

        return item

    text = fetch_article_text(url)

    if not text:

        item["enrichment"] = {"status": "failed"}

        return item

    item["text"] = text

    item["text_completeness"] = "full_scraped"

    item["word_count"] = compute_word_count(text)

    item["enrichment"] = {"status": "scraped", "char_count": len(text)}

    return item


# ---------------------------------------------------------
# File
# ---------------------------------------------------------

def enrich_file(
    game,
    platform,
    review_type,
    progress_callback=None,
    cancel_event=None,
):

    def report(message, ratio=None):

        if progress_callback:
            progress_callback(message, ratio=ratio)

    if review_type != "critic":

        logger.info(
            f"Enrichment skipped : '{review_type}' reviews are already full text"
        )

        return None

    platform_slug = slugify_segment(platform) or "unknown"

    parsed_filename = get_metacritic_filename(game, review_type, platform, "parsed")
    parsed_base = (
        parsed_filename[:-5] if parsed_filename.endswith(".json") else parsed_filename
    )

    parsed = load_parsed_merged(get_parsed_folder(game), parsed_base)

    if parsed is None:

        raise FileNotFoundError(
            f"No parsed critic file found for '{game}' ({platform_slug})"
        )

    logger.info(f"Reading : {parsed_base} (merged from all parts)")

    items = parsed.get("items", [])

    total = len(items) or 1

    scraped = failed = no_url = video_url = 0

    for index, item in enumerate(items):

        check_cancelled(cancel_event)

        enrich_item(item)

        status = item["enrichment"]["status"]

        if status == "scraped":
            scraped += 1
        elif status == "failed":
            failed += 1
        elif status == "video_url":
            video_url += 1
        else:
            no_url += 1

        report(
            f"Enriching {game} {platform_slug} : {index + 1}/{len(items)} "
            f"({scraped} scraped, {failed} failed, {no_url} no url, {video_url} video url)",
            ratio=(index + 1) / total,
        )

    meta = dict(parsed.get("meta") or {})

    meta["enrichment_summary"] = {
        "scraped": scraped,
        "failed": failed,
        "no_url": no_url,
        "video_url": video_url,
        "total": len(items),
    }

    output = save_enriched(
        game,
        get_metacritic_filename(game, review_type, platform, "enriched"),
        meta,
        items,
    )

    logger.info(
        f"Enrichment complete : {scraped} scraped, {failed} failed, "
        f"{no_url} no url, {video_url} video url (total {len(items)})"
    )

    for path in output:
        logger.info(f"Saved : {path}")

    return output


# ---------------------------------------------------------
# All platforms
# ---------------------------------------------------------

def enrich_all_platforms(
    game,
    review_type,
    progress_callback=None,
    cancel_event=None,
):

    platforms = discover_raw_platforms(game, review_type)

    if not platforms:

        logger.warning(
            f"No per-platform raw file found for '{game}' ({review_type})"
        )

        return []

    outputs = []

    total_platforms = len(platforms) or 1

    for platform_index, platform in enumerate(platforms):

        def sub_report(message, ratio=None, platform_index=platform_index):

            if not progress_callback:
                return

            base_ratio = platform_index / total_platforms

            overall = base_ratio

            if ratio is not None:
                overall += ratio / total_platforms

            progress_callback(message, ratio=min(overall, 1.0))

        try:

            outputs.append(
                enrich_file(
                    game,
                    platform,
                    review_type,
                    progress_callback=sub_report,
                    cancel_event=cancel_event,
                )
            )

        except FileNotFoundError:

            logger.warning(
                f"No parsed critic file for platform '{platform}' - skipping enrichment"
            )

    return outputs


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():

    if len(sys.argv) < 3:

        print(
            "Usage : "
            "python -m enrichers.enrich_metacritic <game> <platform>"
        )

        return

    game = sys.argv[1]
    platform = sys.argv[2]

    if platform.strip().lower() in ALL_PLATFORMS_TOKENS:

        enrich_all_platforms(game, "critic")

    else:

        enrich_file(game, platform, "critic")


if __name__ == "__main__":

    main()
