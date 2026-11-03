# =============================================================================
# config.py
# Project : Secure Hospital Network for Reliable Patient Data Communication
# Module  : Feature/Routing Protocols
# Purpose : Defines dummy hospital departments as sender/receiver nodes
#           and the dummy patient messages they exchange.
# NOTE    : All patient data is completely fictional / dummy.
# =============================================================================

# ---------------------------------------------------------------------------
# Hospital Department Nodes
# Each department acts as a network node that can SEND or RECEIVE data.
# ---------------------------------------------------------------------------
DEPARTMENTS = {
    "ICU":          "192.168.1.10",   # Intensive Care Unit
    "RADIOLOGY":    "192.168.1.20",   # Radiology / Imaging
    "PHARMACY":     "192.168.1.30",   # Pharmacy
    "EMERGENCY":    "192.168.1.40",   # Emergency Room
    "LAB":          "192.168.1.50",   # Laboratory
    "GENERAL_OPD":  "192.168.1.60",   # General Out-Patient Department
}

# ---------------------------------------------------------------------------
# Dummy transmission scenarios (sender, receiver, message)
# These are completely made-up, non-real patient records.
# ---------------------------------------------------------------------------
TRANSMISSION_SCENARIOS = [
    {
        "sender":   "EMERGENCY",
        "receiver": "ICU",
        "message":  "PATIENT#001 CRITICAL BP=180/120 TRANSFER_REQUESTED",
    },
    {
        "sender":   "LAB",
        "receiver": "GENERAL_OPD",
        "message":  "PATIENT#002 BLOOD_REPORT HEMOGLOBIN=13.5 NORMAL",
    },
    {
        "sender":   "RADIOLOGY",
        "receiver": "ICU",
        "message":  "PATIENT#003 XRAY_RESULT CHEST=CLEAR NO_ANOMALY",
    },
]

# ---------------------------------------------------------------------------
# Protocol / channel parameters (tweak these to experiment!)
# ---------------------------------------------------------------------------
FRAME_SIZE        = 8     # Number of characters per frame payload
WINDOW_SIZE       = 4     # Sliding-window / Go-Back-N window size
CORRUPTION_PROB   = 0.25  # Probability (0–1) that a frame gets corrupted in transit
MAX_RETRANSMIT    = 5     # Maximum retransmission attempts per frame before giving up
