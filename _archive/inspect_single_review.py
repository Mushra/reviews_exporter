from bs4 import BeautifulSoup


with open(
    "critic_pc.html",
    encoding="utf-8"
) as f:
    soup = BeautifulSoup(f, "html.parser")


reviews_container = soup.select_one(
    ".c-reviews-container"
)


children = reviews_container.find_all(
    recursive=False
)


print("Nombre de reviews directes :", len(children))


for i, review in enumerate(children[:3]):

    print("\n================")
    print("REVIEW", i)

    print(
        "Balise :",
        review.name
    )

    print(
        "Classes :",
        review.get("class")
    )

    print(
        review.get_text(
            " ",
            strip=True
        )[:500]
    )
