import time


def scroll_until_complete(
    page,
    selector,
    max_iterations=30,
    wait_time=1
):

    print(
        "Chargement progressif..."
    )


    previous_count = 0
    stagnant_iterations = 0


    for iteration in range(max_iterations):

        current_count = page.locator(
            selector
        ).count()


        print(
            f"Reviews chargées : {current_count}"
        )


        if current_count > previous_count:

            stagnant_iterations = 0

            previous_count = current_count


        else:

            stagnant_iterations += 1



        # Scroll vers le bas

        page.evaluate(
            """
            window.scrollTo(
                0,
                document.body.scrollHeight
            )
            """
        )


        time.sleep(
            wait_time
        )


        # On force un second déclencheur éventuel
        page.mouse.wheel(
            0,
            2000
        )


        time.sleep(
            wait_time
        )


        # Arrêt uniquement après plusieurs essais sans progression

        if stagnant_iterations >= 3:

            break



    print(
        "Chargement terminé"
    )