"""
UPE-78 v12.0 Degradation Controller

6-level cascade from NOMINAL to EMERGENCY.
Level 6 drops all neural/formal checks.
"""

from typing import Dict
from dataclasses import dataclass


@dataclass
class DegradationStatus:
    level: int
    name: str
    sea_enabled: bool
    fvp_enabled: bool
    ecpe_enabled: bool
    oci_only: bool
    cache_fallback: bool


class UPE78_DegradationController:
    """
    6-Level Degradation Controller
    """

    LEVELS = {
        1: "NOMINAL",
        2: "MONITORING",
        3: "REDUCED",
        4: "DEGRADED",
        5: "MINIMAL",
        6: "EMERGENCY"
    }

    def __init__(self):
        self.level = 1

    def set_level(self, level: int) -> DegradationStatus:
        self.level = max(1, min(6, level))
        return self.get_status()

    def get_status(self) -> DegradationStatus:
        name = self.LEVELS[self.level]
        return DegradationStatus(
            level=self.level,
            name=name,
            sea_enabled=self.level <= 3,
            fvp_enabled=self.level <= 4,
            ecpe_enabled=self.level <= 5,
            oci_only=self.level >= 6,
            cache_fallback=self.level >= 5
        )

    def should_run_full_pipeline(self) -> bool:
        return self.level <= 3
