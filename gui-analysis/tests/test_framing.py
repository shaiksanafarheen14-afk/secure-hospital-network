"""Unit tests for Data Link Layer framing (Character Stuffing and Bit Stuffing)."""

import unittest
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.framing_adapter import FramingAdapter


class TestFramingAdapter(unittest.TestCase):
    """Test character and bit stuffing algorithms."""

    def setUp(self):
        self.adapter = FramingAdapter()

    def test_character_stuffing_without_escape(self):
        data = "PATIENT_VITALS_NORMAL"
        res = self.adapter.character_stuff(data)
        framed = res["framed_output"]

        self.assertTrue(framed.startswith("[DLE STX]"))
        self.assertTrue(framed.endswith("[DLE ETX]"))

        unstuffed = self.adapter.character_unstuff(framed)
        self.assertEqual(unstuffed, data)

    def test_character_stuffing_with_dle_in_payload(self):
        # Payload containing the DLE escape sequence
        data = "DATA DLE TEXT DLE END"
        res = self.adapter.character_stuff(data)
        framed = res["framed_output"]

        # Must have doubled DLE: "DLE DLE"
        self.assertIn("DLE DLE", framed)

        unstuffed = self.adapter.character_unstuff(framed)
        self.assertEqual(unstuffed, data)

    def test_bit_stuffing_consecutive_ones(self):
        # Six consecutive ones: 111111 -> should stuff a zero after 5 ones: 1111101
        data_bits = "01111110"
        res = self.adapter.bit_stuff(data_bits)
        self.assertGreater(res["num_stuffed_zeros"], 0)

        unstuffed = self.adapter.bit_unstuff(res["framed_bits"])
        self.assertEqual(unstuffed, data_bits)

    def test_bit_stuffing_multiple_patterns(self):
        # Long bit sequence with multiple runs of 5 ones
        data_bits = "11111011111110011111"
        res = self.adapter.bit_stuff(data_bits)
        unstuffed = self.adapter.bit_unstuff(res["framed_bits"])
        self.assertEqual(unstuffed, data_bits)

    def test_text_to_bit_roundtrip(self):
        text = "Hospital"
        bits = self.adapter.text_to_bit_string(text)
        reconstructed = self.adapter.bit_string_to_text(bits)
        self.assertEqual(reconstructed, text)


if __name__ == "__main__":
    unittest.main()
