# =============================================================================
# ack.py — ACK (Acknowledgement) Mechanism
# =============================================================================
# After a receiver processes a frame, it sends back an ACK (positive) or
# a NAK (negative acknowledgement) to the sender:
#
#   ACK (n)  → "Frame n received correctly — send next frame"
#   NAK (n)  → "Frame n was corrupted — please retransmit from frame n"
#
# In Go-Back-N ARQ, NAKs trigger retransmission from the bad frame onward.
# =============================================================================

from reliable_transmission.crc import verify_crc


# String constants for acknowledgement types
ACK = "ACK"
NAK = "NAK"


def process_frame(frame: dict) -> tuple:
    """
    Receiver-side: validates a frame and generates an acknowledgement.

    Steps:
      1. Extract seq, data, and CRC from the frame
      2. Verify CRC using the CRC module
      3. Return ACK if valid, NAK if corrupted

    Args:
        frame (dict): The received frame (may be corrupted)

    Returns:
        tuple: (ack_type: str, seq_num: int, data_or_none: str | None)
               - ack_type   : "ACK" or "NAK"
               - seq_num    : sequence number of this frame
               - data_or_none: the data payload if valid, else None
    """
    seq = frame["seq"]
    data = frame["data"]
    received_crc = frame["crc"]

    if verify_crc(seq, data, received_crc):
        # Frame is valid → send ACK and return the data
        return ACK, seq, data
    else:
        # Frame is corrupted → send NAK, discard data
        return NAK, seq, None


def format_ack(ack_type: str, seq_num: int) -> str:
    """
    Returns a human-readable acknowledgement message string.

    Args:
        ack_type (str): "ACK" or "NAK"
        seq_num  (int): The sequence number being acknowledged

    Returns:
        str: e.g. "<- [OK] ACK(2)" or "<- [!!] NAK(2)"
    """
    symbol = "[OK]" if ack_type == ACK else "[!!]"
    return f"<- {symbol} {ack_type}({seq_num})"
