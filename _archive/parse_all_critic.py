from pathlib import Path
import subprocess
import sys


def parse_all(game):

    raw_dir = Path(
        "data"
    ) / game / "raw"


    output_dir = Path(
        "data"
    ) / game / "parsed"


    output_dir.mkdir(
        exist_ok=True
    )


    html_files = list(
        raw_dir.glob(
            "*_critic_*.html"
        )
    )


    if not html_files:

        print(
            "Aucun fichier HTML trouvé"
        )

        return



    print(
        f"{len(html_files)} fichiers trouvés"
    )



    for html_file in html_files:


        print()
        print("==============================")
        print(
            f"Parsing : {html_file.name}"
        )
        print("==============================")


        command = [

            sys.executable,

            "parsers/parse_critic_html.py",

            str(html_file),

            str(output_dir)

        ]


        result = subprocess.run(
            command
        )


        if result.returncode != 0:

            print(
                f"⚠️ Erreur parsing {html_file.name}"
            )



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "Usage : python parse_all_critic.py <game>"
        )

        sys.exit(1)



    parse_all(
        sys.argv[1]
    )