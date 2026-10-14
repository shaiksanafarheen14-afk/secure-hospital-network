"""
main.py
-------
Entry point for the simulation.

Orchestrates the full pipeline:
  1. Build sender/receiver department nodes.
  2. Compose a dummy patient-data message.
  3. Split the message into frames (with CRC).
  4. Run the Sliding Window / Go-Back-N ARQ simulation over a noisy channel.
  5. Reassemble the received frames into the original message.
  6. Print a final delivery report.

Run with:
    python main.py
or with custom parameters:
    python main.py --window 4 --corruption 0.4 --seed 7
"""

import argparse
import sys

# Add the current directory to sys.path so imports work regardless of
# where the user runs the script from.
sys.path.insert(0, ".")

import display        as ui
from departments  import get_sender, get_receiver, get_message
from framing      import create_frames, reassemble
from sliding_window import run_go_back_n


# ── Command-line argument parsing ────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hospital Reliable Data Transmission Simulation (Go-Back-N ARQ)"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=3,
        help="Sliding window size (default: 3)",
    )
    parser.add_argument(
        "--corruption",
        type=float,
        default=0.30,
        help="Channel corruption rate 0.0–1.0 (default: 0.30 = 30%%)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible channel simulation (default: 42)",
    )
    parser.add_argument(
        "--frame-size",
        type=int,
        default=50,
        help="Characters per frame payload (default: 50)",
    )
    return parser.parse_args()


# ── Main simulation ───────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    # ── 1. Header banner ────────────────────────────────────────────────────
    ui.banner("Secure Hospital Network for Reliable Patient Data Communication")
    ui.banner("Module: Reliable Data Transmission and Error Detection")

    # ── 2. Department node setup ─────────────────────────────────────────────
    sender   = get_sender()
    receiver = get_receiver()

    ui.section("Network Nodes")
    ui.info(f"SENDER   → {sender.name}  ({sender.description})")
    ui.info(f"RECEIVER → {receiver.name}  ({receiver.description})")

    # ── 3. Message composition ───────────────────────────────────────────────
    message = get_message()

    ui.section("Original Message (Dummy Patient Data)")
    # Print each record on its own line for readability
    for record in message.split(" || "):
        ui.info(f"  • {record.strip()}")

    # ── 4. Framing ───────────────────────────────────────────────────────────
    frames = create_frames(message, frame_size=args.frame_size)

    ui.section("Framing")
    ui.info(f"Message length : {len(message)} characters")
    ui.info(f"Frame size     : {args.frame_size} characters per frame")
    ui.info(f"Total frames   : {len(frames)}")
    print()

    for f in frames:
        preview = f["data"][:30].replace("\n", " ")
        ui.info(f"  Frame [{f['seq']:02d}] | CRC: {f['crc_hex']} | Preview: {preview!r}…")

    # ── 5. Transmission (Sliding Window / Go-Back-N) ─────────────────────────
    print()
    ui.info(f"Window size    : {args.window}")
    ui.info(f"Corruption rate: {args.corruption * 100:.0f}%")
    ui.info(f"RNG seed       : {args.seed}")

    received_frames = run_go_back_n(
        frames,
        window_size     = args.window,
        corruption_rate = args.corruption,
        seed            = args.seed,
    )

    # ── 6. Reassembly ────────────────────────────────────────────────────────
    ui.section("Message Reassembly")
    reconstructed = reassemble(received_frames)

    if reconstructed == message:
        ui.info("✔ Reconstructed message matches the original exactly.")
    else:
        ui.info("⚠ Warning: Reconstructed message differs from original!")

    # ── 7. Final delivery report ─────────────────────────────────────────────
    ui.delivery_report(sender.name, receiver.name, reconstructed[:120] + "…")


if __name__ == "__main__":
    main()
