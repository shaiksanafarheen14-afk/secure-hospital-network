# =============================================================================
# channel.py — Packet Corruption Simulation
# =============================================================================
# In real networks, frames can be corrupted during transmission due to:
#   - Electrical interference / noise
#   - Hardware faults
#   - Signal degradation
#
# This module simulates a "noisy channel" that randomly corrupts frames.
# Corruption is modelled by tampering with the CRC value of a frame,
# making the receiver's CRC check fail — just as a real bit-flip would.
# =============================================================================

import random
import copy


# Default probability that any given frame gets corrupted (0.0 to 1.0)
# 0.3 means ~30% chance of corruption per frame
DEFAULT_CORRUPTION_RATE = 0.3


def transmit_frame(frame: dict, corruption_rate: float = DEFAULT_CORRUPTION_RATE) -> dict:
    """
    Simulates sending a frame through a noisy channel.

    With probability `corruption_rate`, the frame's CRC is altered to
    simulate a bit-flip error during transmission.

    Args:
        frame            (dict):  The original frame to transmit
        corruption_rate  (float): Probability of corruption (0.0 – 1.0)

    Returns:
        dict: The frame as received (possibly corrupted)
    """
    # Deep-copy so we don't modify the original frame object
    received_frame = copy.deepcopy(frame)

    if random.random() < corruption_rate:
        # Corrupt the CRC by flipping it to a bogus value
        received_frame["crc"] = "CORRUPTED"
        received_frame["_corrupted"] = True   # Internal flag for display
    else:
        received_frame["_corrupted"] = False

    return received_frame


def set_seed(seed: int):
    """
    Sets the random seed for reproducible simulation results.

    Args:
        seed (int): Any integer seed value
    """
    random.seed(seed)
