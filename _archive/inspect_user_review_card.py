from bs4 import BeautifulSoup



HTML_FILE = "user_debug.html"



def main():


    with open(
        HTML_FILE,
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
        f"Nombre de cartes trouvées : {len(cards)}"
    )


    if not cards:

        print(
            "Aucune carte trouvée"
        )

        return



    card = cards[0]


    print(
        "\n=============================="
    )

    print(
        "STRUCTURE COMPLETE PREMIERE REVIEW"
    )

    print(
        "==============================\n"
    )


    print(
        card.prettify()[:10000]
    )



    print(
        "\n=============================="
    )

    print(
        "TEXT EXTRAIT"
    )

    print(
        "==============================\n"
    )


    print(
        card.get_text(
            "\n",
            strip=True
        )
    )



if __name__ == "__main__":

    main()