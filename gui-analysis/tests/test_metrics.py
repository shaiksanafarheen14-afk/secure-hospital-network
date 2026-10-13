"""Unit tests for performance calculations and summary statistics."""

import unittest
import sys
from pathlib import Path

# Ensure gui-analysis is in sys.path
test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from core.models import TransmissionResult, DeliveryStatus
from core.metrics import (
    calculate_loss_rate,
    calculate_success_rate,
    calculate_throughput,
    calculate_jitter,
    compute_metrics_summary
)


class TestMetricsCalculations(unittest.TestCase):
    """Test mathematical formulas and aggregation logic."""

    def test_calculate_loss_rate(self):
        self.assertEqual(calculate_loss_rate(100, 5), 5.0)
        self.assertEqual(calculate_loss_rate(50, 10), 20.0)
        self.assertEqual(calculate_loss_rate(0, 0), 0.0)
        self.assertEqual(calculate_loss_rate(10, 0), 0.0)

    def test_calculate_success_rate(self):
        self.assertEqual(calculate_success_rate(100, 95), 95.0)
        self.assertEqual(calculate_success_rate(20, 15), 75.0)
        self.assertEqual(calculate_success_rate(0, 0), 0.0)

    def test_calculate_throughput(self):
        # 1000 bytes in 1.0 second: (1000 * 8) / 1000 = 8.0 kbps
        self.assertEqual(calculate_throughput(1000, 1.0), 8.0)
        # 2500 bytes in 2.0 seconds: (2500 * 8) / (2000) = 10.0 kbps
        self.assertEqual(calculate_throughput(2500, 2.0), 10.0)
        # Zero duration handling
        self.assertEqual(calculate_throughput(1000, 0.0), 0.0)

    def test_calculate_jitter(self):
        delays = [10.0, 15.0, 12.0, 20.0]
        # Diff: |15-10|=5, |12-15|=3, |20-12|=8. Sum = 16. Mean = 16/3 = 5.33
        self.assertAlmostEqual(calculate_jitter(delays), 5.33, places=2)
        # Single element or empty list
        self.assertEqual(calculate_jitter([10.0]), 0.0)
        self.assertEqual(calculate_jitter([]), 0.0)

    def test_compute_metrics_summary(self):
        results = [
            TransmissionResult(1, 1, "00:01", "ICU", "Server", 100, "AES", "Bit", "Valid", DeliveryStatus.DELIVERED, 10.0, 0, True),
            TransmissionResult(2, 2, "00:02", "ICU", "Server", 100, "AES", "Bit", "Valid", DeliveryStatus.DELIVERED, 20.0, 0, True),
            TransmissionResult(3, 3, "00:03", "ICU", "Server", 100, "AES", "Bit", "Corrupt", DeliveryStatus.CORRUPTED, 15.0, 1, True),
            TransmissionResult(4, 4, "00:04", "ICU", "Server", 100, "AES", "Bit", "Valid", DeliveryStatus.LOST, 50.0, 2, True),
        ]
        summary = compute_metrics_summary(results, simulated_duration_seconds=1.0)
        self.assertEqual(summary.total_sent, 4)
        self.assertEqual(summary.total_received, 2)
        self.assertEqual(summary.total_lost, 1)
        self.assertEqual(summary.total_retransmitted, 3)
        self.assertEqual(summary.total_corrupted, 1)
        self.assertEqual(summary.success_rate_percent, 50.0)
        self.assertEqual(summary.average_delay_ms, 15.0)  # (10 + 20) / 2
        # Delivered bytes = 200 bytes. (200 * 8) / 1000 = 1.6 kbps
        self.assertEqual(summary.throughput_kbps, 1.6)


if __name__ == "__main__":
    unittest.main()
