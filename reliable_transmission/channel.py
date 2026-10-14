"""
channel.py
----------
Simulates a noisy / unreliable network channel between two departments.

Features:
  - Packet corruption  : randomly flips a character in a frame's data
  - Corruption rate    : configurable probability (0.0 = perfect, 1.0 = always corrupts)
  - Deterministic mode : pass a fixed seed for reproducible demonstrations

The channel does NOT know about CRC — it just mangles the raw data.
"""

import random
import copy


# Default probability that any given frame gets corrupted
DEFAULT_CORRUPTION_RATE = 0.30   # 30 % chance of corruption per frame


def transmit(frame: dict,
             corruption_rate: float = DEFAULT_CORRUPTION_RATE,
             rng: random.Random = None) -> tuple:
    """
    Simulate sending a frame through an unreliable channel.

    Args:
        frame            : The frame dict to transmit (will NOT be mutated).
        corruption_rate  : Probability (0–1) that the frame gets corrupted.
        rng              : Optional random.Random instance for reproducibility.

    Returns:
        (received_frame, was_corrupted)
          received_frame : A copy of the frame, possibly with corrupted data.
          was_corrupted  : True if the channel introduced an error.
    """
    if rng is None:
        rng = random.Random()

    # Deep-copy so we never mutate the original frame
    received = copy.deepcopy(frame)
    was_corrupted = False

    if rng.random() < corruption_rate:
        was_corrupted = True
        received["data"] = _corrupt_data(received["data"], rng)

    return received, was_corrupted


def _corrupt_data(data: str, rng: random.Random) -> str:
    """
    Introduce a single-character corruption into a data string.

    Strategy: pick a random position and replace the character with
    a different ASCII character (simulating a bit-flip).

    Args:
        data : Original payload string.
        rng  : Random instance.

    Returns:
        Corrupted string.
    """
    if not data:
        return data

    pos = rng.randint(0, len(data) - 1)        # random position to corrupt
    original_char = data[pos]

    # Choose a replacement character that is definitely different
    replacement = chr((ord(original_char) + rng.randint(1, 25)) % 128)

    corrupted = data[:pos] + replacement + data[pos + 1 :]
    return corrupted
