from playwright.sync_api import sync_playwright


URL = "https://www.metacritic.com/game/elden-ring/critic-reviews/?platform=pc"


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


    print("Chargement page...")

    page.goto(URL)

    page.wait_for_timeout(5000)


    # On fait défiler progressivement
    for i in range(10):

        print("Scroll", i + 1)

        page.mouse.wheel(
            0,
            3000
        )

        page.wait_for_timeout(2000)


    html = page.content()


    with open(
        "critic_pc_full.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)


    print("HTML complet sauvegardé")


    input("Entrée pour fermer...")

    browser.close()
