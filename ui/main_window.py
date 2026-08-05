from pathlib import Path
import os
import threading
import traceback


from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QTextEdit,
    QMessageBox,
    QTabWidget,
    QFrame,
)


from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    QObject,
)


from core.logger import Logger

from ui.tabs.metacritic_tab import MetacriticTab
from ui.tabs.steam_tab import SteamTab
from ui.tabs.youtube_tab import YoutubeTab
from ui.settings_dialog import SettingsDialog

from core.cancellation import PipelineCancelled



# =============================================================
# Worker
# =============================================================


class PipelineWorker(QObject):

    progress = Signal(int, str)
    finished = Signal()
    error = Signal(str)
    cancelled = Signal()

    def __init__(self, func, kwargs, cancel_event=None):

        super().__init__()

        self.func = func
        self.kwargs = kwargs
        self.cancel_event = cancel_event

    def run(self):

        try:

            self.func(
                progress_callback=self.progress.emit,
                cancel_event=self.cancel_event,
                **self.kwargs,
            )

            self.finished.emit()

        except PipelineCancelled:

            self.cancelled.emit()

        except Exception as error:

            traceback.print_exc()

            self.error.emit(str(error))



# =============================================================
# Main Window
# =============================================================


class MainWindow(QWidget):

    log_signal = Signal(str)

    def __init__(self):

        super().__init__()

        self.destination_folder = None

        self.thread = None
        self.worker = None
        self.cancel_event = None

        self._logger_callback = None
        self._last_log = None

        self._build_ui()

        self.log_signal.connect(self._append_log)

    # =============================================================
    # UI
    # =============================================================

    def _build_ui(self):

        self.setWindowTitle("Review Exporter")
        self.resize(960, 780)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        body = QVBoxLayout()
        body.setContentsMargins(20, 16, 20, 16)
        body.setSpacing(14)

        self.tabs = QTabWidget()

        self.metacritic_tab = MetacriticTab()
        self.steam_tab = SteamTab()
        self.youtube_tab = YoutubeTab()

        self.tabs.addTab(self.metacritic_tab, "Metacritic")
        self.tabs.addTab(self.steam_tab, "Steam")
        self.tabs.addTab(self.youtube_tab, "YouTube")

        body.addWidget(self.tabs)

        body.addWidget(self._build_shared_panel())

        body_widget = QWidget()
        body_widget.setLayout(body)

        layout.addWidget(body_widget)

        self.setLayout(layout)

    def _build_header(self):

        header = QFrame()
        header.setProperty("role", "header")

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 16, 20, 16)

        titles = QVBoxLayout()
        titles.setSpacing(2)

        title = QLabel("Review Exporter")
        title.setProperty("role", "title")

        subtitle = QLabel("Metacritic · Steam · YouTube — JSON export for LLM analysis")
        subtitle.setProperty("role", "subtitle")

        titles.addWidget(title)
        titles.addWidget(subtitle)

        header_layout.addLayout(titles)
        header_layout.addStretch()

        settings_button = QPushButton("⚙ Settings")
        settings_button.clicked.connect(self._open_settings)

        header_layout.addWidget(settings_button)

        header.setLayout(header_layout)

        return header

    def _build_shared_panel(self):

        card = QFrame()
        card.setProperty("role", "card")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        destination_row = QHBoxLayout()

        self.destination_label = QLabel("No export folder selected")
        self.destination_label.setProperty("role", "subtitle")

        self.destination_button = QPushButton("Choose export folder")
        self.destination_button.clicked.connect(self._select_destination)

        destination_row.addWidget(self.destination_label)
        destination_row.addStretch()
        destination_row.addWidget(self.destination_button)

        layout.addLayout(destination_row)

        actions_row = QHBoxLayout()

        self.process_button = QPushButton("Start extraction")
        self.process_button.setProperty("role", "primary")
        self.process_button.clicked.connect(self._start_process)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_process)

        self.open_button = QPushButton("Open files")
        self.open_button.clicked.connect(self._open_files)

        actions_row.addWidget(self.process_button)
        actions_row.addWidget(self.cancel_button)
        actions_row.addWidget(self.open_button)
        actions_row.addStretch()

        layout.addLayout(actions_row)

        progress_row = QHBoxLayout()

        self.progress = QProgressBar()
        self.progress.setValue(0)

        progress_row.addWidget(self.progress)

        layout.addLayout(progress_row)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(180)

        layout.addWidget(self.log_output)

        card.setLayout(layout)

        return card

    def _append_log(self, message):

        try:

            if message == self._last_log:
                return

            self.log_output.append(message)

            self._last_log = message

        except Exception:
            pass

    # =============================================================
    # Settings
    # =============================================================

    def _open_settings(self):

        dialog = SettingsDialog(self)

        dialog.exec()

        self.youtube_tab.refresh_key_status()

    # =============================================================
    # Destination
    # =============================================================

    def _select_destination(self):

        folder = QFileDialog.getExistingDirectory(self, "Select export folder")

        if folder:

            self.destination_folder = folder

            self.destination_label.setText(folder)

    # =============================================================
    # Pipeline
    # =============================================================

    def _current_tab(self):

        return self.tabs.currentWidget()

    def _start_process(self):

        tab = self._current_tab()

        request = tab.get_request(self.destination_folder)

        if not request:
            return

        if not self._logger_callback:

            self._logger_callback = lambda msg: self.log_signal.emit(msg)

            try:
                Logger.add_listener(self._logger_callback)
            except Exception:
                self._logger_callback = None

        try:
            self.progress.setValue(0)
        except Exception:
            pass

        self._set_running(True)

        self.cancel_event = threading.Event()

        self.thread = QThread()

        self.worker = PipelineWorker(
            request["func"],
            request["kwargs"],
            cancel_event=self.cancel_event,
        )

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.progress.connect(self._update_progress)
        self.worker.finished.connect(self._pipeline_finished)
        self.worker.error.connect(self._pipeline_error)
        self.worker.cancelled.connect(self._pipeline_cancelled)

        self.thread.start()

    def _cancel_process(self):

        if self.cancel_event:

            self.cancel_event.set()

            self._write_log("Cancelling...")

            self.cancel_button.setEnabled(False)

    def _update_progress(self, percent, message):

        self.progress.setValue(percent)

        self._write_log(f"{percent}% - {message}")

    def _pipeline_finished(self):

        try:
            self.progress.setValue(100)
        except Exception:
            pass

        self._write_log("Pipeline finished.")

        try:
            self.youtube_tab.refresh_project_list()
        except Exception:
            pass

        self._cleanup_thread()

    def _pipeline_error(self, message):

        self._write_log(f"ERROR : {message}")

        QMessageBox.critical(self, "Pipeline error", message)

        self._cleanup_thread()

    def _pipeline_cancelled(self):

        try:
            self.progress.setValue(0)
        except Exception:
            pass

        self._write_log("Pipeline cancelled.")

        self._cleanup_thread()

    def _cleanup_thread(self):

        try:
            if self._logger_callback:
                Logger.remove_listener(self._logger_callback)
                self._logger_callback = None
        except Exception:
            pass

        try:
            if self.thread:
                self.thread.quit()
                self.thread.wait()
        except Exception:
            pass

        self.thread = None
        self.worker = None
        self.cancel_event = None

        self._set_running(False)

    def _set_running(self, running):

        self.process_button.setEnabled(not running)
        self.cancel_button.setEnabled(running)
        self.destination_button.setEnabled(not running)
        self.tabs.setEnabled(not running)

        for tab in [self.metacritic_tab, self.steam_tab, self.youtube_tab]:

            try:
                tab.set_running(running)
            except Exception:
                pass

    # =============================================================
    # Files
    # =============================================================

    def _open_files(self):

        if self.destination_folder:

            path = Path(self.destination_folder)

            if path.exists():
                os.startfile(path)
                return

            QMessageBox.warning(
                self,
                "Folder not found",
                f"Export folder not found : {path}",
            )

            return

        from core.paths import get_data_directory

        path = get_data_directory()

        if path.exists():
            os.startfile(path)
            return

        QMessageBox.information(
            self,
            "No destination",
            "No export folder selected.",
        )

    # =============================================================
    # Utils
    # =============================================================

    def _write_log(self, message):

        try:
            self.log_signal.emit(message)
        except Exception:
            try:
                self.log_output.append(message)
            except Exception:
                pass
