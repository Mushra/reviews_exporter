"""One-off: re-parse every existing raw file under the new Review schema.

Usage:
    python -m core.reparse_all
"""

import re

from core.filesystem import get_data_directory
from core.logger import Logger

from parsers.parse_metacritic_api import parse_file as parse_metacritic_file
from parsers.parse_steam_api import parse_file as parse_steam_file
from parsers.parse_youtube_api import parse_file as parse_youtube_file, find_raw_file
from parsers.parse_youtube_transcripts import parse_and_merge as parse_youtube_transcripts
from core.filesystem import load_json


logger = Logger(__name__)


METACRITIC_PATTERN = re.compile(r"^(.+)_metacritic_(critic|user)_(.+)_raw$")
STEAM_PATTERN = re.compile(r"^(.+)_steam_pc_raw$")
# Checked before YOUTUBE_PATTERN below - "_transcript_raw" stems would
# otherwise also match the looser "_raw" pattern and get fed to the
# comments parser instead of being merged as transcripts.
YOUTUBE_TRANSCRIPT_PATTERN = re.compile(r"^(.+)_youtube_.+_transcript_raw$")
YOUTUBE_PATTERN = re.compile(r"^(.+)_youtube_.+_raw$")


def reparse_all():

    data_dir = get_data_directory()

    total = 0

    for game_folder in sorted(data_dir.iterdir()):

        if not game_folder.is_dir() or game_folder.name == "cache":
            continue

        game = game_folder.name

        raw_folder = game_folder / "raw"

        if not raw_folder.exists():
            continue

        seen_youtube_ids = set()
        has_transcript_raw = False

        for file in sorted(raw_folder.glob("*.json")):

            stem = file.stem

            if YOUTUBE_TRANSCRIPT_PATTERN.match(stem):

                has_transcript_raw = True

                continue

            match = METACRITIC_PATTERN.match(stem)

            if match:

                _, review_type, platform_slug = match.groups()

                try:

                    parse_metacritic_file(game, platform_slug, review_type)

                    total += 1

                except Exception as error:

                    logger.error(f"Failed to parse {file} : {error}")

                continue

            if STEAM_PATTERN.match(stem):

                try:

                    parse_steam_file(game)

                    total += 1

                except Exception as error:

                    logger.error(f"Failed to parse {file} : {error}")

                continue

            if YOUTUBE_PATTERN.match(stem):

                try:

                    raw = load_json(file)

                except Exception as error:

                    logger.error(f"Could not read {file} : {error}")

                    continue

                video_id = raw.get("video_id")

                if not video_id or video_id in seen_youtube_ids:
                    continue

                seen_youtube_ids.add(video_id)

                try:

                    parse_youtube_file(game, video_id)

                    total += 1

                except Exception as error:

                    logger.error(f"Failed to parse {file} : {error}")

                continue

            logger.warning(f"Unrecognized raw file pattern : {file}")

        if has_transcript_raw:

            try:

                parse_youtube_transcripts(game)

                total += 1

            except Exception as error:

                logger.error(f"Failed to parse YouTube transcripts for {game} : {error}")

    logger.info(f"Re-parse complete : {total} file(s) processed")

    return total


if __name__ == "__main__":

    reparse_all()
