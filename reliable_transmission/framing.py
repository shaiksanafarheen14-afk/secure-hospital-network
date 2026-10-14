"""
framing.py
----------
Handles dividing a long message into fixed-size frames and
reassembling received frames back into the original message.

Framing (beginner explanation):
  In real networks, large data is broken into smaller "frames" (chunks)
  before being sent. Each frame has:
    - A sequence number  : so the receiver knows the order
    - The data payload   : a chunk of the original message
    - A CRC checksum     : so the receiver can detect corruption

Frame structure (as a Python dict):
  {
      "seq"  : int,   # sequence number (0-based)
      "data" : str,   # payload string
      "crc"  : int,   # CRC-8 checksum of the data
  }
"""

from crc import compute_crc8, crc_to_hex

# Default size of each frame's data payload (characters)
FRAME_SIZE = 50


def create_frames(message: str, frame_size: int = FRAME_SIZE) -> list:
    """
    Split a message string into a list of frame dictionaries.

    Args:
        message    : The full message to be transmitted.
        frame_size : Number of characters per frame payload.

    Returns:
        A list of frame dicts, each containing 'seq', 'data', 'crc'.
    """
    frames = []

    # Split the message into equal-sized chunks
    chunks = [message[i : i + frame_size] for i in range(0, len(message), frame_size)]

    for seq_num, chunk in enumerate(chunks):
        crc_value = compute_crc8(chunk)    # compute CRC for this chunk
        frame = {
            "seq" : seq_num,
            "data": chunk,
            "crc" : crc_value,
            "crc_hex": crc_to_hex(crc_value),
        }
        frames.append(frame)

    return frames


def frame_count(message: str, frame_size: int = FRAME_SIZE) -> int:
    """Return how many frames a message will be split into."""
    return -(-len(message) // frame_size)   # ceiling division


def reassemble(frames: list) -> str:
    """
    Reassemble a list of received frame dicts back into the original message.

    Args:
        frames : List of successfully received frame dicts (in order).

    Returns:
        The reconstructed message string.
    """
    # Sort by sequence number just in case they arrive out of order
    sorted_frames = sorted(frames, key=lambda f: f["seq"])
    return "".join(f["data"] for f in sorted_frames)
