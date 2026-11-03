# =============================================================================
# crc.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Implements CRC-8 (Cyclic Redundancy Check) for error detection.
#           The sender computes a checksum and appends it to each frame.
#           The receiver recomputes the checksum and verifies integrity.
# =============================================================================

# CRC-8 polynomial: 0x07  (x^8 + x^2 + x + 1)
# This is a simple, well-known 8-bit CRC used in many embedded systems.
CRC8_POLY = 0x07


def compute_crc8(data: str) -> int:
    """
    Compute an 8-bit CRC checksum for a given string.

    How it works (simplified):
      1. Start with crc = 0.
      2. For each character, XOR its ASCII value into crc.
      3. For each of the 8 bits, if the top bit is set, shift left and XOR
         with the polynomial; otherwise just shift left.
      4. The final crc (masked to 8 bits) is the checksum.

    Args:
        data (str): The frame payload string.

    Returns:
        int: An 8-bit CRC checksum (0–255).
    """
    crc = 0  # Starting value

    for char in data:
        # XOR current CRC with the byte value of this character
        crc ^= ord(char)

        # Process each of the 8 bits
        for _ in range(8):
            if crc & 0x80:          # If the most-significant bit is 1
                crc = (crc << 1) ^ CRC8_POLY
            else:
                crc <<= 1           # Just shift left by 1

            crc &= 0xFF             # Keep only the lowest 8 bits

    return crc


def attach_crc(frame: dict) -> dict:
    """
    Compute and attach the CRC checksum to a frame dictionary.

    Adds a key 'crc' to the frame containing its checksum.

    Args:
        frame (dict): Frame with at least a 'payload' key.

    Returns:
        dict: The same frame dict with a new 'crc' key.
    """
    frame["crc"] = compute_crc8(frame["payload"])
    return frame


def verify_crc(frame: dict) -> bool:
    """
    Verify the CRC of a received frame.

    Recomputes the CRC from the payload and compares with the stored value.

    Args:
        frame (dict): Frame with 'payload' and 'crc' keys.

    Returns:
        bool: True if the frame is intact, False if it is corrupted.
    """
    expected_crc = compute_crc8(frame["payload"])
    return expected_crc == frame.get("crc", -1)


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly: python crc.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_payload = "CRITICAL"
    crc_val = compute_crc8(test_payload)
    print("=== CRC-8 Demo ===")
    print(f"  Payload : '{test_payload}'")
    print(f"  CRC-8   : {crc_val}  (0x{crc_val:02X})")

    frame = {"seq_num": 0, "payload": test_payload, "total": 1}
    frame = attach_crc(frame)
    print(f"\n  Frame with CRC: {frame}")
    print(f"  Verification  : {'PASS ✓' if verify_crc(frame) else 'FAIL ✗'}")

    # Simulate corruption by changing one character
    frame["payload"] = "CRITI@AL"
    print(f"\n  After corruption: payload='{frame['payload']}'")
    print(f"  Verification     : {'PASS ✓' if verify_crc(frame) else 'FAIL ✗'}")
