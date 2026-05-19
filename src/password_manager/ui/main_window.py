from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QToolBar, QPushButton, QVBoxLayout, QWidget, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from password_manager.ui.dialogs import AddEntryDialog, EditEntryDialog
from password_manager.ui.profile_dialog import ProfileDialog  # ✅ New
from password_manager.core import storage, google_sync, email_otp, config_manager  # ✅ Combined imports


class VaultMainWindow(QMainWindow):
    def __init__(self, master_password, vault_path):
        super().__init__()
        self.master_password = master_password
        self.vault_path = vault_path

        self.setWindowTitle("🔐 Password Manager Vault")
        self.resize(750, 400)

        self.revealed_row = None

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Username", "Password", "Notes"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)

        self.table.cellDoubleClicked.connect(self.handle_double_click)

        # ---- Toolbar ----
        toolbar = QToolBar()
        add_btn = QPushButton("➕ Add Entry")
        add_btn.clicked.connect(self.add_entry)
        delete_btn = QPushButton("🗑️ Delete Entry")
        delete_btn.clicked.connect(self.delete_entry)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_vault)
        profile_btn = QPushButton("⚙️ Profile")
        profile_btn.clicked.connect(self.open_profile)
        logout_btn = QPushButton("🚪 Log Out")
        logout_btn.clicked.connect(self.logout)

        toolbar.addWidget(add_btn)
        toolbar.addWidget(delete_btn)
        toolbar.addWidget(refresh_btn)
        toolbar.addWidget(profile_btn)
        toolbar.addWidget(logout_btn)

        # ---- Layout ----
        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.statusBar().showMessage("🔐 Vault unlocked")
        self.load_vault()

    # ========================================
    # 📂 VAULT MANAGEMENT
    # ========================================

    def load_vault(self):
        """Decrypt and display all vault entries."""
        try:
            self.entries = storage.list_entries(self.master_password, self.vault_path)
            self.table.setRowCount(len(self.entries))
            for row, entry in enumerate(self.entries):
                self.table.setItem(row, 0, QTableWidgetItem(entry.get("title", "")))
                self.table.setItem(row, 1, QTableWidgetItem(entry.get("username", "")))
                masked = "•" * len(entry.get("password", ""))
                self.table.setItem(row, 2, QTableWidgetItem(masked))
                self.table.setItem(row, 3, QTableWidgetItem(entry.get("notes", "")))
            self.statusBar().showMessage(f"✅ Loaded {len(self.entries)} entries")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load vault:\n{e}")

    def handle_double_click(self, row, column):
        """Reveal password or open edit dialog."""
        if column == 2:
            self.toggle_password_visibility(row)
        else:
            self.edit_entry(row)

    def toggle_password_visibility(self, row):
        """Reveal or hide the password when double-clicked."""
        if self.revealed_row == row:
            masked = "•" * len(self.entries[row].get("password", ""))
            self.table.item(row, 2).setText(masked)
            self.revealed_row = None
            self.statusBar().showMessage("🙈 Password hidden")
        else:
            real_pwd = self.entries[row].get("password", "")
            self.table.item(row, 2).setText(real_pwd)
            self.revealed_row = row
            self.statusBar().showMessage("👁️ Password revealed (double-click to hide)")

    # ========================================
    # ➕ ADD ENTRY
    # ========================================

    def add_entry(self):
        """Open dialog to add new entry and refresh table."""
        dialog = AddEntryDialog(self)
        if dialog.exec() == 1:
            entry = dialog.get_entry()
            try:
                storage.add_entry(self.master_password, self.vault_path, entry)
                self.statusBar().showMessage(f"✅ Added entry: {entry['title']}")
                self.load_vault()

                # ☁️ Upload to Google Drive
                try:
                    google_sync.upload_vault(self.vault_path)
                    print("☁️ Vault synced to Google Drive (add entry).")
                except Exception as e:
                    print(f"⚠️ Failed to sync vault after adding: {e}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add entry:\n{e}")

    # ========================================
    # ✏️ EDIT ENTRY (with Email OTP)
    # ========================================

    def edit_entry(self, row):
        """Open dialog to edit an existing entry, secured by stored email OTP."""
        entry = self.entries[row]

        # ✅ Load stored email from config
        config = config_manager.load_config()
        email = config.get("email", "")
        if not email:
            QMessageBox.warning(self, "No Email Found", "Please set your registered email in Profile settings first.")
            return

        # ✅ Send OTP
        sent_otp = email_otp.send_otp_email(email)
        if not sent_otp:
            QMessageBox.critical(self, "Error", "Failed to send OTP. Please try again.")
            return

        # ✅ Verify OTP
        user_otp, ok = QInputDialog.getText(self, "OTP Verification", f"Enter OTP sent to {email}:")
        if not ok or user_otp != sent_otp:
            QMessageBox.critical(self, "Invalid OTP", "Incorrect OTP entered.")
            return

        # ✅ Proceed if verified
        dialog = EditEntryDialog(entry, self)
        if dialog.exec() == 1:
            new_entry = dialog.get_updated_entry()
            try:
                storage.update_entry(self.master_password, self.vault_path, row, new_entry)
                self.statusBar().showMessage(f"✏️ Edited entry: {entry.get('title', '')}")
                self.load_vault()

                # ☁️ Upload to Google Drive
                try:
                    google_sync.upload_vault(self.vault_path)
                    print("☁️ Vault synced to Google Drive (edit entry).")
                except Exception as e:
                    print(f"⚠️ Failed to sync vault after editing: {e}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update entry:\n{e}")

    # ========================================
    # 🗑️ DELETE ENTRY (with Email OTP)
    # ========================================

    def delete_entry(self):
        """Delete the selected entry, secured by stored email OTP."""
        self.load_vault()
        selected = self.table.currentRow()

        if selected == -1 or selected >= len(self.entries):
            QMessageBox.warning(self, "No Selection", "Please select a valid entry to delete.")
            return

        # ✅ Load stored email
        config = config_manager.load_config()
        email = config.get("email", "")
        if not email:
            QMessageBox.warning(self, "No Email Found", "Please set your registered email in Profile settings first.")
            return

        # ✅ Send OTP
        sent_otp = email_otp.send_otp_email(email)
        if not sent_otp:
            QMessageBox.critical(self, "Error", "Failed to send OTP. Please try again.")
            return

        # ✅ Verify OTP
        user_otp, ok = QInputDialog.getText(self, "OTP Verification", f"Enter OTP sent to {email}:")
        if not ok or user_otp != sent_otp:
            QMessageBox.critical(self, "Invalid OTP", "Incorrect OTP entered.")
            return

        # ✅ Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{self.entries[selected].get('title', '')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                storage.delete_entry(self.master_password, self.vault_path, selected)
                self.statusBar().showMessage("🗑️ Entry deleted")
                self.load_vault()

                # ☁️ Upload to Google Drive
                try:
                    google_sync.upload_vault(self.vault_path)
                    print("☁️ Vault synced to Google Drive (delete entry).")
                except Exception as e:
                    print(f"⚠️ Failed to sync vault after deleting: {e}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete entry:\n{e}")

    # ========================================
    # ⚙️ PROFILE & LOGOUT
    # ========================================

    def open_profile(self):
        """Open the user profile/settings dialog."""
        dialog = ProfileDialog(self)
        dialog.exec()

    def logout(self):
        """Logout from Google account and close the app."""
        confirm = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to log out of Google and exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                google_sync.logout_google()
                self.statusBar().showMessage("🚪 Logged out from Google")
                print("✅ Logout completed. Closing app...")
            except Exception as e:
                print(f"⚠️ Logout failed: {e}")
            self.close()
