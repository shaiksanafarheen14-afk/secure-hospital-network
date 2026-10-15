# Secure Hospital Network for Reliable Patient Data Communication

> **Module:** Reliable Data Transmission and Error Detection  
> **Branch:** `feature/reliable-transmission`  
> **Language:** Python 3 (no external dependencies)

---

## Overview

This project simulates a **secure hospital network** where patient data is transmitted reliably between hospital departments (e.g., Emergency Room → ICU). It demonstrates core **data communication** concepts taught in networking courses, implemented entirely in plain Python with beginner-friendly comments.

> ⚠️ **No real patient data is used.** All messages are fictional dummy data for educational purposes only.

---

## Features

| # | Feature | Module |
|---|---------|--------|
| 1 | **Department Nodes** — ER, ICU, Lab, Ward, Pharmacy as sender/receiver | `nodes.py` |
| 2 | **Framing** — Message split into fixed-size frames with sequence numbers | `framing.py` |
| 3 | **CRC Error Detection** — CRC-32 checksum computed and verified per frame | `crc.py` |
| 4 | **ACK / NAK Mechanism** — Positive and negative acknowledgements | `ack.py` |
| 5 | **Packet Corruption Simulation** — Noisy channel randomly corrupts frames | `channel.py` |
| 6 | **Retransmission** — Corrupted frames are automatically retransmitted | `go_back_n.py` |
| 7 | **Sliding Window & Go-Back-N ARQ** — Pipelined retransmission protocol | `go_back_n.py` |
| 8 | **Clear Terminal Output** — Colour-coded, step-by-step transmission log | `utils.py` |

---

## Folder Structure

```
HOSPITALSECURENETWORK/
├── reliable_transmission/
│   ├── __init__.py      # Package marker
│   ├── nodes.py         # Sender/Receiver department nodes + dummy data
│   ├── framing.py       # Frame creation and parsing
│   ├── crc.py           # CRC-32 error detection
│   ├── channel.py       # Noisy channel / corruption simulation
│   ├── ack.py           # ACK/NAK acknowledgement mechanism
│   ├── go_back_n.py     # Stop-and-Wait + Go-Back-N ARQ
│   └── utils.py         # Terminal display helpers
├── main.py              # ← Run this file
└── README.md            # This file
```

---

## How to Run

### Prerequisites
- **Python 3.7+** installed  
- No external packages required — standard library only

### Steps

```bash
# 1. Open a terminal in the project folder
cd path/to/HOSPITALSECURENETWORK

# 2. Run the simulation
python main.py
```

On **Windows** you can also double-click `main.py` if Python is associated with `.py` files, or use:

```powershell
python main.py
```

---

## What to Expect

The terminal will display:

1. **Setup** — Sender (ER) and receiver (ICU) departments, the dummy message, and the frames created from it.
2. **Stop-and-Wait ARQ** — Each frame sent one at a time; corrupted frames retransmitted immediately.
3. **Go-Back-N ARQ** — Multiple frames sent in a sliding window; on corruption the sender goes back and retransmits from the error point.
4. **Final Summary** — Comparison of both protocols: how many frames each delivered and the reconstructed message.
5. **Receiver Inbox** — Messages confirmed as received by the ICU department.

### Sample Output Snippet

```
════════════════════════════════════════════════════════════════════
  🏥  SECURE HOSPITAL NETWORK
  📡  Reliable Data Transmission & Error Detection
════════════════════════════════════════════════════════════════════

  → SEND Frame 0 [Seq:0 | Data:'PatientID:P002 Stat' | CRC:3A1F9B2C]
  ✓ OK      Frame 0  ← ✅ ACK(0)
  → SEND Frame 1 [Seq:1 | Data:'us:Critical BP:90/6' | CRC:7D4E1A3F]
  ✗ CORRUPT Frame 1  ← ❌ NAK(1)
  ⟳ RETRANSMIT from Frame 1  (retry 1/8)
  → SEND Frame 1 [Seq:1 | Data:'us:Critical BP:90/6' | CRC:7D4E1A3F]
  ✓ OK      Frame 1  ← ✅ ACK(1)
  ...
  ✅  MESSAGE DELIVERED SUCCESSFULLY to Intensive Care Unit (ICU)
```

---

## Configuration

You can tweak these constants at the top of `main.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `RANDOM_SEED` | `42` | Fix seed for reproducible results |
| `CORRUPTION_RATE` | `0.35` | Fraction of frames corrupted (0.0 – 1.0) |
| `WINDOW_SIZE` | `3` | Go-Back-N sliding window size |
| `MAX_RETRIES` | `8` | Max retransmission attempts per frame |
| `CHANNEL` | `"ER_to_ICU"` | Which department pair communicates |
| `MESSAGE_INDEX` | `1` | Which dummy message to transmit |

---

## Key Concepts Demonstrated

- **Framing** — Dividing a data stream into manageable frames with headers
- **CRC-32** — Hash-based error detection (industry standard in Ethernet, ZIP)
- **ARQ Protocols** — Automatic Repeat reQuest for reliable delivery
- **Sliding Window** — Pipelining frames to improve channel utilisation
- **Go-Back-N** — Retransmit the error frame and all subsequent frames

---

*Created for educational purposes — Secure Hospital Network Project*
