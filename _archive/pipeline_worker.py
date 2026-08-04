from PySide6.QtCore import (
    QThread,
    Signal
)


from core.logger import Logger

from core.runner import (
    run_pipeline,
    PipelineError
)



logger = Logger(__name__)




class PipelineWorker(QThread):


    progress = Signal(
        int,
        str
    )


    finished = Signal(
        bool,
        str
    )



    def __init__(

        self,

        game,

        platform,

        extract_user,

        extract_critic,

        process_user,

        process_critic,

        destination_folder

    ):


        super().__init__()



        self.game = game

        self.platform = platform

        self.extract_user = extract_user

        self.extract_critic = extract_critic

        self.process_user = process_user

        self.process_critic = process_critic

        self.destination_folder = destination_folder




    def run(self):


        try:


            run_pipeline(

                game=self.game,

                platform=self.platform,

                extract_user=self.extract_user,

                extract_critic=self.extract_critic,

                process_user=self.process_user,

                process_critic=self.process_critic,

                destination_folder=self.destination_folder,

                progress_callback=self.update_progress

            )


            self.finished.emit(

                True,

                "Pipeline completed successfully"

            )



        except PipelineError as error:


            self.finished.emit(

                False,

                str(error)

            )



        except Exception as error:


            logger.error(
                str(error)
            )


            self.finished.emit(

                False,

                f"Unexpected error : {error}"

            )




    def update_progress(

        self,

        percent,

        message

    ):


        self.progress.emit(

            percent,

            message

        )