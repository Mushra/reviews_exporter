from pathlib import Path
import json
import re

from core.paths import (
    get_data_directory as get_default_data_directory,
    set_data_directory as configure_data_directory,
)


# ---------------------------------------------------------------------
# Racine du projet
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent


DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


DATA_DIR = get_default_data_directory()



# ---------------------------------------------------------------------
# Configuration runtime
# ---------------------------------------------------------------------

def set_data_directory(
    directory: str | Path
):

    global DATA_DIR

    DATA_DIR = configure_data_directory(directory)
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )



def get_data_directory():

    return DATA_DIR



# ---------------------------------------------------------------------
# Dossiers principaux
# ---------------------------------------------------------------------

def get_game_folder(
    game: str
) -> Path:


    folder = (
        DATA_DIR
        /
        game
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



def get_raw_folder(
    game: str
) -> Path:


    folder = (
        get_game_folder(game)
        /
        "raw"
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



def get_parsed_folder(
    game: str
) -> Path:


    folder = (
        get_game_folder(game)
        /
        "parsed"
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



def get_enriched_folder(
    game: str
) -> Path:


    folder = (
        get_game_folder(game)
        /
        "enriched"
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



def get_aggregate_folder(
    game: str
) -> Path:


    folder = (
        get_game_folder(game)
        /
        "aggregate"
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



def get_markdown_folder(
    game: str
) -> Path:


    folder = (
        get_game_folder(game)
        /
        "markdown"
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    return folder



# ---------------------------------------------------------------------
# Nommage fichiers
# ---------------------------------------------------------------------

def slugify_segment(value: str) -> str:

    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-")



def get_html_filename(
    game: str,
    review_type: str,
    platform: str
) -> str:


    return (
        f"{game}_{review_type}_{platform}.html"
    )



def get_metacritic_filename(
    game: str,
    review_type: str,
    platform: str,
    stage: str
) -> str:

    safe_platform = slugify_segment(platform) or "unknown"

    return (
        f"{game}_metacritic_{review_type}_{safe_platform}_{stage}.json"
    )



def get_steam_filename(
    game: str,
    stage: str
) -> str:

    return (
        f"{game}_steam_pc_{stage}.json"
    )



def get_youtube_filename(
    game: str,
    channel_title: str,
    video_title: str,
    stage: str
) -> str:

    channel_slug = slugify_segment(channel_title) or "unknown-channel"
    title_slug = slugify_segment(video_title) or "unknown-video"

    return (
        f"{game}_youtube_{channel_slug}_{title_slug}_{stage}.json"
    )



def get_aggregate_filename(
    game: str,
    review_type: str
) -> str:


    return (
        f"{game}_{review_type}_reviews.json"
    )



# ---------------------------------------------------------------------
# Sauvegarde HTML RAW
# ---------------------------------------------------------------------

def save_html(
    game: str,
    review_type: str,
    platform: str,
    html: str
) -> Path:


    output = (
        get_raw_folder(game)
        /
        get_html_filename(
            game,
            review_type,
            platform
        )
    )


    output.write_text(
        html,
        encoding="utf-8"
    )


    return output



def load_html(
    game: str,
    review_type: str,
    platform: str
) -> str:


    file = (
        get_raw_folder(game)
        /
        get_html_filename(
            game,
            review_type,
            platform
        )
    )


    return file.read_text(
        encoding="utf-8"
    )



# ---------------------------------------------------------------------
# Sauvegarde JSON RAW API
# ---------------------------------------------------------------------

def save_raw_json(
    game: str,
    filename: str,
    data
) -> Path:


    output = (
        get_raw_folder(game)
        /
        filename
    )


    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


    return output



# ---------------------------------------------------------------------
# Sauvegarde JSON/JSONL PARSED avec enveloppe meta + items
# ---------------------------------------------------------------------

# Large parsed files switch to JSONL (one item per line) so they can be
# streamed/chunked by downstream RAG/embedding pipelines instead of being
# loaded fully into memory as a single JSON array.
JSONL_ITEM_THRESHOLD = 1000
JSONL_BYTE_THRESHOLD = 2_000_000


def _save_meta_items_envelope(
    folder: Path,
    filename: str,
    meta: dict,
    items: list,
) -> Path:

    base = filename[:-5] if filename.endswith(".json") else filename

    items_size = len(
        json.dumps(items, ensure_ascii=False)
    )

    use_jsonl = (
        len(items) > JSONL_ITEM_THRESHOLD
        or items_size > JSONL_BYTE_THRESHOLD
    )

    if use_jsonl:

        output = folder / f"{base}.jsonl"

        with open(output, "w", encoding="utf-8") as f:

            f.write(
                json.dumps({"meta": meta}, ensure_ascii=False) + "\n"
            )

            for item in items:

                f.write(
                    json.dumps(item, ensure_ascii=False) + "\n"
                )

        return output

    output = folder / f"{base}.json"

    with open(output, "w", encoding="utf-8") as f:

        json.dump(
            {"meta": meta, "items": items},
            f,
            indent=2,
            ensure_ascii=False,
        )

    return output


def save_parsed(
    game: str,
    filename: str,
    meta: dict,
    items: list,
) -> Path:

    return _save_meta_items_envelope(
        get_parsed_folder(game),
        filename,
        meta,
        items,
    )


def save_enriched(
    game: str,
    filename: str,
    meta: dict,
    items: list,
) -> Path:

    return _save_meta_items_envelope(
        get_enriched_folder(game),
        filename,
        meta,
        items,
    )


def load_parsed(path: Path):
    """Load a parsed file, transparently handling both the plain-JSON
    envelope ({"meta":..., "items":...}) and the JSONL variant (meta on
    the first line, one item per following line)."""

    if str(path).endswith(".jsonl"):

        meta = None
        items = []

        with open(path, encoding="utf-8") as f:

            for line_index, line in enumerate(f):

                line = line.strip()

                if not line:
                    continue

                if line_index == 0:
                    meta = json.loads(line).get("meta")
                else:
                    items.append(json.loads(line))

        return {"meta": meta, "items": items}

    return load_json(path)



def load_json(
    path: Path
):


    with open(
        path,
        encoding="utf-8"
    ) as f:


        return json.load(f)



# ---------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------

def save_aggregate(
    game: str,
    review_type: str,
    data
) -> Path:


    output = (
        get_aggregate_folder(game)
        /
        get_aggregate_filename(
            game,
            review_type
        )
    )


    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


    return output



# ---------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------

def open_game_folder(
    game: str
):

    return get_game_folder(
        game
    )



def list_existing_projects():

    if not DATA_DIR.exists():
        return []

    return sorted(
        folder.name
        for folder in DATA_DIR.iterdir()
        if folder.is_dir()
    )