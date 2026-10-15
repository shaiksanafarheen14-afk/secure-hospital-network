# =============================================================================
# go_back_n.py -- Sliding Window / Go-Back-N ARQ Simulation
# =============================================================================
# Go-Back-N ARQ (Automatic Repeat reQuest) is a sliding window protocol:
#
#   - The sender maintains a "window" of W frames that can be in-flight
#     (sent but not yet acknowledged) at the same time.
#   - When the receiver detects a corrupted frame N, it sends NAK(N).
#   - The sender then "goes back" and retransmits frame N and ALL frames
#     after N that were already sent (even if they were fine).
#   - This continues until all frames are acknowledged.
#
# Window size (W) controls throughput:
#   W=1  --> Stop-and-Wait (simplest)
#   W>1  --> Pipelined (more efficient)
# =============================================================================

import time

from reliable_transmission.channel import transmit_frame
from reliable_transmission.ack import process_frame, format_ack, ACK, NAK
from reliable_transmission.framing import frame_to_str
from reliable_transmission.utils import (
    print_section,
    print_sender_action,
    print_receiver_action,
    print_window,
    print_retransmit,
    print_success,
    print_failure,
)

# Pause between frame transmissions (seconds) -- slows output for readability
TRANSMISSION_DELAY = 0.2


def run_go_back_n(
    frames: list,
    window_size: int = 3,
    corruption_rate: float = 0.3,
    max_retries: int = 10,
) -> list:
    """
    Simulates the Go-Back-N ARQ protocol over a noisy channel.

    Args:
        frames          (list):  List of frame dicts from framing.create_frames()
        window_size     (int):   Sliding window size W (default 3)
        corruption_rate (float): Probability a frame gets corrupted (0-1)
        max_retries     (int):   Max retransmission attempts before giving up

    Returns:
        list[str]: The received data payloads in order (successful frames only)
    """
    total_frames = len(frames)
    received_data = [None] * total_frames   # Stores successfully received payloads
    base = 0          # Left edge of the window (oldest unACKed frame)
    next_seq = 0      # Next frame to send
    retry_count = 0   # Global retry counter (safety valve)

    print_section("GO-BACK-N ARQ SIMULATION")
    print(f"  [i] Total frames   : {total_frames}")
    print(f"  [i] Window size    : {window_size}")
    print(f"  [i] Corruption rate: {corruption_rate * 100:.0f}%")
    print()

    # Keep going until all frames are acknowledged
    while base < total_frames:

        # --- SENDER: Send all frames within the current window ---
        while next_seq < total_frames and next_seq < base + window_size:
            print_window(base, next_seq, window_size, total_frames)
            print_sender_action(next_seq, frames[next_seq])
            time.sleep(TRANSMISSION_DELAY)
            next_seq += 1

        # --- CHANNEL + RECEIVER: Process each sent frame in the window ---
        error_at = None   # Track the first NAK position in this window pass

        for seq in range(base, next_seq):
            # Transmit through noisy channel
            received = transmit_frame(frames[seq], corruption_rate)

            # Receiver checks the frame
            ack_type, ack_seq, data = process_frame(received)
            ack_msg = format_ack(ack_type, ack_seq)

            if ack_type == ACK:
                # Frame received correctly
                print_receiver_action(seq, ack_msg, corrupted=False)
                received_data[seq] = data
            else:
                # Frame corrupted -- record the first error
                print_receiver_action(seq, ack_msg, corrupted=True)
                if error_at is None:
                    error_at = seq
                break  # Stop processing; will retransmit from error_at

            time.sleep(TRANSMISSION_DELAY)

        # --- ARQ DECISION ---
        if error_at is not None:
            # Go-Back-N: retransmit from the error frame
            retry_count += 1
            if retry_count > max_retries:
                print_failure(error_at)
                break
            print_retransmit(error_at, retry_count, max_retries)
            next_seq = error_at   # Roll the send pointer back
            # base stays the same -- window slides only on ACK
        else:
            # All frames in this window pass --> slide the window forward
            base = next_seq

    print()
    return [d for d in received_data if d is not None]


def run_stop_and_wait(
    frames: list,
    corruption_rate: float = 0.3,
    max_retries: int = 10,
) -> list:
    """
    Simulates Stop-and-Wait ARQ (window_size = 1) for comparison.

    Args:
        frames          (list):  List of frame dicts
        corruption_rate (float): Probability a frame gets corrupted
        max_retries     (int):   Max retransmission attempts per frame

    Returns:
        list[str]: Successfully received data payloads
    """
    print_section("STOP-AND-WAIT ARQ SIMULATION (Window = 1)")
    print(f"  [i] Total frames   : {len(frames)}")
    print(f"  [i] Corruption rate: {corruption_rate * 100:.0f}%")
    print()

    received_data = []

    for frame in frames:
        attempts = 0
        while attempts <= max_retries:
            attempts += 1
            print_sender_action(frame["seq"], frame, attempt=attempts)
            received = transmit_frame(frame, corruption_rate)
            ack_type, ack_seq, data = process_frame(received)
            ack_msg = format_ack(ack_type, ack_seq)
            corrupted = (ack_type == NAK)
            print_receiver_action(ack_seq, ack_msg, corrupted=corrupted)

            if ack_type == ACK:
                received_data.append(data)
                time.sleep(TRANSMISSION_DELAY)
                break
            else:
                print_retransmit(frame["seq"], attempts, max_retries)
                time.sleep(TRANSMISSION_DELAY)
        else:
            print_failure(frame["seq"])

    print()
    return received_data
