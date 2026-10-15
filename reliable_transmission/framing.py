# =============================================================================
# framing.py — Frame Creation and Parsing
# =============================================================================
# In data communication, a "frame" is a structured packet of data.
# Here we divide a message into fixed-size chunks and wrap each chunk
# with metadata: frame number, data payload, and a CRC checksum.
#
# Frame structure (as a Python dict):
#   {
#     "seq"  : int,   # Sequence number (frame's position in the stream)
#     "data" : str,   # The actual data payload (chunk of the full message)
#     "crc"  : str,   # CRC checksum computed over seq + data
#   }
# =============================================================================

from reliable_transmission.crc import compute_crc


# Maximum number of characters per frame payload
FRAME_SIZE = 20


def create_frames(message: str) -> list:
    """
    Splits a message string into a list of frames.

    Each frame is a dict containing:
      - seq  : sequence number (0-based)
      - data : payload chunk
      - crc  : CRC checksum of (seq + data)

    Args:
        message (str): Full message to be framed

    Returns:
        list[dict]: List of frame dictionaries
    """
    frames = []
    chunks = _split_into_chunks(message, FRAME_SIZE)

    for seq_num, chunk in enumerate(chunks):
        crc_value = compute_crc(f"{seq_num}{chunk}")  # CRC covers seq + data
        frame = {
            "seq": seq_num,
            "data": chunk,
            "crc": crc_value,
        }
        frames.append(frame)

    return frames


def parse_frame(frame: dict) -> tuple:
    """
    Extracts and returns the components of a frame.

    Args:
        frame (dict): A frame dictionary

    Returns:
        tuple: (seq_number, data_payload, crc_value)
    """
    return frame["seq"], frame["data"], frame["crc"]


def _split_into_chunks(text: str, size: int) -> list:
    """
    Helper: splits a string into fixed-size chunks.

    Args:
        text (str): The string to split
        size (int): Max characters per chunk

    Returns:
        list[str]: List of chunk strings
    """
    return [text[i: i + size] for i in range(0, len(text), size)]


def frame_to_str(frame: dict) -> str:
    """
    Returns a human-readable string representation of a frame.

    Args:
        frame (dict): A frame dictionary

    Returns:
        str: Formatted string like "[Seq:0 | Data:'hello' | CRC:ABCD]"
    """
    return (
        f"[Seq:{frame['seq']} | "
        f"Data:'{frame['data']}' | "
        f"CRC:{frame['crc']}]"
    )
