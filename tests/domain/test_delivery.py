from bot.modules.security.inventory_crypto import InventoryCipher
from bot.services.delivery import build_delivery_snapshot, decrypt_delivery_snapshot


def test_inventory_cipher_roundtrips_sensitive_content_without_plaintext_storage() -> None:
    cipher = InventoryCipher("test-secret")
    encrypted = cipher.encrypt("login:password")

    assert encrypted != "login:password"
    assert cipher.decrypt(encrypted) == "login:password"


def test_delivery_snapshot_keeps_encrypted_text_and_can_be_decrypted_for_display() -> None:
    cipher = InventoryCipher("test-secret")
    encrypted = cipher.encrypt("login:password")

    snapshot = build_delivery_snapshot(encrypted_inventory_content=encrypted)

    assert snapshot.encrypted_text == encrypted
    assert decrypt_delivery_snapshot(encrypted_text=snapshot.encrypted_text, cipher=cipher) == "login:password"
    assert snapshot.delivered_at is not None
