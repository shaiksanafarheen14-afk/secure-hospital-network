"""
departments.py
--------------
Defines hospital departments as sender and receiver nodes.
Uses dummy (fictional) patient data — no real patient information is used.

Each department node holds:
  - A name          : the department identifier
  - A message       : the data it wants to transmit
"""

from dataclasses import dataclass


@dataclass
class Department:
    """Represents a hospital department acting as a network node."""
    name: str        # e.g. "Radiology"
    role: str        # "sender" or "receiver"
    description: str # brief description of the department


# ─────────────────────────────────────────────
# Dummy patient records (fictional data only)
# ─────────────────────────────────────────────

DUMMY_PATIENT_RECORDS = [
    "Patient: John Doe | Age: 45 | Diagnosis: Hypertension | Ward: A3",
    "Patient: Jane Roe | Age: 30 | Diagnosis: Appendicitis | Ward: B1",
    "Patient: Sam Ray | Age: 67 | Diagnosis: Diabetes Type 2 | Ward: C5",
    "Patient: Ava Lee | Age: 22 | Diagnosis: Fractured Arm  | Ward: D2",
    "Patient: Bob Cox | Age: 55 | Diagnosis: Flu Symptoms   | Ward: A7",
    "Patient: Mia Fox | Age: 38 | Diagnosis: Migraine       | Ward: B4",
]

# ─────────────────────────────────────────────
# Pre-defined department nodes
# ─────────────────────────────────────────────

DEPARTMENTS = {
    "radiology": Department(
        name="Radiology Department",
        role="sender",
        description="Sends imaging and scan results to the Emergency Ward",
    ),
    "emergency": Department(
        name="Emergency Ward",
        role="receiver",
        description="Receives patient data from various departments",
    ),
    "pharmacy": Department(
        name="Pharmacy",
        role="sender",
        description="Sends prescription and medication data",
    ),
    "icu": Department(
        name="ICU (Intensive Care Unit)",
        role="receiver",
        description="Receives critical patient updates",
    ),
}


def get_sender() -> Department:
    """Return the default sender department."""
    return DEPARTMENTS["radiology"]


def get_receiver() -> Department:
    """Return the default receiver department."""
    return DEPARTMENTS["emergency"]


def get_message() -> str:
    """
    Build a multi-line dummy patient message that will be
    split into frames for transmission.
    """
    # Join a subset of dummy records into one message string
    return " || ".join(DUMMY_PATIENT_RECORDS)
