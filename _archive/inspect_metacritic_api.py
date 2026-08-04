import requests
import json
import sys


GAME = "elden-ring"
PLATFORM = "pc"


HEADERS = {

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36",

    "Accept":
        "application/json"

}



def inspect_api(
    review_type
):


    if review_type == "user":

        url = (
            "https://backend.metacritic.com/reviews/metacritic/user/"
            f"games/{GAME}/platform/{PLATFORM}/web"
        )


    elif review_type == "critic":

        url = (
            "https://backend.metacritic.com/reviews/metacritic/critic/"
            f"games/{GAME}/platform/{PLATFORM}/web"
        )


    else:

        raise ValueError(
            "review_type doit être user ou critic"
        )



    params = {

        "offset": 0,

        "limit": 1,

        "filterBySentiment": "all",

        "sort": "date",

        "componentName":
            f"{review_type}-reviews",

        "componentDisplayName":
            f"{review_type} Reviews",

        "componentType":
            "ReviewList"

    }



    print()
    print("=" * 50)
    print(
        f"Inspection API {review_type}"
    )
    print("=" * 50)

    print(url)



    response = requests.get(

        url,

        params=params,

        headers=HEADERS,

        timeout=30

    )


    print()

    print(
        "Status :",
        response.status_code
    )


    print(
        "Content-Type :",
        response.headers.get(
            "content-type"
        )
    )


    if response.status_code != 200:

        print(
            response.text[:1000]
        )

        return



    data = response.json()



    output = (
        f"{review_type}_api_debug.json"
    )


    with open(

        output,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            data,

            f,

            indent=2,

            ensure_ascii=False

        )



    print()

    print(
        f"Sauvegardé : {output}"
    )


    print()

    print(
        "Clés principales :"
    )


    if isinstance(data, dict):

        for key in data.keys():

            print(
                "-",
                key
            )


    print()

    print(
        json.dumps(

            data,

            indent=2,

            ensure_ascii=False

        )[:3000]

    )



if __name__ == "__main__":


    target = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "user"
    )


    inspect_api(
        target
    )