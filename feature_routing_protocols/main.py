# -*- coding: utf-8 -*-
# =============================================================================
# main.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Branch  : feature/routing-protocols
#
# PURPOSE : Entry point for the simulation.
#           Runs both Sliding Window ARQ and Go-Back-N ARQ for each
#           dummy hospital-department transmission scenario defined in
#           config.py, and prints a full step-by-step terminal log.
#
# RUN     : python main.py            (from inside feature_routing_protocols/)
#           python -m feature_routing_protocols.main  (from project root)
# =============================================================================

import os
import sys

# ── Windows console fix: use UTF-8 so special characters print correctly ──────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Make sure Python can find sibling modules regardless of where main.py
#    is invoked from. ──────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config         import TRANSMISSION_SCENARIOS, DEPARTMENTS, WINDOW_SIZE, \
                           FRAME_SIZE, CORRUPTION_PROB
from framing        import reassemble_message
from sliding_window import sliding_window_arq, go_back_n_arq


# ─────────────────────────────────────────────────────────────────────────────
# Terminal formatting helpers
# ─────────────────────────────────────────────────────────────────────────────
def banner(text: str, char: str = "█", width: int = 70) -> None:
    """Print a prominent banner for major sections."""
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width)


def section(text: str) -> None:
    """Print a section sub-header."""
    print(f"\n{'─' * 70}")
    print(f"  ▶  {text}")
    print(f"{'─' * 70}")


def result_box(sender: str, receiver: str,
               original: str, reassembled: str, protocol: str) -> None:
    """Print the final delivery result in a clear summary box."""
    match = (original == reassembled)
    status = "✅ DELIVERED SUCCESSFULLY" if match else "❌ DELIVERY FAILED"
    print(f"""
  ╔══════════════════════════════════════════════════════════════════════╗
  ║  PROTOCOL  : {protocol:<57}║
  ║  FROM      : {sender:<57}║
  ║  TO        : {receiver:<57}║
  ║  ORIGINAL  : {original[:57]:<57}║
  ║  RECEIVED  : {reassembled[:57]:<57}║
  ║  STATUS    : {status:<57}║
  ╚══════════════════════════════════════════════════════════════════════╝""")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SIMULATION
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Welcome header ───────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  [+] SECURE HOSPITAL NETWORK - RELIABLE PATIENT DATA COMMUNICATION")
    print("      Module  : Feature / Routing Protocols")
    print("      Branch  : feature/routing-protocols")
    print("=" * 70)

    print(f"\n  Network Parameters:")
    print(f"    Frame Size       : {FRAME_SIZE} characters per frame")
    print(f"    Window Size      : {WINDOW_SIZE} frames")
    print(f"    Corruption Prob  : {CORRUPTION_PROB * 100:.0f}%  "
          f"(chance a frame is corrupted in transit)")

    print(f"\n  Registered Hospital Departments:")
    for dept, ip in DEPARTMENTS.items():
        print(f"    {dept:<14}  →  {ip}")

    # ── Run each transmission scenario ───────────────────────────────────────
    for scenario_idx, scenario in enumerate(TRANSMISSION_SCENARIOS, start=1):
        sender   = scenario["sender"]
        receiver = scenario["receiver"]
        message  = scenario["message"]

        banner(f"SCENARIO {scenario_idx} of {len(TRANSMISSION_SCENARIOS)}  |  "
               f"{sender} → {receiver}", char="▓")

        print(f"\n  Sender IP   : {DEPARTMENTS.get(sender,   'Unknown')}")
        print(f"  Receiver IP : {DEPARTMENTS.get(receiver, 'Unknown')}")
        print(f"  Message     : '{message}'")
        print(f"  Length      : {len(message)} characters")

        # ────────────────────────────────────────────────────────────────────
        # PART A — SLIDING WINDOW ARQ
        # ────────────────────────────────────────────────────────────────────
        section("PART A: SLIDING WINDOW ARQ")
        sw_frames     = sliding_window_arq(sender, receiver, message)
        sw_reassembled = reassemble_message(sw_frames)
        result_box(sender, receiver, message, sw_reassembled,
                   "Sliding Window ARQ")

        # ────────────────────────────────────────────────────────────────────
        # PART B — GO-BACK-N ARQ
        # ────────────────────────────────────────────────────────────────────
        section("PART B: GO-BACK-N ARQ")
        gbn_frames      = go_back_n_arq(sender, receiver, message)
        gbn_reassembled = reassemble_message(gbn_frames)
        result_box(sender, receiver, message, gbn_reassembled,
                   "Go-Back-N ARQ")

    # ── Final summary ─────────────────────────────────────────────────────────
    banner("ALL SCENARIOS COMPLETE - SIMULATION FINISHED", char="=")
    print("\n  Summary of concepts demonstrated:")
    print("    [OK] Patient department nodes as sender / receiver")
    print("    [OK] Message framing (fixed-size character frames)")
    print("    [OK] CRC-8 error detection (checksum per frame)")
    print("    [OK] Packet corruption simulation (random bit-flip)")
    print("    [OK] ACK / NACK acknowledgement mechanism")
    print("    [OK] Retransmission on error (up to MAX_RETRANSMIT times)")
    print("    [OK] Sliding Window ARQ protocol")
    print("    [OK] Go-Back-N ARQ protocol")
    print("\n  All data used is DUMMY / FICTIONAL - no real patient records.\n")
    print("=" * 70 + "\n")


# ── Standard Python entry-point guard ────────────────────────────────────────
if __name__ == "__main__":
    main()
