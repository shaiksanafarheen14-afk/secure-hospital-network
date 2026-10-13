# secure-hospital-network
# Secure Hospital Network for Reliable Patient Data Communication

A college Computer Networks project focused on secure, reliable, and fault-tolerant transmission of clinical telemetry and patient records across hospital department subnetworks.

---

## 1. Project Overview & Architecture
In modern healthcare systems, medical devices (ICU monitors, ECG machines, radiology scanners, and pharmacy dispensers) transmit vital patient records across local network infrastructures. This project demonstrates core networking principles:
- **Application & Presentation Layer:** Confidentiality and integrity via Authenticated Encryption (AES + HMAC-SHA256).
- **Transport & Network Layer:** Reliable end-to-end transport via Sliding Window and Go-Back-N (GBN) ARQ; shortest path routing via Dijkstra's Algorithm and Distance Vector Routing.
- **Data Link Layer:** Byte-oriented and bit-oriented framing via Character Stuffing (`DLE STX`/`ETX`) and Bit Stuffing (HDLC `01111110`); hardware-level error detection via Cyclic Redundancy Check (CRC-16 / CRC-32).
- **GUI & Performance Analysis:** Desktop dashboard with live telemetry KPI cards, vector charts, transmission table, and Wireshark trace importer.

---

## 2. Team Feature Branches & Responsibilities
Each team member develops their module in their assigned Git branch:

| Feature Branch | Assigned Area | Key Concepts |
|---|---|---|
| `feature/encryption` | Cryptography & Security | AES Encryption, Decryption, Session Key Management |
| `feature/framing` | Data Link Layer Framing | Character Stuffing, Bit Stuffing, Flag delimiters |
| `feature/crc` | Error Detection | CRC-16, CRC-32, Modulo-2 Arithmetic |
| `feature/reliable-transmission` | Transport Layer Reliability | Sliding Window, Go-Back-N ARQ, Timeouts, ACKs |
| `feature/routing-protocols` | Network Layer Routing | Dijkstra's Shortest Path, Distance Vector Routing |
| `feature/network-design` | Network Architecture | Subnetting, Topology Design, IP Addressing |
| **`feature/gui-analysis`** *(Current)* | **GUI & Performance Analysis** | **Desktop UI, Teammate Adapters, Charts, Metrics Engine** |

---

## 3. Quick Start Guide

### 3.1 Install Dependencies
Make sure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
```
*(Dependencies: `cryptography>=42.0.0`. Standard Tkinter is included with Python on Windows).*

### 3.2 Run the Application
Launch from the repository root:
```bash
python main.py
```
Or launch directly from the GUI analysis directory:
```bash
python gui-analysis/main.py
```

### 3.3 Run the Automated Unit Tests
To verify all performance calculations, cryptographic adapters, framing, CRC, and routing algorithms:
```bash
python -m unittest discover -s gui-analysis/tests -p "test_*.py"
```
*(26 tests passing).*

---

## 4. Teammate Module Integration Guide
To connect your feature branch into the GUI:
1. All protocol modules interface through the adapter layer located in `gui-analysis/modules/`.
2. When your feature branch is merged, place your functions in `crc/`, `encryption/`, `framing/`, `reliable-transmission/`, or `routing-protocols/`.
3. The adapter dynamically detects your functions without modifying the GUI code.
4. For detailed integration guides and test scripts, refer to [gui-analysis/README.md](file:///c:/Users/Lenovo/secure-hospital-network/gui-analysis/README.md).

---

## 5. Academic Disclaimer
*All patient names, vitals, and diagnostic notes displayed in this application are synthetic mock data for academic demonstration purposes only. All network latency, packet loss, and channel noise values are simulated algorithms to demonstrate computer networking principles.*