"""Encryption & Decryption Adapter for Secure Patient Data Communication.

Demonstrates authenticated symmetric encryption (AES-128-CBC + HMAC-SHA256 via Fernet)
to ensure confidentiality, integrity, and authenticity of clinical messages.

Academic Disclaimer:
Standard cryptography library is utilized. This demonstration proves networking
and security concepts in a clinical topology. Never deploy demo keys in production.
"""

import base64
import os
from typing import Tuple, Optional

try:
    from modules.base_adapter import BaseProtocolAdapter, AdapterStatus
except (ImportError, ValueError):
    try:
        from .base_adapter import BaseProtocolAdapter, AdapterStatus
    except (ImportError, ValueError):
        from base_adapter import BaseProtocolAdapter, AdapterStatus

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    Fernet = None
    InvalidToken = Exception


class EncryptionAdapter(BaseProtocolAdapter):
    """Adapter managing encryption/decryption of patient data frames."""

    def __init__(self):
        super().__init__(
            protocol_name="Encryption & Decryption",
            candidate_modules=["encryption.cipher", "modules.encryption", "encryption"]
        )
        self.key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None
        self.generate_new_key()

    def generate_new_key(self) -> bytes:
        """Generate a fresh 256-bit key for authenticated symmetric encryption."""
        if HAS_CRYPTOGRAPHY:
            self.key = Fernet.generate_key()
            self._fernet = Fernet(self.key)
        else:
            # Fallback mock key if cryptography library is unavailable
            self.key = base64.urlsafe_b64encode(os.urandom(32))
            self._fernet = None
        return self.key

    def set_key(self, key_bytes: bytes):
        """Set a specific key."""
        self.key = key_bytes
        if HAS_CRYPTOGRAPHY:
            self._fernet = Fernet(key_bytes)

    def encrypt_payload(self, plaintext: str) -> Tuple[bytes, str]:
        """
        Encrypt patient plaintext using authenticated cipher.
        Returns:
            Tuple of (ciphertext_bytes, algorithm_info_string)
        """
        # If teammate module is integrated and has an encrypt method, try it
        if self.status == AdapterStatus.TEAMMATE_INTEGRATED and hasattr(self.external_instance, "encrypt"):
            try:
                res = self.external_instance.encrypt(plaintext, self.key)
                return (res if isinstance(res, bytes) else str(res).encode(), "Teammate AES Module")
            except Exception:
                pass

        # Reference authenticated implementation using Fernet
        if HAS_CRYPTOGRAPHY and self._fernet:
            token = self._fernet.encrypt(plaintext.encode("utf-8"))
            return (token, "Fernet (AES-128-CBC + HMAC-SHA256)")
        else:
            # Simple fallback base64 encoding (clearly labeled as unauthenticated mock)
            encoded = base64.b64encode(plaintext.encode("utf-8"))
            return (encoded, "Fallback Mock (Base64 - Academic Demonstration Only)")

    def decrypt_payload(self, ciphertext: bytes) -> Tuple[Optional[str], bool, str]:
        """
        Decrypt ciphertext and verify cryptographic authentication tag.
        Returns:
            Tuple of (decrypted_plaintext, is_authentic_bool, status_message)
        """
        if self.status == AdapterStatus.TEAMMATE_INTEGRATED and hasattr(self.external_instance, "decrypt"):
            try:
                res = self.external_instance.decrypt(ciphertext, self.key)
                return (str(res), True, "Teammate Decryption Successful")
            except Exception as e:
                return (None, False, f"Teammate Decryption Failed: {e}")

        if HAS_CRYPTOGRAPHY and self._fernet:
            try:
                decrypted = self._fernet.decrypt(ciphertext)
                return (decrypted.decode("utf-8"), True, "Authentication & Decryption Verified (HMAC Valid)")
            except InvalidToken:
                return (None, False, "Decryption Failed: Tampered or Corrupted Ciphertext (HMAC Invalid)")
            except Exception as e:
                return (None, False, f"Decryption Error: {str(e)}")
        else:
            try:
                decrypted = base64.b64decode(ciphertext).decode("utf-8")
                return (decrypted, True, "Mock Fallback Decoded")
            except Exception as e:
                return (None, False, f"Mock Decode Error: {e}")

    def tamper_ciphertext(self, ciphertext: bytes) -> bytes:
        """
        Deliberately flip a byte in the ciphertext to simulate man-in-the-middle
        or transmission corruption to demonstrate HMAC authentication rejection.
        """
        if not ciphertext or len(ciphertext) < 10:
            return ciphertext
        byte_list = bytearray(ciphertext)
        # Flip bit in the middle of ciphertext
        target_idx = len(byte_list) // 2
        byte_list[target_idx] ^= 0x55
        return bytes(byte_list)

    def mask_sensitive_payload(self, raw_text: str) -> str:
        """Sanitize sensitive plaintext preview for transmission logs."""
        if len(raw_text) <= 16:
            return "[PROTECTED PAYLOAD]"
        return f"[PROTECTED PAYLOAD: {len(raw_text)} chars - Encrypted at Source]"
