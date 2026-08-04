import sys
import traceback

from core.api import fetch_reviews
from core.filesystem import save_raw_json
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
    progress_callback=None
):


    logger.info(
        f"Extraction API : {game} - {platform} - {review_type}"
    )


    if review_type not in VALID_REVIEW_TYPES:

        raise ValueError(
            f"Type invalide : {review_type}. "
            f"Valeurs possibles : {VALID_REVIEW_TYPES}"
        )



    logger.info(
        "Appel API Metacritic..."
    )


    if progress_callback:

        progress_callback(
            f"Extraction {review_type} : connexion API...",
            ratio=0.0
        )



    data = fetch_reviews(
        game,
        platform,
        review_type,
        progress_callback=progress_callback
    )



    if not data:

        logger.warning(
            "Aucune donnée retournée par l'API"
        )

        return None



    logger.info(
        "Réponse API reçue"
    )


    if isinstance(data, dict):

        items = (
            data
            .get("items", [])
        )

        total = (
            data
            .get("totalResults")
        )


        logger.info(
            f"Reviews reçues : {len(items)} / {total}"
        )


    if progress_callback:

        progress_callback(
            f"Extraction {review_type} : sauvegarde JSON brut...",
            ratio=0.8
        )



    output = save_raw_json(
        game,
        review_type,
        platform,
        data
    )


    logger.info(
        f"Sauvegardé : {output}"
    )


    if progress_callback:

        progress_callback(
            f"Extraction {review_type} terminée",
            ratio=1.0
        )


    return output





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
            f"Erreur extraction : {error}"
        )

        traceback.print_exc()





if __name__ == "__main__":

    main()