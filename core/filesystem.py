from pathlib import Path
import json

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

def get_html_filename(
    game: str,
    review_type: str,
    platform: str
) -> str:


    return (
        f"{game}_{review_type}_{platform}.html"
    )



def get_json_filename(
    game: str,
    review_type: str,
    platform: str
) -> str:


    return (
        f"{game}_{review_type}_{platform}.json"
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
    review_type: str,
    platform: str,
    data
) -> Path:


    output = (
        get_raw_folder(game)
        /
        get_json_filename(
            game,
            review_type,
            platform
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



def load_raw_json(
    game: str,
    review_type: str,
    platform: str
):


    file = (
        get_raw_folder(game)
        /
        get_json_filename(
            game,
            review_type,
            platform
        )
    )


    with open(
        file,
        encoding="utf-8"
    ) as f:


        return json.load(f)



# ---------------------------------------------------------------------
# Sauvegarde JSON PARSED
# ---------------------------------------------------------------------

def save_json(
    game: str,
    review_type: str,
    platform: str,
    data
) -> Path:


    output = (
        get_parsed_folder(game)
        /
        get_json_filename(
            game,
            review_type,
            platform
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