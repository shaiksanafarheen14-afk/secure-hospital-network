"""Entry point for Secure Hospital Network GUI & Performance Analysis."""

import sys
import os
from pathlib import Path
import tkinter as tk

# Ensure current and parent directory are on sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from gui.app import HospitalNetworkApp


def main():
    """Launch Desktop GUI Application."""
    root = tk.Tk()
    app = HospitalNetworkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
