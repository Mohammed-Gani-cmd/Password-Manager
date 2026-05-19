import tempfile, os
from password_manager.core import storage

def test_vault_cycle():
    pw = "master123"
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "vault.pmgr")
        storage.create_vault(pw, path)
        storage.add_entry(pw, path, {"title": "Test", "username": "user", "password": "pass"})
        entries = storage.list_entries(pw, path)
        assert entries[0]["title"] == "Test"
