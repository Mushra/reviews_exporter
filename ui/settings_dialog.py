from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from core.config import get_youtube_api_key, set_youtube_api_key


class SettingsDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("YouTube Data v3 API key")
        title.setProperty("role", "section")
        layout.addWidget(title)

        hint = QLabel(
            "Required to extract comments from YouTube videos.\n"
            "Create a key at console.cloud.google.com (YouTube Data v3 API)."
        )
        hint.setProperty("role", "subtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("AIza...")
        self.key_input.setText(get_youtube_api_key() or "")
        layout.addWidget(self.key_input)

        self.status_label = QLabel()
        self.status_label.setProperty("role", "subtitle")
        layout.addWidget(self.status_label)

        self._refresh_status()

        buttons = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.setProperty("role", "primary")
        save_button.clicked.connect(self._save)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        buttons.addStretch()
        buttons.addWidget(close_button)
        buttons.addWidget(save_button)

        layout.addLayout(buttons)

        self.setLayout(layout)

    def _refresh_status(self):

        if get_youtube_api_key():
            self.status_label.setText("Status : key configured")
        else:
            self.status_label.setText("Status : no key configured")

    def _save(self):

        key = self.key_input.text().strip()

        set_youtube_api_key(key)

        self._refresh_status()

        self.accept()
