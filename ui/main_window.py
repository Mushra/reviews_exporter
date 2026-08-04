from pathlib import Path
import os
import traceback


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QMessageBox,
    QListWidget,
    QListWidgetItem
)


from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QObject,
    QTimer
)


from services.metacritic_search import search_games


from pipeline.runner import (
    run_pipeline,
    PipelineError
)

from core.logger import Logger



# =============================================================
# Worker
# =============================================================


class PipelineWorker(QObject):


    progress = Signal(
        int,
        str
    )


    finished = Signal()


    error = Signal(
        str
    )



    def __init__(
        self,
        params
    ):

        super().__init__()

        self.params = params



    def run(self):

        try:

            run_pipeline(
                progress_callback=self.progress.emit,
                **self.params
            )


            self.finished.emit()


        except Exception as error:

            traceback.print_exc()

            self.error.emit(
                str(error)
            )





# =============================================================
# Main Window
# =============================================================


class MainWindow(QWidget):
    log_signal = Signal(str)


    def __init__(self):

        super().__init__()


        self.selected_game = None

        self.destination_folder = None

        self.thread = None

        self.worker = None


        self.search_timer = QTimer()

        self.search_timer.setSingleShot(
            True
        )

        self.search_timer.timeout.connect(
            self.execute_search
        )


        self.build_ui()

        # Logger listener callback and last log to avoid duplicates
        self._logger_callback = None
        self._last_log = None

        # Connect log signal to UI appender
        self.log_signal.connect(self._append_log)



    # =============================================================
    # UI
    # =============================================================


    def build_ui(self):

        self.setWindowTitle(
            "Metacritic Review Exporter"
        )


        self.resize(
            900,
            700
        )


        layout = QVBoxLayout()



        layout.addWidget(
            QLabel("Game")
        )


        self.game_input = QLineEdit()

        self.game_input.setPlaceholderText(
            "Search game..."
        )


        self.game_input.textChanged.connect(
            self.on_game_search
        )


        layout.addWidget(
            self.game_input
        )



        self.results_list = QListWidget()

        self.results_list.setMaximumHeight(
            150
        )


        self.results_list.itemClicked.connect(
            self.select_game
        )


        layout.addWidget(
            self.results_list
        )



        layout.addWidget(
            QLabel("Platform")
        )


        self.platform_box = QComboBox()


        self.platform_box.addItems(
            [
                "all platform",
                "pc",
                "ps5",
                "xbox",
                "switch"
            ]
        )


        layout.addWidget(
            self.platform_box
        )



        destination = QHBoxLayout()


        self.destination_label = QLabel(
            "No destination selected"
        )


        self.destination_button = QPushButton(
            "Choose Folder"
        )


        self.destination_button.clicked.connect(
            self.select_destination
        )


        destination.addWidget(
            self.destination_label
        )


        destination.addWidget(
            self.destination_button
        )


        layout.addLayout(
            destination
        )



        layout.addWidget(
            QLabel("Operations")
        )



        self.extract_user = QCheckBox(
            "Extract User Reviews"
        )

        self.extract_critic = QCheckBox(
            "Extract Critic Reviews"
        )

        self.process_user = QCheckBox(
            "Process User Reviews"
        )

        self.process_critic = QCheckBox(
            "Process Critic Reviews"
        )


        for checkbox in [

            self.extract_user,
            self.extract_critic,
            self.process_user,
            self.process_critic

        ]:

            checkbox.setChecked(True)

            layout.addWidget(
                checkbox
            )



        actions = QHBoxLayout()



        self.process_button = QPushButton(
            "Process"
        )


        self.process_button.clicked.connect(
            self.start_process
        )


        self.open_button = QPushButton(
            "Open Files"
        )


        self.open_button.clicked.connect(
            self.open_files
        )


        actions.addWidget(
            self.process_button
        )

        actions.addWidget(
            self.open_button
        )


        layout.addLayout(
            actions
        )



        self.progress = QProgressBar()


        layout.addWidget(
            self.progress
        )



        self.log_output = QTextEdit()


        self.log_output.setReadOnly(
            True
        )


        layout.addWidget(
            self.log_output
        )


        self.setLayout(
            layout
        )


    def _append_log(self, message):

        # This runs on UI thread via log_signal
        try:
            if message == self._last_log:
                return

            self.log_output.append(
                message
            )

            self._last_log = message

        except Exception:
            pass



    # =============================================================
    # Search
    # =============================================================


    def on_game_search(
        self,
        text
    ):

        self.search_timer.stop()


        if len(text.strip()) < 2:

            self.results_list.clear()

            return


        self.search_timer.start(
            400
        )



    def execute_search(self):

        text = self.game_input.text().strip()


        try:

            results = search_games(
                text
            )


            self.results_list.clear()


            for game in results:


                item = QListWidgetItem(
                    f"{game['title']} ({game['slug']})"
                )


                item.setData(
                    Qt.UserRole,
                    game
                )


                self.results_list.addItem(
                    item
                )


        except Exception as error:

            self.write_log(
                f"Search error : {error}"
            )



    def select_game(
        self,
        item
    ):

        self.selected_game = item.data(
            Qt.UserRole
        )


        self.game_input.setText(
            self.selected_game["title"]
        )


        self.write_log(
            f"Selected : {self.selected_game['title']}"
        )



    # =============================================================
    # Destination
    # =============================================================


    def select_destination(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select destination"
        )


        if folder:

            self.destination_folder = folder

            self.destination_label.setText(
                folder
            )



    # =============================================================
    # Pipeline
    # =============================================================


    def start_process(self):


        if not self.selected_game:

            QMessageBox.warning(
                self,
                "Missing game",
                "Please select a game."
            )

            return



        params = {

            "game":
                self.selected_game["slug"],


            "platform":
                self.platform_box.currentText(),


            "extract_user":
                self.extract_user.isChecked(),


            "extract_critic":
                self.extract_critic.isChecked(),


            "process_user":
                self.process_user.isChecked(),


            "process_critic":
                self.process_critic.isChecked(),


            "destination_folder":
                self.destination_folder

        }



        # Register logger listener to stream logs into the UI (avoid duplicate registration)
        if not self._logger_callback:
            self._logger_callback = lambda msg: self.log_signal.emit(msg)
            try:
                Logger.add_listener(self._logger_callback)
            except Exception:
                self._logger_callback = None

        # Reset progress
        try:
            self.progress.setValue(0)
        except Exception:
            pass

        self.set_running(
            True
        )


        self.thread = QThread()


        self.worker = PipelineWorker(
            params
        )


        self.worker.moveToThread(
            self.thread
        )


        self.thread.started.connect(
            self.worker.run
        )


        self.worker.progress.connect(
            self.update_progress
        )


        self.worker.finished.connect(
            self.pipeline_finished
        )


        self.worker.error.connect(
            self.pipeline_error
        )


        self.thread.start()



    def update_progress(
        self,
        percent,
        message
    ):

        self.progress.setValue(
            percent
        )


        self.write_log(
            f"{percent}% - {message}"
        )



    def pipeline_finished(self):

        # Ensure progress is complete
        try:
            self.progress.setValue(100)
        except Exception:
            pass

        self.write_log(
            "Pipeline completed."
        )

        self.cleanup_thread()



    def pipeline_error(
        self,
        message
    ):

        self.write_log(
            f"ERROR : {message}"
        )


        QMessageBox.critical(
            self,
            "Pipeline Error",
            message
        )


        self.cleanup_thread()



    def cleanup_thread(self):

        # Remove logger listener
        try:
            if self._logger_callback:
                Logger.remove_listener(self._logger_callback)
                self._logger_callback = None
        except Exception:
            pass

        # Quit and wait thread
        try:
            if self.thread:
                self.thread.quit()
                self.thread.wait()
        except Exception:
            pass

        # Clear references
        self.thread = None
        self.worker = None

        # Re-enable controls
        self.set_running(False)



    def set_running(
        self,
        running
    ):

        self.process_button.setEnabled(
            not running
        )


        self.destination_button.setEnabled(
            not running
        )

        # Disable/enable other controls
        try:
            self.game_input.setEnabled(not running)
            self.results_list.setEnabled(not running)
            self.platform_box.setEnabled(not running)

            for checkbox in [
                self.extract_user,
                self.extract_critic,
                self.process_user,
                self.process_critic
            ]:
                checkbox.setEnabled(not running)
        except Exception:
            pass



    # =============================================================
    # Files
    # =============================================================


    def open_files(self):

        # If explicit destination set, open it
        if self.destination_folder:

            path = Path(self.destination_folder)

            if path.exists():
                os.startfile(path)
                return

            QMessageBox.warning(
                self,
                "Folder not found",
                f"Destination folder not found: {path}"
            )
            return

        # Otherwise try default parsed folder for selected game
        if not self.selected_game:

            QMessageBox.information(
                self,
                "No destination",
                "No destination selected and no game selected."
            )
            return

        slug = self.selected_game.get("slug")

        if not slug:
            QMessageBox.information(
                self,
                "No slug",
                "Selected game has no slug."
            )
            return

        from core.paths import get_data_directory

        path = get_data_directory() / slug / "parsed"

        if path.exists():
            os.startfile(path)
            return

        QMessageBox.warning(
            self,
            "Folder not found",
            f"Parsed folder not found: {path}"
        )



    # =============================================================
    # Utils
    # =============================================================


    def write_log(
        self,
        message
    ):

        # Route all logs through the UI signal for thread-safety and dedup
        try:
            self.log_signal.emit(message)
        except Exception:
            # Fallback: append directly
            try:
                self.log_output.append(message)
            except Exception:
                pass