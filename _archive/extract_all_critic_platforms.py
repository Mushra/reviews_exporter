from playwright.sync_api import sync_playwright
from pathlib import Path
import subprocess
import sys
import re


VALID_PLATFORMS = {
    "pc",
    "playstation-4",
    "playstation-5",
    "xbox-one",
    "xbox-series-x",
    "nintendo-switch"
}


PLATFORM_ALIASES = {
    "ps5": "playstation-5"
}



def discover_platforms(game):

    url = (
        f"https://www.metacritic.com/game/{game}/critic-reviews/"
    )


    print("==============================")
    print("Découverte des plateformes")
    print("==============================")
    print(url)
    print()


    platforms = set()


    with sync_playwright() as p:


        browser = p.chromium.launch(
            headless=True
        )


        page = browser.new_page()


        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )


        html = page.content()


        browser.close()



    matches = re.findall(
        r"platform=([a-z0-9\-]+)",
        html
    )


    for platform in matches:


        # Normalisation des alias
        if platform in PLATFORM_ALIASES:

            platform = PLATFORM_ALIASES[platform]


        # Garde uniquement les plateformes supportées
        if platform in VALID_PLATFORMS:

            platforms.add(platform)



    platforms = sorted(
        platforms
    )


    print(
        "Plateformes retenues :"
    )


    for platform in platforms:

        print(
            f"- {platform}"
        )


    print()


    return platforms




def extract_platform(game, platform):


    print()
    print("==============================")
    print(f"Extraction : {platform}")
    print("==============================")


    command = [

        sys.executable,

        "extractors/extract_critic_platform.py",

        game,

        platform

    ]


    result = subprocess.run(
        command
    )


    if result.returncode != 0:

        print(
            f"⚠️ Échec extraction {platform}"
        )





def main():


    if len(sys.argv) < 2:


        print(
            "Usage : python extract_all_critic_platforms.py <game>"
        )


        print(
            "Exemple : python extract_all_critic_platforms.py elden-ring"
        )


        sys.exit(1)



    game = sys.argv[1]


    platforms = discover_platforms(
        game
    )


    if not platforms:


        print(
            "Aucune plateforme trouvée"
        )

        return



    for platform in platforms:


        extract_platform(
            game,
            platform
        )



    print()
    print("==============================")
    print("Extraction terminée")
    print("==============================")



if __name__ == "__main__":

    main()