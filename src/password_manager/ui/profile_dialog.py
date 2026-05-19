from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from password_manager.core import config_manager

class ProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Profile & Settings")
        self.setFixedSize(400, 280)

        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; }
            QLabel { color: #E0E0E0; font-size: 13px; }
            QLineEdit {
                background-color: #2B2B2B;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 4px 8px;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px 12px;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Load existing configuration
        config = config_manager.load_config()

        self.email_input = QLineEdit(config.get("email", ""))
        self.vault_input = QLineEdit(config.get("vault_path", ""))
        self.drive_input = QLineEdit(config.get("drive_link", ""))

        form.addRow("📬 Registered Email:", self.email_input)
        form.addRow("🔐 Vault Path:", self.vault_input)
        form.addRow("☁️ Google Drive Link:", self.drive_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_config(self):
        """Save the updated user configuration."""
        new_data = {
            "email": self.email_input.text(),
            "vault_path": self.vault_input.text(),
            "drive_link": self.drive_input.text(),
        }
        config_manager.save_config(new_data)
        QMessageBox.information(self, "Saved", "✅ Configuration updated successfully!")
        self.accept()
