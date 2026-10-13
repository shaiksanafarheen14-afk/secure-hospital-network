"""Secure Patient Data Communication Demo Tab.

Demonstrates authenticated encryption/decryption (AES-128-CBC + HMAC-SHA256 via Fernet)
using synthetic clinical patient records across hospital departments.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time

try:
    from gui.theme import COLORS, FONTS
    from core.models import PatientRecord, TransmissionResult, DeliveryStatus
    from core.synthetic_data import get_preset_synthetic_records, HOSPITAL_DEPARTMENTS
except (ImportError, ValueError):
    from ..theme import COLORS, FONTS
    from ...core.models import PatientRecord, TransmissionResult, DeliveryStatus
    from ...core.synthetic_data import get_preset_synthetic_records, HOSPITAL_DEPARTMENTS


class PatientCommTab(tk.Frame):
    """Interactive end-to-end secure transmission view."""

    def __init__(self, parent, app_controller, **kwargs):
        super().__init__(parent, bg=COLORS["bg_main"], **kwargs)
        self.app = app_controller
        self.presets = get_preset_synthetic_records()
        self.current_ciphertext: bytes = b""
        self.is_channel_tampered = False

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_main"], padx=14, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # ---------------------------------------------------------
        # Top Bar: Department & Preset Selection
        # ---------------------------------------------------------
        top_bar = tk.LabelFrame(
            container, text=" Transmission Endpoints & Synthetic Patient Profile ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=8, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        top_bar.pack(fill=tk.X, pady=(0, 10))

        # Endpoint row
        ep_row = tk.Frame(top_bar, bg=COLORS["bg_surface"])
        ep_row.pack(fill=tk.X, pady=4)

        tk.Label(ep_row, text="Sender Department:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 6))
        self.sender_var = tk.StringVar(value="ICU Ward 3")
        sender_cb = ttk.Combobox(ep_row, textvariable=self.sender_var, values=HOSPITAL_DEPARTMENTS[:-1], state="readonly", width=20)
        sender_cb.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(ep_row, text="Receiver Department:", font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 6))
        self.receiver_var = tk.StringVar(value="Central Hospital Server")
        receiver_cb = ttk.Combobox(ep_row, textvariable=self.receiver_var, values=HOSPITAL_DEPARTMENTS, state="readonly", width=22)
        receiver_cb.pack(side=tk.LEFT, padx=(0, 20))

        # Preset selector row
        preset_row = tk.Frame(top_bar, bg=COLORS["bg_surface"])
        preset_row.pack(fill=tk.X, pady=(6, 2))

        tk.Label(preset_row, text="Load Synthetic Record:", font=FONTS["body_bold"], fg=COLORS["primary"], bg=COLORS["bg_surface"]).pack(side=tk.LEFT, padx=(0, 6))
        preset_titles = [f"{p.patient_id} - {p.department} ({p.condition})" for p in self.presets]
        self.preset_var = tk.StringVar(value=preset_titles[0])
        preset_cb = ttk.Combobox(preset_row, textvariable=self.preset_var, values=preset_titles, state="readonly", width=45)
        preset_cb.pack(side=tk.LEFT, padx=(0, 10))
        preset_cb.bind("<<ComboboxSelected>>", self._on_preset_selected)

        btn_load = tk.Button(
            preset_row, text="Apply Preset", font=FONTS["caption"],
            bg=COLORS["bg_entry"], fg=COLORS["primary"], relief=tk.FLAT,
            command=self._load_selected_preset
        )
        btn_load.pack(side=tk.LEFT)

        # ---------------------------------------------------------
        # Main Split: Sender Station vs Receiver Station
        # ---------------------------------------------------------
        split_frame = tk.Frame(container, bg=COLORS["bg_main"])
        split_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        split_frame.columnconfigure(0, weight=1)
        split_frame.columnconfigure(1, weight=1)

        # Left Column: Sender Station
        sender_box = tk.LabelFrame(
            split_frame, text=" SENDER STATION (Origin Node) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        sender_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(
            sender_box, text="Clinical Record Payload (Synthetic JSON / Plaintext):",
            font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        self.txt_plaintext = tk.Text(
            sender_box, height=8, bg=COLORS["bg_surface_alt"], fg=COLORS["text_primary"],
            font=FONTS["code"], wrap=tk.WORD, insertbackground=COLORS["primary"]
        )
        self.txt_plaintext.pack(fill=tk.BOTH, expand=True, pady=(4, 8))

        # Encryption controls
        enc_bar = tk.Frame(sender_box, bg=COLORS["bg_surface"])
        enc_bar.pack(fill=tk.X, pady=(0, 8))

        btn_encrypt = tk.Button(
            enc_bar, text="① Encrypt & Frame Payload", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["text_dark"], activebackground=COLORS["primary_hover"],
            relief=tk.FLAT, padx=10, pady=4, command=self._encrypt_payload
        )
        btn_encrypt.pack(side=tk.LEFT)

        btn_gen_key = tk.Button(
            enc_bar, text="Gen New Key", font=FONTS["caption"],
            bg=COLORS["bg_entry"], fg=COLORS["text_secondary"], relief=tk.FLAT, padx=6, pady=4,
            command=self._generate_key
        )
        btn_gen_key.pack(side=tk.LEFT, padx=6)

        # Ciphertext display box
        tk.Label(
            sender_box, text="Encrypted Ciphertext Token (Confidential & Authenticated):",
            font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        self.txt_ciphertext = tk.Text(
            sender_box, height=5, bg=COLORS["bg_surface_alt"], fg=COLORS["secondary"],
            font=FONTS["code"], wrap=tk.CHAR, state=tk.DISABLED
        )
        self.txt_ciphertext.pack(fill=tk.X, pady=(4, 8))

        # Channel impairment options
        chan_frame = tk.Frame(sender_box, bg=COLORS["bg_surface_alt"], padx=8, pady=6)
        chan_frame.pack(fill=tk.X)

        self.tamper_var = tk.BooleanVar(value=False)
        chk_tamper = tk.Checkbutton(
            chan_frame, text="Simulate Channel Tampering / MITM (Corrupt ciphertext byte)",
            variable=self.tamper_var, font=FONTS["caption"],
            fg=COLORS["warning"], bg=COLORS["bg_surface_alt"], selectcolor=COLORS["bg_main"],
            activebackground=COLORS["bg_surface_alt"], activeforeground=COLORS["warning"]
        )
        chk_tamper.pack(side=tk.LEFT)

        btn_transmit = tk.Button(
            chan_frame, text="② Transmit Frame ->", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg=COLORS["text_dark"], relief=tk.FLAT, padx=10, pady=3,
            command=self._transmit_frame
        )
        btn_transmit.pack(side=tk.RIGHT)

        # Right Column: Receiver Station
        receiver_box = tk.LabelFrame(
            split_frame, text=" RECEIVER STATION (Destination Node) ",
            font=FONTS["section_header"], fg=COLORS["primary"], bg=COLORS["bg_surface"],
            padx=12, pady=10, highlightthickness=1, highlightbackground=COLORS["border"]
        )
        receiver_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        tk.Label(
            receiver_box, text="Incoming Frame Buffer:",
            font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        self.lbl_buffer_info = tk.Label(
            receiver_box, text="Buffer status: Awaiting transmission...",
            font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_surface"], anchor="w"
        )
        self.lbl_buffer_info.pack(fill=tk.X, pady=2)

        self.txt_receiver_buffer = tk.Text(
            receiver_box, height=4, bg=COLORS["bg_surface_alt"], fg=COLORS["text_secondary"],
            font=FONTS["code"], wrap=tk.CHAR, state=tk.DISABLED
        )
        self.txt_receiver_buffer.pack(fill=tk.X, pady=(2, 8))

        # Receiver action bar
        rcv_bar = tk.Frame(receiver_box, bg=COLORS["bg_surface"])
        rcv_bar.pack(fill=tk.X, pady=(0, 8))

        btn_decrypt = tk.Button(
            rcv_bar, text="③ Authenticate & Decrypt Payload", font=FONTS["body_bold"],
            bg=COLORS["success"], fg=COLORS["text_dark"], activebackground="#34d399",
            relief=tk.FLAT, padx=10, pady=4, command=self._decrypt_payload
        )
        btn_decrypt.pack(side=tk.LEFT)

        self.lbl_auth_status = tk.Label(
            rcv_bar, text="Authentication Status: Not Checked",
            font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_surface"]
        )
        self.lbl_auth_status.pack(side=tk.RIGHT)

        # Decrypted Record Output
        tk.Label(
            receiver_box, text="Verified Patient Plaintext (Accessible only upon Valid Decryption):",
            font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=COLORS["bg_surface"]
        ).pack(anchor="w")

        self.txt_decrypted = tk.Text(
            receiver_box, height=9, bg=COLORS["bg_surface_alt"], fg=COLORS["text_primary"],
            font=FONTS["code"], wrap=tk.WORD, state=tk.DISABLED
        )
        self.txt_decrypted.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # Populate initial preset
        self._load_selected_preset()

    def _on_preset_selected(self, event=None):
        self._load_selected_preset()

    def _load_selected_preset(self):
        sel_idx = 0
        current_title = self.preset_var.get()
        for idx, p in enumerate(self.presets):
            if p.patient_id in current_title:
                sel_idx = idx
                break
        rec = self.presets[sel_idx]
        self.txt_plaintext.delete("1.0", tk.END)
        self.txt_plaintext.insert(tk.END, rec.to_json())

    def _generate_key(self):
        new_k = self.app.encryption_adapter.generate_new_key()
        messagebox.showinfo(
            "Session Key Generated",
            f"New 256-bit AES encryption session key generated!\nKey prefix: {new_k[:12].decode('latin1', errors='ignore')}..."
        )
        self.app.dashboard_tab.log_event("SECURITY: New cryptographic session key established for department endpoints.")

    def _encrypt_payload(self):
        plaintext = self.txt_plaintext.get("1.0", tk.END).strip()
        if not plaintext:
            messagebox.showwarning("Empty Payload", "Please enter or select a synthetic patient record.")
            return

        ciphertext, algo_name = self.app.encryption_adapter.encrypt_payload(plaintext)
        self.current_ciphertext = ciphertext

        self.txt_ciphertext.config(state=tk.NORMAL)
        self.txt_ciphertext.delete("1.0", tk.END)
        self.txt_ciphertext.insert(tk.END, ciphertext.decode("utf-8", errors="replace"))
        self.txt_ciphertext.config(state=tk.DISABLED)

        # Masked preview for privacy
        masked = self.app.encryption_adapter.mask_sensitive_payload(plaintext)
        self.app.dashboard_tab.log_event(
            f"ENCRYPT: {self.sender_var.get()} encrypted patient payload ({len(ciphertext)} bytes) using {algo_name}. {masked}"
        )

    def _transmit_frame(self):
        if not self.current_ciphertext:
            messagebox.showwarning("Transmission Error", "Please encrypt the payload before transmitting.")
            return

        transmitted_data = self.current_ciphertext
        if self.tamper_var.get():
            transmitted_data = self.app.encryption_adapter.tamper_ciphertext(transmitted_data)
            self.is_channel_tampered = True
            tamper_msg = "[!] CHANNEL CORRUPTION: 1 byte flipped in transit to simulate malicious tampering/noise."
        else:
            self.is_channel_tampered = False
            tamper_msg = "[OK] Channel transit normal (Clean transmission)."

        self.txt_receiver_buffer.config(state=tk.NORMAL)
        self.txt_receiver_buffer.delete("1.0", tk.END)
        self.txt_receiver_buffer.insert(tk.END, transmitted_data.decode("utf-8", errors="replace"))
        self.txt_receiver_buffer.config(state=tk.DISABLED)

        self.lbl_buffer_info.config(
            text=f"Frame received: {len(transmitted_data)} bytes from {self.sender_var.get()} | {tamper_msg}",
            fg=COLORS["warning"] if self.is_channel_tampered else COLORS["text_secondary"]
        )

        self.app.dashboard_tab.log_event(
            f"TRANSMIT: Dispatched frame from {self.sender_var.get()} -> {self.receiver_var.get()}. {tamper_msg}"
        )

    def _decrypt_payload(self):
        content = self.txt_receiver_buffer.get("1.0", tk.END).strip().encode("utf-8")
        if not content:
            messagebox.showwarning("Buffer Empty", "Receiver buffer is empty. Transmit a frame first.")
            return

        decrypted_text, is_valid, status_msg = self.app.encryption_adapter.decrypt_payload(content)

        self.txt_decrypted.config(state=tk.NORMAL)
        self.txt_decrypted.delete("1.0", tk.END)

        if is_valid and decrypted_text:
            self.lbl_auth_status.config(text="● Authentic (HMAC Valid)", fg=COLORS["success"])
            self.txt_decrypted.insert(tk.END, decrypted_text)
            self.app.dashboard_tab.log_event(
                f"RECEIVER SUCCESS: {self.receiver_var.get()} verified authentication tag and decrypted record successfully."
            )
            # Record successful transmission result
            self.app.record_transmission(
                sender=self.sender_var.get(),
                receiver=self.receiver_var.get(),
                frame_size=len(content),
                delivery_status=DeliveryStatus.DELIVERED,
                latency_ms=14.5,
                crc_status="Valid (Checked)"
            )
        else:
            self.lbl_auth_status.config(text="● REJECTED (Tampered / Invalid HMAC)", fg=COLORS["danger"])
            self.txt_decrypted.insert(
                tk.END,
                f"*** SECURITY INTEGRITY FAILURE ***\n\n{status_msg}\n\n"
                "The patient data packet was REJECTED by the receiver because the HMAC-SHA256 authentication tag "
                "did not match the ciphertext. This prevents altered vitals or unauthorized payloads from entering the clinical system!"
            )
            self.app.dashboard_tab.log_event(
                f"SECURITY ALERT: {self.receiver_var.get()} detected corrupted/tampered ciphertext! Authentication failed."
            )
            self.app.record_transmission(
                sender=self.sender_var.get(),
                receiver=self.receiver_var.get(),
                frame_size=len(content),
                delivery_status=DeliveryStatus.CORRUPTED,
                latency_ms=8.0,
                crc_status="Tampered / Decryption Failed"
            )

        self.txt_decrypted.config(state=tk.DISABLED)
