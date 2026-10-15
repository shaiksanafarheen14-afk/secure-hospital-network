# =============================================================================
# utils.py -- Terminal Display Helpers
# =============================================================================
# Centralised pretty-print functions used across the simulation.
# Keeping all display logic here makes the other modules cleaner.
# =============================================================================

from reliable_transmission.framing import frame_to_str

# ANSI colour codes for terminal output (work on most modern terminals)
RESET   = "\033[0m"
BOLD    = "\033[1m"
GREEN   = "\033[92m"
RED     = "\033[91m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"
WHITE   = "\033[97m"


def _c(text: str, colour: str) -> str:
    """Wraps text in an ANSI colour code."""
    return f"{colour}{text}{RESET}"


def print_banner():
    """Prints the project banner at startup."""
    print()
    print(_c("=" * 68, CYAN))
    print(_c("  [HOSPITAL]  SECURE HOSPITAL NETWORK", BOLD + WHITE))
    print(_c("  [NETWORK]   Reliable Data Transmission & Error Detection", CYAN))
    print(_c("=" * 68, CYAN))
    print()


def print_section(title: str):
    """Prints a section divider with a title."""
    print()
    print(_c("-" * 68, MAGENTA))
    print(_c(f"  >> {title}", BOLD + MAGENTA))
    print(_c("-" * 68, MAGENTA))
    print()


def print_channel_info(sender: str, receiver: str, message: str):
    """Prints a summary of the transmission about to happen."""
    print(f"  [SND] {_c('Sender  :', YELLOW)} {_c(sender, BOLD)}")
    print(f"  [RCV] {_c('Receiver:', YELLOW)} {_c(receiver, BOLD)}")
    print(f"  [MSG] {_c('Message :', YELLOW)} {message}")
    print()


def print_frames_summary(frames: list):
    """Prints a summary table of all frames before transmission."""
    print(_c("  Frames created:", CYAN))
    for f in frames:
        print(f"    {frame_to_str(f)}")
    print()


def print_window(base: int, next_seq: int, window_size: int, total: int):
    """Prints a visual representation of the current sliding window."""
    slots = []
    for i in range(total):
        if i < base:
            slots.append(_c(f"[{i}:ACK]", GREEN))          # Already ACKed
        elif i < next_seq:
            slots.append(_c(f"[{i}:->]", YELLOW))          # In-flight / sent
        elif i < base + window_size:
            slots.append(_c(f"[{i}:   ]", CYAN))           # In window, not sent yet
        else:
            slots.append(f"[{i}:   ]")                     # Outside window
    print("  Window: " + " ".join(slots))


def print_sender_action(seq: int, frame: dict, attempt: int = 1):
    """Prints a sender transmission log line."""
    prefix = _c("  -> SEND", GREEN)
    seq_tag = _c(f"Frame {seq}", BOLD + GREEN)
    if attempt > 1:
        seq_tag += _c(f" (attempt #{attempt})", YELLOW)
    print(f"{prefix} {seq_tag} {frame_to_str(frame)}")


def print_receiver_action(seq: int, ack_msg: str, corrupted: bool):
    """Prints a receiver response log line."""
    if corrupted:
        print(f"  {_c('[x] CORRUPT', RED)}  Frame {seq}  {_c(ack_msg, RED)}")
    else:
        print(f"  {_c('[+] OK     ', GREEN)}  Frame {seq}  {_c(ack_msg, GREEN)}")


def print_retransmit(seq: int, retry: int, max_retries: int):
    """Prints a retransmission notice."""
    print(_c(f"  [~] RETRANSMIT from Frame {seq}  "
             f"(retry {retry}/{max_retries})", YELLOW))
    print()


def print_success(message: str, receiver_name: str):
    """Prints the final delivery success message."""
    print(_c("-" * 68, GREEN))
    print(_c(f"  [OK] MESSAGE DELIVERED SUCCESSFULLY to {receiver_name}", BOLD + GREEN))
    print(f"  [>>] Reconstructed: {_c(message, BOLD + WHITE)}")
    print(_c("-" * 68, GREEN))


def print_failure(seq: int):
    """Prints a max-retry failure message."""
    print(_c(f"  [!!] FAILED: Frame {seq} could not be delivered "
             f"after maximum retries.", RED))


def print_final_summary(results: list):
    """Prints the final comparison table of protocol results."""
    print_section("FINAL DELIVERY SUMMARY")
    print(f"  {'Protocol':<25}  {'Frames Delivered':<18}  Message")
    print("  " + "-" * 64)
    for protocol, count, msg in results:
        status = _c("[OK]", GREEN) if msg else _c("[!!]", RED)
        print(f"  {status}  {protocol:<23}  {str(count):<18}  {msg or 'FAILED'}")
    print()
