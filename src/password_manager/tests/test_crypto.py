from password_manager.core import crypto

def test_encrypt_decrypt():
    key = crypto.derive_key("password", crypto.generate_salt())
    msg = b"secret message"
    token = crypto.encrypt(msg, key)
    plain = crypto.decrypt(token, key)
    assert plain == msg
