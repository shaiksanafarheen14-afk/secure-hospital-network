"""Custom reusable UI widgets: StatCard, Canvas Line Chart, and Canvas Bar Chart."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Tuple
try:
    from gui.theme import COLORS, FONTS
except (ImportError, ValueError):
    try:
        from .theme import COLORS, FONTS
    except (ImportError, ValueError):
        from theme import COLORS, FONTS


class StatCard(tk.Frame):
    """High-contrast KPI card displaying a primary metric, label, and status indicator."""

    def __init__(self, parent, title: str, initial_value: str = "0", subtext: str = "", accent_color: str = COLORS["primary"], **kwargs):
        super().__init__(parent, bg=COLORS["bg_surface"], highlightthickness=1, highlightbackground=COLORS["border"], **kwargs)
        self.accent_color = accent_color

        # Left accent stripe
        self.stripe = tk.Frame(self, bg=accent_color, width=5)
        self.stripe.pack(side=tk.LEFT, fill=tk.Y)

        # Content frame
        self.content = tk.Frame(self, bg=COLORS["bg_surface"], padx=10, pady=8)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_lbl = tk.Label(
            self.content, text=title.upper(), font=FONTS["stat_label"],
            fg=COLORS["text_muted"], bg=COLORS["bg_surface"], anchor="w"
        )
        self.title_lbl.pack(fill=tk.X)

        self.value_lbl = tk.Label(
            self.content, text=initial_value, font=FONTS["stat_value"],
            fg=COLORS["text_primary"], bg=COLORS["bg_surface"], anchor="w"
        )
        self.value_lbl.pack(fill=tk.X)

        self.subtext_lbl = tk.Label(
            self.content, text=subtext, font=FONTS["caption"],
            fg=COLORS["text_secondary"], bg=COLORS["bg_surface"], anchor="w"
        )
        self.subtext_lbl.pack(fill=tk.X)

    def set_value(self, value: str, subtext: Optional[str] = None):
        self.value_lbl.config(text=value)
        if subtext is not None:
            self.subtext_lbl.config(text=subtext)


class CanvasLineChart(tk.Frame):
    """Zero-dependency vector Line Chart rendered on a Tkinter Canvas."""

    def __init__(self, parent, title: str = "Latency per Packet (ms)", height: int = 180, **kwargs):
        super().__init__(parent, bg=COLORS["bg_surface"], highlightthickness=1, highlightbackground=COLORS["border"], **kwargs)
        self.title_text = title

        # Title Header
        header = tk.Frame(self, bg=COLORS["bg_surface"], padx=8, pady=4)
        header.pack(fill=tk.X)
        self.title_lbl = tk.Label(
            header, text=title, font=FONTS["subtitle"],
            fg=COLORS["primary"], bg=COLORS["bg_surface"]
        )
        self.title_lbl.pack(side=tk.LEFT)

        # Canvas
        self.canvas = tk.Canvas(
            self, bg=COLORS["bg_surface_alt"], height=height,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.data_points: List[float] = []

    def update_data(self, points: List[float]):
        """Set new data points and trigger canvas redraw."""
        self.data_points = points
        self.redraw()

    def redraw(self):
        """Draw axes, grid lines, data points, and average line."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        pad_left = 45
        pad_right = 20
        pad_top = 20
        pad_bottom = 30

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # If no data, display placeholder
        if not self.data_points:
            self.canvas.create_text(
                w / 2, h / 2,
                text="No transmission latency data recorded yet.\nRun a transmission to populate graph.",
                fill=COLORS["text_muted"], font=FONTS["caption"], justify=tk.CENTER
            )
            return

        # Compute min/max
        max_val = max(self.data_points)
        min_val = min(self.data_points)
        # Avoid zero division
        if max_val == min_val:
            max_val += 10.0
            min_val = max(0.0, min_val - 5.0)
        else:
            max_val = max_val * 1.15
            min_val = max(0.0, min_val * 0.85)

        val_range = max_val - min_val

        # Draw grid lines and Y-axis labels
        grid_steps = 4
        for i in range(grid_steps + 1):
            y_val = min_val + (val_range * i / grid_steps)
            y_pos = pad_top + chart_h - (chart_h * i / grid_steps)
            
            # Subtle grid line
            self.canvas.create_line(
                pad_left, y_pos, w - pad_right, y_pos,
                fill=COLORS["border_subtle"], dash=(2, 4)
            )
            # Y label
            self.canvas.create_text(
                pad_left - 8, y_pos,
                text=f"{y_val:.1f}", fill=COLORS["text_muted"],
                font=FONTS["caption"], anchor="e"
            )

        # Plot data points
        n = len(self.data_points)
        coords = []
        for idx, val in enumerate(self.data_points):
            x_pos = pad_left if n <= 1 else pad_left + (idx / (n - 1)) * chart_w
            y_pos = pad_top + chart_h - ((val - min_val) / val_range) * chart_h
            coords.append((x_pos, y_pos))

        # Connecting lines
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill=COLORS["primary"], width=2, smooth=True)

        # Draw average line
        avg_val = sum(self.data_points) / len(self.data_points)
        avg_y = pad_top + chart_h - ((avg_val - min_val) / val_range) * chart_h
        self.canvas.create_line(
            pad_left, avg_y, w - pad_right, avg_y,
            fill=COLORS["warning"], dash=(4, 3), width=1
        )
        self.canvas.create_text(
            w - pad_right, avg_y - 8,
            text=f"Avg: {avg_val:.1f}ms", fill=COLORS["warning"],
            font=FONTS["caption"], anchor="e"
        )

        # Draw points
        for idx, (x_pos, y_pos) in enumerate(coords):
            self.canvas.create_oval(
                x_pos - 3, y_pos - 3, x_pos + 3, y_pos + 3,
                fill=COLORS["secondary"], outline=COLORS["bg_main"], width=1
            )
            # Label first, last, and every few points
            if n <= 10 or idx in (0, n - 1):
                self.canvas.create_text(
                    x_pos, pad_top + chart_h + 12,
                    text=f"P{idx + 1}", fill=COLORS["text_muted"],
                    font=FONTS["caption"], anchor="n"
                )


class CanvasBarChart(tk.Frame):
    """Zero-dependency categorical Bar Chart rendered on a Tkinter Canvas."""

    def __init__(self, parent, title: str = "Packet Delivery Breakdown", height: int = 180, **kwargs):
        super().__init__(parent, bg=COLORS["bg_surface"], highlightthickness=1, highlightbackground=COLORS["border"], **kwargs)
        self.title_text = title

        # Title Header
        header = tk.Frame(self, bg=COLORS["bg_surface"], padx=8, pady=4)
        header.pack(fill=tk.X)
        self.title_lbl = tk.Label(
            header, text=title, font=FONTS["subtitle"],
            fg=COLORS["primary"], bg=COLORS["bg_surface"]
        )
        self.title_lbl.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(
            self, bg=COLORS["bg_surface_alt"], height=height,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        # Category mapping: label -> (count, color)
        self.categories: Dict[str, Tuple[int, str]] = {
            "Delivered": (0, COLORS["success"]),
            "Retransmitted": (0, COLORS["warning"]),
            "Corrupted": (0, COLORS["danger"]),
            "Lost": (0, "#b91c1c")
        }

    def update_counts(self, delivered: int, retransmitted: int, corrupted: int, lost: int):
        self.categories["Delivered"] = (delivered, COLORS["success"])
        self.categories["Retransmitted"] = (retransmitted, COLORS["warning"])
        self.categories["Corrupted"] = (corrupted, COLORS["danger"])
        self.categories["Lost"] = (lost, "#991b1b")
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        pad_top = 25
        pad_bottom = 35
        chart_h = h - pad_top - pad_bottom

        total = sum(c[0] for c in self.categories.values())
        max_count = max([c[0] for c in self.categories.values()] + [1])

        cat_names = list(self.categories.keys())
        num_cats = len(cat_names)
        col_width = (w - 40) / num_cats
        bar_width = min(col_width * 0.55, 45)

        for i, name in enumerate(cat_names):
            count, color = self.categories[name]
            x_center = 20 + (i + 0.5) * col_width
            
            # Bar height proportional to max_count
            bar_h = (count / max_count) * chart_h if max_count > 0 else 0
            y_bottom = pad_top + chart_h
            y_top = y_bottom - bar_h

            # Draw bar
            if bar_h > 0:
                self.canvas.create_rectangle(
                    x_center - bar_width / 2, y_top,
                    x_center + bar_width / 2, y_bottom,
                    fill=color, outline=COLORS["border"], width=1
                )

            # Value label on top of bar
            self.canvas.create_text(
                x_center, y_top - 8,
                text=str(count), fill=COLORS["text_primary"],
                font=FONTS["body_bold"]
            )

            # Category label below
            self.canvas.create_text(
                x_center, y_bottom + 10,
                text=name, fill=COLORS["text_secondary"],
                font=FONTS["caption"], anchor="n"
            )

        # Baseline axis line
        self.canvas.create_line(15, pad_top + chart_h, w - 15, pad_top + chart_h, fill=COLORS["border"], width=1)
