# =============================================================================
# ack.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Implements the ACK (Acknowledgement) / NACK (Negative-ACK) 
#           mechanism. The receiver inspects each frame and replies with
#           ACK (frame OK) or NACK (frame corrupted, please resend).
# =============================================================================

from crc import verify_crc


# ─────────────────────────────────────────────────────────────────────────────
# Response type constants — makes the code readable
# ─────────────────────────────────────────────────────────────────────────────
ACK  = "ACK"   # Positive acknowledgement  → frame received correctly
NACK = "NACK"  # Negative acknowledgement  → frame is corrupted, resend it


def receiver_check(frame: dict) -> str:
    """
    Receiver-side check: inspect the incoming frame and return ACK or NACK.

    Steps performed:
      1. Run CRC verification on the received frame's payload.
      2. If CRC passes  → reply ACK  (frame is intact).
      3. If CRC fails   → reply NACK (frame was corrupted in transit).

    Args:
        frame (dict): The received frame containing 'payload' and 'crc' keys.

    Returns:
        str: 'ACK' or 'NACK'
    """
    if verify_crc(frame):
        return ACK    # CRC matched — frame is good
    else:
        return NACK   # CRC mismatch — frame is corrupted


def format_ack_message(response: str, seq_num: int) -> str:
    """
    Build a human-readable ACK/NACK message string for terminal output.

    Args:
        response (str): 'ACK' or 'NACK'
        seq_num  (int): Sequence number of the frame being acknowledged.

    Returns:
        str: A formatted acknowledgement message.
    """
    if response == ACK:
        return f"  [RECEIVER] → ACK  for Frame {seq_num:02d}  ✓  (Frame received correctly)"
    else:
        return f"  [RECEIVER] → NACK for Frame {seq_num:02d}  ✗  (CRC failed — requesting retransmission)"


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly: python ack.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from framing import create_frames
    from crc import attach_crc

    print("=== ACK / NACK Demo ===")
    frame = attach_crc(create_frames("HELLO")[0])

    # Test 1: Good frame
    response = receiver_check(frame)
    print(f"  Good frame  → {response}")

    # Test 2: Corrupted frame (manually corrupt the payload)
    bad_frame = dict(frame)         # shallow copy is fine here
    bad_frame["payload"] = "H@LLO"  # manually corrupt
    response = receiver_check(bad_frame)
    print(f"  Bad frame   → {response}")
