import traceback


from core.logger import Logger

from extractors.extract_metacritic_reviews import (
    extract_reviews
)

from parsers.parse_metacritic_api import (
    parse_file
)

from core.exporter import (
    export_parsed_reviews
)



logger = Logger(__name__)




class PipelineError(Exception):
    pass





def run_pipeline(

    game: str,

    platform: str,

    extract_user: bool = True,

    extract_critic: bool = True,

    process_user: bool = True,

    process_critic: bool = True,

    destination_folder: str = None,

    progress_callback=None

):

    """
    Execute full extraction + processing pipeline.

    Parameters
    ----------

    game:
        Game slug.

    platform:
        Platform slug.

    extract_user:
        Extract user reviews.

    extract_critic:
        Extract critic reviews.

    process_user:
        Parse user reviews.

    process_critic:
        Parse critic reviews.

    destination_folder:
        Optional export folder for parsed files.

    progress_callback:
        Function(percent:int, message:str)

    """



    result = {

        "success": False,

        "game": game,

        "platform": platform,

        "exported_files": []

    }




    steps = []



    # -------------------------------------------------------------
    # Build pipeline steps
    # -------------------------------------------------------------


    if extract_user:

        steps.append(
            (
                "extract",
                "user"
            )
        )


    if extract_critic:

        steps.append(
            (
                "extract",
                "critic"
            )
        )


    if process_user:

        steps.append(
            (
                "process",
                "user"
            )
        )


    if process_critic:

        steps.append(
            (
                "process",
                "critic"
            )
        )



    # Export only if something is processed

    if destination_folder and (
        process_user
        or process_critic
    ):

        steps.append(
            (
                "export",
                "parsed"
            )
        )



    total_steps = len(
        steps
    )



    if total_steps == 0:

        raise PipelineError(
            "Aucune opération sélectionnée"
        )



    completed = 0




    def update_progress(
        message
    ):

        nonlocal completed


        completed += 1


        percent = int(

            completed
            /
            total_steps
            *
            100

        )


        if progress_callback:

            progress_callback(
                percent,
                message
            )





    logger.info(
        f"Lancement pipeline : {game} - {platform}"
    )




    # -------------------------------------------------------------
    # Execute pipeline
    # -------------------------------------------------------------


    for action, target in steps:


        try:


            # -----------------------------------------------------
            # Extraction
            # -----------------------------------------------------

            if action == "extract":


                logger.info(
                    f"Extraction {target} reviews..."
                )


                extract_reviews(

                    game,

                    platform,

                    target

                )


                update_progress(

                    f"Extraction {target} terminée"

                )




            # -----------------------------------------------------
            # Processing
            # -----------------------------------------------------

            elif action == "process":


                logger.info(
                    f"Processing {target} reviews..."
                )


                parse_file(

                    game,

                    platform,

                    target

                )


                update_progress(

                    f"Processing {target} terminé"

                )




            # -----------------------------------------------------
            # Export
            # -----------------------------------------------------

            elif action == "export":


                logger.info(
                    "Export parsed reviews..."
                )


                files = export_parsed_reviews(

                    game,

                    destination_folder

                )


                result["exported_files"] = [

                    str(file)

                    for file in files

                ]


                update_progress(

                    f"{len(files)} fichiers exportés"

                )




        except Exception as error:


            logger.error(

                f"Erreur pipeline {action}/{target} : {error}"

            )


            traceback.print_exc()



            raise PipelineError(

                f"{action} {target} impossible : {error}"

            )





    if progress_callback:

        progress_callback(

            100,

            "Terminé"

        )




    result["success"] = True



    logger.info(
        "Pipeline terminé avec succès"
    )



    return result