from urllib.parse import quote
from bs4 import BeautifulSoup



BASE_URL = "https://www.metacritic.com"



# ---------------------------------------------------------------------
# URL Builder
# ---------------------------------------------------------------------


def build_review_url(
    game,
    review_type,
    platform=None
):

    """
    Génère une URL Metacritic.

    Exemple :

    build_review_url(
        "elden-ring",
        "critic",
        "pc"
    )

    retourne :

    https://www.metacritic.com/game/elden-ring/critic-reviews/?platform=pc
    """


    url = (
        f"{BASE_URL}/game/"
        f"{quote(game)}/"
        f"{review_type}-reviews/"
    )


    if platform:

        url += (
            f"?platform={quote(platform)}"
        )


    return url



def build_critic_reviews_url(
    game,
    platform=None
):

    return build_review_url(
        game,
        "critic",
        platform
    )



def build_user_reviews_url(
    game,
    platform=None
):

    return build_review_url(
        game,
        "user",
        platform
    )



# ---------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------


def normalize_platform(
    platform
):

    """
    Normalise les noms de plateformes.
    """


    replacements = {

        "ps5":
            "playstation-5",

        "xbox-series-x-s":
            "xbox-series-x"

    }


    return replacements.get(
        platform,
        platform
    )



def extract_platforms_from_html(
    html
):

    """
    Extrait les plateformes disponibles
    depuis une page Metacritic.
    """


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    platforms = set()



    for link in soup.find_all(
        "a",
        href=True
    ):


        href = link["href"]


        if "platform=" not in href:

            continue


        value = (
            href
            .split("platform=")[1]
            .split("&")[0]
        )


        platforms.add(
            normalize_platform(value)
        )



    return sorted(
        platforms
    )



def is_valid_platform(
    platform
):

    """
    Filtre les alias inutiles.
    """


    invalid = {

        "ps5",

        "xbox-series-x-s"

    }


    return (
        platform not in invalid
    )