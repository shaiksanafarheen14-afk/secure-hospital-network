# -*- coding: utf-8 -*-
# =============================================================================
# sliding_window.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Implements two ARQ (Automatic Repeat reQuest) protocols:
#
#   1. SLIDING WINDOW  — Sends up to WINDOW_SIZE frames without waiting for
#                        individual ACKs, then slides the window forward as
#                        ACKs arrive (selective / cumulative approach).
#
#   2. GO-BACK-N ARQ   — On receiving a NACK for frame N, the sender goes
#                        back and retransmits frame N AND all subsequent
#                        frames already sent in the current window.
#
# Both protocols are simulated step-by-step with detailed terminal output.
# =============================================================================

import time
import sys

# Windows console fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import WINDOW_SIZE, MAX_RETRANSMIT
from framing  import create_frames, reassemble_message
from crc      import attach_crc, verify_crc
from channel  import transmit_frame
from ack      import receiver_check, format_ack_message, ACK, NACK


# ─────────────────────────────────────────────────────────────────────────────
# Helper: print a divider line for readability
# ─────────────────────────────────────────────────────────────────────────────
def _divider(char="─", width=70):
    print(char * width)


# ─────────────────────────────────────────────────────────────────────────────
# PROTOCOL 1: SLIDING WINDOW (Stop-and-Wait extended to a window)
# ─────────────────────────────────────────────────────────────────────────────
def sliding_window_arq(sender: str, receiver: str, message: str,
                       window_size: int = WINDOW_SIZE) -> list:
    """
    Sliding Window ARQ simulation.

    The sender maintains a window of up to `window_size` unacknowledged frames.
    Frames that get NACK'd are individually retransmitted until ACK'd.

    Args:
        sender      (str): Name of the sending department.
        receiver    (str): Name of the receiving department.
        message     (str): The full message to transmit.
        window_size (int): Maximum number of unacknowledged frames in flight.

    Returns:
        list: Successfully received (and verified) frames in order.
    """
    print("\n")
    _divider("═")
    print(f"  PROTOCOL: SLIDING WINDOW ARQ")
    print(f"  FROM    : {sender}  →  TO: {receiver}")
    print(f"  MESSAGE : '{message}'")
    print(f"  WINDOW  : {window_size} frames")
    _divider("═")

    # Step 1 – Frame the message and attach CRC to each frame
    frames = [attach_crc(f) for f in create_frames(message)]
    print(f"\n  [FRAMING] Message split into {len(frames)} frame(s) "
          f"(frame size = {len(frames[0]['payload'])} chars each)\n")

    received_frames = []  # Frames successfully acknowledged by receiver
    base   = 0            # Start of the current window (first unACK'd frame)

    while base < len(frames):
        # ── Determine which frames are currently inside the window ──────────
        window_end = min(base + window_size, len(frames))
        window     = frames[base:window_end]

        print(f"  [WINDOW ] Sending frames {base}–{window_end - 1} "
              f"(window size = {len(window)})")
        _divider()

        # ── Try to deliver each frame in the window ─────────────────────────
        i = base
        while i < window_end:
            frame       = frames[i]
            retries     = 0
            frame_acked = False

            while not frame_acked and retries <= MAX_RETRANSMIT:
                attempt_label = "" if retries == 0 else f"  (retry #{retries})"
                print(f"\n  [SENDER  ] Sending Frame {frame['seq_num']:02d} | "
                      f"payload='{frame['payload']}' | "
                      f"CRC=0x{frame['crc']:02X}{attempt_label}")

                # ── Pass frame through the (possibly corrupting) channel ────
                received = transmit_frame(frame)

                if received["corrupted"]:
                    print(f"  [CHANNEL ] ⚡ Frame {frame['seq_num']:02d} CORRUPTED in transit! "
                          f"payload became '{received['payload']}'")
                else:
                    print(f"  [CHANNEL ] ✔  Frame {frame['seq_num']:02d} arrived intact")

                # ── Receiver checks CRC and sends ACK / NACK ───────────────
                response = receiver_check(received)
                print(format_ack_message(response, frame["seq_num"]))

                if response == ACK:
                    frame_acked = True
                    received_frames.append(frame)   # Store the ORIGINAL (clean) frame
                    print(f"  [STATUS  ] Frame {frame['seq_num']:02d} ✓ ACCEPTED")
                else:
                    retries += 1
                    if retries > MAX_RETRANSMIT:
                        print(f"  [ERROR   ] Frame {frame['seq_num']:02d} exceeded max retries "
                              f"({MAX_RETRANSMIT}). DROPPED.")
                    else:
                        print(f"  [SENDER  ] Retransmitting Frame {frame['seq_num']:02d} ...")

            i += 1  # Move to next frame inside the window

        # ── Slide the window forward ────────────────────────────────────────
        base = window_end
        if base < len(frames):
            print(f"\n  [WINDOW ] Sliding window → next base = {base}")

    _divider("═")
    return received_frames


# ─────────────────────────────────────────────────────────────────────────────
# PROTOCOL 2: GO-BACK-N ARQ
# ─────────────────────────────────────────────────────────────────────────────
def go_back_n_arq(sender: str, receiver: str, message: str,
                  window_size: int = WINDOW_SIZE) -> list:
    """
    Go-Back-N ARQ simulation.

    The sender sends up to `window_size` frames. If ANY frame gets a NACK,
    the sender goes back to that frame and retransmits IT and all frames
    that came after it in the current window.

    Args:
        sender      (str): Name of the sending department.
        receiver    (str): Name of the receiving department.
        message     (str): The full message to transmit.
        window_size (int): Maximum number of unacknowledged frames in flight.

    Returns:
        list: Successfully received frames in order.
    """
    print("\n")
    _divider("═")
    print(f"  PROTOCOL: GO-BACK-N ARQ")
    print(f"  FROM    : {sender}  →  TO: {receiver}")
    print(f"  MESSAGE : '{message}'")
    print(f"  WINDOW  : {window_size} frames")
    _divider("═")

    # Step 1 – Frame the message and attach CRC to each frame
    frames = [attach_crc(f) for f in create_frames(message)]
    print(f"\n  [FRAMING] Message split into {len(frames)} frame(s)\n")

    received_frames   = {}   # seq_num → frame  (only successfully ACK'd frames)
    base              = 0    # First unacknowledged frame
    global_retries    = 0    # Guard against infinite loops

    while base < len(frames) and global_retries <= MAX_RETRANSMIT * len(frames):
        # ── Determine the current window ────────────────────────────────────
        window_end = min(base + window_size, len(frames))
        window     = frames[base:window_end]

        print(f"  [WINDOW ] GBN window: frames {base}–{window_end - 1}")
        _divider()

        nack_frame_idx = None   # If set, we must go back to this frame

        # ── Send each frame in the window one by one ────────────────────────
        for frame in window:
            print(f"\n  [SENDER  ] Sending Frame {frame['seq_num']:02d} | "
                  f"payload='{frame['payload']}' | CRC=0x{frame['crc']:02X}")

            # Pass through potentially corrupting channel
            received = transmit_frame(frame)

            if received["corrupted"]:
                print(f"  [CHANNEL ] ⚡ Frame {frame['seq_num']:02d} CORRUPTED! "
                      f"payload='{received['payload']}'")
            else:
                print(f"  [CHANNEL ] ✔  Frame {frame['seq_num']:02d} OK")

            # Receiver checks and replies
            response = receiver_check(received)
            print(format_ack_message(response, frame["seq_num"]))

            if response == NACK:
                # Go-Back-N rule: stop sending and go back to this frame
                nack_frame_idx = frame["seq_num"]
                print(f"\n  [GBN     ] ⚠  NACK received for Frame {frame['seq_num']:02d}.")
                print(f"  [GBN     ]    Go-Back-N: will retransmit from Frame {nack_frame_idx} onward.")
                global_retries += 1
                break   # Stop sending rest of window; go back

            else:
                # ACK received — this frame is successfully delivered
                received_frames[frame["seq_num"]] = frame
                print(f"  [STATUS  ] Frame {frame['seq_num']:02d} ✓ ACCEPTED  "
                      f"(total accepted: {len(received_frames)}/{len(frames)})")

        if nack_frame_idx is not None:
            # Go back — do NOT advance base; retransmit from the NACK'd frame
            base = nack_frame_idx
            print(f"  [GBN     ] Going back to base = {base}\n")
        else:
            # All frames in this window were ACK'd — slide window forward
            base = window_end
            if base < len(frames):
                print(f"\n  [WINDOW ] All frames ACK'd. Sliding → base = {base}")

    _divider("═")
    # Build ordered list from the dict
    return [received_frames[k] for k in sorted(received_frames.keys())]


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly: python sliding_window.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    msg    = "PATIENT#001 CRITICAL BP=180/120"
    frames = sliding_window_arq("EMERGENCY", "ICU", msg, window_size=3)
    result = reassemble_message(frames)
    print(f"\n  Final reassembled (SW) : '{result}'")

    frames = go_back_n_arq("EMERGENCY", "ICU", msg, window_size=3)
    result = reassemble_message(frames)
    print(f"\n  Final reassembled (GBN): '{result}'")
