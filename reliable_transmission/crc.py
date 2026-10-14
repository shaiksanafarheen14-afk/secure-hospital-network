"""
crc.py
------
Implements CRC-8 (Cyclic Redundancy Check) error detection.

How CRC works (beginner explanation):
  1. Sender treats the data as a big binary number.
  2. It divides that number by a fixed polynomial (the "generator").
  3. The remainder of the division is the CRC checksum.
  4. The checksum is sent along with the data.
  5. The receiver performs the same division on the received data.
  6. If the remainder is 0 → no error.  If non-zero → data was corrupted.

We use CRC-8 (polynomial 0x07) for simplicity.
"""

# CRC-8 generator polynomial (0x07 = x^8 + x^2 + x + 1)
CRC8_POLYNOMIAL = 0x07


def compute_crc8(data: str) -> int:
    """
    Compute the CRC-8 checksum for a string of data.

    Args:
        data: The input string to checksum.

    Returns:
        An integer in range 0–255 representing the CRC byte.
    """
    crc = 0  # start with register = 0

    for char in data:
        # XOR the next data byte into the high byte of the CRC register
        crc ^= ord(char)

        # Process each of the 8 bits
        for _ in range(8):
            if crc & 0x80:          # if the top bit is set …
                crc = (crc << 1) ^ CRC8_POLYNOMIAL  # … XOR with polynomial
            else:
                crc <<= 1           # … otherwise just shift left

            crc &= 0xFF             # keep only the lower 8 bits

    return crc


def crc_to_hex(crc: int) -> str:
    """Return CRC as a two-character uppercase hex string (e.g. '3F')."""
    return f"{crc:02X}"


def verify_crc8(data: str, received_crc: int) -> bool:
    """
    Check whether the received CRC matches the computed CRC for the data.

    Args:
        data         : The received data string.
        received_crc : The CRC value that was transmitted alongside the data.

    Returns:
        True if CRC matches (no error detected), False otherwise.
    """
    expected = compute_crc8(data)
    return expected == received_crc
