"""
sliding_window.py
-----------------
Implements the Sliding Window protocol with Go-Back-N (GBN) ARQ.

Key concepts (beginner explanation):
─────────────────────────────────────
Sliding Window:
  Instead of sending one frame and waiting for its ACK before sending the next
  (Stop-and-Wait), the sender can have multiple frames "in flight" at once.
  The maximum number of unacknowledged frames allowed at a time is the
  WINDOW SIZE (W).

  Example (W=3):
    Send frames 0, 1, 2  →  wait for ACKs
    When ACK-0 arrives   →  send frame 3  (window "slides" forward)
    When ACK-1 arrives   →  send frame 4  …and so on

Go-Back-N ARQ:
  If a NACK (or timeout) is received for frame N, the sender goes BACK to
  frame N and retransmits ALL frames from N onwards (within the window).
  This is simpler than Selective Repeat but may retransmit some correct frames.

This module drives the entire transmission loop and returns the list of
successfully received frames in order.
"""

import random
from channel  import transmit
from ack      import process_received_frame, is_ack
import display as ui


def run_go_back_n(frames: list,
                  window_size: int = 3,
                  corruption_rate: float = 0.30,
                  seed: int = 42) -> list:
    """
    Simulate Go-Back-N ARQ over a noisy channel.

    Args:
        frames          : List of frame dicts produced by framing.create_frames().
        window_size     : Number of frames the sender can have in-flight at once.
        corruption_rate : Probability that the channel corrupts any one frame.
        seed            : RNG seed for reproducible output.

    Returns:
        List of successfully received (and verified) frame dicts, in order.
    """
    rng             = random.Random(seed)   # seeded RNG for reproducibility
    total_frames    = len(frames)
    received_frames = [None] * total_frames  # slots for received frames

    base  = 0   # index of the oldest unacknowledged frame
    stats = {"sent": 0, "retransmitted": 0, "corrupted": 0}

    ui.section("Go-Back-N ARQ Transmission")
    ui.info(f"Total frames : {total_frames}")
    ui.info(f"Window size  : {window_size}")
    ui.info(f"Corruption   : {corruption_rate * 100:.0f}% per frame")
    print()

    while base < total_frames:
        # ── Build the current window ───────────────────────────────────────
        window_end = min(base + window_size, total_frames)
        window     = list(range(base, window_end))

        ui.window_state(base, window)

        # ── Transmit every frame in the window ────────────────────────────
        error_at = None   # first frame in window where an error occurred

        for seq in window:
            frame = frames[seq]
            ui.send(seq, frame["data"][:20] + "…", frame["crc_hex"])
            stats["sent"] += 1

            # Send through the noisy channel
            received_frame, was_corrupted = transmit(frame, corruption_rate, rng)

            if was_corrupted:
                stats["corrupted"] += 1
                ui.corrupt(seq)

            # Receiver checks CRC and sends ACK or NACK
            response = process_received_frame(received_frame)

            if is_ack(response):
                # Frame received correctly — store it
                ui.received_ok(seq, received_frame["data"][:20] + "…")
                ui.ack(seq)
                received_frames[seq] = received_frame

            else:
                # CRC mismatch — receiver sends NACK
                ui.received_error(seq)
                ui.nack(seq)
                if error_at is None:
                    error_at = seq  # remember the first bad frame

                # In Go-Back-N we stop processing the rest of the window
                # when the first error occurs
                break

        # ── Decide how to advance the window ──────────────────────────────
        if error_at is None:
            # All frames in this window were delivered successfully
            base = window_end      # slide window all the way forward
        else:
            # Go Back to the frame where the error occurred
            ui.retransmit(error_at)
            stats["retransmitted"] += (window_end - error_at)
            base = error_at        # go back and retry from that frame

        print()  # blank line between window rounds

    # ── Final statistics ──────────────────────────────────────────────────
    _print_stats(stats, total_frames)

    return received_frames


def _print_stats(stats: dict, total: int) -> None:
    """Print a summary table of transmission statistics."""
    ui.section("Transmission Statistics")
    print(f"  {'Frames sent (total)':<35}: {stats['sent']}")
    print(f"  {'Frames corrupted by channel':<35}: {stats['corrupted']}")
    print(f"  {'Retransmissions (Go-Back-N)':<35}: {stats['retransmitted']}")
    print(f"  {'Frames successfully delivered':<35}: {total}")
