from bs4 import BeautifulSoup

with open(
    "critic_pc_full.html",
    encoding="utf-8"
) as f:
    soup = BeautifulSoup(f, "html.parser")


review = soup.select(
    ".c-reviews-container > div"
)[0]


print(review.prettify())