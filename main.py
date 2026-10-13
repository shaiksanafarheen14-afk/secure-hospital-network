"""Root Convenience Launcher for Secure Hospital Network.

Usage:
    python main.py
"""

import sys
from pathlib import Path

# Add gui-analysis to sys.path so modules can resolve cleanly
repo_root = Path(__file__).resolve().parent
gui_analysis_dir = repo_root / "gui-analysis"

if str(gui_analysis_dir) not in sys.path:
    sys.path.insert(0, str(gui_analysis_dir))

if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from gui.app import HospitalNetworkApp
import tkinter as tk


def main():
    """Launch the Hospital Network Dashboard."""
    root = tk.Tk()
    app = HospitalNetworkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
