"""
UPE-78 v12.0 Constant Registry

Honest physical constant registry with CODATA grounding.
All values traceable to empirical measurement.

STATUS: Development stage. Not validated for production.
"""

from typing import Dict, Tuple, Optional
import math


class UPE78Constants:
    """
    Physical constant registry with explicit uncertainty tracking.

    v12.0 CHANGES:
    - lambda_U and f_Omega DISCARDED (inherited from falsified v10.1 claims)
    - alpha_inv fixed to full CODATA 137.035999084(21)
    - Sigma-deviation is PRIMARY metric for all numerical claims
    - p_magnitude relabeled as UNVERIFIED_HYPOTHESIS
    """

    # CODATA 2018 / PDG 2024 values
    alpha_inv: float = 137.035999084
    alpha_inv_unc: float = 0.000000021

    c: float = 299792458.0  # m/s (exact by SI definition, derived from measurement)
    hbar: float = 1.054571817e-34  # J*s
    hbar_unc: float = 0.000000027e-34

    G: float = 6.67430e-11  # m^3 kg^-1 s^-2
    G_unc: float = 0.00015e-11

    planck_length: float = 1.616255e-35  # m
    planck_length_unc: float = 0.000018e-35

    electron_mass: float = 9.1093837015e-31  # kg
    electron_mass_unc: float = 0.0000000028e-31

    proton_mass: float = 1.67262192369e-27  # kg
    proton_mass_unc: float = 0.00000000051e-27

    # Neural frequency ranges (empirical)
    neural_freq_low: float = 0.5  # Hz (delta)
    neural_freq_high: float = 100.0  # Hz (gamma upper bound)

    # RF/Microwave ranges (for EM coupling claims)
    rf_freq_low: float = 1e3  # Hz
    rf_freq_high: float = 3e11  # Hz

    # UPE-NATIVE phenomenological quantities (NOT standard physics corrections)
    # These have NO empirical meaning outside UPE-78 formalism
    lambda_U: Optional[float] = None  # DISCARDED in v12.0 - no physical basis
    f_Omega: Optional[float] = None   # DISCARDED in v12.0 - no physical basis

    # p_magnitude: trivial algebraic identity, NOT a physical constant
    p_magnitude_status: str = "UNVERIFIED_HYPOTHESIS"

    # Base-13 combinatorial facts (mathematical, not physical)
    C_13_2: int = math.comb(13, 2)  # 78
    C_20_2: int = math.comb(20, 2)  # 190

    @classmethod
    def validate_alpha_inv(cls, claimed: float) -> Dict:
        """Validate fine-structure constant against CODATA.

        PRIMARY metric: sigma-deviation (no relative-error sleight-of-hand).
        """
        diff = abs(claimed - cls.alpha_inv)
        sigma = diff / cls.alpha_inv_unc
        relative = diff / cls.alpha_inv

        return {
            'claimed': claimed,
            'codata': cls.alpha_inv,
            'sigma_deviation': sigma,
            'relative_error': relative,
            'valid': sigma < 5.0,  # 5-sigma threshold
            'primary_metric': 'sigma',
            'status': 'VERIFIED' if sigma < 5.0 else 'FALSIFIED'
        }

    @classmethod
    def validate_planck_length(cls, claimed: float) -> Dict:
        """Validate Planck length against CODATA."""
        diff = abs(claimed - cls.planck_length)
        sigma = diff / cls.planck_length_unc if cls.planck_length_unc > 0 else float('inf')
        relative = diff / cls.planck_length

        return {
            'claimed': claimed,
            'codata': cls.planck_length,
            'sigma_deviation': sigma,
            'relative_error': relative,
            'valid': sigma < 5.0,
            'status': 'VERIFIED' if sigma < 5.0 else 'FALSIFIED'
        }

    @classmethod
    def validate_neural_frequency(cls, claimed: float) -> Dict:
        """Validate claimed neural frequency against empirical bounds."""
        in_range = cls.neural_freq_low <= claimed <= cls.neural_freq_high
        return {
            'claimed': claimed,
            'bounds': (cls.neural_freq_low, cls.neural_freq_high),
            'valid': in_range,
            'status': 'VERIFIED' if in_range else 'FALSIFIED',
            'note': '27.2MHz is NOT a neural frequency; it is EM/RF coupling. Use f_Omega label.'
        }

    @classmethod
    def get_registry(cls) -> Dict:
        """Return full registry with status annotations."""
        return {
            'alpha_inv': {'value': cls.alpha_inv, 'unc': cls.alpha_inv_unc, 'source': 'CODATA 2018'},
            'c': {'value': cls.c, 'unc': 0.0, 'source': 'SI definition (derived from measurement)'},
            'hbar': {'value': cls.hbar, 'unc': cls.hbar_unc, 'source': 'CODATA 2018'},
            'G': {'value': cls.G, 'unc': cls.G_unc, 'source': 'CODATA 2018'},
            'planck_length': {'value': cls.planck_length, 'unc': cls.planck_length_unc, 'source': 'CODATA 2018'},
            'electron_mass': {'value': cls.electron_mass, 'unc': cls.electron_mass_unc, 'source': 'PDG 2024'},
            'proton_mass': {'value': cls.proton_mass, 'unc': cls.proton_mass_unc, 'source': 'PDG 2024'},
            'lambda_U': {'value': None, 'status': 'DISCARDED_v12', 'reason': 'Inherited from falsified v10.1 claim'},
            'f_Omega': {'value': None, 'status': 'DISCARDED_v12', 'reason': 'Inherited from falsified v10.1 claim'},
            'p_magnitude': {'value': 0.4341926086, 'status': 'UNVERIFIED_HYPOTHESIS', 'reason': 'Trivial algebraic identity, no external standard'},
        }
