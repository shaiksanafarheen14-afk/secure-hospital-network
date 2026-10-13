"""Base adapter definition for teammate protocol integration.

Defines status tracking (Local reference vs Teammate integrated) and auto-discovery
to facilitate seamless pairing as other teammates merge their work.
"""

from enum import Enum
import importlib
import sys
from pathlib import Path
from typing import Optional, Any, Tuple


class AdapterStatus(str, Enum):
    LOCAL_REFERENCE = "Local Reference (Active)"
    TEAMMATE_INTEGRATED = "Teammate Module Integrated"
    PENDING_EXTERNAL = "Pending Teammate Code"


class BaseProtocolAdapter:
    """Base class for all protocol adapters."""

    def __init__(self, protocol_name: str, candidate_modules: list[str]):
        self.protocol_name = protocol_name
        self.candidate_modules = candidate_modules
        self.status = AdapterStatus.LOCAL_REFERENCE
        self.source_module_name: Optional[str] = None
        self.external_instance: Optional[Any] = None

        self._attempt_teammate_discovery()

    def _attempt_teammate_discovery(self):
        """Check if teammate's module exists in sys.path or parent directories."""
        # Ensure project root is in sys.path
        root_path = Path(__file__).resolve().parent.parent.parent
        if str(root_path) not in sys.path:
            sys.path.insert(0, str(root_path))

        for mod_name in self.candidate_modules:
            try:
                mod = importlib.import_module(mod_name)
                self.external_instance = mod
                self.source_module_name = mod_name
                self.status = AdapterStatus.TEAMMATE_INTEGRATED
                return
            except (ImportError, AttributeError):
                continue

        # If not found, stay on local reference implementation
        self.status = AdapterStatus.LOCAL_REFERENCE
        self.source_module_name = "gui-analysis.modules.internal"

    def get_status_info(self) -> Tuple[str, str]:
        """Returns tuple of (Status label, Source description)."""
        return (self.status.value, self.source_module_name or "Internal Reference Implementation")
