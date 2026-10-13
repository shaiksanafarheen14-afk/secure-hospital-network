"""Performance Analysis Tab: Transmission Result Table, Vector Canvas Charts, Batch Testing & CSV/Wireshark Import."""

import os
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

try:
    from gui.theme import COLORS, FONTS
    from gui.widgets import CanvasLineChart, CanvasBarChart
    from core.models import TransmissionResult, DeliveryStatus
    from core.synthetic_data import HOSPITAL_DEPARTMENTS, generate_random_synthetic_record
    from modules.wireshark_parser import WiresharkTraceParser
except (ImportError, ValueError):
    from ..theme import COLORS, FONTS
    from ..widgets import CanvasLineChart, CanvasBarChart
    from ...core.models import TransmissionResult, DeliveryStatus
    from ...core.synthetic_data import HOSPITAL_DEPARTMENTS, generate_random_synthetic_record
    from ...modules.wireshark_parser import WiresharkTraceParser


class PerformanceTab(tk.Frame):
    """Detailed performance analysis with metrics, graphs, tables, and trace importer."""

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, bg=COLORS["bg_main"], **kwargs)
        self.app = app_controller

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=14, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------
        # Action Control Toolbar
        # ---------------------------------------------------------
        toolbar = tk.Frame(container, bg=COLORS["bg_surface"], padx=12, pady=8, highlightthickness=1, highlightbackground=COLORS["border"])
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # Batch Simulation controls
        tk.Label(toolbar, text="Batch Packets:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 4))
        self.batch_count_var = tk.IntVar(value=15)
        sp_batch = tk.Spinbox(toolbar, from_=5, to=100, textvariable=self.batch_count_var, width=5, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        sp_batch.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(toolbar, text="Sim Loss Rate %:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 4))
        self.sim_loss_var = tk.IntVar(value=10)
        sp_loss = tk.Spinbox(toolbar, from_=0, to=50, textvariable=self.sim_loss_var, width=5, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        sp_loss.pack(side=tk.LEFT, padx=(0, 14))

        btn_batch = tk.Button(
            toolbar, text="▶ Run Batch Simulation", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=10, pady=3,
            command=self._run_batch_simulation
        )
        btn_batch.pack(side=tk.LEFT, padx=(0, 10))

        # Import & Export Buttons
        btn_import = tk.Button(
            toolbar, text="📂 Import Wireshark / CSV Trace", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=10, pady=3,
            command=self._import_trace_file
        )
        btn_import.pack(side=tk.LEFT, padx=(0, 8))

        btn_export = tk.Button(
            toolbar, text="💾 Export CSV", font=FONTS["caption"],
            bg=COLORS["bg_entry"], fg=COLORS["text_secondary"], relief=tk.FLAT, padx=8, pady=3,
            command=self._export_csv
        )
        btn_export.pack(side=tk.LEFT, padx=(0, 8))

        btn_reset = tk.Button(
            toolbar, text="↺ Reset All", font=FONTS["caption"],
            bg="#7f1d1d", fg=COLORS["text_primary"], relief=tk.FLAT, padx=8, pady=3,
            command=self._reset_metrics
        )
        btn_reset.pack(side=tk.RIGHT)

        # ---------------------------------------------------------
        # Charts Row (Line Chart & Bar Chart)
        # ---------------------------------------------------------
        charts_frame = tk.Frame(container, bg=COLORS["bg_main"])
        charts_frame.pack(fill=tk.X, pady=(0, 10))
        charts_frame.columnconfigure(0, weight=3)
        charts_frame.columnconfigure(1, weight=2)

        # Vector Line Chart: Latency per packet
        self.latency_chart = CanvasLineChart(
            charts_frame, title="Packet Latency Progression (ms) [Simulated]", height=170
        )
        self.latency_chart.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # Vector Bar Chart: Delivery breakdown
        self.outcome_chart = CanvasBarChart(
            charts_frame, title="Transmission Delivery Breakdown", height=170
        )
        self.outcome_chart.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # ---------------------------------------------------------
        # Transmission Results Table (ttk.Treeview)
        # ---------------------------------------------------------
        table_box = tk.LabelFrame(
            container, text=" Transmission History Table (Real-Time Packet Records) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=8, pady=6, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        table_box.pack(fill=tk.BOTH, expand=True)

        cols = (
            "id", "seq", "time", "sender", "receiver",
            "size", "enc", "framing", "crc", "status", "latency", "retries", "data_tag"
        )
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=8, selectmode="browse")

        # Headings
        self.tree.heading("id", text="Pkt #")
        self.tree.heading("seq", text="Seq")
        self.tree.heading("time", text="Timestamp")
        self.tree.heading("sender", text="Sender Department")
        self.tree.heading("receiver", text="Receiver Host")
        self.tree.heading("size", text="Size (B)")
        self.tree.heading("enc", text="Cipher")
        self.tree.heading("framing", text="Framing")
        self.tree.heading("crc", text="CRC Check")
        self.tree.heading("status", text="Delivery Status")
        self.tree.heading("latency", text="Latency (ms)")
        self.tree.heading("retries", text="Retries")
        self.tree.heading("data_tag", text="Nature")

        # Column widths
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("seq", width=45, anchor="center")
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("sender", width=140, anchor="w")
        self.tree.column("receiver", width=140, anchor="w")
        self.tree.column("size", width=65, anchor="center")
        self.tree.column("enc", width=90, anchor="center")
        self.tree.column("framing", width=95, anchor="center")
        self.tree.column("crc", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("latency", width=85, anchor="center")
        self.tree.column("retries", width=55, anchor="center")
        self.tree.column("data_tag", width=85, anchor="center")

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_box, orient=tk.VERTICAL, command=self.tree.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = ttk.Scrollbar(table_box, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Style tags
        self.tree.tag_configure("delivered", foreground=COLORS["success"])
        self.tree.tag_configure("retransmitted", foreground=COLORS["warning"])
        self.tree.tag_configure("lost", foreground=COLORS["danger"])
        self.tree.tag_configure("corrupted", foreground="#f87171")

    def refresh_view(self, results: List[TransmissionResult]):
        """Repopulate table and update charts with current transmission results."""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        latencies: List[float] = []
        c_delivered = 0
        c_retrans = 0
        c_corrupt = 0
        c_lost = 0

        for r in results:
            tag = "delivered"
            if r.delivery_status == DeliveryStatus.DELIVERED:
                c_delivered += 1
                latencies.append(r.latency_ms)
            elif r.delivery_status == DeliveryStatus.RETRANSMITTED:
                c_retrans += 1
                latencies.append(r.latency_ms)
                tag = "retransmitted"
            elif r.delivery_status == DeliveryStatus.CORRUPTED or "corrupt" in r.crc_status.lower():
                c_corrupt += 1
                tag = "corrupted"
            else:
                c_lost += 1
                tag = "lost"

            self.tree.insert("", tk.END, values=(
                r.packet_id,
                r.seq_num,
                r.timestamp_str,
                r.sender,
                r.receiver,
                r.frame_size_bytes,
                r.encryption_algorithm,
                r.framing_type,
                r.crc_status,
                r.delivery_status.value,
                f"{r.latency_ms:.1f}",
                r.retransmissions,
                "[Simulated]" if r.is_simulated else "[Measured]"
            ), tags=(tag,))

        # Update charts
        self.latency_chart.update_data(latencies)
        self.outcome_chart.update_counts(
            delivered=c_delivered,
            retransmitted=c_retrans,
            corrupted=c_corrupt,
            lost=c_lost
        )

    def _run_batch_simulation(self):
        count = self.batch_count_var.get()
        loss_pct = self.sim_loss_var.get()
        sender = random.choice(HOSPITAL_DEPARTMENTS[:-1])
        receiver = "Central Hospital Server"

        self.app.dashboard_tab.log_event(
            f"BATCH SIMULATION: Starting burst transfer of {count} packets from {sender} (Configured loss rate: {loss_pct}%)..."
        )

        for i in range(count):
            seq = i + 1
            is_lost = random.randint(1, 100) <= loss_pct
            is_corrupt = (not is_lost) and (random.randint(1, 100) <= 8)
            retries = 1 if (is_lost or is_corrupt) else 0

            if is_lost:
                status = DeliveryStatus.LOST
                latency = round(random.uniform(35.0, 60.0), 2)
                crc_stat = "Lost in Transit"
            elif is_corrupt:
                status = DeliveryStatus.CORRUPTED
                latency = round(random.uniform(15.0, 28.0), 2)
                crc_stat = "Corrupted (CRC Error)"
            else:
                status = DeliveryStatus.DELIVERED
                latency = round(random.uniform(8.5, 22.0), 2)
                crc_stat = "Valid (CRC Checked)"

            res = TransmissionResult(
                packet_id=len(self.app.transmission_history) + 1,
                seq_num=seq,
                timestamp_str=time.strftime("%H:%M:%S"),
                sender=sender,
                receiver=receiver,
                frame_size_bytes=random.randint(72, 160),
                encryption_algorithm="AES-128-CBC",
                framing_type="Bit Stuffing",
                crc_status=crc_stat,
                delivery_status=status,
                latency_ms=latency,
                retransmissions=retries,
                is_simulated=True
            )
            self.app.add_transmission_result(res)

        self.app.dashboard_tab.log_event(
            f"BATCH COMPLETED: {count} packets processed. Performance metrics and charts updated."
        )

    def _import_trace_file(self):
        # Default sample file path
        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "sample_data",
            "sample_hospital_wireshark_trace.csv"
        )

        selected_file = filedialog.askopenfilename(
            title="Import Wireshark CSV or Simulation Trace",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialdir=os.path.dirname(sample_path) if os.path.exists(sample_path) else "."
        )

        target = selected_file if selected_file else (sample_path if os.path.exists(sample_path) else "")
        if not target:
            return

        imported_records, msg = WiresharkTraceParser.parse_csv_file(target)
        if not imported_records:
            messagebox.showerror("Import Error", msg)
            return

        for r in imported_records:
            self.app.add_transmission_result(r)

        messagebox.showinfo("Import Successful", f"{msg}\nAll records tagged as [Simulated Trace].")
        self.app.dashboard_tab.log_event(f"TRACE IMPORT: Loaded {len(imported_records)} packets from {os.path.basename(target)}.")

    def _export_csv(self):
        if not self.app.transmission_history:
            messagebox.showwarning("Export Warning", "No transmission history to export.")
            return

        default_name = f"hospital_network_metrics_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        save_path = filedialog.asksaveasfilename(
            title="Export Transmission Results to CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV Files", "*.csv")]
        )
        if not save_path:
            return

        ok, msg = WiresharkTraceParser.export_to_csv(self.app.transmission_history, save_path)
        if ok:
            messagebox.showinfo("Export Successful", msg)
        else:
            messagebox.showerror("Export Failed", msg)

    def _reset_metrics(self):
        confirm = messagebox.askyesno("Reset All Metrics", "Are you sure you want to clear all transmission logs and reset performance statistics?")
        if confirm:
            self.app.clear_all_transmissions()
            self.app.dashboard_tab.log_event("SYSTEM: All metrics and transmission histories have been reset.")
