"""Main Application Window & Coordinator for Secure Hospital Network GUI."""

import tkinter as tk
from tkinter import ttk
import time
from typing import List, Tuple, Dict, Any, Optional

try:
    from gui.theme import COLORS, FONTS
    from gui.tabs.dashboard_tab import DashboardTab
    from gui.tabs.patient_comm_tab import PatientCommTab
    from gui.tabs.protocols_tab import ProtocolsTab
    from gui.tabs.performance_tab import PerformanceTab
    from core.models import TransmissionResult, DeliveryStatus, NetworkMetricsSummary
    from core.metrics import compute_metrics_summary
    from modules.encryption_adapter import EncryptionAdapter
    from modules.framing_adapter import FramingAdapter
    from modules.crc_adapter import CRCAdapter
    from modules.reliable_transmission_adapter import ReliableTransmissionAdapter
    from modules.routing_adapter import RoutingAdapter
except (ImportError, ValueError):
    from .theme import COLORS, FONTS
    from .tabs.dashboard_tab import DashboardTab
    from .tabs.patient_comm_tab import PatientCommTab
    from .tabs.protocols_tab import ProtocolsTab
    from .tabs.performance_tab import PerformanceTab
    from ..core.models import TransmissionResult, DeliveryStatus, NetworkMetricsSummary
    from ..core.metrics import compute_metrics_summary
    from ..modules.encryption_adapter import EncryptionAdapter
    from ..modules.framing_adapter import FramingAdapter
    from ..modules.crc_adapter import CRCAdapter
    from ..modules.reliable_transmission_adapter import ReliableTransmissionAdapter
    from ..modules.routing_adapter import RoutingAdapter


class HospitalNetworkApp:
    """Main application controller managing protocol adapters, shared state, and UI tabs."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Secure Hospital Network - Patient Data Communication & Performance Analysis")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)
        self.root.configure(bg=COLORS["bg_main"])

        # Configure ttk styles for dark modern look
        self._configure_styles()

        # Initialize Protocol Adapters
        self.encryption_adapter = EncryptionAdapter()
        self.framing_adapter = FramingAdapter()
        self.crc_adapter = CRCAdapter()
        self.reliable_adapter = ReliableTransmissionAdapter()
        self.routing_adapter = RoutingAdapter()

        # Transmission state
        self.transmission_history: List[TransmissionResult] = []
        self.metrics_summary = NetworkMetricsSummary()

        # Build main layout
        self._build_layout()

        # Update initial views
        self.update_all_views()

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Notebook tabs styling
        style.configure("TNotebook", background=COLORS["bg_main"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLORS["bg_surface"],
            foreground=COLORS["text_secondary"],
            padding=[16, 8],
            font=FONTS["subtitle"]
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", COLORS["text_dark"])]
        )

        # Treeview styling
        style.configure(
            "Treeview",
            background=COLORS["bg_surface_alt"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_surface_alt"],
            font=FONTS["code"],
            rowheight=24,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["bg_surface"],
            foreground=COLORS["primary"],
            font=FONTS["body_bold"],
            borderwidth=1,
            relief=tk.FLAT
        )
        style.map("Treeview", background=[("selected", COLORS["bg_entry"])])

        # Scrollbar
        style.configure("Vertical.TScrollbar", background=COLORS["bg_surface"], troughcolor=COLORS["bg_main"])
        style.configure("Horizontal.TScrollbar", background=COLORS["bg_surface"], troughcolor=COLORS["bg_main"])

    def _build_layout(self):
        # 1. Main Navigation Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dashboard_tab = DashboardTab(self.notebook, self)
        self.patient_comm_tab = PatientCommTab(self.notebook, self)
        self.protocols_tab = ProtocolsTab(self.notebook, self)
        self.performance_tab = PerformanceTab(self.notebook, self)

        self.notebook.add(self.dashboard_tab, text="  Dashboard & Network Health  ")
        self.notebook.add(self.patient_comm_tab, text="  Secure Patient Data Transfer  ")
        self.notebook.add(self.protocols_tab, text="  Protocol Lab (Framing/CRC/ARQ/Route)  ")
        self.notebook.add(self.performance_tab, text="  Performance & Trace Analysis  ")

        # 2. Bottom Status Bar
        self.status_bar = tk.Frame(self.root, bg=COLORS["bg_surface"], padx=12, pady=4, highlightthickness=1, highlightbackground=COLORS["border_subtle"])
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_branch_status = tk.Label(
            self.status_bar,
            text="Git Branch: feature/gui-analysis | System: Operational",
            font=FONTS["caption"], fg=COLORS["success"], bg=COLORS["bg_surface"]
        )
        self.lbl_branch_status.pack(side=tk.LEFT)

        self.lbl_summary_bar = tk.Label(
            self.status_bar,
            text="Total Packets: 0 | Delivered: 0 | Success Rate: 0.0%",
            font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]
        )
        self.lbl_summary_bar.pack(side=tk.RIGHT)

    def get_adapter_status_info(self, key: str) -> Tuple[str, str]:
        """Look up status info for a protocol adapter."""
        mapping = {
            "encryption": self.encryption_adapter,
            "framing": self.framing_adapter,
            "crc": self.crc_adapter,
            "reliable": self.reliable_adapter,
            "routing": self.routing_adapter
        }
        adapter = mapping.get(key)
        if adapter:
            return adapter.get_status_info()
        return ("Pending External", "Not loaded")

    def record_transmission(
        self,
        sender: str,
        receiver: str,
        frame_size: int,
        delivery_status: DeliveryStatus,
        latency_ms: float,
        crc_status: str = "Valid",
        retransmissions: int = 0
    ):
        """Record a single transmission result and update all tabs."""
        seq = len(self.transmission_history) + 1
        res = TransmissionResult(
            packet_id=seq,
            seq_num=seq,
            timestamp_str=time.strftime("%H:%M:%S"),
            sender=sender,
            receiver=receiver,
            frame_size_bytes=frame_size,
            encryption_algorithm="AES-128-CBC + HMAC",
            framing_type="Bit Stuffing",
            crc_status=crc_status,
            delivery_status=delivery_status,
            latency_ms=latency_ms,
            retransmissions=retransmissions,
            is_simulated=True
        )
        self.add_transmission_result(res)

    def add_transmission_result(self, result: TransmissionResult):
        """Add a transmission result and refresh UI views."""
        self.transmission_history.append(result)
        self.update_all_views()

    def clear_all_transmissions(self):
        """Reset all transmission logs and statistics."""
        self.transmission_history.clear()
        self.update_all_views()

    def update_all_views(self):
        """Recalculate summary metrics and refresh all active tab views."""
        self.metrics_summary = compute_metrics_summary(self.transmission_history)
        
        # Update Dashboard
        self.dashboard_tab.refresh_metrics(self.metrics_summary)
        
        # Update Performance View
        self.performance_tab.refresh_view(self.transmission_history)

        # Update Status Bar
        self.lbl_summary_bar.config(
            text=f"Total Packets: {self.metrics_summary.total_sent} | Delivered: {self.metrics_summary.total_received} | Success Rate: {self.metrics_summary.success_rate_percent:.1f}% | Avg Delay: {self.metrics_summary.average_delay_ms:.1f}ms"
        )
