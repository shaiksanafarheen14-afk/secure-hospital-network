"""Reliable Data Transfer Adapter: Sliding Window & Go-Back-N (GBN) ARQ.

Simulates Transport / Data Link Layer reliable transmission protocols:
- Sliding Window mechanics (Window Size N)
- Cumulative Acknowledgments (ACKs)
- Timeout detection
- Go-Back-N bulk retransmission of unacknowledged window frames
"""

import time
import random
from typing import List, Dict, Any, Tuple

try:
    from modules.base_adapter import BaseProtocolAdapter, AdapterStatus
except (ImportError, ValueError):
    try:
        from .base_adapter import BaseProtocolAdapter, AdapterStatus
    except (ImportError, ValueError):
        from base_adapter import BaseProtocolAdapter, AdapterStatus

try:
    from core.models import TransmissionResult, DeliveryStatus
except (ImportError, ValueError):
    from ..core.models import TransmissionResult, DeliveryStatus


class ReliableTransmissionAdapter(BaseProtocolAdapter):
    """Adapter for Sliding Window and Go-Back-N ARQ protocol simulation."""

    def __init__(self):
        super().__init__(
            protocol_name="Reliable Transmission (Go-Back-N ARQ)",
            candidate_modules=["reliable_transmission.gbn", "modules.reliable_transmission", "reliable_transmission"]
        )

    def simulate_gbn_transmission(
        self,
        total_packets: int = 8,
        window_size: int = 4,
        loss_indices: List[int] = None,
        base_delay_ms: float = 18.0,
        sender_name: str = "ICU Ward 3",
        receiver_name: str = "Central Hospital Server"
    ) -> Dict[str, Any]:
        """
        Simulate Go-Back-N ARQ transmission.
        Args:
            total_packets: Number of frames to transmit.
            window_size: Size of sliding window (N).
            loss_indices: List of sequence numbers to drop on their first attempt.
            base_delay_ms: One-way base propagation delay in milliseconds.
            sender_name: Sending department.
            receiver_name: Receiving node.
        Returns:
            Dict containing step-by-step event log, window progression, and TransmissionResult records.
        """
        if loss_indices is None:
            loss_indices = [2]  # Default: drop packet #2 on first attempt

        events: List[str] = []
        transmission_results: List[TransmissionResult] = []

        base = 0
        next_seq = 0
        expected_seq = 0
        retransmission_counts = {i: 0 for i in range(total_packets)}
        dropped_attempts = set(loss_indices)

        events.append(f"[INIT] Initializing Go-Back-N ARQ: N={window_size}, Total Packets={total_packets}")
        events.append(f"[CONFIG] Simulating intentional drop on packet sequence(s): {loss_indices}")

        while base < total_packets:
            # 1. Send packets within window
            while next_seq < base + window_size and next_seq < total_packets:
                win_range = f"[{base}..{min(base + window_size - 1, total_packets - 1)}]"
                events.append(f"  -> TX: Sent Packet #{next_seq} | Window: {win_range}")
                next_seq += 1

            # 2. Simulate transit of packet at 'base'
            curr_pkt = base
            if curr_pkt in dropped_attempts:
                # Packet was lost in transit
                retransmission_counts[curr_pkt] += 1
                dropped_attempts.remove(curr_pkt)
                events.append(f"  [X] LOSS: Packet #{curr_pkt} was lost in transit (Simulated Channel Impairment)")
                events.append(f"  [!] TIMEOUT: Sender timer expired for Packet #{curr_pkt}")
                events.append(f"  <-- GBN RECOVERY: Go-Back-N triggered. Resending window from #{base}...")

                # Record the failed attempt
                transmission_results.append(TransmissionResult(
                    packet_id=len(transmission_results) + 1,
                    seq_num=curr_pkt,
                    timestamp_str=time.strftime("%H:%M:%S"),
                    sender=sender_name,
                    receiver=receiver_name,
                    frame_size_bytes=random.randint(64, 128),
                    encryption_algorithm="AES-128-CBC",
                    framing_type="Bit Stuffing",
                    crc_status="Valid (Uncorrupted)",
                    delivery_status=DeliveryStatus.LOST,
                    latency_ms=round(base_delay_ms * 2.5, 2),
                    retransmissions=retransmission_counts[curr_pkt],
                    is_simulated=True
                ))

                # Go-Back-N rule: next_seq is reset to base so all unACKed packets are re-sent
                next_seq = base
                continue

            # 3. Successful arrival at receiver
            measured_delay = round(base_delay_ms + random.uniform(1.2, 5.8), 2)
            events.append(f"  <- RX: Packet #{curr_pkt} received in-order. Receiver emits ACK #{curr_pkt}")
            
            # Record successful delivery
            status = DeliveryStatus.DELIVERED if retransmission_counts[curr_pkt] == 0 else DeliveryStatus.RETRANSMITTED
            transmission_results.append(TransmissionResult(
                packet_id=len(transmission_results) + 1,
                seq_num=curr_pkt,
                timestamp_str=time.strftime("%H:%M:%S"),
                sender=sender_name,
                receiver=receiver_name,
                frame_size_bytes=random.randint(64, 128),
                encryption_algorithm="AES-128-CBC",
                framing_type="Bit Stuffing",
                crc_status="Valid (CRC Checked)",
                delivery_status=status,
                latency_ms=measured_delay,
                retransmissions=retransmission_counts[curr_pkt],
                is_simulated=True
            ))

            # Slide window forward
            base += 1
            events.append(f"  [SLIDE] ACK #{curr_pkt} received at Sender. Window slides forward to [{base}..{min(base + window_size - 1, total_packets - 1)}]")

        events.append(f"[DONE] All {total_packets} packets successfully acknowledged via Go-Back-N.")

        return {
            "window_size": window_size,
            "total_packets": total_packets,
            "events_log": events,
            "transmission_results": transmission_results,
            "retransmission_counts": retransmission_counts
        }
