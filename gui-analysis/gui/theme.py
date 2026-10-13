"""UI Theme, styling constants, and color palettes for Hospital Network Dashboard."""

# Professional Medical Tech Dark/Modern Palette
COLORS = {
    "bg_main": "#0b132b",          # Deep navy background
    "bg_surface": "#1c2541",       # Surface/Card container background
    "bg_surface_alt": "#162038",   # Alternate card background
    "bg_entry": "#243254",         # Text input & table row highlight
    "border": "#3a506b",           # Container borders
    "border_subtle": "#253552",    # Subtle dividers
    
    "primary": "#00b4d8",          # Cyan / Medical blue accent
    "primary_hover": "#48cae4",    # Lighter cyan hover
    "secondary": "#6fffe9",        # Bright teal highlights
    
    "success": "#10b981",          # Emerald / Healthy vitals / Delivered
    "warning": "#f59e0b",          # Amber / High latency / Retransmission
    "danger": "#ef4444",           # Coral / Packet loss / CRC Error
    "info": "#3b82f6",             # Information blue
    
    "text_primary": "#f8fafc",     # High contrast bright white
    "text_secondary": "#cbd5e1",   # Light slate
    "text_muted": "#94a3b8",       # Muted gray-slate
    "text_dark": "#0f172a",        # Dark text for bright badges
}

FONTS = {
    "title": ("Segoe UI", 16, "bold"),
    "subtitle": ("Segoe UI", 11, "bold"),
    "section_header": ("Segoe UI", 12, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "caption": ("Segoe UI", 9),
    "code": ("Consolas", 10),
    "code_bold": ("Consolas", 10, "bold"),
    "stat_value": ("Segoe UI", 20, "bold"),
    "stat_label": ("Segoe UI", 9, "bold")
}
