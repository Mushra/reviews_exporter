from extractors.extract_review_platform import extract_review_page


def main():

    import sys


    if len(sys.argv) < 3:

        print(
            "Usage : python -m extractors.extract_critic_platform <game> <platform>"
        )

        return


    game = sys.argv[1]

    platform = sys.argv[2]


    extract_review_page(
        game,
        "critic",
        platform
    )



if __name__ == "__main__":

    main()