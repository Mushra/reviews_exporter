from bs4 import BeautifulSoup


with open(
    "critic_pc.html",
    encoding="utf-8"
) as f:
    soup = BeautifulSoup(f, "html.parser")


reviews_container = soup.select_one(
    ".c-reviews-container"
)

reviews = reviews_container.find_all(
    recursive=False
)


print("Nombre de reviews trouvées :", len(reviews))


for i, review in enumerate(reviews[:3]):

    text = review.get_text(
        " ",
        strip=True
    )

    print("\n================")
    print("Review", i)
    print(text)
