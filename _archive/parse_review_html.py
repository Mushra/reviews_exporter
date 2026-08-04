from bs4 import BeautifulSoup
from pathlib import Path
from models.review import Review
import re



def get_text(element):

    if element is None:
        return ""

    return element.get_text(
        " ",
        strip=True
    )



def parse_score(element):

    if element is None:
        return None


    value = get_text(
        element
    )


    if value.isdigit():

        return int(value)


    return None



def extract_metadata(path: Path):

    """
    Exemple :
    elden-ring_user_pc.html

    Retour :
    game = elden-ring
    review_type = user
    platform = pc
    """


    filename = path.stem


    match = re.match(
        r"(.+)_(critic|user)_([a-z0-9\-]+)",
        filename
    )


    if not match:

        raise ValueError(
            f"Nom invalide : {filename}"
        )


    return (

        match.group(1),

        match.group(2),

        match.group(3)

    )



def extract_author(header):

    """
    Critic :
        Attack of the Fanboy

    User :
        Shizador
    """


    if header is None:

        return ""


    copy = BeautifulSoup(
        str(header),
        "html.parser"
    )


    score = copy.select_one(
        ".c-siteReviewScore"
    )


    if score:

        score.decompose()


    return copy.get_text(
        " ",
        strip=True
    )



def extract_source_url(card):

    """
    URL interne Metacritic.

    Disponible surtout pour les user reviews.
    """


    header = card.select_one(
        '[data-testid="review-card-header"]'
    )


    if header and header.has_attr(
        "href"
    ):

        return (
            "https://www.metacritic.com"
            +
            header["href"]
        )


    return ""



def extract_external_url(card):

    """
    URL externe pour les critic reviews.
    Vide pour user reviews.
    """


    link = card.select_one(
        '.review-footer a[href^="http"]'
    )


    if link:

        return link["href"]


    return ""



def parse_review_html(
    html_file: Path
):


    with open(
        html_file,
        encoding="utf-8"
    ) as f:


        soup = BeautifulSoup(
            f,
            "html.parser"
        )


    game, review_type, platform = extract_metadata(
        html_file
    )


    cards = soup.select(
        '[data-testid="review-card"]'
    )


    print(
        f"Reviews trouvées : {len(cards)}"
    )


    reviews = []



    for card in cards:


        review = Review(

            game=game,

            review_type=review_type,

            platform=platform,


            author=extract_author(
                card.select_one(
                    '[data-testid="review-card-header"]'
                )
            ),


            date=get_text(
                card.select_one(
                    '[data-testid="review-card-date"]'
                )
            ),


            score=parse_score(
                card.select_one(
                    ".c-siteReviewScore span"
                )
            ),


            title="",


            text=get_text(
                card.select_one(
                    '[data-testid="review-quote-text"]'
                )
            ),


            source_url=extract_source_url(
                card
            ),


            external_url=extract_external_url(
                card
            ),


            metadata={}

        )


        reviews.append(
            review
        )


    return reviews



def parse_review_file(
    html_file: str | Path
):

    return parse_review_html(
        Path(html_file)
    )