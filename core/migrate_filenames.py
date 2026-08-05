"""
One-off migration: renames existing raw/parsed JSON files under data/<game>/
from the old {game}_{review_type}_{platform}.json scheme to the new
standardized nomenclature (see core/filesystem.py get_*_filename helpers).

Usage:
    python -m core.migrate_filenames [--dry-run]
"""

import re
import sys

from core.filesystem import (
    get_data_directory,
    get_metacritic_filename,
    get_steam_filename,
    get_youtube_filename,
    load_json,
)
from core.logger import Logger


logger = Logger(__name__)


VIDEO_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def _classify(game, stem):

    prefix = f"{game}_"

    if not stem.startswith(prefix):
        return None

    remainder = stem[len(prefix):]

    if remainder == "steam_all":
        return ("steam", {})

    match = re.match(r"^youtube_([a-zA-Z0-9_-]{11})$", remainder)

    if match:
        return ("youtube", {"video_id": match.group(1)})

    match = re.match(r"^(critic|user)_(.+)$", remainder)

    if match:
        return ("metacritic", {
            "review_type": match.group(1),
            "platform": match.group(2),
        })

    return None


def _youtube_meta_from_raw(data):

    meta = data.get("meta") or {}

    return meta.get("channel_title"), meta.get("title")


def _youtube_meta_from_parsed(data):

    if not data:
        return None, None

    first = data[0]

    return first.get("publication"), first.get("metadata", {}).get("video_title")


def _migrate_folder(game, folder, stage, dry_run):

    if not folder.exists():
        return []

    renames = []

    for file in sorted(folder.glob("*.json")):

        info = _classify(game, file.stem)

        if not info:
            continue

        kind, data = info

        if kind == "steam":

            new_name = get_steam_filename(game, stage)

        elif kind == "youtube":

            try:
                raw = load_json(file)
            except Exception as error:
                logger.warning(f"Could not read {file} : {error}")
                continue

            if stage == "raw":
                channel_title, video_title = _youtube_meta_from_raw(raw)
            else:
                channel_title, video_title = _youtube_meta_from_parsed(raw)

            new_name = get_youtube_filename(
                game,
                channel_title,
                video_title or data["video_id"],
                stage,
            )

        else:

            new_name = get_metacritic_filename(
                game,
                data["review_type"],
                data["platform"],
                stage,
            )

        target = folder / new_name

        if target == file:
            continue

        renames.append((file, target))

    for source, target in renames:

        logger.info(f"Rename : {source.name} -> {target.name}")

        if not dry_run:

            if target.exists():
                logger.warning(f"Target already exists, skipping : {target}")
                continue

            source.rename(target)

    return renames


def migrate_all(dry_run=False):

    data_dir = get_data_directory()

    total = 0

    for game_folder in sorted(data_dir.iterdir()):

        if not game_folder.is_dir() or game_folder.name == "cache":
            continue

        game = game_folder.name

        for stage, subfolder_name in (("raw", "raw"), ("parsed", "parsed")):

            subfolder = game_folder / subfolder_name

            renames = _migrate_folder(game, subfolder, stage, dry_run)

            total += len(renames)

    logger.info(
        f"Migration {'(dry-run) ' if dry_run else ''}complete : "
        f"{total} file(s) renamed"
    )

    return total


def main():

    dry_run = "--dry-run" in sys.argv

    migrate_all(dry_run=dry_run)


if __name__ == "__main__":

    main()
