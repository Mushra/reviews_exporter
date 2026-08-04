from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sys


@dataclass
class CriticReview:

    game: str
    platform: str
    review_type: str
    date: str
    publication: str
    score: int | None
    quote: str
    full_review_url: str



def get_text(element):

    if element is None:
        return ""

    return element.get_text(
        " ",
        strip=True
    )



def get_publication(header):

    if header is None:
        return ""


    header_copy = BeautifulSoup(
        str(header),
        "html.parser"
    )


    score = header_copy.select_one(
        ".c-siteReviewScore"
    )


    if score:
        score.decompose()


    return header_copy.get_text(
        " ",
        strip=True
    )



def parse_score(score_element):

    if score_element is None:
        return None


    value = score_element.get_text(
        strip=True
    )


    if value.isdigit():

        return int(value)


    print(
        f"⚠️ Score non numérique ignoré : {value}"
    )


    return None



def get_metadata(html_file):

    """
    Exemple :
    elden-ring_critic_pc.html

    retourne :
    game = elden-ring
    platform = pc
    """


    filename = html_file.stem


    parts = filename.split(
        "_critic_"
    )


    if len(parts) != 2:

        raise ValueError(
            f"Nom de fichier invalide : {filename}"
        )


    game = parts[0]
    platform = parts[1]


    return game, platform



def parse_critic_html(html_file):


    with open(
        html_file,
        encoding="utf-8"
    ) as f:


        soup = BeautifulSoup(
            f,
            "html.parser"
        )



    cards = soup.select(
        '[data-testid="review-card"]'
    )


    print(
        f"Reviews trouvées : {len(cards)}"
    )



    game, platform = get_metadata(
        html_file
    )



    reviews = []



    for card in cards:


        full_review = card.select_one(
            '.review-footer a[href^="http"]'
        )


        review = CriticReview(

            game=game,

            platform=platform,

            review_type="critic",


            date=get_text(
                card.select_one(
                    '[data-testid="review-card-date"]'
                )
            ),


            publication=get_publication(
                card.select_one(
                    '[data-testid="review-card-header"]'
                )
            ),


            score=parse_score(
                card.select_one(
                    ".c-siteReviewScore span"
                )
            ),


            quote=get_text(
                card.select_one(
                    '[data-testid="review-quote-text"]'
                )
            ),


            full_review_url=(

                full_review["href"]

                if full_review

                else ""

            )

        )


        reviews.append(
            review
        )



    return reviews




def save_json(
    reviews,
    output_file
):


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            [
                asdict(review)
                for review in reviews
            ],

            f,

            indent=2,

            ensure_ascii=False

        )





def main():


    if len(sys.argv) < 2:


        print(
            "Usage : python parse_critic_html.py <html_file> [output_dir]"
        )

        sys.exit(1)



    html_file = Path(
        sys.argv[1]
    )



    if not html_file.exists():

        raise FileNotFoundError(
            html_file
        )



    reviews = parse_critic_html(
        html_file
    )



    game, platform = get_metadata(
        html_file
    )



    if len(sys.argv) >= 3:

        output_dir = Path(
            sys.argv[2]
        )


    else:

        output_dir = (
            html_file.parents[1]
            / "parsed"
        )



    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )



    output_file = (

        output_dir

        / f"{game}_critic_{platform}.json"

    )



    save_json(
        reviews,
        output_file
    )



    print(
        f"{len(reviews)} reviews exportées."
    )


    print(
        f"JSON sauvegardé : {output_file}"
    )




if __name__ == "__main__":

    main()