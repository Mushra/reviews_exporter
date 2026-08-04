from extractors.extract_review_platform import extract_review_page


def main():


    import sys


    if len(sys.argv) < 3:

        print(
            "Usage : python -m extractors.extract_user_platform <game> <platform>"
        )

        print(
            "Exemple : python -m extractors.extract_user_platform elden-ring pc"
        )

        return



    game = sys.argv[1]

    platform = sys.argv[2]



    extract_review_page(
        game,
        "user",
        platform
    )



if __name__ == "__main__":

    main()