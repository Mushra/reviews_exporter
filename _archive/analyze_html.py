from pathlib import Path
from bs4 import BeautifulSoup

file = Path("metacritic_page.html")

html = file.read_text(encoding="utf-8")

print("Taille HTML :", len(html), "caractères")

soup = BeautifulSoup(html, "html.parser")

print("\nTitre :")
print(soup.title.text if soup.title else "Aucun")

print("\nRecherche de mots clés :")

keywords = [
    "review",
    "user",
    "score",
    "rating",
    "critic",
    "comment"
]

for keyword in keywords:
    count = html.lower().count(keyword)
    print(f"{keyword}: {count}")
