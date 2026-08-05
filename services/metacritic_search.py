import json

import requests

from pathlib import Path

from core.logger import Logger
from core.paths import get_data_directory



logger = Logger(__name__)



CACHE_FILE = get_data_directory() / "cache" / "game_search.json"



SEARCH_URL = (
    "https://backend.metacritic.com/"
    "composer/metacritic/pages/search/{query}/web"
)




# ---------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------


def load_cache():


    if not CACHE_FILE.exists():

        return {}



    try:

        with open(
            CACHE_FILE,
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )


    except Exception:

        return {}




def save_cache(
    cache
):


    CACHE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            cache,

            file,

            indent=2,

            ensure_ascii=False

        )




# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def normalize(
    value
):

    return (

        value

        .lower()

        .strip()

    )




def score_result(
    title,
    query
):


    title = normalize(
        title
    )


    query = normalize(
        query
    )



    if title == query:

        return 100



    if title.startswith(query):

        return 80



    if query in title:

        return 50



    return 10




# ---------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------


def search_games(

    query: str,

    limit: int = 10

):


    if not query or len(
        query.strip()
    ) < 2:

        return []



    query = query.strip()



    cache = load_cache()



    cache_key = query.lower()



    if cache_key in cache:

        return cache[
            cache_key
        ]



    url = SEARCH_URL.format(
        query=query
    )



    params = {

        "contentOnly":
            "true",

        "page":
            1,

        "offset":
            0,

        "limit":
            30

    }



    headers = {

        "User-Agent":
            "Mozilla/5.0",

        "Origin":
            "https://www.metacritic.com",

        "Accept":
            "application/json"

    }



    try:

        response = requests.get(

            url,

            params=params,

            headers=headers,

            timeout=10

        )


        response.raise_for_status()



        data = response.json()



    except Exception as error:


        logger.error(

            f"Metacritic search error : {error}"

        )


        return []




    candidates = []





    def scan(
        value
    ):


        if isinstance(
            value,
            dict
        ):


            if (

                value.get(
                    "title"
                )

                and

                value.get(
                    "slug"
                )

            ):


                candidates.append(
                    value
                )



            for child in value.values():

                scan(
                    child
                )



        elif isinstance(
            value,
            list
        ):


            for child in value:

                scan(
                    child
                )




    scan(
        data
    )




    results = []

    seen = set()




    for item in candidates:



        slug = item.get(
            "slug"
        )


        if not slug:

            continue



        if slug in seen:

            continue



        seen.add(
            slug
        )



        title = item.get(
            "title",
            ""
        )



        results.append({

            "title":
                title,

            "slug":
                slug,

            "score":
                score_result(
                    title,
                    query
                ),

            "url":
                item.get(
                    "url",
                    ""
                )

        })




    results.sort(

        key=lambda item:
            item["score"],

        reverse=True

    )



    results = results[:limit]



    cache[cache_key] = results


    save_cache(
        cache
    )



    return results




def get_game_slug(
    title
):


    results = search_games(
        title,
        limit=1
    )


    if not results:

        return None



    return results[0]["slug"]