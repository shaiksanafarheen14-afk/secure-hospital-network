# =============================================================================
# main.py — Entry Point for the Hospital Network Simulation
# =============================================================================
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Reliable Data Transmission and Error Detection
# Branch  : feature/reliable-transmission
#
# HOW TO RUN:
#   python main.py
#
# WHAT IT DOES:
#   1. Sets up two hospital departments as sender and receiver nodes
#   2. Picks a dummy patient message and breaks it into frames
#   3. Runs Stop-and-Wait ARQ (window = 1) to show basic retransmission
#   4. Runs Go-Back-N ARQ (window = 3) to show pipelined sliding-window ARQ
#   5. Prints a final summary comparing both protocols
#
# NOTE: No real patient data is used. All data is fictional for demo purposes.
# =============================================================================

from reliable_transmission.nodes import DepartmentNode
from reliable_transmission.framing import create_frames
from reliable_transmission.channel import set_seed
from reliable_transmission.go_back_n import run_go_back_n, run_stop_and_wait
from reliable_transmission.utils import (
    print_banner,
    print_section,
    print_channel_info,
    print_frames_summary,
    print_success,
    print_final_summary,
)

# ── Configuration ─────────────────────────────────────────────────────────────

# Fix random seed so results are reproducible on every run.
# Change this value (or remove set_seed) to see different corruption patterns.
RANDOM_SEED = 42

# Probability that any frame gets corrupted in transit (0.0 = perfect channel)
CORRUPTION_RATE = 0.35

# Go-Back-N window size (how many frames can be in-flight simultaneously)
WINDOW_SIZE = 3

# Maximum retransmission attempts before giving up on a frame
MAX_RETRIES = 8

# ── Scenario Definition ───────────────────────────────────────────────────────

# Choose a communication channel (key must exist in nodes.DUMMY_MESSAGES)
CHANNEL = "ER_to_ICU"

# Select which message in that channel to transmit (0-based index)
MESSAGE_INDEX = 1

# ── Main Simulation ───────────────────────────────────────────────────────────

def main():
    """Main function — orchestrates the full simulation."""

    # --- 1. Setup nodes (departments) ---
    set_seed(RANDOM_SEED)   # Fix randomness for reproducibility

    sender   = DepartmentNode("Emergency Room (ER)",        role="sender")
    receiver = DepartmentNode("Intensive Care Unit (ICU)",  role="receiver")

    # --- 2. Get dummy message ---
    messages = sender.get_messages(CHANNEL)
    message  = messages[MESSAGE_INDEX]  # Pick the second message in the list

    # --- 3. Print banner and setup info ---
    print_banner()
    print_section("TRANSMISSION SETUP")
    print_channel_info(sender.name, receiver.name, message)

    # --- 4. Frame the message ---
    frames = create_frames(message)
    print_frames_summary(frames)

    # =========================================================================
    # SIMULATION A: Stop-and-Wait ARQ  (Sliding Window with size = 1)
    # =========================================================================
    # Reset seed so both simulations face the same random corruption pattern
    set_seed(RANDOM_SEED)
    saw_data = run_stop_and_wait(
        frames,
        corruption_rate=CORRUPTION_RATE,
        max_retries=MAX_RETRIES,
    )
    saw_message = "".join(saw_data) if saw_data else None

    if saw_message:
        print_success(saw_message, receiver.name)
        receiver.receive(saw_message)

    # =========================================================================
    # SIMULATION B: Go-Back-N ARQ  (Sliding Window with size = WINDOW_SIZE)
    # =========================================================================
    set_seed(RANDOM_SEED)  # Same seed → same corruption pattern
    gbn_data = run_go_back_n(
        frames,
        window_size=WINDOW_SIZE,
        corruption_rate=CORRUPTION_RATE,
        max_retries=MAX_RETRIES,
    )
    gbn_message = "".join(gbn_data) if gbn_data else None

    if gbn_message:
        print_success(gbn_message, receiver.name)
        receiver.receive(gbn_message)

    # =========================================================================
    # 5. Final Summary
    # =========================================================================
    results = [
        ("Stop-and-Wait (W=1)",       len(saw_data),  saw_message),
        (f"Go-Back-N (W={WINDOW_SIZE})", len(gbn_data), gbn_message),
    ]
    print_final_summary(results)

    # Show receiver's inbox
    receiver.show_inbox()
    print()


if __name__ == "__main__":
    main()
