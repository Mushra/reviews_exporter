from pathlib import Path
import shutil

from core.logger import Logger
from core.filesystem import get_parsed_folder


logger = Logger(__name__)



def export_parsed_reviews(
    game: str,
    destination_folder: str
):

    """
    Export only parsed reviews to user selected folder.

    Output:

    destination/
        game/
            game_user_platform.json
            game_critic_platform.json

    """

    source = get_parsed_folder(
        game
    )


    if not source.exists():

        raise FileNotFoundError(
            f"Dossier parsed introuvable : {source}"
        )


    destination = (
        Path(destination_folder)
        /
        game
    )


    destination.mkdir(
        parents=True,
        exist_ok=True
    )


    exported = []


    for file in source.glob("*.json"):


        target = (
            destination
            /
            file.name
        )


        shutil.copy2(
            file,
            target
        )


        exported.append(
            target
        )


        logger.info(
            f"Export : {target}"
        )


    return exported