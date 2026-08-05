import re

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from PySide6.QtCore import Qt, QTimer

from core.steam_api import search_apps
from pipeline.runner import run_steam_pipeline


def slugify(value: str) -> str:

    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)

    return value.strip("-") or "steam-game"


class SteamTab(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.selected_app = None
        self._suppress_search = False

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._execute_search)

        self._build_ui()

    # -----------------------------------------------------------
    # UI
    # -----------------------------------------------------------

    def _build_ui(self):

        layout = QVBoxLayout()
        layout.setSpacing(10)

        section = QLabel("Game search")
        section.setProperty("role", "section")
        layout.addWidget(section)

        self.game_input = QLineEdit()
        self.game_input.setPlaceholderText("Search a game on Steam...")
        self.game_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.game_input)

        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(130)
        self.results_list.itemClicked.connect(self._select_app)
        self.results_list.setVisible(False)
        layout.addWidget(self.results_list)

        self.selected_label = QLabel("No game selected")
        self.selected_label.setProperty("role", "subtitle")
        layout.addWidget(self.selected_label)

        section2 = QLabel("Operations")
        section2.setProperty("role", "section")
        layout.addWidget(section2)

        self.extract_reviews = QCheckBox("Extract all Steam reviews")
        self.process_reviews = QCheckBox("Process Steam reviews")

        for checkbox in [self.extract_reviews, self.process_reviews]:
            checkbox.setChecked(True)
            layout.addWidget(checkbox)

        note = QLabel(
            "Extraction fetches every available review via the public "
            "Steam API (can take a while for large games)."
        )
        note.setProperty("role", "subtitle")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()

        self.setLayout(layout)

    # -----------------------------------------------------------
    # Search
    # -----------------------------------------------------------

    def _hide_results(self):

        self.results_list.setVisible(False)
        QTimer.singleShot(0, self.results_list.clear)

    def _on_search_text_changed(self, text):

        if self._suppress_search:
            return

        self.search_timer.stop()

        if len(text.strip()) < 2:
            self._hide_results()
            return

        self.search_timer.start(400)

    def _execute_search(self):

        text = self.game_input.text().strip()

        try:

            results = search_apps(text)

            self.results_list.clear()

            for app in results:

                item = QListWidgetItem(app["title"])
                item.setData(Qt.UserRole, app)

                self.results_list.addItem(item)

            self.results_list.setVisible(bool(results))

        except Exception as error:

            self._hide_results()

            QMessageBox.warning(self, "Search failed", str(error))

    def _select_app(self, item):

        self.selected_app = item.data(Qt.UserRole)

        self.search_timer.stop()

        self._suppress_search = True
        self.game_input.setText(self.selected_app["title"])
        self._suppress_search = False

        self._hide_results()
        self.game_input.clearFocus()

        self.selected_label.setText(f"Selected : {self.selected_app['title']}")

    # -----------------------------------------------------------
    # Pipeline request
    # -----------------------------------------------------------

    def get_request(self, destination_folder):

        if not self.selected_app:

            QMessageBox.warning(self, "Missing game", "Please select a Steam game.")

            return None

        game_slug = slugify(self.selected_app["title"])

        kwargs = {
            "game": game_slug,
            "appid": self.selected_app["appid"],
            "extract": self.extract_reviews.isChecked(),
            "process": self.process_reviews.isChecked(),
            "destination_folder": destination_folder,
        }

        return {"func": run_steam_pipeline, "kwargs": kwargs, "game": game_slug}

    def set_running(self, running):

        self.game_input.setEnabled(not running)
        self.results_list.setEnabled(not running)
        self.extract_reviews.setEnabled(not running)
        self.process_reviews.setEnabled(not running)
