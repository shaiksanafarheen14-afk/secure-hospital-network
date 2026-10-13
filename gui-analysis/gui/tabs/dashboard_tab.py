"""Dashboard Tab: High-level hospital network health, KPI metrics cards, and node statuses."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List

try:
    from gui.theme import COLORS, FONTS
    from gui.widgets import StatCard
    from core.models import NetworkMetricsSummary, TransmissionResult
except (ImportError, ValueError):
    from ..theme import COLORS, FONTS
    from ..widgets import StatCard
    from ...core.models import NetworkMetricsSummary, TransmissionResult


class DashboardTab(tk.Frame):
    """Main system overview dashboard."""

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, bg=COLORS["bg_main"], **kwargs)
        self.app = app_controller

        # Main scrollable canvas container to ensure it fits on any resolution
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=16, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------
        # Header & Project Disclaimer Banner
        # ---------------------------------------------------------
        header_frame = tk.Frame(container, bg=COLORS["bg_surface"], padx=14, pady=10, highlightthickness=1, highlightbackground=COLORS["border"])
        header_frame.pack(fill=tk.X, pady=(0, 12))

        title_lbl = tk.Label(
            header_frame, text="Secure Hospital Network for Reliable Patient Data Communication",
            font=FONTS["title"], fg=COLORS["primary"], bg=COLORS["bg_surface"], anchor="w"
        )
        title_lbl.pack(fill=tk.X)

        sub_lbl = tk.Label(
            header_frame,
            text="GUI Integration, Modular Protocol Adapters & Real-Time Performance Analytics",
            font=FONTS["subtitle"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"], anchor="w"
        )
        sub_lbl.pack(fill=tk.X, pady=(2, 6))

        # Academic disclaimer badge
        badge_frame = tk.Frame(header_frame, bg=COLORS["bg_surface_alt"], padx=8, pady=4, highlightthickness=1, highlightbackground=COLORS["border_subtle"])
        badge_frame.pack(fill=tk.X)
        disclaimer_lbl = tk.Label(
            badge_frame,
            text="[!] ACADEMIC DEMONSTRATION NOTICE: All patient vitals are synthetic mock samples. Network latency and impairments are simulated algorithms for Computer Networks demonstration.",
            font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_surface_alt"], anchor="w"
        )
        disclaimer_lbl.pack(side=tk.LEFT)

        # ---------------------------------------------------------
        # KPI Metrics Cards (6-grid)
        # ---------------------------------------------------------
        cards_frame = tk.Frame(container, bg=COLORS["bg_main"])
        cards_frame.pack(fill=tk.X, pady=(0, 12))
        for col in range(6):
            cards_frame.columnconfigure(col, weight=1, uniform="kpi")

        self.card_sent = StatCard(cards_frame, title="Total Sent", initial_value="0", subtext="Packets dispatched", accent_color=COLORS["info"])
        self.card_sent.grid(row=0, column=0, padx=4, sticky="nsew")

        self.card_delivered = StatCard(cards_frame, title="Delivered", initial_value="0", subtext="Success: 0.0%", accent_color=COLORS["success"])
        self.card_delivered.grid(row=0, column=1, padx=4, sticky="nsew")

        self.card_lost = StatCard(cards_frame, title="Packet Loss", initial_value="0", subtext="Loss Rate: 0.0%", accent_color=COLORS["danger"])
        self.card_lost.grid(row=0, column=2, padx=4, sticky="nsew")

        self.card_retrans = StatCard(cards_frame, title="Retransmitted", initial_value="0", subtext="Go-Back-N recoveries", accent_color=COLORS["warning"])
        self.card_retrans.grid(row=0, column=3, padx=4, sticky="nsew")

        self.card_delay = StatCard(cards_frame, title="Avg Delay", initial_value="0.0 ms", subtext="[Simulated Latency]", accent_color=COLORS["secondary"])
        self.card_delay.grid(row=0, column=4, padx=4, sticky="nsew")

        self.card_throughput = StatCard(cards_frame, title="Throughput", initial_value="0.0 kbps", subtext="[Simulated Rate]", accent_color=COLORS["primary"])
        self.card_throughput.grid(row=0, column=5, padx=4, sticky="nsew")

        # ---------------------------------------------------------
        # Mid Section: Hospital Nodes & Protocol Integration Status
        # ---------------------------------------------------------
        mid_frame = tk.Frame(container, bg=COLORS["bg_main"])
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        mid_frame.columnconfigure(0, weight=1)
        mid_frame.columnconfigure(1, weight=1)

        # Left Column: Department Nodes Status
        nodes_box = tk.LabelFrame(
            mid_frame, text=" Hospital Network Subnets & Department Nodes ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        nodes_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.node_widgets: Dict[str, tk.Label] = {}
        departments = [
            ("ICU Ward 3", "Subnet 192.168.10.0/24 | Priority: High (Telemetry)"),
            ("Cardiology Unit", "Subnet 192.168.20.0/24 | Priority: Medium (ECG Traces)"),
            ("Radiology & Imaging", "Subnet 192.168.30.0/24 | Priority: Normal (Bulk Scans)"),
            ("Emergency Care Unit", "Subnet 192.168.40.0/24 | Priority: Critical (Triage Alert)"),
            ("Central Pharmacy", "Subnet 192.168.50.0/24 | Priority: High (Prescriptions)"),
            ("Central Hospital Server", "Data Center 192.168.1.1 | Status: Aggregator Host")
        ]

        for i, (dept, desc) in enumerate(departments):
            row_f = tk.Frame(nodes_box, bg=COLORS["bg_surface_alt"], padx=8, pady=4)
            row_f.pack(fill=tk.X, pady=2)
            
            dot = tk.Label(row_f, text="●", fg=COLORS["success"], bg=COLORS["bg_surface_alt"], font=("Segoe UI", 12))
            dot.pack(side=tk.LEFT, padx=(0, 6))

            name_lbl = tk.Label(row_f, text=dept, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_surface_alt"])
            name_lbl.pack(side=tk.LEFT)

            info_lbl = tk.Label(row_f, text=desc, font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_surface_alt"])
            info_lbl.pack(side=tk.RIGHT)

        # Right Column: Protocol Adapters & Teammate Integration Status
        modules_box = tk.LabelFrame(
            mid_frame, text=" Protocol Modules & Teammate Integration Registry ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        modules_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.module_status_labels: Dict[str, tk.Label] = {}
        protocols = [
            ("Encryption & Security", "Fernet AES-128-CBC + HMAC-SHA256 (Authenticated)", "encryption"),
            ("Framing & Stuffing", "Bit Stuffing (HDLC) & Character Stuffing (DLE STX/ETX)", "framing"),
            ("Error Detection", "CRC-16-CCITT & CRC-32 Polynomial Checksums", "crc"),
            ("Reliable Transmission", "Go-Back-N ARQ & Sliding Window Protocol", "reliable"),
            ("Routing Protocols", "Dijkstra Shortest Path & Distance Vector Exchange", "routing")
        ]

        for proto_name, algo, key in protocols:
            p_frame = tk.Frame(modules_box, bg=COLORS["bg_surface_alt"], padx=8, pady=4)
            p_frame.pack(fill=tk.X, pady=2)

            t_lbl = tk.Label(p_frame, text=proto_name, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_surface_alt"])
            t_lbl.pack(side=tk.LEFT)

            # Status Pill
            status_text, src = self.app.get_adapter_status_info(key)
            status_lbl = tk.Label(
                p_frame, text=f"[{status_text}]", font=FONTS["caption"],
                fg=COLORS["success"] if "Integrated" in status_text else COLORS["secondary"],
                bg=COLORS["bg_surface_alt"]
            )
            status_lbl.pack(side=tk.RIGHT)
            self.module_status_labels[key] = status_lbl

            algo_lbl = tk.Label(p_frame, text=f"- {algo}", font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_surface_alt"])
            algo_lbl.pack(side=tk.LEFT, padx=6)

        # ---------------------------------------------------------
        # Bottom: Recent Live Activity Log
        # ---------------------------------------------------------
        log_box = tk.LabelFrame(
            container, text=" Live Activity & Transmission Stream (Sanitized) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=6, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        log_box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_box, height=5, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.WORD, borderwidth=0, highlightthickness=0
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_box, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log_event("SYSTEM INITIALIZED: Secure Hospital Network Dashboard ready. Adapters active.")

    def log_event(self, message: str):
        """Append timestamped message to dashboard stream."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def refresh_metrics(self, summary: NetworkMetricsSummary):
        """Update KPI card numbers when transmissions occur."""
        self.card_sent.set_value(str(summary.total_sent), f"{summary.total_received + summary.total_lost} processed")
        self.card_delivered.set_value(
            str(summary.total_received),
            f"Success: {summary.success_rate_percent:.1f}%"
        )
        loss_rate = ((summary.total_lost / summary.total_sent * 100.0) if summary.total_sent > 0 else 0.0)
        self.card_lost.set_value(
            str(summary.total_lost),
            f"Loss Rate: {loss_rate:.1f}%"
        )
        self.card_retrans.set_value(
            str(summary.total_retransmitted),
            f"CRC Corrupted: {summary.total_corrupted}"
        )
        self.card_delay.set_value(
            f"{summary.average_delay_ms:.1f} ms",
            f"Jitter: {summary.jitter_ms:.1f} ms"
        )
        self.card_throughput.set_value(
            f"{summary.throughput_kbps:.1f} kbps",
            f"{summary.throughput_pps:.1f} pkts/sec"
        )
