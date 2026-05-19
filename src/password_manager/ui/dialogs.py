from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QFormLayout,
    QDialogButtonBox, QPushButton, QMessageBox, QHBoxLayout, QLabel
)
from password_manager.core import pwgen


# ===============================
# 🔐 Login Dialog (with MFA)
# ===============================

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unlock Vault")
        self.setFixedSize(320, 240)

        # ---- Dark Style ----
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
                padding: 5px 10px;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.path_input = QLineEdit("vault.pmgr")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.totp_input = QLineEdit()
        self.totp_input.setMaxLength(6)
        self.totp_input.setPlaceholderText("6-digit code")

        form.addRow("Vault Path:", self.path_input)
        form.addRow("Master Password:", self.password_input)
        form.addRow("TOTP Code:", self.totp_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_credentials(self):
        return (
            self.password_input.text(),
            self.path_input.text(),
            self.totp_input.text()
        )


# ===============================
# ➕ Add Entry Dialog (with Password Generator)
# ===============================

class AddEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Entry")
        self.setFixedSize(350, 280)

        # ---- Dark Theme ----
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
                padding: 5px 10px;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.title = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.notes = QLineEdit()

        # 🧮 Password generator button beside password field
        gen_btn_layout = QHBoxLayout()
        gen_btn = QPushButton("🔐 Generate Password")
        gen_btn.clicked.connect(self.generate_password)
        gen_btn_layout.addWidget(self.password)
        gen_btn_layout.addWidget(gen_btn)

        form.addRow("Title:", self.title)
        form.addRow("Username:", self.username)
        form.addRow("Password:", gen_btn_layout)
        form.addRow("Notes:", self.notes)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addLayout(form)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def generate_password(self):
        """Generate a new strong password and set it in the field."""
        try:
            pwd = pwgen.generate_password(
                length=16,
                use_upper=True,
                use_lower=True,
                use_digits=True,
                use_symbols=True
            )
            self.password.setText(pwd)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def get_entry(self):
        """Return entry data as a dictionary."""
        return {
            "title": self.title.text(),
            "username": self.username.text(),
            "password": self.password.text(),
            "notes": self.notes.text(),
        }


# ===============================
# ✏️ Edit Entry Dialog
# ===============================

class EditEntryDialog(QDialog):
    def __init__(self, entry_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Entry")
        self.setFixedSize(350, 280)

        # ---- Dark Theme ----
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
                padding: 5px 10px;
                color: #E0E0E0;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Pre-fill with existing data
        self.title = QLineEdit(entry_data.get("title", ""))
        self.username = QLineEdit(entry_data.get("username", ""))
        self.password = QLineEdit(entry_data.get("password", ""))
        self.notes = QLineEdit(entry_data.get("notes", ""))

        form.addRow("Title:", self.title)
        form.addRow("Username:", self.username)
        form.addRow("Password:", self.password)
        form.addRow("Notes:", self.notes)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addLayout(form)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

    def get_updated_entry(self):
        """Return updated entry values as a dictionary."""
        return {
            "title": self.title.text(),
            "username": self.username.text(),
            "password": self.password.text(),
            "notes": self.notes.text(),
        }
