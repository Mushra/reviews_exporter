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




    def step_range(
        index
    ):

        start = int(
            index
            *
            100
            /
            total_steps
        )

        end = int(
            (index + 1)
            *
            100
            /
            total_steps
        )

        if index == total_steps - 1:
            end = 100

        if end <= start:
            end = min(start + 1, 100)

        return start, end


    def make_progress_report(
        start,
        end
    ):

        def report(
            message,
            ratio=None
        ):

            if not progress_callback:
                return

            if ratio is None:
                percent = min(
                    start + 1,
                    end
                )
            else:
                percent = int(
                    start
                    + ratio
                    *
                    (end - start)
                )
                percent = min(
                    max(start, percent),
                    end
                )

            progress_callback(
                percent,
                message
            )

        return report





    logger.info(
        f"Lancement pipeline : {game} - {platform}"
    )




    # -------------------------------------------------------------
    # Execute pipeline
    # -------------------------------------------------------------


    for step_index, (action, target) in enumerate(steps):


        try:


            # -----------------------------------------------------
            # Extraction
            # -----------------------------------------------------

            if action == "extract":


                logger.info(
                    f"Extraction {target} reviews..."
                )


                start, end = step_range(
                    step_index
                )

                extract_reviews(

                    game,

                    platform,

                    target,

                    progress_callback=make_progress_report(
                        start,
                        end
                    )

                )




            # -----------------------------------------------------
            # Processing
            # -----------------------------------------------------

            elif action == "process":


                logger.info(
                    f"Processing {target} reviews..."
                )


                start, end = step_range(
                    step_index
                )

                parse_file(

                    game,

                    platform,

                    target

                )


                make_progress_report(
                    start,
                    end
                )(
                    f"Processing {target} terminé",
                    ratio=1.0
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


                start, end = step_range(
                    step_index
                )

                make_progress_report(
                    start,
                    end
                )(
                    f"{len(files)} fichiers exportés",
                    ratio=1.0
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