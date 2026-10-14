# Secure Hospital Network for Reliable Patient Data Communication

## Module: Reliable Data Transmission and Error Detection

> **Branch:** `feature/reliable-transmission`
> **Language:** Python 3.8+ (standard library only — no pip installs needed)

---

## 🏥 Overview

This project simulates a **reliable data communication system** between hospital departments (e.g., Radiology sending patient records to the Emergency Ward). It demonstrates core networking concepts from scratch using beginner-friendly, well-commented Python code.

---

## ✨ Features

| # | Feature | File |
|---|---------|------|
| 1 | Department sender/receiver nodes with dummy patient data | `departments.py` |
| 2 | Message framing — splits messages into fixed-size frames | `framing.py` |
| 3 | CRC-8 error detection | `crc.py` |
| 4 | ACK / NACK acknowledgement mechanism | `ack.py` |
| 5 | Packet corruption simulation (noisy channel) | `channel.py` |
| 6 | Automatic retransmission on error detection | `sliding_window.py` |
| 7 | Sliding Window + Go-Back-N ARQ | `sliding_window.py` |
| 8 | Colour-coded terminal output showing every transmission step | `display.py` |

---

## 📁 Folder Structure

```
reliable_transmission/
├── main.py            ← Entry point
├── departments.py     ← Sender / Receiver department nodes
├── framing.py         ← Message → frames conversion
├── crc.py             ← CRC-8 checksum logic
├── channel.py         ← Noisy channel (corruption simulator)
├── ack.py             ← ACK / NACK logic
├── sliding_window.py  ← Sliding Window + Go-Back-N ARQ
├── display.py         ← Colour terminal output helpers
├── requirements.txt   ← No external packages needed
└── README.md          ← This file
```

---

## 🚀 How to Run

### Prerequisites
- Python **3.8 or higher** installed
- A terminal that supports ANSI colour codes  
  (PowerShell, CMD, Git Bash, macOS Terminal, Linux shell)

### Step 1 — Navigate to the project folder
```bash
cd HOSPITALPROJECT/reliable_transmission
```

### Step 2 — Run with default settings
```bash
python main.py
```

### Step 3 — Optional: customise parameters
```bash
# Change window size, corruption rate, and RNG seed
python main.py --window 4 --corruption 0.4 --seed 7

# All available options
python main.py --help
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--window` | `3` | Sliding window size (frames in flight) |
| `--corruption` | `0.30` | Channel corruption rate (0.0 – 1.0) |
| `--seed` | `42` | RNG seed (use different seeds to vary results) |
| `--frame-size` | `50` | Characters per frame payload |

---

## 🔬 How It Works (Step by Step)

```
[Radiology Dept]          [Noisy Channel]          [Emergency Ward]
      │                         │                          │
      │── Frame 0 + CRC ──────►│── (may corrupt) ───────►│── CRC check
      │                         │                          │── ACK / NACK
      │◄─────────────────────────────── ACK 0 ────────────│
      │── Frame 1 + CRC ──────►│── (may corrupt) ───────►│
      │◄─────────────────────────────── NACK 1 ───────────│  ← error!
      │── Go-Back-N: retransmit from Frame 1 ─────────────│
      ...
      │   All frames delivered → message reassembled       │
```

1. **Framing**: The message is split into 50-character frames, each tagged with a CRC-8 checksum.  
2. **Transmission**: Frames are sent through the noisy channel (which may flip characters).  
3. **Error Detection**: The receiver recomputes CRC; a mismatch triggers a NACK.  
4. **Go-Back-N ARQ**: On NACK, the sender goes back to the failed frame and retransmits that frame and all subsequent ones in the window.  
5. **Reassembly**: Once all frames are received intact, the original message is reconstructed.

---

## 🔒 Data Privacy

This project uses **entirely fictional, dummy patient data**. No real patient names, diagnoses, or medical information are included anywhere in the codebase.

---

## 🧪 Example Output (abbreviated)

```
══════════════════════════════════════════════════════════════════════
  Secure Hospital Network for Reliable Patient Data Communication
══════════════════════════════════════════════════════════════════════

── Network Nodes ────────────────────────────────────────────────────
  SENDER   → Radiology Department
  RECEIVER → Emergency Ward

── Go-Back-N ARQ Transmission ───────────────────────────────────────
  🪟 Window base=0 | Frames in window: [0, 1, 2]
  📤 Sending   Frame [00] | Data: 'Patient: John Doe | Age…' | CRC: A3
  ✅ Received  Frame [00] — CRC OK
  📩 ACK sent  for Frame [00]
  📤 Sending   Frame [01] | Data: 'Patient: Jane Roe | Age…' | CRC: 7F
  ⚡ Corrupted Frame [01] — bit-flip injected by channel
  ❌ Error     Frame [01] — CRC mismatch detected!
  📩 NACK sent for Frame [01] — requesting retransmission
  🔄 Retransmitting Frame [01]
  ...

══════════════════════════════════════════════════════════════════════
  🏥 FINAL MESSAGE DELIVERED SUCCESSFULLY
══════════════════════════════════════════════════════════════════════
  From     : Radiology Department
  To       : Emergency Ward
  Message  : Patient: John Doe | Age: 45 | Diagnosis: Hypertension…
══════════════════════════════════════════════════════════════════════
```

---

## 📚 Concepts Covered

- **Framing** — dividing data into manageable transmission units  
- **CRC (Cyclic Redundancy Check)** — polynomial-based error detection  
- **ACK/NACK** — positive and negative acknowledgements  
- **Stop-and-Wait vs Sliding Window** — efficiency comparison  
- **Go-Back-N ARQ** — automatic repeat request on error  
- **Noise simulation** — modelling real-world channel unreliability  
