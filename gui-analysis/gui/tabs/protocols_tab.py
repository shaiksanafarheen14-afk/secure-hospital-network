"""Protocols Tab: Framing (Bit & Char Stuffing), CRC Error Detection, Go-Back-N ARQ, and Hospital Routing."""

import tkinter as tk
from tkinter import ttk, messagebox
import json

try:
    from gui.theme import COLORS, FONTS
    from core.models import DeliveryStatus
except (ImportError, ValueError):
    from ..theme import COLORS, FONTS
    from ...core.models import DeliveryStatus


class ProtocolsTab(tk.Frame):
    """Deep-dive interactive laboratory for Computer Networks protocol layers."""

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, bg=COLORS["bg_main"], **kwargs)
        self.app = app_controller

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=14, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Sub-notebook for organized protocol exploration
        self.sub_notebook = ttk.Notebook(container)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        # 4 Sub-Tabs
        self.tab_framing = tk.Frame(self.sub_notebook, bg=COLORS["bg_main"], padx=12, pady=10)
        self.tab_crc = tk.Frame(self.sub_notebook, bg=COLORS["bg_main"], padx=12, pady=10)
        self.tab_gbn = tk.Frame(self.sub_notebook, bg=COLORS["bg_main"], padx=12, pady=10)
        self.tab_routing = tk.Frame(self.sub_notebook, bg=COLORS["bg_main"], padx=12, pady=10)

        self.sub_notebook.add(self.tab_framing, text=" 1. Framing & Stuffing ")
        self.sub_notebook.add(self.tab_crc, text=" 2. CRC Error Detection ")
        self.sub_notebook.add(self.tab_gbn, text=" 3. Go-Back-N ARQ (Sliding Window) ")
        self.sub_notebook.add(self.tab_routing, text=" 4. Hospital Routing (Dijkstra / DV) ")

        self._build_framing_subtab()
        self._build_crc_subtab()
        self._build_gbn_subtab()
        self._build_routing_subtab()

    # =========================================================================
    # SUBTAB 1: Framing & Stuffing
    # =========================================================================
    def _build_framing_subtab(self):
        p = self.tab_framing
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)

        # Left Column: Character Stuffing
        char_box = tk.LabelFrame(
            p, text=" Character Stuffing (Byte-Oriented Framing) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        char_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)

        tk.Label(
            char_box, text="Framing Flags: Header=[DLE STX], Trailer=[DLE ETX], Escape=[DLE]",
            font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        tk.Label(char_box, text="Input Data Payload:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w", pady=(6, 2))
        self.char_input = tk.Entry(char_box, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"], insertbackground=COLORS["primary"])
        self.char_input.insert(0, "PATIENT_ID: 104 DLE HR: 88 DLE TEMP: 37.0")
        self.char_input.pack(fill=tk.X, pady=(0, 8))

        btn_char_stuff = tk.Button(
            char_box, text="Apply Character Stuffing", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=8, pady=3,
            command=self._run_character_stuffing
        )
        btn_char_stuff.pack(anchor="w", pady=(0, 6))

        tk.Label(char_box, text="Framed Output Stream:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w")
        self.char_output = tk.Text(char_box, height=4, font=FONTS["code"], bg=COLORS["bg_surface_alt"], fg=COLORS["secondary"], wrap=tk.WORD)
        self.char_output.pack(fill=tk.X, pady=(2, 6))

        tk.Label(char_box, text="Unstuffed Receiver Verification:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w")
        self.char_unstuff_lbl = tk.Label(char_box, text="Awaiting test...", font=FONTS["code"], fg=COLORS["text_muted"], bg=COLORS["bg_surface_alt"], anchor="w", padx=6, pady=4)
        self.char_unstuff_lbl.pack(fill=tk.X)

        # Right Column: Bit Stuffing
        bit_box = tk.LabelFrame(
            p, text=" Bit Stuffing (Bit-Oriented HDLC Framing) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        bit_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=4)

        tk.Label(
            bit_box, text="Flag Pattern: 01111110 | Rule: Insert '0' after five consecutive '1's",
            font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        tk.Label(bit_box, text="Binary Bit Stream (0s and 1s):", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w", pady=(6, 2))
        self.bit_input = tk.Entry(bit_box, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"], insertbackground=COLORS["primary"])
        self.bit_input.insert(0, "0110111111011111110011")
        self.bit_input.pack(fill=tk.X, pady=(0, 8))

        btn_bit_stuff = tk.Button(
            bit_box, text="Apply Bit Stuffing (HDLC)", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=8, pady=3,
            command=self._run_bit_stuffing
        )
        btn_bit_stuff.pack(anchor="w", pady=(0, 6))

        tk.Label(bit_box, text="Framed Bitstream (Flags + Stuffed Body):", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w")
        self.bit_output = tk.Text(bit_box, height=4, font=FONTS["code"], bg=COLORS["bg_surface_alt"], fg=COLORS["primary"], wrap=tk.CHAR)
        self.bit_output.pack(fill=tk.X, pady=(2, 6))

        tk.Label(bit_box, text="Unstuffed Receiver Bitstream:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w")
        self.bit_unstuff_lbl = tk.Label(bit_box, text="Awaiting test...", font=FONTS["code"], fg=COLORS["text_muted"], bg=COLORS["bg_surface_alt"], anchor="w", padx=6, pady=4)
        self.bit_unstuff_lbl.pack(fill=tk.X)

    def _run_character_stuffing(self):
        data = self.char_input.get()
        res = self.app.framing_adapter.character_stuff(data)
        self.char_output.delete("1.0", tk.END)
        self.char_output.insert(tk.END, res["framed_output"])

        unstuffed = self.app.framing_adapter.character_unstuff(res["framed_output"])
        is_match = (unstuffed == data)
        self.char_unstuff_lbl.config(
            text=f"Receiver Verified ({'MATCH [OK]' if is_match else 'MISMATCH'}): {unstuffed}",
            fg=COLORS["success"] if is_match else COLORS["danger"]
        )

    def _run_bit_stuffing(self):
        bits = self.bit_input.get().strip()
        res = self.app.framing_adapter.bit_stuff(bits)
        self.bit_output.delete("1.0", tk.END)
        self.bit_output.insert(tk.END, f"{res['framed_bits']}\n(Inserted {res['num_stuffed_zeros']} stuffed '0' bits)")

        unstuffed = self.app.framing_adapter.bit_unstuff(res["framed_bits"])
        is_match = (unstuffed == res["original_bits"])
        self.bit_unstuff_lbl.config(
            text=f"Receiver Verified ({'MATCH [OK]' if is_match else 'MISMATCH'}): {unstuffed}",
            fg=COLORS["success"] if is_match else COLORS["danger"]
        )

    # =========================================================================
    # SUBTAB 2: CRC Error Detection
    # =========================================================================
    def _build_crc_subtab(self):
        p = self.tab_crc
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)

        # Left Column: Frame Checksum & Interactive Bit Corruption Injection
        left_box = tk.LabelFrame(
            p, text=" CRC Checksum Generation & Error Injection ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(left_box, text="Test Message String:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(anchor="w")
        self.crc_input = tk.Entry(left_box, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        self.crc_input.insert(0, "PATIENT_VITALS: HR=80,SPO2=99,TEMP=37.1")
        self.crc_input.pack(fill=tk.X, pady=(2, 6))

        # Algorithm choice
        algo_f = tk.Frame(left_box, bg=COLORS["bg_surface"])
        algo_f.pack(fill=tk.X, pady=4)
        tk.Label(algo_f, text="Polynomial:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.crc_algo_var = tk.StringVar(value="CRC-16-CCITT")
        cb_crc = ttk.Combobox(algo_f, textvariable=self.crc_algo_var, values=["CRC-16-CCITT", "CRC-32"], state="readonly", width=16)
        cb_crc.pack(side=tk.LEFT, padx=8)

        btn_calc_crc = tk.Button(
            algo_f, text="Compute Checksum", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=8,
            command=self._compute_crc
        )
        btn_calc_crc.pack(side=tk.LEFT)

        self.lbl_crc_val = tk.Label(left_box, text="Computed Checksum: None", font=FONTS["body_bold"], fg=COLORS["secondary"], bg=COLORS["bg_surface"], anchor="w")
        self.lbl_crc_val.pack(fill=tk.X, pady=4)

        # Error injection section
        err_box = tk.LabelFrame(left_box, text=" Physical Layer Noise Simulation ", font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_surface_alt"], padx=8, pady=6)
        err_box.pack(fill=tk.X, pady=(8, 4))

        tk.Label(err_box, text="Simulate transmission line interference by flipping 1 bit in frame:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface_alt"]).pack(anchor="w")
        
        btn_f = tk.Frame(err_box, bg=COLORS["bg_surface_alt"])
        btn_f.pack(fill=tk.X, pady=4)

        btn_clean_check = tk.Button(
            btn_f, text="Check Clean Frame", font=FONTS["caption"],
            bg=COLORS["success"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=8,
            command=self._check_clean_frame
        )
        btn_clean_check.pack(side=tk.LEFT, padx=(0, 6))

        btn_corrupt = tk.Button(
            btn_f, text="[!] Flip 1 Bit & Check Frame", font=FONTS["caption"],
            bg=COLORS["danger"], fg=COLORS["text_primary"], relief=tk.FLAT, padx=8,
            command=self._corrupt_and_check_frame
        )
        btn_corrupt.pack(side=tk.LEFT)

        self.lbl_crc_check_result = tk.Label(
            left_box, text="Verification Result: Not Run", font=FONTS["body_bold"],
            fg=COLORS["text_muted"], bg=COLORS["bg_surface"], anchor="w"
        )
        self.lbl_crc_check_result.pack(fill=tk.X, pady=6)

        # Right Column: Pedagogical Modulo-2 XOR Division Visualizer
        right_box = tk.LabelFrame(
            p, text=" Modulo-2 Long Division (Educational Step-by-Step) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        right_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        div_ctrl = tk.Frame(right_box, bg=COLORS["bg_surface"])
        div_ctrl.pack(fill=tk.X, pady=(0, 6))

        tk.Label(div_ctrl, text="Data:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.div_data_in = tk.Entry(div_ctrl, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"], width=14)
        self.div_data_in.insert(0, "1101011011")
        self.div_data_in.pack(side=tk.LEFT, padx=4)

        tk.Label(div_ctrl, text="Gen P(x):", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.div_gen_in = tk.Entry(div_ctrl, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"], width=8)
        self.div_gen_in.insert(0, "10011")
        self.div_gen_in.pack(side=tk.LEFT, padx=4)

        btn_demo_div = tk.Button(
            div_ctrl, text="Demonstrate Division", font=FONTS["caption"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT,
            command=self._run_modulo2_demo
        )
        btn_demo_div.pack(side=tk.LEFT, padx=4)

        self.txt_div_steps = tk.Text(
            right_box, height=12, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.WORD
        )
        self.txt_div_steps.pack(fill=tk.BOTH, expand=True)

        self._run_modulo2_demo()

    def _compute_crc(self):
        text = self.crc_input.get().encode("utf-8")
        algo = self.crc_algo_var.get()
        c = self.app.crc_adapter.compute_checksum(text, algo)
        self.last_crc = c
        self.lbl_crc_val.config(text=f"Computed Checksum ({algo}): {c}")

    def _check_clean_frame(self):
        text = self.crc_input.get().encode("utf-8")
        algo = self.crc_algo_var.get()
        c = self.app.crc_adapter.compute_checksum(text, algo)
        is_valid = self.app.crc_adapter.verify_checksum(text, c, algo)
        self.lbl_crc_check_result.config(
            text=f"● CRC Verification: MATCH [Valid Frame - No Errors Detected] ({c})",
            fg=COLORS["success"]
        )

    def _corrupt_and_check_frame(self):
        text = self.crc_input.get().encode("utf-8")
        algo = self.crc_algo_var.get()
        original_crc = self.app.crc_adapter.compute_checksum(text, algo)

        # Invert 1 bit in payload
        corrupted_bytes = self.app.crc_adapter.inject_bit_error(text, byte_offset=2, bit_pos=1)
        new_crc = self.app.crc_adapter.compute_checksum(corrupted_bytes, algo)
        is_valid = self.app.crc_adapter.verify_checksum(corrupted_bytes, original_crc, algo)

        self.lbl_crc_check_result.config(
            text=f"● CRC ERROR DETECTED! Frame Rejected.\n  Expected: {original_crc} | Computed: {new_crc}",
            fg=COLORS["danger"]
        )
        self.app.dashboard_tab.log_event(
            f"CRC DETECTED CORRUPTION: Bit flip in frame triggered CRC mismatch ({original_crc} != {new_crc}). Frame dropped."
        )

    def _run_modulo2_demo(self):
        data = self.div_data_in.get().strip()
        gen = self.div_gen_in.get().strip()
        res = self.app.crc_adapter.step_by_step_modulo2_division(data, gen)

        self.txt_div_steps.delete("1.0", tk.END)
        self.txt_div_steps.insert(tk.END, f"--- CRC MODULO-2 POLYNOMIAL DIVISION DEMO ---\n")
        self.txt_div_steps.insert(tk.END, f"Input Data:               {res['original_data']}\n")
        self.txt_div_steps.insert(tk.END, f"Generator Polynomial G(x): {res['generator_polynomial']} (degree {res['degree_k']})\n")
        self.txt_div_steps.insert(tk.END, f"Augmented Data:           {res['augmented_data']}\n")
        self.txt_div_steps.insert(tk.END, f"Remainder (CRC Checksum): {res['remainder_crc']}\n")
        self.txt_div_steps.insert(tk.END, f"Transmitted Codeword:     {res['transmitted_codeword']}\n\n")
        self.txt_div_steps.insert(tk.END, "Step-by-Step XOR Operations:\n")
        for s in res["steps_log"]:
            self.txt_div_steps.insert(tk.END, f" • {s}\n")

    # =========================================================================
    # SUBTAB 3: Go-Back-N ARQ (Sliding Window)
    # =========================================================================
    def _build_gbn_subtab(self):
        p = self.tab_gbn

        ctrl_frame = tk.LabelFrame(
            p, text=" Go-Back-N Protocol Simulation Parameters ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        ctrl_frame.pack(fill=tk.X, pady=(0, 8))

        row = tk.Frame(ctrl_frame, bg=COLORS["bg_surface"])
        row.pack(fill=tk.X)

        tk.Label(row, text="Sliding Window Size (N):", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 4))
        self.gbn_win_var = tk.IntVar(value=4)
        sp_win = tk.Spinbox(row, from_=1, to=8, textvariable=self.gbn_win_var, width=5, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        sp_win.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(row, text="Total Packets:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 4))
        self.gbn_total_var = tk.IntVar(value=8)
        sp_tot = tk.Spinbox(row, from_=4, to=20, textvariable=self.gbn_total_var, width=5, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        sp_tot.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(row, text="Drop Packet # on 1st try:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 4))
        self.gbn_drop_var = tk.IntVar(value=2)
        sp_drop = tk.Spinbox(row, from_=-1, to=15, textvariable=self.gbn_drop_var, width=5, font=FONTS["code"], bg=COLORS["bg_entry"], fg=COLORS["text_primary"])
        sp_drop.pack(side=tk.LEFT, padx=(0, 16))

        btn_sim_gbn = tk.Button(
            row, text="▶ Run Go-Back-N ARQ Simulation", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=12, pady=3,
            command=self._run_gbn_simulation
        )
        btn_sim_gbn.pack(side=tk.LEFT)

        # Simulation Event Stream
        log_box = tk.LabelFrame(
            p, text=" Go-Back-N Protocol State Trace (Sender Window, ACKs, Timeouts & Retransmissions) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        log_box.pack(fill=tk.BOTH, expand=True)

        self.txt_gbn_log = tk.Text(
            log_box, height=12, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.WORD
        )
        self.txt_gbn_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_box, orient=tk.VERTICAL, command=self.txt_gbn_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_gbn_log.config(yscrollcommand=scrollbar.set)

    def _run_gbn_simulation(self):
        n = self.gbn_win_var.get()
        total = self.gbn_total_var.get()
        drop = self.gbn_drop_var.get()
        drops = [drop] if drop >= 0 else []

        sim_res = self.app.reliable_adapter.simulate_gbn_transmission(
            total_packets=total, window_size=n, loss_indices=drops
        )

        self.txt_gbn_log.delete("1.0", tk.END)
        for line in sim_res["events_log"]:
            self.txt_gbn_log.insert(tk.END, f"{line}\n")
        self.txt_gbn_log.see(tk.END)

        # Add records to main app
        for r in sim_res["transmission_results"]:
            self.app.add_transmission_result(r)

        self.app.dashboard_tab.log_event(
            f"ARQ SIMULATION: Go-Back-N completed for {total} packets (Window N={n}). Retransmitted packets: {sum(sim_res['retransmission_counts'].values())}."
        )

    # =========================================================================
    # SUBTAB 4: Hospital Routing (Dijkstra / Distance Vector)
    # =========================================================================
    def _build_routing_subtab(self):
        p = self.tab_routing
        p.columnconfigure(0, weight=1)
        p.columnconfigure(1, weight=1)

        # Left Column: Dijkstra Shortest Path Finder
        dijk_box = tk.LabelFrame(
            p, text=" Dijkstra's Shortest Path Algorithm (Link-State) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        dijk_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        nodes = self.app.routing_adapter.get_nodes()

        row1 = tk.Frame(dijk_box, bg=COLORS["bg_surface"])
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="Source:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.dijk_src_var = tk.StringVar(value="ICU Ward")
        cb_src = ttk.Combobox(row1, textvariable=self.dijk_src_var, values=nodes, state="readonly", width=14)
        cb_src.pack(side=tk.LEFT, padx=(4, 10))

        tk.Label(row1, text="Dest:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.dijk_dst_var = tk.StringVar(value="Central Server")
        cb_dst = ttk.Combobox(row1, textvariable=self.dijk_dst_var, values=nodes, state="readonly", width=14)
        cb_dst.pack(side=tk.LEFT, padx=4)

        btn_find_path = tk.Button(
            row1, text="Find Shortest Path", font=FONTS["caption"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], relief=tk.FLAT,
            command=self._run_dijkstra
        )
        btn_find_path.pack(side=tk.LEFT, padx=6)

        self.txt_dijkstra = tk.Text(
            dijk_box, height=12, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.WORD
        )
        self.txt_dijkstra.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        # Right Column: Distance Vector Routing Table Matrix
        dv_box = tk.LabelFrame(
            p, text=" Distance Vector Routing Tables (Bellman-Ford) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=10, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        dv_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        row2 = tk.Frame(dv_box, bg=COLORS["bg_surface"])
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="Select Node Table:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT)
        self.dv_node_var = tk.StringVar(value="ICU Ward")
        cb_dv = ttk.Combobox(row2, textvariable=self.dv_node_var, values=nodes, state="readonly", width=16)
        cb_dv.pack(side=tk.LEFT, padx=6)
        cb_dv.bind("<<ComboboxSelected>>", lambda e: self._show_distance_vector())

        btn_show_dv = tk.Button(
            row2, text="Generate DV Matrix", font=FONTS["caption"],
            bg=COLORS["secondary"], fg=COLORS["text_dark"], relief=tk.FLAT,
            command=self._show_distance_vector
        )
        btn_show_dv.pack(side=tk.LEFT, padx=4)

        self.txt_dv = tk.Text(
            dv_box, height=12, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.WORD
        )
        self.txt_dv.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        self._run_dijkstra()
        self._show_distance_vector()

    def _run_dijkstra(self):
        src = self.dijk_src_var.get()
        dst = self.dijk_dst_var.get()
        res = self.app.routing_adapter.run_dijkstra(src, dst)

        self.txt_dijkstra.delete("1.0", tk.END)
        self.txt_dijkstra.insert(tk.END, f"=== DIJKSTRA SHORTEST PATH CALCULATION ===\n")
        self.txt_dijkstra.insert(tk.END, f"Source Department:      {src}\n")
        self.txt_dijkstra.insert(tk.END, f"Destination Department: {dst}\n")
        path_str = " -> ".join(res["path"])
        self.txt_dijkstra.insert(tk.END, f"Optimal Route:          {path_str}\n")
        self.txt_dijkstra.insert(tk.END, f"Total Path Metric:      {res['total_cost_ms']} ms latency\n")
        self.txt_dijkstra.insert(tk.END, f"Total Hop Count:        {res['hop_count']} hops\n\n")
        self.txt_dijkstra.insert(tk.END, "Edge Relaxations:\n")
        for log in res["relaxation_log"][:8]:
            self.txt_dijkstra.insert(tk.END, f" • {log}\n")

    def _show_distance_vector(self):
        dv_tables = self.app.routing_adapter.run_distance_vector()
        node = self.dv_node_var.get()
        table = dv_tables.get(node, [])

        self.txt_dv.delete("1.0", tk.END)
        self.txt_dv.insert(tk.END, f"=== DISTANCE VECTOR ROUTING TABLE: {node.upper()} ===\n")
        self.txt_dv.insert(tk.END, f"{'Destination Subnet':<24} | {'Cost (ms)':<10} | {'Next Hop':<18}\n")
        self.txt_dv.insert(tk.END, "-" * 60 + "\n")
        for entry in table:
            self.txt_dv.insert(
                tk.END,
                f"{entry['destination']:<24} | {entry['cost_ms']:<10.1f} | {entry['next_hop']:<18}\n"
            )
