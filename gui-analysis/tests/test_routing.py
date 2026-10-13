"""Unit tests for hospital network routing (Dijkstra and Distance Vector)."""

import unittest
import sys
from pathlib import Path

test_dir = Path(__file__).resolve().parent.parent
if str(test_dir) not in sys.path:
    sys.path.insert(0, str(test_dir))

from modules.routing_adapter import RoutingAdapter


class TestRoutingAdapter(unittest.TestCase):
    """Test Dijkstra shortest path and Distance Vector routing matrix."""

    def setUp(self):
        self.adapter = RoutingAdapter()

    def test_dijkstra_shortest_path(self):
        # ICU Ward -> Central Server
        # ICU -> Core Router (4.0) -> Central Server (3.0) = Total 7.0 ms
        res = self.adapter.run_dijkstra("ICU Ward", "Central Server")

        self.assertEqual(res["source"], "ICU Ward")
        self.assertEqual(res["destination"], "Central Server")
        self.assertEqual(res["total_cost_ms"], 7.0)
        self.assertEqual(res["path"], ["ICU Ward", "Core Router", "Central Server"])
        self.assertEqual(res["hop_count"], 2)

    def test_dijkstra_same_source_dest(self):
        res = self.adapter.run_dijkstra("ICU Ward", "ICU Ward")
        self.assertEqual(res["total_cost_ms"], 0.0)
        self.assertEqual(res["path"], ["ICU Ward"])

    def test_distance_vector_convergence(self):
        tables = self.adapter.run_distance_vector()
        self.assertIn("ICU Ward", tables)
        self.assertIn("Central Server", tables)

        # Distance from ICU to Central Server in Distance Vector must match Dijkstra cost (7.0 ms)
        icu_table = tables["ICU Ward"]
        server_entry = next((e for e in icu_table if e["destination"] == "Central Server"), None)
        self.assertIsNotNone(server_entry)
        self.assertEqual(server_entry["cost_ms"], 7.0)
        self.assertEqual(server_entry["next_hop"], "Core Router")


if __name__ == "__main__":
    unittest.main()
