import re

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from core.config import get_youtube_api_key
from core.youtube_api import parse_video_id
from core.filesystem import list_existing_projects
from pipeline.runner import run_youtube_pipeline


def slugify(value: str) -> str:

    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-") or "youtube-project"


class YoutubeTab(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.video_urls = []

        self._build_ui()

    # -----------------------------------------------------------
    # UI
    # -----------------------------------------------------------

    def _build_ui(self):

        layout = QVBoxLayout()
        layout.setSpacing(10)

        section = QLabel("Project")
        section.setProperty("role", "section")
        layout.addWidget(section)

        self.project_input = QComboBox()
        self.project_input.setEditable(True)
        self.project_input.lineEdit().setPlaceholderText(
            "New project name (e.g. elden-ring-youtube)"
        )
        layout.addWidget(self.project_input)

        project_hint = QLabel(
            "Pick an existing project to add more videos to it, or type a "
            "new name to start one. This only groups the raw/processed data "
            "internally — it's separate from the export folder below."
        )
        project_hint.setProperty("role", "subtitle")
        project_hint.setWordWrap(True)
        layout.addWidget(project_hint)

        self.refresh_project_list()

        section2 = QLabel("Cherry-picked videos")
        section2.setProperty("role", "section")
        layout.addWidget(section2)

        add_row = QHBoxLayout()

        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Paste a YouTube URL or ID...")
        self.video_input.returnPressed.connect(self._add_video)

        add_button = QPushButton("Add")
        add_button.setProperty("role", "primary")
        add_button.clicked.connect(self._add_video)

        add_row.addWidget(self.video_input)
        add_row.addWidget(add_button)

        layout.addLayout(add_row)

        self.video_list = QListWidget()
        self.video_list.setMaximumHeight(150)
        layout.addWidget(self.video_list)

        remove_button = QPushButton("Remove selection")
        remove_button.clicked.connect(self._remove_selected)
        layout.addWidget(remove_button)

        section3 = QLabel("Operations")
        section3.setProperty("role", "section")
        layout.addWidget(section3)

        self.extract_comments = QCheckBox("Extract comments")
        self.process_comments = QCheckBox("Process comments")

        for checkbox in [self.extract_comments, self.process_comments]:
            checkbox.setChecked(True)
            layout.addWidget(checkbox)

        self.extract_transcripts = QCheckBox("Extract transcripts")
        self.process_transcripts = QCheckBox("Process transcripts")

        for checkbox in [self.extract_transcripts, self.process_transcripts]:
            checkbox.setChecked(False)
            layout.addWidget(checkbox)

        self.key_status = QLabel()
        self.key_status.setProperty("role", "subtitle")
        layout.addWidget(self.key_status)

        self.refresh_key_status()

        layout.addStretch()

        self.setLayout(layout)

    # -----------------------------------------------------------
    # Project selection
    # -----------------------------------------------------------

    def refresh_project_list(self):

        current = self.project_input.currentText()

        self.project_input.blockSignals(True)

        self.project_input.clear()
        self.project_input.addItems(list_existing_projects())

        self.project_input.setCurrentText(current)

        self.project_input.blockSignals(False)

    # -----------------------------------------------------------
    # Video list management
    # -----------------------------------------------------------

    def _add_video(self):

        text = self.video_input.text().strip()

        if not text:
            return

        video_id = parse_video_id(text)

        if not video_id:

            QMessageBox.warning(
                self,
                "Invalid URL",
                "Unrecognized YouTube URL or ID.",
            )

            return

        if text in self.video_urls:

            self.video_input.clear()

            return

        self.video_urls.append(text)

        item = QListWidgetItem(f"{text}  →  {video_id}")

        self.video_list.addItem(item)

        self.video_input.clear()

    def _remove_selected(self):

        for item in self.video_list.selectedItems():

            row = self.video_list.row(item)

            self.video_list.takeItem(row)

            del self.video_urls[row]

    # -----------------------------------------------------------
    # Settings
    # -----------------------------------------------------------

    def refresh_key_status(self):

        if get_youtube_api_key():
            self.key_status.setText("YouTube API key : configured")
        else:
            self.key_status.setText(
                "YouTube API key : not configured (see Settings ⚙)"
            )

    # -----------------------------------------------------------
    # Pipeline request
    # -----------------------------------------------------------

    def get_request(self, destination_folder):

        project = self.project_input.currentText().strip()

        if not project:

            QMessageBox.warning(
                self,
                "Missing project name",
                "Please enter a project name.",
            )

            return None

        if not self.video_urls:

            QMessageBox.warning(
                self,
                "No video",
                "Please add at least one YouTube video.",
            )

            return None

        api_key = get_youtube_api_key()

        if not api_key:

            QMessageBox.warning(
                self,
                "Missing API key",
                "Configure your YouTube API key in Settings ⚙.",
            )

            return None

        game_slug = project if project in list_existing_projects() else slugify(project)

        kwargs = {
            "game": game_slug,
            "video_urls": list(self.video_urls),
            "api_key": api_key,
            "extract": self.extract_comments.isChecked(),
            "process": self.process_comments.isChecked(),
            "extract_transcripts": self.extract_transcripts.isChecked(),
            "process_transcripts": self.process_transcripts.isChecked(),
            "destination_folder": destination_folder,
        }

        return {"func": run_youtube_pipeline, "kwargs": kwargs, "game": game_slug}

    def set_running(self, running):

        self.project_input.setEnabled(not running)
        self.video_input.setEnabled(not running)
        self.video_list.setEnabled(not running)
        self.extract_comments.setEnabled(not running)
        self.process_comments.setEnabled(not running)
        self.extract_transcripts.setEnabled(not running)
        self.process_transcripts.setEnabled(not running)
