from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs


GAME = "elden-ring"

URL = f"https://www.metacritic.com/game/{GAME}/"


PLATFORM_ALIASES = {
    "ps5": "playstation-5",
}


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("Chargement...")
    page.goto(URL)

    page.wait_for_timeout(5000)


    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(e => e.href)
        """
    )


    platforms = set()


    for href in links:

        if "platform=" not in href:
            continue

        query = urlparse(href).query

        params = parse_qs(query)

        if "platform" not in params:
            continue

        platform = params["platform"][0]

        # Normalisation
        platform = PLATFORM_ALIASES.get(
            platform,
            platform
        )

        platforms.add(platform)


    print("\nPlateformes trouvées :")

    for platform in sorted(platforms):
        print("-", platform)


    input("\nEntrée pour fermer...")

    browser.close()
