# =============================================================================
# channel.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Simulates an unreliable network channel that may corrupt frames
#           in transit, mimicking real-world packet loss / bit-flip errors.
# =============================================================================

import random
import copy
from config import CORRUPTION_PROB


def transmit_frame(frame: dict, corruption_prob: float = CORRUPTION_PROB) -> dict:
    """
    Simulate sending a frame over a potentially unreliable network channel.

    With probability `corruption_prob`, one character in the frame's payload
    is randomly replaced with a different character, simulating a bit-flip
    or data corruption event.

    Args:
        frame            (dict) : The frame to transmit (must have 'payload' key).
        corruption_prob  (float): Probability (0.0 – 1.0) of corruption.
                                  0.0 = perfect channel, 1.0 = always corrupt.

    Returns:
        dict: A copy of the frame, possibly with a corrupted payload.
              A 'corrupted' key (bool) is added to record what happened.
    """
    # Work on a copy so we don't modify the sender's original frame
    transmitted = copy.deepcopy(frame)

    # Roll the dice — did corruption occur?
    if random.random() < corruption_prob:
        payload = list(transmitted["payload"])  # Convert string to list of chars

        if payload:  # Safety: only corrupt if there's something to corrupt
            # Pick a random position in the payload to corrupt
            corrupt_idx = random.randint(0, len(payload) - 1)

            # Replace that character with a random printable ASCII character
            # chr(33) = '!' and chr(126) = '~' covers printable ASCII range
            original_char = payload[corrupt_idx]
            new_char = original_char
            while new_char == original_char:          # Ensure it actually changes
                new_char = chr(random.randint(33, 126))

            payload[corrupt_idx] = new_char
            transmitted["payload"] = "".join(payload)
            transmitted["corrupted"] = True           # Flag it as corrupted
    else:
        transmitted["corrupted"] = False              # Frame arrived intact

    return transmitted


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly: python channel.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from framing import create_frames
    from crc import attach_crc

    print("=== Channel Simulation Demo (10 transmissions) ===")
    sample_frame = attach_crc(create_frames("HELLO")[0])

    for trial in range(10):
        received = transmit_frame(sample_frame, corruption_prob=0.5)
        status   = "CORRUPTED ✗" if received["corrupted"] else "OK        ✓"
        print(f"  Trial {trial + 1:02d}: payload='{received['payload']}' | {status}")
