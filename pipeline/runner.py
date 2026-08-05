import traceback


from core.logger import Logger

from extractors.extract_metacritic_reviews import (
    extract_reviews
)

from parsers.parse_metacritic_api import (
    parse_file,
    parse_all_platforms
)

from core.api import is_all_platforms

from extractors.extract_steam_reviews import (
    extract_steam_reviews
)

from parsers.parse_steam_api import (
    parse_file as parse_steam_file
)

from extractors.extract_youtube_comments import (
    extract_videos as extract_youtube_videos
)

from parsers.parse_youtube_api import (
    parse_files as parse_youtube_files
)

from core.youtube_api import parse_video_id

from core.exporter import (
    export_parsed_reviews
)

from core.cancellation import check_cancelled, PipelineCancelled



logger = Logger(__name__)




class PipelineError(Exception):
    pass


# ---------------------------------------------------------------------
# Shared progress helpers
# ---------------------------------------------------------------------

def _step_range(index, total_steps):

    start = int(index * 100 / total_steps)
    end = int((index + 1) * 100 / total_steps)

    if index == total_steps - 1:
        end = 100

    if end <= start:
        end = min(start + 1, 100)

    return start, end


def _make_progress_report(progress_callback, start, end):

    def report(message, ratio=None):

        if not progress_callback:
            return

        if ratio is None:
            percent = min(start + 1, end)
        else:
            percent = int(start + ratio * (end - start))
            percent = min(max(start, percent), end)

        progress_callback(percent, message)

    return report





def run_pipeline(

    game: str,

    platform: str,

    extract_user: bool = True,

    extract_critic: bool = True,

    process_user: bool = True,

    process_critic: bool = True,

    destination_folder: str = None,

    progress_callback=None,

    cancel_event=None

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
            "No operation selected"
        )



    step_range = _step_range

    def make_progress_report(
        start,
        end
    ):

        return _make_progress_report(
            progress_callback,
            start,
            end
        )




    logger.info(
        f"Starting pipeline : {game} - {platform}"
    )




    # -------------------------------------------------------------
    # Execute pipeline
    # -------------------------------------------------------------


    for step_index, (action, target) in enumerate(steps):


        check_cancelled(cancel_event)


        try:


            # -----------------------------------------------------
            # Extraction
            # -----------------------------------------------------

            if action == "extract":


                logger.info(
                    f"Extraction {target} reviews..."
                )


                start, end = step_range(
                    step_index,
                    total_steps
                )

                extract_reviews(

                    game,

                    platform,

                    target,

                    progress_callback=make_progress_report(
                        start,
                        end
                    ),

                    cancel_event=cancel_event

                )




            # -----------------------------------------------------
            # Processing
            # -----------------------------------------------------

            elif action == "process":


                logger.info(
                    f"Processing {target} reviews..."
                )


                start, end = step_range(
                    step_index,
                    total_steps
                )

                if is_all_platforms(platform):

                    parse_all_platforms(

                        game,

                        target

                    )

                else:

                    try:

                        parse_file(

                            game,

                            platform,

                            target

                        )

                    except FileNotFoundError:

                        logger.warning(
                            f"No raw {target} reviews for platform "
                            f"'{platform}' - nothing to process"
                        )


                make_progress_report(
                    start,
                    end
                )(
                    f"Processing {target} complete",
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
                    step_index,
                    total_steps
                )

                make_progress_report(
                    start,
                    end
                )(
                    f"{len(files)} files exported",
                    ratio=1.0
                )




        except PipelineCancelled:

            logger.warning(
                f"Pipeline cancelled during {action}/{target}"
            )

            raise

        except Exception as error:


            logger.error(

                f"Pipeline error {action}/{target} : {error}"

            )


            traceback.print_exc()



            raise PipelineError(

                f"{action} {target} failed : {error}"

            )





    if progress_callback:

        progress_callback(

            100,

            "Done"

        )




    result["success"] = True



    logger.info(
        "Pipeline completed successfully"
    )



    return result


# =============================================================
# Steam pipeline
# =============================================================

def run_steam_pipeline(
    game: str,
    appid,
    extract: bool = True,
    process: bool = True,
    destination_folder: str = None,
    progress_callback=None,
    cancel_event=None,
):

    result = {
        "success": False,
        "game": game,
        "appid": appid,
        "exported_files": [],
    }

    steps = []

    if extract:
        steps.append("extract")

    if process:
        steps.append("process")

    if destination_folder and process:
        steps.append("export")

    total_steps = len(steps)

    if total_steps == 0:
        raise PipelineError("No operation selected")

    logger.info(f"Starting Steam pipeline : {game} - appid {appid}")

    for step_index, action in enumerate(steps):

        check_cancelled(cancel_event)

        start, end = _step_range(step_index, total_steps)
        report = _make_progress_report(progress_callback, start, end)

        try:

            if action == "extract":

                logger.info("Extracting Steam reviews...")

                extract_steam_reviews(
                    game,
                    appid,
                    progress_callback=report,
                    cancel_event=cancel_event,
                )

            elif action == "process":

                logger.info("Processing Steam reviews...")

                parse_steam_file(game)

                report("Processing Steam complete", ratio=1.0)

            elif action == "export":

                logger.info("Exporting Steam parsed reviews...")

                files = export_parsed_reviews(game, destination_folder)

                result["exported_files"] = [str(file) for file in files]

                report(f"{len(files)} files exported", ratio=1.0)

        except PipelineCancelled:

            logger.warning(f"Steam pipeline cancelled during {action}")

            raise

        except Exception as error:

            logger.error(f"Steam pipeline error {action} : {error}")

            traceback.print_exc()

            raise PipelineError(f"{action} failed : {error}")

    if progress_callback:
        progress_callback(100, "Done")

    result["success"] = True

    logger.info("Steam pipeline completed successfully")

    return result


# =============================================================
# YouTube pipeline
# =============================================================

def run_youtube_pipeline(
    game: str,
    video_urls: list,
    api_key: str,
    extract: bool = True,
    process: bool = True,
    destination_folder: str = None,
    progress_callback=None,
    cancel_event=None,
):

    result = {
        "success": False,
        "game": game,
        "videos": video_urls,
        "exported_files": [],
    }

    if not video_urls:
        raise PipelineError("No video selected")

    video_ids = [
        video_id
        for video_id in (parse_video_id(url) for url in video_urls)
        if video_id
    ]

    if not video_ids:
        raise PipelineError("No valid YouTube URL/ID")

    steps = []

    if extract:
        steps.append("extract")

    if process:
        steps.append("process")

    if destination_folder and process:
        steps.append("export")

    total_steps = len(steps)

    if total_steps == 0:
        raise PipelineError("No operation selected")

    logger.info(f"Starting YouTube pipeline : {game} - {len(video_ids)} video(s)")

    for step_index, action in enumerate(steps):

        check_cancelled(cancel_event)

        start, end = _step_range(step_index, total_steps)
        report = _make_progress_report(progress_callback, start, end)

        try:

            if action == "extract":

                logger.info("Extracting YouTube comments...")

                extract_youtube_videos(
                    game,
                    video_urls,
                    api_key,
                    progress_callback=report,
                    cancel_event=cancel_event,
                )

            elif action == "process":

                logger.info("Processing YouTube comments...")

                parse_youtube_files(game, video_ids)

                report("Processing YouTube complete", ratio=1.0)

            elif action == "export":

                logger.info("Exporting YouTube parsed reviews...")

                files = export_parsed_reviews(game, destination_folder)

                result["exported_files"] = [str(file) for file in files]

                report(f"{len(files)} files exported", ratio=1.0)

        except PipelineCancelled:

            logger.warning(f"YouTube pipeline cancelled during {action}")

            raise

        except Exception as error:

            logger.error(f"YouTube pipeline error {action} : {error}")

            traceback.print_exc()

            raise PipelineError(f"{action} failed : {error}")

    if progress_callback:
        progress_callback(100, "Done")

    result["success"] = True

    logger.info("YouTube pipeline completed successfully")

    return result