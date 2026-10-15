# =============================================================================
# crc.py — CRC (Cyclic Redundancy Check) Error Detection
# =============================================================================
# CRC is a popular error-detection technique used in networking.
# The sender computes a checksum (CRC value) from the data and appends it.
# The receiver recomputes the CRC from the received data and compares it.
# If the two CRC values differ → the frame is corrupted.
#
# We use Python's built-in binascii.crc32 which implements CRC-32,
# a standard 32-bit CRC algorithm used in Ethernet, ZIP files, etc.
# =============================================================================

import binascii


def compute_crc(data: str) -> str:
    """
    Computes the CRC-32 checksum of a string.

    Steps:
      1. Encode the string to bytes (UTF-8)
      2. Run crc32 algorithm → produces a 32-bit integer
      3. Convert to an 8-character uppercase hex string (e.g. "1A2B3C4D")

    Args:
        data (str): The input string to checksum

    Returns:
        str: 8-character uppercase hexadecimal CRC value
    """
    # Encode string to bytes, then compute CRC-32
    raw_bytes = data.encode("utf-8")
    crc_int = binascii.crc32(raw_bytes)

    # & 0xFFFFFFFF ensures positive unsigned 32-bit integer (cross-platform)
    crc_hex = format(crc_int & 0xFFFFFFFF, "08X")
    return crc_hex


def verify_crc(seq: int, data: str, received_crc: str) -> bool:
    """
    Verifies a frame's CRC checksum.

    Recomputes the CRC from seq + data and compares with the received CRC.

    Args:
        seq          (int): The frame's sequence number
        data         (str): The frame's data payload
        received_crc (str): The CRC value that came with the frame

    Returns:
        bool: True if CRC matches (frame is valid), False if corrupted
    """
    expected_crc = compute_crc(f"{seq}{data}")
    return expected_crc == received_crc
