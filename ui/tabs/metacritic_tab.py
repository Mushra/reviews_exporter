from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from PySide6.QtCore import Qt, QTimer

from services.metacritic_search import search_games
from core.api import fetch_game_platforms
from pipeline.runner import run_pipeline


class MetacriticTab(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.selected_game = None
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
        self.game_input.setPlaceholderText("Search a game on Metacritic...")
        self.game_input.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self.game_input)

        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(130)
        self.results_list.itemClicked.connect(self._select_game)
        self.results_list.setVisible(False)
        layout.addWidget(self.results_list)

        self.selected_label = QLabel("No game selected")
        self.selected_label.setProperty("role", "subtitle")
        layout.addWidget(self.selected_label)

        platform_row = QHBoxLayout()
        platform_row.addWidget(QLabel("Platform"))

        self.platform_box = QComboBox()
        self.platform_box.addItem("all platform")
        self.platform_box.setEnabled(False)
        platform_row.addWidget(self.platform_box)
        platform_row.addStretch()

        layout.addLayout(platform_row)

        section2 = QLabel("Operations")
        section2.setProperty("role", "section")
        layout.addWidget(section2)

        self.extract_user = QCheckBox("Extract user reviews")
        self.extract_critic = QCheckBox("Extract critic reviews")
        self.process_user = QCheckBox("Process user reviews")
        self.process_critic = QCheckBox("Process critic reviews")

        for checkbox in [
            self.extract_user,
            self.extract_critic,
            self.process_user,
            self.process_critic,
        ]:
            checkbox.setChecked(True)
            layout.addWidget(checkbox)

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

            results = search_games(text)

            self.results_list.clear()

            for game in results:

                item = QListWidgetItem(f"{game['title']} ({game['slug']})")
                item.setData(Qt.UserRole, game)

                self.results_list.addItem(item)

            self.results_list.setVisible(bool(results))

        except Exception as error:

            self._hide_results()

            QMessageBox.warning(self, "Search failed", str(error))

    def _select_game(self, item):

        self.selected_game = item.data(Qt.UserRole)

        self.search_timer.stop()

        self._suppress_search = True
        self.game_input.setText(self.selected_game["title"])
        self._suppress_search = False

        self._hide_results()
        self.game_input.clearFocus()

        self.selected_label.setText(f"Selected : {self.selected_game['title']}")

        self._refresh_platforms()

    # -----------------------------------------------------------
    # Platform discovery
    # -----------------------------------------------------------

    def _refresh_platforms(self):

        self.platform_box.clear()
        self.platform_box.addItem("all platform")
        self.platform_box.setEnabled(False)

        if not self.selected_game:
            return

        try:

            platforms = fetch_game_platforms(self.selected_game["slug"])

        except Exception as error:

            QMessageBox.warning(self, "Platform discovery failed", str(error))

            platforms = []

        for platform in platforms:

            self.platform_box.addItem(
                platform.get("name") or platform["slug"],
                platform["slug"],
            )

        self.platform_box.setEnabled(True)

    # -----------------------------------------------------------
    # Pipeline request
    # -----------------------------------------------------------

    def get_request(self, destination_folder):

        if not self.selected_game:

            QMessageBox.warning(self, "Missing game", "Please select a game.")

            return None

        platform = self.platform_box.currentData() or self.platform_box.currentText()

        kwargs = {
            "game": self.selected_game["slug"],
            "platform": platform,
            "extract_user": self.extract_user.isChecked(),
            "extract_critic": self.extract_critic.isChecked(),
            "process_user": self.process_user.isChecked(),
            "process_critic": self.process_critic.isChecked(),
            "destination_folder": destination_folder,
        }

        return {"func": run_pipeline, "kwargs": kwargs, "game": self.selected_game["slug"]}

    def set_running(self, running):

        self.game_input.setEnabled(not running)
        self.results_list.setEnabled(not running)
        self.platform_box.setEnabled(not running)

        for checkbox in [
            self.extract_user,
            self.extract_critic,
            self.process_user,
            self.process_critic,
        ]:
            checkbox.setEnabled(not running)
