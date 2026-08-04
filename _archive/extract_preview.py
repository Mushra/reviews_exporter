from bs4 import BeautifulSoup

with open("metacritic_page.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")


# Cherche la section user reviews
section = soup.select_one(".product-hero__user-reviews")

if not section:
    print("Section user reviews introuvable")
    exit()

print("Section trouvée")


# Affiche les div enfants qui semblent contenir des reviews
cards = section.select("div")

print("Nombre de div :", len(cards))


for i, card in enumerate(cards[:20]):
    text = card.get_text(" ", strip=True)

    if len(text) > 50:
        print("\n--- CARD", i, "---")
        print(text[:500])
