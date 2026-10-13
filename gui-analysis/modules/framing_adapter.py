"""Framing Adapter: Character Stuffing and Bit Stuffing for Data Link Layer.

Implements standard Computer Networks Data Link Layer framing techniques:
1. Character Stuffing (Byte-oriented with DLE STX / DLE ETX)
2. Bit Stuffing (Bit-oriented HDLC with 01111110 flag and zero-insertion after 5 ones)
"""

from typing import Tuple, Dict, Any

try:
    from modules.base_adapter import BaseProtocolAdapter, AdapterStatus
except (ImportError, ValueError):
    try:
        from .base_adapter import BaseProtocolAdapter, AdapterStatus
    except (ImportError, ValueError):
        from base_adapter import BaseProtocolAdapter, AdapterStatus


class FramingAdapter(BaseProtocolAdapter):
    """Adapter managing data link layer framing and deframing."""

    FLAG_BIT = "01111110"  # HDLC 0x7E Flag
    FLAG_CHAR_START = "DLE STX"
    FLAG_CHAR_END = "DLE ETX"
    ESCAPE_CHAR = "DLE"

    def __init__(self):
        super().__init__(
            protocol_name="Framing & Stuffing",
            candidate_modules=["framing.stuffing", "modules.framing", "framing"]
        )

    # -------------------------------------------------------------
    # Character Stuffing
    # -------------------------------------------------------------
    def character_stuff(self, data: str) -> Dict[str, Any]:
        """
        Applies character stuffing to data string.
        Rule: Every occurrence of 'DLE' in data is escaped with an extra 'DLE'.
        Framed as: [DLE STX] + stuffed_data + [DLE ETX]
        """
        # Escape any DLE with DLE DLE
        stuffed = data.replace(self.ESCAPE_CHAR, f"{self.ESCAPE_CHAR} {self.ESCAPE_CHAR}")
        framed = f"[{self.FLAG_CHAR_START}] {stuffed} [{self.FLAG_CHAR_END}]"
        
        return {
            "original": data,
            "stuffed_payload": stuffed,
            "framed_output": framed,
            "flags_used": f"{self.FLAG_CHAR_START} ... {self.FLAG_CHAR_END}",
            "method": "Character Stuffing (Byte-Oriented)"
        }

    def character_unstuff(self, framed: str) -> str:
        """
        Removes framing flags and unstuffs duplicated DLE escape characters.
        """
        start_tag = f"[{self.FLAG_CHAR_START}]"
        end_tag = f"[{self.FLAG_CHAR_END}]"
        
        cleaned = framed
        if cleaned.startswith(start_tag):
            cleaned = cleaned[len(start_tag):].strip()
        if cleaned.endswith(end_tag):
            cleaned = cleaned[:-len(end_tag)].strip()

        # Unstuff DLE DLE -> DLE
        unstuffed = cleaned.replace(f"{self.ESCAPE_CHAR} {self.ESCAPE_CHAR}", self.ESCAPE_CHAR)
        return unstuffed

    # -------------------------------------------------------------
    # Bit Stuffing
    # -------------------------------------------------------------
    def bit_stuff(self, bit_stream: str) -> Dict[str, Any]:
        """
        Applies bit stuffing (HDLC rule):
        Whenever 5 consecutive '1's appear, insert a '0'.
        Surrounded by '01111110' flags.
        """
        # Sanitize input bit stream (keep only '0' and '1')
        clean_bits = "".join(b for b in bit_stream if b in ("0", "1"))
        if not clean_bits:
            clean_bits = "00000000"

        stuffed_bits = []
        consecutive_ones = 0
        stuffed_indices = []

        for bit in clean_bits:
            stuffed_bits.append(bit)
            if bit == "1":
                consecutive_ones += 1
                if consecutive_ones == 5:
                    stuffed_bits.append("0")  # Insert stuffed 0
                    stuffed_indices.append(len(stuffed_bits) - 1)
                    consecutive_ones = 0
            else:
                consecutive_ones = 0

        stuffed_body = "".join(stuffed_bits)
        framed = f"{self.FLAG_BIT} {stuffed_body} {self.FLAG_BIT}"

        return {
            "original_bits": clean_bits,
            "stuffed_bits": stuffed_body,
            "framed_bits": framed,
            "num_stuffed_zeros": len(stuffed_indices),
            "flag": self.FLAG_BIT,
            "method": "Bit Stuffing (HDLC 01111110)"
        }

    def bit_unstuff(self, framed_bits: str) -> str:
        """
        Strips flags and removes the stuffed '0' after five consecutive '1's.
        """
        # Remove flags if present
        bits = framed_bits.replace(" ", "")
        if bits.startswith(self.FLAG_BIT):
            bits = bits[len(self.FLAG_BIT):]
        if bits.endswith(self.FLAG_BIT):
            bits = bits[:-len(self.FLAG_BIT)]

        unstuffed = []
        consecutive_ones = 0
        skip_next = False

        for bit in bits:
            if skip_next:
                skip_next = False
                continue

            unstuffed.append(bit)
            if bit == "1":
                consecutive_ones += 1
                if consecutive_ones == 5:
                    skip_next = True  # Discard the stuffed '0'
                    consecutive_ones = 0
            else:
                consecutive_ones = 0

        return "".join(unstuffed)

    @staticmethod
    def text_to_bit_string(text: str) -> str:
        """Convert ASCII text string to binary bit string."""
        return "".join(f"{ord(c):08b}" for c in text)

    @staticmethod
    def bit_string_to_text(bits: str) -> str:
        """Convert binary bit string back to ASCII text string."""
        clean = "".join(b for b in bits if b in ("0", "1"))
        chars = []
        for i in range(0, len(clean), 8):
            byte = clean[i:i + 8]
            if len(byte) == 8:
                chars.append(chr(int(byte, 2)))
        return "".join(chars)
