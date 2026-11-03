import binascii
import unittest

from crc import calculate_crc, format_crc, verify_checksum
from crc.checker import calculate_crc as calculate_crc_from_checker
from modules.crc import calculate_crc as calculate_crc_from_modules


class TestCRC(unittest.TestCase):
    def test_crc16_ccitt_known_reference_value(self):
        self.assertEqual(calculate_crc(b"123456789"), 0x29B1)
        self.assertEqual(calculate_crc(b"123456789", "CRC-16-CCITT"), 0x29B1)

    def test_crc16_is_deterministic(self):
        data = b"PATIENT_DATA_FRAME_101"
        self.assertEqual(calculate_crc(data), calculate_crc(data))

    def test_crc32_matches_ieee_reference_implementation(self):
        data = b"123456789"
        self.assertEqual(calculate_crc(data, "CRC-32"), 0xCBF43926)
        self.assertEqual(calculate_crc(data, "CRC-32"), binascii.crc32(data))

    def test_empty_input_checksums(self):
        self.assertEqual(calculate_crc(b""), 0xFFFF)
        self.assertEqual(calculate_crc(b"", "CRC-32"), 0)

    def test_checksum_verification_accepts_integer_and_hexadecimal(self):
        data = b"TELEMETRY_VITALS: HR=78"
        crc16 = calculate_crc(data)
        crc32 = calculate_crc(data, "CRC-32")

        self.assertTrue(verify_checksum(data, crc16))
        self.assertTrue(verify_checksum(data, format_crc(crc16)))
        self.assertTrue(verify_checksum(data, format_crc(crc32, "CRC-32"), "CRC-32"))

    def test_verification_detects_corrupted_data(self):
        data = b"TELEMETRY_VITALS: HR=78"
        original_crc = calculate_crc(data)
        corrupted = bytearray(data)
        corrupted[3] ^= 1 << 2

        self.assertFalse(verify_checksum(bytes(corrupted), original_crc))

    def test_compatibility_import_paths_share_the_implementation(self):
        data = b"123456789"
        expected = calculate_crc(data)

        self.assertEqual(calculate_crc_from_checker(data), expected)
        self.assertEqual(calculate_crc_from_modules(data), expected)

    def test_unsupported_algorithm_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported CRC algorithm"):
            calculate_crc(b"data", "CRC-8")

    def test_invalid_data_is_rejected(self):
        for data in ("data", bytearray(b"data"), None):
            with self.subTest(data=data):
                with self.assertRaisesRegex(TypeError, "data must be bytes"):
                    calculate_crc(data)

    def test_invalid_checksum_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "hexadecimal CRC"):
            verify_checksum(b"data", "not-a-checksum")

    def test_hex_formatting_uses_algorithm_width(self):
        self.assertEqual(format_crc(0x29B1), "0x29B1")
        self.assertEqual(format_crc(0xCBF43926, "CRC-32"), "0xCBF43926")


if __name__ == "__main__":
    unittest.main()
