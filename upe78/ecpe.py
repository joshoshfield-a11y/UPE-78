"""
UPE-78 v12.0 ECPE: Evidence-Confidence Propagation Engine

HONEST STATUS:
- Real sklearn LogisticRegression for Platt scaling
- ECE computed with bootstrap CI, NOT asserted as 0.000255
- Previous ECE = 0.000255 claim REMOVED (was target value, never measured)
- QED exclusion at 1e12 orders is a hard threshold, not a derived probability

REQUIRES: pip install scikit-learn numpy
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import math


class UPE78_ECPE:
    """
    Evidence-Confidence Propagation Engine v12.0

    - Bayesian factor graph (simplified product-of-odds)
    - Platt scaling with real sklearn calibration
    - QED exclusion at 10^12 orders deviation
    """

    def __init__(self):
        self.calibration_model = None
        self.qed_threshold = 12.0  # log10 orders
        self.ece_measured = None
        self.ece_ci = None

    def platt_scale(self, raw_scores: np.ndarray, labels: np.ndarray) -> Dict:
        """Real Platt scaling using sklearn LogisticRegression."""
        try:
            from sklearn.linear_model import LogisticRegression
            self.calibration_model = LogisticRegression(max_iter=1000)
            scores_reshaped = raw_scores.reshape(-1, 1)
            self.calibration_model.fit(scores_reshaped, labels)
            calibrated = self.calibration_model.predict_proba(scores_reshaped)[:, 1]
            ece = self._calculate_ece(calibrated, labels)
            ci = self._bootstrap_ece(calibrated, labels)
            self.ece_measured = ece
            self.ece_ci = ci
            return {
                "calibrated_scores": calibrated,
                "ece": ece,
                "ece_ci_95": ci,
                "valid": True,
                "measured": True,
                "asserted": False
            }
        except ImportError:
            calibrated = 1.0 / (1.0 + np.exp(-raw_scores))
            return {
                "calibrated_scores": calibrated,
                "ece": None,
                "valid": False,
                "reason": "sklearn not installed",
                "measured": False
            }

    def _calculate_ece(self, probs: np.ndarray, labels: np.ndarray,
                       n_bins: int = 10) -> float:
        """Calculate Expected Calibration Error."""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        for i in range(n_bins):
            if i == n_bins - 1:
                mask = (probs >= bin_boundaries[i]) & (probs <= bin_boundaries[i + 1])
            else:
                mask = (probs >= bin_boundaries[i]) & (probs < bin_boundaries[i + 1])
            if np.sum(mask) > 0:
                avg_conf = np.mean(probs[mask])
                avg_acc = np.mean(labels[mask])
                ece += (np.sum(mask) / len(labels)) * abs(avg_conf - avg_acc)
        return ece

    def _bootstrap_ece(self, probs: np.ndarray, labels: np.ndarray,
                       n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Bootstrap 95% CI for ECE."""
        n = len(probs)
        eces = []
        for _ in range(n_bootstrap):
            idx = np.random.choice(n, n, replace=True)
            eces.append(self._calculate_ece(probs[idx], labels[idx]))
        return (float(np.percentile(eces, 2.5)), float(np.percentile(eces, 97.5)))

    def qed_exclusion(self, claim_value: float, baseline: float) -> Dict:
        """QED Exclusion Logic."""
        if baseline == 0:
            return {"excluded": False, "reason": "Zero baseline"}
        ratio = abs(claim_value / baseline)
        orders = math.log10(ratio) if ratio > 0 else 0
        excluded = orders > self.qed_threshold
        return {
            "excluded": excluded,
            "orders_deviation": orders,
            "threshold": self.qed_threshold,
            "action": "PURGE" if excluded else "RETAIN"
        }

    def propagate(self, claim_id: str, evidence_scores: List[float],
                  prior: float = 0.5) -> Dict:
        """Bayesian belief propagation via product of odds."""
        posterior = prior
        for score in evidence_scores:
            if score <= 0 or score >= 1:
                continue
            lr = score / (1.0 - score)
            posterior = (posterior * lr) / (posterior * lr + (1.0 - posterior))
        return {
            "claim_id": claim_id,
            "prior": prior,
            "posterior": posterior,
            "evidence_count": len(evidence_scores),
            "confidence": posterior
        }
