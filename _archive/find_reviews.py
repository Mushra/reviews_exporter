from bs4 import BeautifulSoup

with open("metacritic_page.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Cherche tous les éléments contenant "Read More"
elements = soup.find_all(string=lambda text: text and "Read More" in text)

print("Nombre de Read More trouvés :", len(elements))

for i, element in enumerate(elements[:5]):
    print("\n--- Exemple", i + 1, "---")
    parent = element.parent

    # remonte quelques niveaux
    for _ in range(5):
        parent = parent.parent

    print(parent.prettify()[:1000])
