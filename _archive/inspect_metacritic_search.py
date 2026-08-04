import requests
import json


QUERY = "Elden"


URLS = [

    f"https://www.metacritic.com/search/{QUERY}",

    f"https://www.metacritic.com/search/{QUERY}/",

    f"https://backend.metacritic.com/search?q={QUERY}",

    f"https://backend.metacritic.com/search/metacritic?q={QUERY}",

]



headers = {

    "User-Agent":
        "Mozilla/5.0",

    "Accept":
        "application/json,text/plain,*/*",

}



for url in URLS:

    print("\n" + "=" * 80)

    print(url)


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )


        print(
            "Status:",
            response.status_code
        )


        print(
            "Content-Type:",
            response.headers.get(
                "content-type"
            )
        )


        print(
            response.text[:300]
        )


    except Exception as e:

        print(
            "ERROR:",
            e
        )