from playwright.sync_api import sync_playwright

GAME = "elden-ring"

PLATFORMS = [
    "playstation-5",
    "pc",
    "xbox-series-x"
]


def inspect_platform(page, platform):

    url = (
        f"https://www.metacritic.com/game/"
        f"{GAME}/critic-reviews/?platform={platform}"
    )

    print("\n==============================")
    print("Plateforme :", platform)
    print("URL :", url)

    page.goto(url)

    page.wait_for_timeout(5000)

    print("Titre :", page.title())

    html = page.content()

    filename = f"critic_{platform}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print("Sauvé :", filename)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page(
        viewport={
            "width": 1280,
            "height": 1000
        }
    )

    for platform in PLATFORMS:
        inspect_platform(page, platform)

    input("\nEntrée pour fermer...")

    browser.close()
