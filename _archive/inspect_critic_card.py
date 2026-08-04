from bs4 import BeautifulSoup


with open(
    "critic_pc.html",
    encoding="utf-8"
) as f:
    soup = BeautifulSoup(f, "html.parser")


# Cherche un élément contenant "Read More"
target = soup.find(
    string=lambda t: t and "Read More" in t
)


if not target:
    print("Aucun Read More trouvé")
    exit()


print("Read More trouvé")

element = target.parent


# Remonte dans l'arbre HTML
for level in range(10):

    print("\n================")
    print("Niveau", level)

    print(
        "Balise :",
        element.name
    )

    print(
        "Classes :",
        element.get("class")
    )

    element = element.parent
