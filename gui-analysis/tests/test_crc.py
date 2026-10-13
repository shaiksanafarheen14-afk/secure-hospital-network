"""Unit tests for CRC Error Detection (CRC-16, CRC-32, and bit error injection)."""

import unittest
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.crc_adapter import CRCAdapter


class TestCRCAdapter(unittest.TestCase):
    """Test CRC computation, validation, error injection, and polynomial division."""

    def setUp(self):
        self.adapter = CRCAdapter()

    def test_crc16_deterministic(self):
        data = b"PATIENT_DATA_FRAME_101"
        crc1 = self.adapter.compute_checksum(data, "CRC-16")
        crc2 = self.adapter.compute_checksum(data, "CRC-16")
        self.assertEqual(crc1, crc2)
        self.assertTrue(crc1.startswith("0x"))

    def test_crc32_deterministic(self):
        data = b"PATIENT_DATA_FRAME_101"
        crc1 = self.adapter.compute_checksum(data, "CRC-32")
        crc2 = self.adapter.compute_checksum(data, "CRC-32")
        self.assertEqual(crc1, crc2)
        self.assertTrue(crc1.startswith("0x"))

    def test_verify_clean_checksum(self):
        data = b"TELEMETRY_VITALS: HR=78"
        crc = self.adapter.compute_checksum(data, "CRC-16")
        self.assertTrue(self.adapter.verify_checksum(data, crc, "CRC-16"))

    def test_detect_injected_bit_error(self):
        data = b"TELEMETRY_VITALS: HR=78"
        original_crc = self.adapter.compute_checksum(data, "CRC-16")

        # Inject 1 bit error in data
        corrupted = self.adapter.inject_bit_error(data, byte_offset=3, bit_pos=2)
        self.assertNotEqual(data, corrupted)

        # Verification must fail!
        self.assertFalse(self.adapter.verify_checksum(corrupted, original_crc, "CRC-16"))

    def test_step_by_step_modulo2_division(self):
        data_bits = "110101"
        gen = "10011"
        res = self.adapter.step_by_step_modulo2_division(data_bits, gen)

        self.assertEqual(res["original_data"], data_bits)
        self.assertEqual(res["generator_polynomial"], gen)
        self.assertEqual(res["degree_k"], 4)
        self.assertEqual(len(res["remainder_crc"]), 4)
        self.assertTrue(len(res["steps_log"]) > 0)


if __name__ == "__main__":
    unittest.main()
