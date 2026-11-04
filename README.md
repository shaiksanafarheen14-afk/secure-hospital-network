
# Secure Hospital Network for Reliable Patient Data Communication

**Module:** Feature/Routing Protocols  
**Branch:** `feature/routing-protocols`  
**Language:** Python 3.x (no external libraries required)

---

## 📋 Project Overview

This project simulates a **secure, reliable data-communication network** between
hospital departments (e.g., ICU, Emergency Room, Radiology, Pharmacy, Lab, OPD).

It demonstrates core **Data Link Layer** and **Transport Layer** concepts:
framing, CRC error detection, ACK/NACK acknowledgements, packet-corruption
simulation, retransmission, and two ARQ (Automatic Repeat reQuest) protocols —
**Sliding Window** and **Go-Back-N**.

> ⚠️ All patient data in this project is **completely dummy / fictional**.
> No real patient records are used.

---

## 🏗️ Folder Structure

```
Hospital Network/
├── feature_routing_protocols/
│   ├── __init__.py          ← Python package marker
│   ├── config.py            ← Department nodes & dummy scenarios
│   ├── framing.py           ← Message → fixed-size frames & reassembly
│   ├── crc.py               ← CRC-8 checksum (error detection)
│   ├── channel.py           ← Unreliable channel (corruption simulation)
│   ├── ack.py               ← ACK / NACK acknowledgement mechanism
│   ├── sliding_window.py    ← Sliding Window & Go-Back-N ARQ protocols
│   └── main.py              ← 🚀 Entry point — run this!
├── README.md
└── requirements.txt
```

---

## ✨ Features

| # | Feature | File |
|---|---------|------|
| 1 | Hospital departments as sender/receiver nodes (dummy data) | `config.py` |
| 2 | Message framing — splits messages into fixed-size frames | `framing.py` |
| 3 | CRC-8 error detection — checksum computed & verified per frame | `crc.py` |
| 4 | ACK / NACK acknowledgement mechanism | `ack.py` |
| 5 | Packet corruption simulation — random bit-flip in transit | `channel.py` |
| 6 | Retransmission — resends corrupted frames (up to MAX_RETRANSMIT) | `sliding_window.py` |
| 7 | Sliding Window ARQ protocol simulation | `sliding_window.py` |
| 8 | Go-Back-N ARQ protocol simulation | `sliding_window.py` |
| 9 | Clear step-by-step terminal output for every transmission | `main.py` |

---

## 🏥 Hospital Department Nodes (Dummy)

| Department | IP Address |
|------------|------------|
| ICU (Intensive Care Unit) | 192.168.1.10 |
| Radiology / Imaging | 192.168.1.20 |
| Pharmacy | 192.168.1.30 |
| Emergency Room | 192.168.1.40 |
| Laboratory | 192.168.1.50 |
| General OPD | 192.168.1.60 |

---

## 🧠 Concepts Explained

### 1. Framing
A long message is divided into small fixed-size chunks called **frames**.
Each frame carries a sequence number and a payload.

```
Message : "PATIENT#001 CRITICAL"
Frame 0 : "PATIENT#"
Frame 1 : "001 CRIT"
Frame 2 : "ICAL"
```

### 2. CRC (Cyclic Redundancy Check)
Before sending, the sender computes a **CRC-8 checksum** over the frame payload.
The receiver recomputes it and checks if they match. A mismatch means corruption.

### 3. ACK / NACK
- **ACK** → "Frame received correctly, send the next one."
- **NACK** → "Frame was corrupted, please resend it."

### 4. Corruption Simulation
The `channel.py` module randomly flips a character in the frame payload with a
configurable probability (`CORRUPTION_PROB` in `config.py`), simulating real
network noise.

### 5. Sliding Window ARQ
The sender keeps a **window** of unacknowledged frames. It sends all frames in
the window; any NACKed frame is individually retransmitted. The window slides
forward as frames are ACKed.

### 6. Go-Back-N ARQ
Like Sliding Window, but stricter: if frame N is NACKed, the sender **goes back**
to frame N and retransmits N and every frame that followed it in the window.

---

## ▶️ How to Run

### Prerequisites
- Python 3.7 or higher installed
- No third-party packages needed

### Step 1 — Open a terminal / PowerShell in the project root

```powershell
cd "c:\Users\Shaik Firdose\Hospital Network"
```

### Step 2 — Run the simulation

**Option A (recommended) — from the project root:**
```powershell
python -m feature_routing_protocols.main
```

**Option B — from inside the module folder:**
```powershell
cd feature_routing_protocols
python main.py
```

### Step 3 — Observe the output

You will see step-by-step output for each transmission scenario:
```
▓▓▓ SCENARIO 1 of 3  |  EMERGENCY → ICU ▓▓▓

  PROTOCOL: SLIDING WINDOW ARQ
  FROM    : EMERGENCY  →  TO: ICU
  MESSAGE : 'PATIENT#001 CRITICAL BP=180/120 TRANSFER_REQUESTED'

  [FRAMING] Message split into 7 frame(s)

  [WINDOW ] Sending frames 0–3
  [SENDER  ] Sending Frame 00 | payload='PATIENT#' | CRC=0xA3
  [CHANNEL ] ✔  Frame 00 arrived intact
  [RECEIVER] → ACK  for Frame 00  ✓
  ...

  ╔═══════════════════════════════════════════╗
  ║  STATUS : ✅ DELIVERED SUCCESSFULLY        ║
  ╚═══════════════════════════════════════════╝
```

### Optional — Run individual modules as self-tests

Each module can be run standalone for a quick demo:

```powershell
cd feature_routing_protocols
python framing.py       # Test framing / reassembly
python crc.py           # Test CRC checksum
python channel.py       # Test corruption simulation
python ack.py           # Test ACK / NACK
python sliding_window.py  # Test both ARQ protocols
```

---

## ⚙️ Configuration (`config.py`)

You can tweak these parameters to experiment:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `FRAME_SIZE` | `8` | Characters per frame payload |
| `WINDOW_SIZE` | `4` | Sliding-window / GBN window size |
| `CORRUPTION_PROB` | `0.25` | Probability (0–1) of frame corruption |
| `MAX_RETRANSMIT` | `5` | Max retransmission attempts before drop |

---

## 📁 Git Branch

This module is developed on branch:
```
feature/routing-protocols
```

---

## 👤 Authors / Contributors

- Hospital Network Team — Module: Feature/Routing Protocols

---

*This project is for educational purposes only. All patient data is fictional.*

# secure-hospital-network
