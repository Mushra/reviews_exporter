import sys

from pathlib import Path

from models.review import Review

from core.filesystem import (
    load_json,
    save_json
)
from core.paths import get_data_directory
from core.logger import Logger


logger = Logger(__name__)



# ---------------------------------------------------------
# ID
# ---------------------------------------------------------

def build_review_id(
    item,
    index,
    review_type
):

    original_id = item.get(
        "id"
    )


    if original_id:

        return str(
            original_id
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
            f"critic-{publication}-{index}"
        )


    return (
        f"user-{index}"
    )



# ---------------------------------------------------------
# Extraction commune
# ---------------------------------------------------------

def extract_product_metadata(
    item
):

    product = item.get(
        "reviewedProduct",
        {}
    )


    return {

        "product_id":
            product.get(
                "id"
            ),

        "product_title":
            product.get(
                "title"
            )

    }



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
# Parsing item
# ---------------------------------------------------------

def parse_item(
    item,
    game,
    platform,
    review_type,
    index
):


    metadata = extract_product_metadata(
        item
    )


    publication = None

    author = item.get(
        "author"
    )


    source = {}


    real_platform = extract_platform(
        item,
        platform
    )



    if review_type == "user":


        metadata.update({

            "spoiler":
                item.get(
                    "spoiler",
                    False
                )

        })



    elif review_type == "critic":


        publication = item.get(
            "publicationName"
        )


        source = {

            "external_url":
                item.get(
                    "url"
                )

        }


        metadata.update({

            "publication_slug":
                item.get(
                    "publicationSlug"
                ),

            "critic_score_summary":
                item.get(
                    "reviewedProduct",
                    {}
                )
                .get(
                    "criticScoreSummary"
                )

        })


        if not author:

            author = None



    return Review(

        id=build_review_id(
            item,
            index,
            review_type
        ),

        game=game,

        review_type=review_type,

        platform=real_platform,

        author=author,

        publication=publication,

        date=item.get(
            "date",
            ""
        ),

        score=item.get(
            "score"
        ),

        text=item.get(
            "quote",
            ""
        ),

        source=source,

        metadata=metadata

    )



# ---------------------------------------------------------
# Collection
# ---------------------------------------------------------

def parse_reviews(
    raw_data,
    game,
    platform,
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
                platform,
                review_type,
                index
            )

        )


    return reviews



# ---------------------------------------------------------
# Fichier
# ---------------------------------------------------------

def parse_file(
    game,
    platform,
    review_type
):


    # Le raw doit garder exactement
    # le nom produit par l'extracteur

    input_file = (

        get_data_directory()
        /
        game
        /
        "raw"
        /
        f"{game}_{review_type}_{platform}.json"

    )



    logger.info(
        f"Lecture : {input_file}"
    )



    raw = load_json(
        input_file
    )



    reviews = parse_reviews(
        raw,
        game,
        platform,
        review_type
    )



    safe_platform = (
        platform
        .replace(
            " ",
            "_"
        )
        .lower()
    )



    output = save_json(

        game,

        review_type,

        safe_platform,

        [

            review.__dict__

            for review in reviews

        ]

    )



    logger.info(
        f"Reviews parsées : {len(reviews)}"
    )


    logger.info(
        f"Sauvegarde : {output}"
    )


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