"""Cyclic Redundancy Check (CRC) Error Detection Adapter.

Implements standard network error detection:
- CRC-16-CCITT (Polynomial 0x1021)
- CRC-32 (IEEE 802.3 Ethernet standard)
- Step-by-step bitwise modulo-2 division demonstration
- Intentional bit corruption injection to test error detection
"""

import binascii
from typing import Tuple, Dict, Any

try:
    from modules.base_adapter import BaseProtocolAdapter, AdapterStatus
except (ImportError, ValueError):
    try:
        from .base_adapter import BaseProtocolAdapter, AdapterStatus
    except (ImportError, ValueError):
        from base_adapter import BaseProtocolAdapter, AdapterStatus


class CRCAdapter(BaseProtocolAdapter):
    """Adapter managing CRC computation, verification, and error injection."""

    # Standard polynomial definitions
    POLYNOMIALS = {
        "CRC-16-CCITT": 0x1021,
        "CRC-32": 0xEDB88320
    }

    def __init__(self):
        super().__init__(
            protocol_name="CRC Error Detection",
            candidate_modules=["crc.checker", "modules.crc", "crc"]
        )

    def compute_crc16(self, data: bytes) -> int:
        """Calculate 16-bit CRC-CCITT (polynomial 0x1021, init 0xFFFF)."""
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    def compute_crc32(self, data: bytes) -> int:
        """Calculate standard 32-bit CRC (IEEE 802.3)."""
        return binascii.crc32(data) & 0xFFFFFFFF

    def compute_checksum(self, data: bytes, algorithm: str = "CRC-16") -> str:
        """
        Compute hex string representation of the chosen CRC algorithm.
        Returns formatted hex e.g. '0x3F1A'
        """
        # If teammate module is integrated, attempt call
        if self.status == AdapterStatus.TEAMMATE_INTEGRATED and hasattr(self.external_instance, "calculate_crc"):
            try:
                res = self.external_instance.calculate_crc(data)
                return hex(res) if isinstance(res, int) else str(res)
            except Exception:
                pass

        if algorithm.upper() == "CRC-32":
            val = self.compute_crc32(data)
            return f"0x{val:08X}"
        else:
            val = self.compute_crc16(data)
            return f"0x{val:04X}"

    def verify_checksum(self, data: bytes, expected_crc_hex: str, algorithm: str = "CRC-16") -> bool:
        """Check if received data matches expected CRC."""
        computed = self.compute_checksum(data, algorithm)
        return computed.strip().upper() == expected_crc_hex.strip().upper()

    def inject_bit_error(self, data: bytes, byte_offset: int = 0, bit_pos: int = 0) -> bytes:
        """
        Invert a single bit in data bytes to simulate physical layer noise.
        """
        if not data:
            return b"\x01"
        barr = bytearray(data)
        safe_offset = byte_offset % len(barr)
        safe_bit = bit_pos % 8
        barr[safe_offset] ^= (1 << safe_bit)
        return bytes(barr)

    def step_by_step_modulo2_division(
        self, data_bits: str = "1101011011", generator: str = "10011"
    ) -> Dict[str, Any]:
        """
        Performs step-by-step bitwise XOR long division (modulo-2 arithmetic).
        Used for educational demonstration of CRC encoding:
        Appends (len(generator) - 1) zeros to data, then divides by generator.
        """
        clean_data = "".join(b for b in data_bits if b in ("0", "1"))
        clean_gen = "".join(b for b in generator if b in ("0", "1"))
        if not clean_data:
            clean_data = "110101"
        if not clean_gen:
            clean_gen = "10011"

        k = len(clean_gen) - 1
        augmented_data = clean_data + ("0" * k)

        steps = []
        rem = list(augmented_data)
        gen = list(clean_gen)
        n = len(rem)
        m = len(gen)

        for i in range(n - k):
            if rem[i] == "1":
                steps.append(f"Bit {i}: Remainder prefix is '1', XOR with generator {clean_gen}")
                for j in range(m):
                    rem[i + j] = "1" if rem[i + j] != gen[j] else "0"
            else:
                steps.append(f"Bit {i}: Remainder prefix is '0', Shift without XOR")

        remainder = "".join(rem[-(k):])
        codeword = clean_data + remainder

        return {
            "original_data": clean_data,
            "generator_polynomial": clean_gen,
            "degree_k": k,
            "augmented_data": augmented_data,
            "remainder_crc": remainder,
            "transmitted_codeword": codeword,
            "steps_log": steps[:12]  # First steps for concise display
        }
