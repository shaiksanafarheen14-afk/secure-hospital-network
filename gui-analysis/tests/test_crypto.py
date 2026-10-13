"""Unit tests for authenticated encryption, decryption, and tamper detection."""

import unittest
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.encryption_adapter import EncryptionAdapter


class TestEncryptionAdapter(unittest.TestCase):
    """Test cryptographic guarantees: confidentiality, authentication, and tamper rejection."""

    def setUp(self):
        self.adapter = EncryptionAdapter()

    def test_encrypt_and_decrypt_clean(self):
        payload = '{"patient_id": "SYN-101", "heart_rate": 80, "condition": "Normal"}'
        ciphertext, algo = self.adapter.encrypt_payload(payload)

        self.assertIsInstance(ciphertext, bytes)
        self.assertNotEqual(ciphertext, payload.encode("utf-8"))
        self.assertIn("Fernet", algo)

        decrypted, is_valid, msg = self.adapter.decrypt_payload(ciphertext)
        self.assertTrue(is_valid)
        self.assertEqual(decrypted, payload)

    def test_tamper_detection(self):
        payload = '{"patient_id": "SYN-101", "heart_rate": 80}'
        ciphertext, _ = self.adapter.encrypt_payload(payload)

        # Invert bit in ciphertext to simulate channel corruption or MITM attack
        tampered_ciphertext = self.adapter.tamper_ciphertext(ciphertext)
        self.assertNotEqual(tampered_ciphertext, ciphertext)

        # Receiver must reject tampered ciphertext
        decrypted, is_valid, msg = self.adapter.decrypt_payload(tampered_ciphertext)
        self.assertFalse(is_valid)
        self.assertIsNone(decrypted)
        self.assertIn("Tampered", msg)

    def test_key_rotation(self):
        old_key = self.adapter.key
        new_key = self.adapter.generate_new_key()
        self.assertNotEqual(old_key, new_key)

    def test_masking_sensitive_payload(self):
        long_text = "Highly Confidential Patient Medical Record - Diabetes Type 2"
        masked = self.adapter.mask_sensitive_payload(long_text)
        self.assertNotIn("Diabetes", masked)
        self.assertIn("PROTECTED PAYLOAD", masked)


if __name__ == "__main__":
    unittest.main()
