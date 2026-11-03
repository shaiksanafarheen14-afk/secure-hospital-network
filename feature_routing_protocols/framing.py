# =============================================================================
# framing.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Splits a raw text message into fixed-size frames and reassembles
#           received frames back into the original message.
# =============================================================================

from config import FRAME_SIZE


def create_frames(message: str, frame_size: int = FRAME_SIZE) -> list:
    """
    Divide a message string into a list of fixed-size character chunks (frames).

    Example:
        message   = "HELLO WORLD"
        frame_size = 4
        frames    = ["HELL", "O WO", "RLD"]

    Args:
        message    (str): The full plaintext message to be sent.
        frame_size (int): Number of characters in each frame payload.

    Returns:
        list of dict: Each dict has:
            - seq_num (int)  : Frame sequence number (0-based).
            - payload (str)  : The character chunk for this frame.
            - total   (int)  : Total number of frames in this message.
    """
    frames = []

    # Split message into chunks of `frame_size` characters
    chunks = [message[i: i + frame_size] for i in range(0, len(message), frame_size)]

    for idx, chunk in enumerate(chunks):
        frame = {
            "seq_num": idx,          # Sequence number of this frame
            "payload": chunk,        # Actual data payload
            "total":   len(chunks),  # Total frame count (useful at receiver)
        }
        frames.append(frame)

    return frames


def reassemble_message(received_frames: list) -> str:
    """
    Reassemble the original message from a list of successfully received frames.

    Frames are sorted by sequence number before joining, so out-of-order
    delivery is handled gracefully.

    Args:
        received_frames (list of dict): Frames that arrived without errors.

    Returns:
        str: The reconstructed original message.
    """
    # Sort frames by their sequence number just in case they arrived out of order
    sorted_frames = sorted(received_frames, key=lambda f: f["seq_num"])

    # Concatenate all payloads in order
    message = "".join(f["payload"] for f in sorted_frames)
    return message


# ---------------------------------------------------------------------------
# Quick self-test (run this file directly: python framing.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = "PATIENT#001 CRITICAL BP=180/120"
    frames = create_frames(sample)
    print("=== Framing Demo ===")
    for f in frames:
        print(f"  Frame {f['seq_num']:02d}/{f['total'] - 1}: '{f['payload']}'")

    rebuilt = reassemble_message(frames)
    print(f"\nReassembled: '{rebuilt}'")
    print(f"Match: {rebuilt == sample}")
