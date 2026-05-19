import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from password_manager.ui.main_window import VaultMainWindow
from password_manager.ui.dialogs import LoginDialog
from password_manager.core import storage, totp, google_sync


def main():
    print("🚀 Starting Password Manager with MFA + Google Drive Sync...")

    app = QApplication(sys.argv)

    # --- 🖌️ Load Dark Theme ---
    theme_path = os.path.join(os.path.dirname(__file__), "ui", "theme.qss")
    if os.path.exists(theme_path):
        try:
            with open(theme_path, "r") as f:
                app.setStyleSheet(f.read())
            print("🎨 Dark theme loaded successfully.")
        except Exception as e:
            print(f"⚠️ Failed to load theme: {e}")
    else:
        print("⚠️ Theme file not found — using default style.")

    # --- 🔒 App Icon (optional) ---
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "lock.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print("🔒 App icon loaded.")
    else:
        print("⚠️ No icon found (optional).")

    # --- 🪪 LOGIN DIALOG ---
    print("🪪 Opening LoginDialog...")
    login = LoginDialog()
    login.show()
    if login.exec() != 1:
        print("❌ Login canceled. Exiting.")
        sys.exit(0)

    master_password, vault_path, totp_code = login.get_credentials()
    print(f"🔑 Vault path: {vault_path}")

    # --- 🔓 VERIFY MASTER PASSWORD ---
    try:
        vault_data, salt, key = storage._load_vault(master_password, vault_path)
        print("✅ Master password verified.")
    except Exception as e:
        print(f"❌ Invalid master password: {e}")
        QMessageBox.critical(None, "Error", f"Invalid master password.\n{e}")
        sys.exit(1)

    # --- 🔐 VERIFY TOTP CODE ---
    mfa_secret = vault_data.get("mfa_secret")
    if mfa_secret:
        print("🔍 Checking TOTP code...")
        if not totp.verify_code(mfa_secret, totp_code):
            print("❌ Invalid or missing TOTP code.")
            QMessageBox.critical(None, "Error", "Invalid or missing TOTP code.")
            sys.exit(1)
        print("✅ MFA verification passed.")
    else:
        print("⚠️ No MFA enabled for this vault (proceeding without).")

    # --- ☁️ GOOGLE DRIVE SYNC (Download latest vault before opening) ---
    try:
        if os.path.exists(vault_path):
            print("☁️ Checking Google Drive for updated vault...")
            google_sync.download_vault(vault_path)
        else:
            print("🆕 No local vault found, checking Google Drive...")
            if not google_sync.download_vault(vault_path):
                print("📦 No existing Drive vault found, starting fresh.")
        print("✅ Google Drive sync (download) completed.")
    except Exception as e:
        print(f"⚠️ Google Drive sync failed: {e}")

    # --- 🪟 OPEN MAIN WINDOW ---
    print("🪟 Launching vault window...")
    window = VaultMainWindow(master_password, vault_path)
    window.show()
    print("✅ GUI initialized. Entering event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
