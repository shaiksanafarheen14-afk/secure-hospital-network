"""
ack.py
------
Implements the ACK (Acknowledgement) and NACK (Negative Acknowledgement)
mechanism used between sender and receiver departments.

How ACK works (beginner explanation):
  - After the receiver gets a frame, it checks the CRC.
  - If the CRC is OK  → receiver sends back ACK  (all good, move on).
  - If the CRC fails  → receiver sends back NACK (please resend this frame).
  - The sender waits for ACK/NACK before sliding its window forward.

ACK/NACK objects are simple dicts:
  { "type": "ACK"  | "NACK", "seq": <frame_sequence_number> }
"""

from crc import verify_crc8


def make_ack(seq_num: int) -> dict:
    """Create a positive acknowledgement for frame `seq_num`."""
    return {"type": "ACK", "seq": seq_num}


def make_nack(seq_num: int) -> dict:
    """Create a negative acknowledgement for frame `seq_num`."""
    return {"type": "NACK", "seq": seq_num}


def process_received_frame(frame: dict) -> dict:
    """
    Inspect a received frame and decide whether to send ACK or NACK.

    The receiver:
      1. Re-computes CRC on the received data.
      2. Compares with the CRC field carried in the frame header.
      3. Returns an ACK if they match, NACK otherwise.

    Args:
        frame : The received frame dict with 'seq', 'data', 'crc' keys.

    Returns:
        An ACK or NACK dict.
    """
    seq  = frame["seq"]
    data = frame["data"]
    received_crc = frame["crc"]

    if verify_crc8(data, received_crc):
        return make_ack(seq)
    else:
        return make_nack(seq)


def is_ack(response: dict) -> bool:
    """Return True if the response is a positive ACK."""
    return response["type"] == "ACK"


def is_nack(response: dict) -> bool:
    """Return True if the response is a NACK."""
    return response["type"] == "NACK"
