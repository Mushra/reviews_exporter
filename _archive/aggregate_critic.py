from pathlib import Path
import json
import sys



def load_reviews(parsed_dir):

    reviews = []


    files = sorted(
        parsed_dir.glob(
            "*_critic_*.json"
        )
    )


    print(
        f"{len(files)} fichiers JSON trouvés"
    )


    for file in files:


        print(
            f"Chargement : {file.name}"
        )


        with open(
            file,
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        reviews.extend(
            data
        )


    return reviews





def build_statistics(reviews):


    platforms = {}


    scores = []


    for review in reviews:


        platform = review.get(
            "platform",
            "unknown"
        )


        platforms[platform] = (
            platforms.get(platform, 0)
            + 1
        )


        score = review.get(
            "score"
        )


        if score is not None:

            scores.append(
                score
            )



    average_score = None


    if scores:

        average_score = round(
            sum(scores) / len(scores),
            2
        )



    return {

        "total_reviews": len(reviews),

        "platforms": platforms,

        "average_score": average_score,

        "scored_reviews": len(scores)

    }





def aggregate(game):


    base_dir = Path(
        "data"
    ) / game


    parsed_dir = (
        base_dir
        / "parsed"
    )


    output_dir = (
        base_dir
        / "aggregate"
    )


    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )



    if not parsed_dir.exists():

        raise FileNotFoundError(
            parsed_dir
        )



    reviews = load_reviews(
        parsed_dir
    )



    statistics = build_statistics(
        reviews
    )



    output = {

        "game": game,

        "review_type": "critic",

        "statistics": statistics,

        "reviews": reviews

    }



    output_file = (
        output_dir
        / f"{game}_critic_reviews.json"
    )



    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(

            output,

            f,

            indent=2,

            ensure_ascii=False

        )



    print()
    print("==============================")
    print("Aggregation terminée")
    print("==============================")
    print(
        f"Reviews totales : {statistics['total_reviews']}"
    )
    print(
        f"Score moyen : {statistics['average_score']}"
    )
    print(
        f"Plateformes : {statistics['platforms']}"
    )
    print(
        f"Fichier : {output_file}"
    )





if __name__ == "__main__":


    if len(sys.argv) < 2:


        print(
            "Usage : python aggregate_critic.py <game>"
        )


        sys.exit(1)



    aggregate(
        sys.argv[1]
    )