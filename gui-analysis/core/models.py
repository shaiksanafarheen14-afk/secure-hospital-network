"""Data models for hospital network communication, packets, and metrics."""

from dataclasses import dataclass, field
from enum import Enum
import json
import time
from typing import Dict, Any, Optional


class DeliveryStatus(str, Enum):
    DELIVERED = "Delivered"
    LOST = "Lost (Timeout)"
    CORRUPTED = "Corrupted (CRC Error)"
    RETRANSMITTED = "Retransmitted"


@dataclass
class PatientRecord:
    """Synthetic clinical patient record (academic demonstration only)."""
    patient_id: str
    department: str
    condition: str
    vitals: Dict[str, Any]
    clinical_note: str
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    def to_json(self) -> str:
        return json.dumps({
            "patient_id": self.patient_id,
            "department": self.department,
            "condition": self.condition,
            "vitals": self.vitals,
            "clinical_note": self.clinical_note,
            "timestamp": self.timestamp,
            "synthetic_disclaimer": "SYNTHETIC_DATA_DEMO_ONLY"
        }, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "PatientRecord":
        data = json.loads(json_str)
        return cls(
            patient_id=data.get("patient_id", "UNKNOWN"),
            department=data.get("department", "General"),
            condition=data.get("condition", "Normal"),
            vitals=data.get("vitals", {}),
            clinical_note=data.get("clinical_note", ""),
            timestamp=data.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        )


@dataclass
class Packet:
    """Network frame carrying encrypted patient payload across hospital subnets."""
    packet_id: int
    seq_num: int
    sender: str
    receiver: str
    payload_plaintext: str
    payload_encrypted: bytes = b""
    framed_data: str = ""
    crc_code: str = ""
    is_corrupted: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class TransmissionResult:
    """Recorded result of a single packet transmission for performance analysis."""
    packet_id: int
    seq_num: int
    timestamp_str: str
    sender: str
    receiver: str
    frame_size_bytes: int
    encryption_algorithm: str
    framing_type: str
    crc_status: str              # "Valid", "Corrupted (CRC Mismatch)", "Bypassed"
    delivery_status: DeliveryStatus
    latency_ms: float
    retransmissions: int
    is_simulated: bool = True    # Explicitly flags whether measurement was simulated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "seq_num": self.seq_num,
            "timestamp": self.timestamp_str,
            "sender": self.sender,
            "receiver": self.receiver,
            "frame_size_bytes": self.frame_size_bytes,
            "encryption": self.encryption_algorithm,
            "framing": self.framing_type,
            "crc_status": self.crc_status,
            "delivery_status": self.delivery_status.value,
            "latency_ms": round(self.latency_ms, 2),
            "retransmissions": self.retransmissions,
            "is_simulated": self.is_simulated
        }


@dataclass
class NetworkMetricsSummary:
    """Aggregated statistical performance summary."""
    total_sent: int = 0
    total_received: int = 0
    total_lost: int = 0
    total_retransmitted: int = 0
    total_corrupted: int = 0
    success_rate_percent: float = 0.0
    average_delay_ms: float = 0.0
    throughput_kbps: float = 0.0
    throughput_pps: float = 0.0
    min_delay_ms: float = 0.0
    max_delay_ms: float = 0.0
    jitter_ms: float = 0.0
