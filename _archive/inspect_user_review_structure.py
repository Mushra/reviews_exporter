from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup



GAME = "elden-ring"
PLATFORM = "pc"



URL = (
    f"https://www.metacritic.com/game/{GAME}/user-reviews/"
    f"?platform={PLATFORM}"
)



def main():


    with sync_playwright() as p:


        browser = p.chromium.launch(
            headless=False
        )


        context = browser.new_context(

            viewport={
                "width": 1600,
                "height": 900
            }

        )


        page = context.new_page()


        print(
            "Chargement :"
        )

        print(
            URL
        )


        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=30000
        )


        print(
            "Page chargée"
        )


        page.wait_for_timeout(
            5000
        )


        html = page.content()


        with open(
            "user_debug.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                html
            )


        print(
            "HTML sauvegardé : user_debug.html"
        )


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        print(
            "\nClasses data-testid trouvées :"
        )


        testids = set()


        for element in soup.find_all():

            if element.has_attr(
                "data-testid"
            ):

                testids.add(
                    element["data-testid"]
                )


        for value in sorted(testids):

            print(
                "-",
                value
            )



        print(
            "\nRecherche de cartes potentielles..."
        )


        candidates = soup.find_all(
            "div"
        )


        for div in candidates:


            text = div.get_text(
                " ",
                strip=True
            )


            if len(text) < 50:

                continue


            if (
                "review" in text.lower()
                or "helpful" in text.lower()
                or "user" in text.lower()
            ):

                print(
                    "\n=============================="
                )

                print(
                    div.name,
                    div.get("class")
                )

                print(
                    text[:500]
                )

                break



        input(
            "\nEntrée pour fermer..."
        )


        browser.close()



if __name__ == "__main__":

    main()