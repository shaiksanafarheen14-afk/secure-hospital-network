"""Wireshark and Network Simulation Trace Importer & Exporter.

Provides documented mechanisms to:
1. Import Wireshark standard CSV packet exports (No., Time, Source, Destination, Protocol, Length, Info).
2. Import structured transmission simulation logs.
3. Export current GUI transmission history to CSV.
4. Generate synthetic sample Wireshark traces for academic demonstration.

NOTE: All imported traces are explicitly tagged as simulated/synthetic data.
"""

import csv
import io
import os
from pathlib import Path
from typing import List, Tuple

try:
    from core.models import TransmissionResult, DeliveryStatus
except (ImportError, ValueError):
    from ..core.models import TransmissionResult, DeliveryStatus


class WiresharkTraceParser:
    """Parser and exporter for packet capture traces."""

    @staticmethod
    def parse_csv_file(file_path: str) -> Tuple[List[TransmissionResult], str]:
        """
        Parse either a Wireshark CSV export or an internal transmission CSV log.
        Returns:
            Tuple of (list_of_TransmissionResult, summary_message)
        """
        if not os.path.exists(file_path):
            return [], f"File not found: {file_path}"

        results: List[TransmissionResult] = []

        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return [], "Empty CSV file."

            # Normalize header column names
            header_clean = [col.strip().lower().replace('"', '').replace("'", "") for col in header]

            # Detect format: Wireshark export vs Hospital Simulator Log
            is_wireshark_export = any("no." in h or "protocol" in h for h in header_clean)

            if is_wireshark_export:
                results = WiresharkTraceParser._parse_wireshark_format(reader, header_clean)
                msg = f"Successfully parsed Wireshark trace: {len(results)} packets imported (Tagged as Simulated Trace)."
            else:
                results = WiresharkTraceParser._parse_simulator_format(reader, header_clean)
                msg = f"Successfully parsed Simulator log: {len(results)} transmission records imported."

        return results, msg

    @staticmethod
    def _parse_wireshark_format(reader, header: List[str]) -> List[TransmissionResult]:
        """Convert standard Wireshark CSV rows into TransmissionResult objects."""
        # Find column indices
        col_no = header.index("no.") if "no." in header else 0
        col_time = header.index("time") if "time" in header else 1
        col_src = header.index("source") if "source" in header else 2
        col_dst = header.index("destination") if "destination" in header else 3
        col_proto = header.index("protocol") if "protocol" in header else 4
        col_len = header.index("length") if "length" in header else 5
        col_info = header.index("info") if "info" in header else (len(header) - 1)

        results = []
        for row in reader:
            if not row or len(row) <= max(col_no, col_len):
                continue
            try:
                pkt_num = int(row[col_no])
            except ValueError:
                pkt_num = len(results) + 1

            try:
                time_sec = float(row[col_time])
                latency_ms = round(time_sec * 1000.0 % 50.0 + 5.0, 2)
            except ValueError:
                latency_ms = 12.5

            src = row[col_src] if col_src < len(row) else "192.168.1.10 (ICU)"
            dst = row[col_dst] if col_dst < len(row) else "192.168.1.1 (Server)"
            proto = row[col_proto] if col_proto < len(row) else "TCP"
            
            try:
                pkt_len = int(row[col_len])
            except (ValueError, IndexError):
                pkt_len = 84

            info = row[col_info] if col_info < len(row) else ""
            is_retrans = "retransmission" in info.lower()
            is_dup = "duplicate" in info.lower()

            status = DeliveryStatus.RETRANSMITTED if (is_retrans or is_dup) else DeliveryStatus.DELIVERED

            results.append(TransmissionResult(
                packet_id=pkt_num,
                seq_num=pkt_num,
                timestamp_str=f"{time_sec:.3f}s" if isinstance(time_sec, float) else "00:00:00",
                sender=f"Wireshark:{src}",
                receiver=f"Wireshark:{dst}",
                frame_size_bytes=pkt_len,
                encryption_algorithm="TLS/Encrypted" if "tls" in proto.lower() else "Payload-AES",
                framing_type=f"Ethernet II ({proto})",
                crc_status="Valid (Wireshark FCS OK)",
                delivery_status=status,
                latency_ms=latency_ms,
                retransmissions=1 if is_retrans else 0,
                is_simulated=True
            ))

        return results

    @staticmethod
    def _parse_simulator_format(reader, header: List[str]) -> List[TransmissionResult]:
        """Convert native hospital network CSV log rows into TransmissionResult objects."""
        results = []
        for i, row in enumerate(reader, start=1):
            if not row or len(row) < 5:
                continue
            try:
                res = TransmissionResult(
                    packet_id=int(row[0]),
                    seq_num=int(row[1]),
                    timestamp_str=str(row[2]),
                    sender=str(row[3]),
                    receiver=str(row[4]),
                    frame_size_bytes=int(row[5]) if len(row) > 5 else 80,
                    encryption_algorithm=str(row[6]) if len(row) > 6 else "AES-128",
                    framing_type=str(row[7]) if len(row) > 7 else "Bit Stuffing",
                    crc_status=str(row[8]) if len(row) > 8 else "Valid",
                    delivery_status=DeliveryStatus(row[9]) if len(row) > 9 and row[9] in [d.value for d in DeliveryStatus] else DeliveryStatus.DELIVERED,
                    latency_ms=float(row[10]) if len(row) > 10 else 15.0,
                    retransmissions=int(row[11]) if len(row) > 11 else 0,
                    is_simulated=True
                )
                results.append(res)
            except Exception:
                continue
        return results

    @staticmethod
    def export_to_csv(results: List[TransmissionResult], destination_path: str) -> Tuple[bool, str]:
        """Export transmission results list to CSV file."""
        try:
            with open(destination_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Packet ID", "Seq Num", "Timestamp", "Sender", "Receiver",
                    "Frame Size (Bytes)", "Encryption", "Framing", "CRC Status",
                    "Delivery Status", "Latency (ms)", "Retransmissions", "Simulated"
                ])
                for r in results:
                    writer.writerow([
                        r.packet_id, r.seq_num, r.timestamp_str, r.sender, r.receiver,
                        r.frame_size_bytes, r.encryption_algorithm, r.framing_type,
                        r.crc_status, r.delivery_status.value, r.latency_ms,
                        r.retransmissions, r.is_simulated
                    ])
            return True, f"Successfully exported {len(results)} records to {destination_path}"
        except Exception as e:
            return False, f"Export failed: {str(e)}"

    @staticmethod
    def create_sample_wireshark_file(target_file_path: str):
        """Create a synthetic sample Wireshark CSV file for immediate test import."""
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        headers = ["No.", "Time", "Source", "Destination", "Protocol", "Length", "Info"]
        sample_rows = [
            ["1", "0.000000", "192.168.10.12 (ICU)", "192.168.1.1 (Central Server)", "TLSv1.3", "128", "Application Data [Patient Telemetry Vitals P-101]"],
            ["2", "0.014210", "192.168.1.1 (Central Server)", "192.168.10.12 (ICU)", "TCP", "66", "443 -> 52140 [ACK] Seq=1 Ack=129 Win=64128"],
            ["3", "0.028900", "192.168.20.15 (Cardiology)", "192.168.1.1 (Central Server)", "TLSv1.3", "144", "Application Data [ECG Diagnostic Alert P-204]"],
            ["4", "0.045100", "192.168.1.1 (Central Server)", "192.168.20.15 (Cardiology)", "TCP", "66", "[TCP Retransmission] 443 -> 52142 [SYN, ACK]"],
            ["5", "0.061200", "192.168.30.22 (Radiology)", "192.168.1.1 (Central Server)", "TLSv1.3", "1240", "Application Data [CT Scan Metadata P-309]"],
            ["6", "0.075400", "192.168.1.1 (Central Server)", "192.168.30.22 (Radiology)", "TCP", "66", "443 -> 52144 [ACK] Seq=1 Ack=1241 Win=65535"],
            ["7", "0.091100", "192.168.40.18 (Emergency)", "192.168.1.1 (Central Server)", "TLSv1.3", "112", "Application Data [Triage Urgent Alert P-412]"],
            ["8", "0.105300", "192.168.50.05 (Pharmacy)", "192.168.1.1 (Central Server)", "TLSv1.3", "96", "Application Data [Medication Verification P-505]"],
        ]
        with open(target_file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(sample_rows)
