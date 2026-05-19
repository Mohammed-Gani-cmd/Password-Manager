from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
import os
from password_manager.core import user_accounts, storage


class AuthWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Password Manager – Sign In")
        self.setFixedSize(360, 250)

        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; }
            QLabel { color: #E0E0E0; font-size: 14px; }
            QLineEdit {
                background-color: #2B2B2B;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3A3A3A;
                border-radius: 6px;
                padding: 6px;
                color: #E0E0E0;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Master Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Sign In")
        self.register_btn = QPushButton("Create Account")
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)

        self.setLayout(layout)

        self.auth_data = None  # (username, master_password, vault_path)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        try:
            user_accounts.verify_user(username, password)
            vault_path = os.path.join(
                os.path.dirname(__file__), "..", f"vault_{username}.pmgr"
            )
            if not os.path.exists(vault_path):
                QMessageBox.warning(self, "Vault Missing", "Vault not found for this user. Please create a new account.")
                return
            self.auth_data = (username, password, vault_path)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        try:
            user_accounts.register_user(username, password)
            vault_path = os.path.join(
                os.path.dirname(__file__), "..", f"vault_{username}.pmgr"
            )
            storage.create_vault(password, vault_path)
            QMessageBox.information(self, "Success", f"Account created for '{username}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
