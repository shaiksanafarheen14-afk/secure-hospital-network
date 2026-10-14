"""
display.py
----------
Handles all terminal output formatting for the simulation.
Provides coloured, structured, beginner-friendly logs for each step.
"""

# Ensure stdout uses UTF-8 on Windows (avoids cp1252 UnicodeEncodeError)
import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ANSI colour codes for terminal output
class Colour:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    WHITE   = "\033[97m"


def banner(title: str) -> None:
    """Print a prominent section banner."""
    width = 70
    line  = "=" * width
    print(f"\n{Colour.CYAN}{Colour.BOLD}{line}")
    print(f"  {title}")
    print(f"{line}{Colour.RESET}\n")


def section(title: str) -> None:
    """Print a sub-section separator."""
    dashes = "-" * max(0, 60 - len(title))
    print(f"\n{Colour.BLUE}{Colour.BOLD}-- {title} {dashes}{Colour.RESET}")


def info(msg: str) -> None:
    """General informational message."""
    print(f"  {Colour.WHITE}{msg}{Colour.RESET}")


def send(frame_num: int, data: str, crc: str) -> None:
    """Log a frame being sent."""
    print(f"  {Colour.CYAN}[SEND]    Frame [{frame_num:02d}] | Data: {data!r:30s} | CRC: {crc}{Colour.RESET}")


def corrupt(frame_num: int) -> None:
    """Log a frame being corrupted in the channel."""
    print(f"  {Colour.RED}[CORRUPT] Frame [{frame_num:02d}] - bit-flip injected by channel{Colour.RESET}")


def received_ok(frame_num: int, data: str) -> None:
    """Log a frame received without errors."""
    print(f"  {Colour.GREEN}[OK]      Frame [{frame_num:02d}] | Data: {data!r} - CRC OK{Colour.RESET}")


def received_error(frame_num: int) -> None:
    """Log a frame received with a CRC error."""
    print(f"  {Colour.RED}[ERROR]   Frame [{frame_num:02d}] - CRC mismatch detected!{Colour.RESET}")


def ack(frame_num: int) -> None:
    """Log an ACK being sent back."""
    print(f"  {Colour.GREEN}[ACK]     Frame [{frame_num:02d}] acknowledged{Colour.RESET}")


def nack(frame_num: int) -> None:
    """Log a NACK (negative acknowledgement)."""
    print(f"  {Colour.YELLOW}[NACK]    Frame [{frame_num:02d}] - requesting retransmission{Colour.RESET}")


def retransmit(frame_num: int) -> None:
    """Log a retransmission event."""
    print(f"  {Colour.MAGENTA}[RESEND]  Frame [{frame_num:02d}] - retransmitting{Colour.RESET}")


def window_state(base: int, window: list) -> None:
    """Show the current sliding-window state."""
    nums = ", ".join(str(w) for w in window)
    print(f"  {Colour.YELLOW}[WINDOW]  base={base} | Frames in window: [{nums}]{Colour.RESET}")


def delivery_report(sender: str, receiver: str, message: str) -> None:
    """Print the final delivery confirmation."""
    width = 70
    line  = "=" * width
    print(f"\n{Colour.GREEN}{Colour.BOLD}{line}")
    print(f"  [HOSPITAL] FINAL MESSAGE DELIVERED SUCCESSFULLY")
    print(f"{line}{Colour.RESET}")
    print(f"  {Colour.CYAN}From     : {sender}{Colour.RESET}")
    print(f"  {Colour.CYAN}To       : {receiver}{Colour.RESET}")
    print(f"  {Colour.GREEN}Message  : {message}{Colour.RESET}")
    print(f"{Colour.GREEN}{Colour.BOLD}{line}{Colour.RESET}\n")
