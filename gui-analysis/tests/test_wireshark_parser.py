"""Unit tests for Wireshark CSV trace parsing and export."""

import unittest
import os
import tempfile
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.wireshark_parser import WiresharkTraceParser
from core.models import TransmissionResult, DeliveryStatus


class TestWiresharkTraceParser(unittest.TestCase):
    """Test Wireshark CSV import and export logic."""

    def test_parse_sample_wireshark_file(self):
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sample_data",
            "sample_hospital_wireshark_trace.csv"
        )
        self.assertTrue(os.path.exists(sample_path))

        results, msg = WiresharkTraceParser.parse_csv_file(sample_path)
        self.assertGreater(len(results), 0)
        self.assertIn("Wireshark", msg)

        # Ensure all imported records are tagged as simulated
        for r in results:
            self.assertTrue(r.is_simulated)
            self.assertGreater(r.frame_size_bytes, 0)
            self.assertGreater(r.latency_ms, 0)

    def test_export_and_reimport_simulator_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = os.path.join(tmpdir, "test_export.csv")
            sample_results = [
                TransmissionResult(1, 1, "12:00:00", "ICU Ward", "Server", 120, "AES", "Bit", "Valid", DeliveryStatus.DELIVERED, 12.4, 0, True),
                TransmissionResult(2, 2, "12:00:01", "Cardiology", "Server", 140, "AES", "Bit", "Valid", DeliveryStatus.DELIVERED, 16.8, 0, True),
            ]

            ok, msg = WiresharkTraceParser.export_to_csv(sample_results, export_path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(export_path))

            # Re-import
            reimported, import_msg = WiresharkTraceParser.parse_csv_file(export_path)
            self.assertEqual(len(reimported), 2)
            self.assertEqual(reimported[0].sender, "ICU Ward")
            self.assertEqual(reimported[1].sender, "Cardiology")


if __name__ == "__main__":
    unittest.main()
