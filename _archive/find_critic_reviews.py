from bs4 import BeautifulSoup


with open(
    "critic_pc.html",
    encoding="utf-8"
) as f:
    soup = BeautifulSoup(f, "html.parser")


container = soup.select_one(
    ".product-reviews-list"
)

if not container:
    print("Liste de reviews introuvable")
    exit()


print("Container trouvé")


# Affiche les enfants directs
children = container.find_all(
    recursive=False
)

print(
    "Enfants directs :",
    len(children)
)


for i, child in enumerate(children[:5]):

    print("\n================")
    print("ELEMENT", i)

    print(
        "Balise :",
        child.name
    )

    print(
        "Classes :",
        child.get("class")
    )

    print(
        child.get_text(
            " ",
            strip=True
        )[:300]
    )
