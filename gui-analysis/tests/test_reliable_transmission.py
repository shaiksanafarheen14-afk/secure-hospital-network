"""Unit tests for Sliding Window & Go-Back-N (GBN) ARQ protocol simulation."""

import unittest
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.reliable_transmission_adapter import ReliableTransmissionAdapter
from core.models import DeliveryStatus


class TestReliableTransmission(unittest.TestCase):
    """Test Go-Back-N sliding window transmission and recovery."""

    def setUp(self):
        self.adapter = ReliableTransmissionAdapter()

    def test_clean_gbn_transmission(self):
        # 6 packets, no drops
        res = self.adapter.simulate_gbn_transmission(
            total_packets=6, window_size=3, loss_indices=[]
        )
        self.assertEqual(res["total_packets"], 6)
        self.assertEqual(res["window_size"], 3)
        self.assertEqual(sum(res["retransmission_counts"].values()), 0)
        self.assertEqual(len(res["transmission_results"]), 6)

        # All delivered
        for r in res["transmission_results"]:
            self.assertEqual(r.delivery_status, DeliveryStatus.DELIVERED)

    def test_gbn_loss_and_retransmission(self):
        # 6 packets, drop packet #2 on first attempt
        res = self.adapter.simulate_gbn_transmission(
            total_packets=6, window_size=3, loss_indices=[2]
        )
        self.assertEqual(res["retransmission_counts"][2], 1)

        # Must record at least 1 LOST result and subsequent RETRANSMITTED
        statuses = [r.delivery_status for r in res["transmission_results"]]
        self.assertIn(DeliveryStatus.LOST, statuses)
        self.assertIn(DeliveryStatus.RETRANSMITTED, statuses)


if __name__ == "__main__":
    unittest.main()
