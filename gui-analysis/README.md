# GUI and Performance Analysis
## Secure Hospital Network for Reliable Patient Data Communication

**Module Responsibility:** Graphical User Interface (GUI), Teammate Module Integration Adapters, and Network Performance Analysis.  
**Working Branch:** `feature/gui-analysis`  
**Framework:** Python 3.12, Tkinter (Desktop GUI), `cryptography` (Fernet authenticated encryption)

---

## 1. Overview & Purpose
This module provides a unified desktop dashboard for monitoring and demonstrating secure, reliable communication of patient health data across hospital clinical subnets (e.g., ICU, Cardiology, Radiology, Pharmacy, Emergency, and Central Server).

### Key Features
1. **System Health Dashboard:**
   - Real-time KPI Stat Cards: Total Packets, Delivered Count, Packet Loss Rate (%), Retransmission Count, Average Delay (ms), and Network Throughput (kbps).
   - Hospital subnetwork node status monitor (ICU, Cardiology, Radiology, Pharmacy, Emergency, Server).
   - Protocol adapter registry showing active implementations versus pending teammate integrations.
   - Live activity stream with sanitized payload logs (protecting patient confidentiality).

2. **Secure Patient Data Communication:**
   - Synthetic clinical patient records only (strictly HIPAA/GDPR-compliant mock samples; never real patient data).
   - Authenticated Symmetric Encryption using standard `cryptography.fernet.Fernet` (AES-128 in CBC mode + HMAC-SHA256 integrity tag).
   - Dynamic session key generation and key rotation.
   - Interactive channel tampering simulator (corrupting a ciphertext byte causes HMAC authentication failure at receiver, rejecting compromised data).

3. **Computer Networks Protocol Laboratory:**
   - **Framing & Stuffing:** Character Stuffing (`[DLE STX]` / `[DLE ETX]` with `DLE DLE` escaping) and Bit Stuffing (HDLC `01111110` flag with zero-insertion after 5 consecutive ones).
   - **Error Detection (CRC):** CRC-16-CCITT and CRC-32 checksum generation, intentional bit error injection, and step-by-step Modulo-2 XOR division visualizer.
   - **Reliable Data Transfer:** Go-Back-N (GBN) ARQ sliding window simulation with configurable window size $N$, sequence numbers, timeouts, and loss recovery.
   - **Routing Protocols:** Hospital network graph topology with Dijkstra's shortest path finder (latency metric) and Distance Vector (Bellman-Ford) routing table matrix.

4. **Performance Analysis & Trace Importer:**
   - Real-time vector Canvas line chart (latency progression per packet with average reference line).
   - Categorical delivery breakdown bar chart (Delivered, Retransmitted, Corrupted, Lost).
   - Detailed transmission results table (`ttk.Treeview`) with per-packet status, latency, frame size, and retry counts.
   - Batch simulation runner for network stress testing (configurable burst size and loss probability).
   - Wireshark CSV trace importer (`No.`, `Time`, `Source`, `Destination`, `Protocol`, `Length`, `Info`) and simulation log exporter.

---

## 2. Directory Structure
```text
gui-analysis/
├── README.md                    # This comprehensive guide
├── main.py                      # Local GUI launcher script
├── sample_data/
│   └── sample_hospital_wireshark_trace.csv  # Pre-generated Wireshark CSV trace
├── core/                        # Data structures and calculation logic (100% GUI-independent)
│   ├── __init__.py
│   ├── models.py                # PatientRecord, Packet, TransmissionResult, DeliveryStatus
│   ├── metrics.py               # Delay, Throughput, Loss %, Success %, Jitter formulas
│   └── synthetic_data.py        # Realistic synthetic patient vitals and mock clinical notes
├── modules/                     # Protocol adapters & integration interfaces
│   ├── __init__.py
│   ├── base_adapter.py          # Base adapter class with teammate discovery mechanism
│   ├── encryption_adapter.py    # Authenticated encryption (Fernet / AES-128-CBC + HMAC)
│   ├── framing_adapter.py       # Character stuffing and Bit stuffing algorithms
│   ├── crc_adapter.py           # CRC-16, CRC-32, bit error injection, modulo-2 division
│   ├── reliable_transmission_adapter.py # Go-Back-N ARQ & Sliding Window engine
│   ├── routing_adapter.py       # Dijkstra algorithm and Distance Vector routing matrix
│   └── wireshark_parser.py      # Wireshark CSV parser & transmission log exporter
├── gui/                         # Presentation Layer (Tkinter)
│   ├── __init__.py
│   ├── theme.py                 # Clinical technology dark palette, fonts, and styles
│   ├── widgets.py               # Reusable StatCards, Canvas Line Chart & Bar Chart
│   ├── app.py                   # Main window coordinator, status bar, and shared state
│   └── tabs/
│       ├── __init__.py
│       ├── dashboard_tab.py     # High-level overview, KPI cards, activity feed
│       ├── patient_comm_tab.py  # Secure clinical transfer demo & crypto inspector
│       ├── protocols_tab.py     # Framing, CRC, Go-Back-N, and Routing deep-dive views
│       └── performance_tab.py   # Transmission log table, charts, stress testing, import/export
└── tests/                       # Automated unit tests (26 test cases)
    ├── __init__.py
    ├── test_metrics.py          # Validates throughput, loss %, delay, and jitter formulas
    ├── test_crypto.py           # Validates encryption, decryption, and tamper rejection
    ├── test_framing.py          # Validates bit and character stuffing round-trips
    ├── test_crc.py              # Validates CRC checksums, modulo-2 division, and error detection
    ├── test_reliable_transmission.py # Validates Go-Back-N packet delivery and recovery
    ├── test_routing.py          # Validates Dijkstra shortest path and Distance Vector convergence
    └── test_wireshark_parser.py # Validates CSV import, Wireshark parsing, and export
```

---

## 3. How to Run the Application

### 3.1 Prerequisites
Ensure Python 3.10+ is installed on your system.
Install the required dependencies:
```bash
pip install -r requirements.txt
```
*(Dependencies: `cryptography>=42.0.0` for authenticated encryption. Tkinter is included in standard Python on Windows).*

### 3.2 Launching the GUI
From the repository root:
```bash
python main.py
```
Or from inside the `gui-analysis` directory:
```bash
python gui-analysis/main.py
```

### 3.3 Running Automated Unit Tests
To run all 26 unit tests from the repository root:
```bash
python -m unittest discover -s gui-analysis/tests -p "test_*.py"
```
Expected output:
```text
Ran 26 tests in 0.016s
OK
```

---

## 4. How the GUI Communicates with Networking Modules
The project follows the **Adapter Pattern** and **Separation of Concerns**:
1. **Decoupled Architecture:**
   - None of the networking math, cryptography, framing, or routing logic resides inside GUI widget classes.
   - Logic lives in `core/` and `modules/`.
2. **Adapter Layer (`modules/base_adapter.py`):**
   - Each networking concept has a dedicated adapter class (`EncryptionAdapter`, `FramingAdapter`, `CRCAdapter`, `ReliableTransmissionAdapter`, `RoutingAdapter`).
   - Adapters maintain an `AdapterStatus` (`LOCAL_REFERENCE`, `TEAMMATE_INTEGRATED`, `PENDING_EXTERNAL`).
   - If a teammate on another branch (e.g., `feature/crc`, `feature/framing`) merges their module into the repository, the adapter automatically detects the module in `sys.path` and delegates execution to their code without requiring a rewrite of the GUI!
   - Until teammates merge their code, the adapter runs a verified internal reference implementation so that the GUI remains 100% functional today.

---

## 5. Performance Metric Calculations

All mathematical calculations are performed in `core/metrics.py`:

1. **Packet Loss Rate (%):**
   $$\text{Loss Rate} = \left(\frac{\text{Total Packets Lost}}{\text{Total Packets Sent}}\right) \times 100$$

2. **Transmission Success Rate (%):**
   $$\text{Success Rate} = \left(\frac{\text{Total Packets Delivered}}{\text{Total Packets Sent}}\right) \times 100$$

3. **Network Throughput (kbps):**
   $$\text{Throughput} = \frac{\text{Successfully Delivered Bytes} \times 8}{\text{Elapsed Duration (Seconds)} \times 1000}$$

4. **Average Delay (ms):**
   $$\text{Average Delay} = \frac{1}{N} \sum_{i=1}^{N} \text{Latency}_i$$

5. **Network Jitter (Delay Variance in ms - RFC 3550 standard):**
   $$\text{Jitter} = \frac{1}{N - 1} \sum_{i=2}^{N} |\text{Latency}_i - \text{Latency}_{i-1}|$$

*Note: All latency figures are simulated to emulate propagation, transmission, and queuing delays across hospital network routers.*

---

## 6. What is Implemented vs. Pending from Teammates

| Module / Protocol | Current Status | Implementation Details |
|---|---|---|
| **GUI & Performance Dashboard** | **Fully Implemented** | Tkinter desktop app, 4 interactive tabs, Canvas vector line & bar charts, Treeview table, KPI cards. |
| **Performance Calculations** | **Fully Implemented** | Decoupled metrics engine calculating throughput, jitter, loss rate, and average latency. |
| **Authenticated Encryption** | **Active Reference** | Uses `cryptography.fernet.Fernet` (AES-128-CBC + HMAC-SHA256). Adapter ready for teammate module. |
| **Framing & Stuffing** | **Active Reference** | Character stuffing (`DLE STX`/`ETX`) and Bit stuffing (`01111110`). Adapter ready for teammate module. |
| **CRC Error Detection** | **Active Reference** | CRC-16-CCITT and CRC-32 polynomial division with bit error injection. Adapter ready for teammate module. |
| **Go-Back-N ARQ** | **Active Reference** | Sliding window transmission engine with sequence tracking and retransmission. Adapter ready for teammate. |
| **Routing Protocols** | **Active Reference** | Dijkstra shortest path and Distance Vector routing table matrix. Adapter ready for teammate. |
| **Wireshark Trace Import** | **Fully Implemented** | Standard Wireshark CSV trace importer, sample capture trace, and CSV log exporter. |

---

## 7. Lecturer Demonstration Guide (Step-by-Step)
When presenting your project to your Computer Networks professor:

1. **Introduction:**
   - State your role: *"I am responsible for GUI Development, Teammate Module Integration, and Network Performance Analysis for our Secure Hospital Network project."*
   - Mention the branch: *"I worked strictly on `feature/gui-analysis` to maintain Git workflow hygiene."*

2. **Tab 1: Dashboard & Network Health:**
   - Show the 6 KPI metric cards and active department nodes (ICU, Cardiology, Radiology, Pharmacy, Emergency, Server).
   - Point out the **Academic Demonstration Notice** and explain that synthetic mock records are used to protect patient privacy.
   - Point out the **Teammate Integration Registry** and explain how the Adapter pattern allows teammates' future modules to plug in seamlessly.

3. **Tab 2: Secure Patient Data Transfer:**
   - Select a synthetic preset (e.g., `SYN-ICU-101 - Vitals`).
   - Click **① Encrypt & Frame Payload**: Explain that authenticated encryption (AES-128-CBC + HMAC-SHA256) protects both confidentiality and integrity.
   - Click **② Transmit Frame ->**: The ciphertext is passed into the channel.
   - Click **③ Authenticate & Decrypt Payload**: Show that the receiver validates the HMAC tag and displays the verified plaintext.
   - **The Wow Moment:** Check *"Simulate Channel Tampering / MITM (Corrupt ciphertext byte)"*, transmit again, and attempt to decrypt. Show the lecturer that the receiver immediately flags `TAMPERING DETECTED: Invalid HMAC Token! Packet rejected.` Explain why authenticated encryption is critical in healthcare networks to prevent data corruption.

4. **Tab 3: Protocol Laboratory:**
   - **Framing:** Test Character Stuffing with `DLE` characters and Bit Stuffing with consecutive `1`s (`01111110`).
   - **CRC:** Show CRC-16 generation. Click **[!] Flip 1 Bit & Check Frame** to demonstrate hardware error detection. Show the step-by-step modulo-2 long division output.
   - **Go-Back-N ARQ:** Set Window Size $N=4$, Total Packets $=8$, Drop Packet $\#2$. Click **Run Go-Back-N ARQ Simulation** and walk through how the sender slides the window upon receiving ACKs and recovers via GBN retransmission when packet 2 drops.
   - **Routing:** Select `ICU Ward` -> `Central Server` and run Dijkstra to show the lowest-latency route (`ICU -> Core Router -> Central Server = 7.0 ms`). Show the Distance Vector routing table.

5. **Tab 4: Performance & Trace Analysis:**
   - Click **▶ Run Batch Simulation** (e.g., 15 packets with 10% simulated loss). Watch the vector Line Chart, Bar Chart, and Treeview table populate live.
   - Click **📂 Import Wireshark / CSV Trace** and load `sample_data/sample_hospital_wireshark_trace.csv`. Show how the GUI parses captured network packet headers and computes summary throughput and loss metrics.
   - Click **💾 Export CSV** to demonstrate test result exporting for project reports.

6. **Demonstrate Automated Tests:**
   - Open the terminal and run: `python -m unittest discover -s gui-analysis/tests -p "test_*.py"`.
   - Show the professor that all 26 unit tests pass cleanly.
