"""
UPE-78 v12.0 CTD: Coherence Threshold Detector

HONEST STATUS:
- Detects sharp slope increases in PSI x PI x EEI under parameter sweep
- Operationally defined, not metaphysical
- Threshold values are tunable parameters, not universal constants
"""

from typing import Dict, List, Optional
import numpy as np


class UPE78_CTD:
    """
    Coherence Threshold Detector v12.0

    Input:  PSI (Phase Stability Index), PI (Persistence Index),
            EEI (Energy Efficiency Index)
    Output: Coherence Score, transition flag
    """

    def __init__(self, psi_threshold: float = 0.6,
                 pi_threshold: float = 0.5,
                 eei_threshold: float = 0.5,
                 slope_threshold: float = 2.0):
        self.psi_threshold = psi_threshold
        self.pi_threshold = pi_threshold
        self.eei_threshold = eei_threshold
        self.slope_threshold = slope_threshold

    def compute_coherence(self, psi: float, pi: float, eei: float) -> Dict:
        """Compute coherence score from triad."""
        noise = 1e-10
        score = (psi * pi * eei) / (psi + pi + eei + noise)
        return {
            "coherence_score": score,
            "psi": psi,
            "pi": pi,
            "eei": eei,
            "components": {"psi": psi, "pi": pi, "eei": eei}
        }

    def detect_transition(self, param_values: List[float],
                          psi_series: List[float],
                          pi_series: List[float],
                          eei_series: List[float]) -> Dict:
        """Detect phase transition by sharp slope increase."""
        if len(param_values) < 3:
            return {"transition_detected": False, "reason": "Insufficient data"}

        coherence_series = [self.compute_coherence(p, i, e)["coherence_score"]
                            for p, i, e in zip(psi_series, pi_series, eei_series)]

        slopes = []
        for i in range(1, len(coherence_series)):
            dx = param_values[i] - param_values[i - 1]
            if abs(dx) < 1e-12:
                slopes.append(0.0)
            else:
                slopes.append((coherence_series[i] - coherence_series[i - 1]) / dx)

        max_slope_idx = np.argmax(np.abs(slopes))
        max_slope = slopes[max_slope_idx]

        transition_detected = abs(max_slope) > self.slope_threshold

        return {
            "transition_detected": transition_detected,
            "max_slope": max_slope,
            "slope_threshold": self.slope_threshold,
            "transition_index": max_slope_idx + 1,
            "param_at_transition": param_values[max_slope_idx + 1] if transition_detected else None,
            "coherence_series": coherence_series,
            "slopes": slopes
        }
