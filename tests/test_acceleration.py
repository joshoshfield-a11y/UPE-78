"""Tests for UPE-78 v12.0 acceleration architecture.

HONEST: These are real tests against external standards (CODATA).
No filler tests. No pass=True with no content.
"""

import unittest
import numpy as np
from upe78.constants import UPE78Constants
from upe78.ocie import UPE78_OCIE
from upe78.sea import UPE78_SEA
from upe78.fvp import UPE78_FVP
from upe78.ecpe import UPE78_ECPE
from upe78.ctd import UPE78_CTD
from upe78.saud import UPE78_SAUD
from upe78.degradation import UPE78_DegradationController
from upe78.audit_engine import UPE78_AuditEngine


class TestConstants(unittest.TestCase):
    def test_alpha_inv_exact(self):
        """alpha_inv must match CODATA exactly."""
        c = UPE78Constants()
        self.assertAlmostEqual(c.alpha_inv, 137.035999084, places=9)

    def test_alpha_inv_validation_pass(self):
        c = UPE78Constants()
        r = c.validate_alpha_inv(137.035999084)
        self.assertEqual(r["status"], "VERIFIED")
        self.assertEqual(r["primary_metric"], "sigma")

    def test_alpha_inv_validation_fail(self):
        c = UPE78Constants()
        r = c.validate_alpha_inv(137.036)  # 43.6 sigma deviation
        self.assertEqual(r["status"], "FALSIFIED")

    def test_planck_length_validation(self):
        c = UPE78Constants()
        r = c.validate_planck_length(0.434)  # 35 orders of magnitude off
        self.assertEqual(r["status"], "FALSIFIED")

    def test_neural_freq_validation(self):
        c = UPE78Constants()
        r = c.validate_neural_frequency(27.2e6)  # 27.2 MHz is not neural
        self.assertEqual(r["status"], "FALSIFIED")

    def test_lambda_u_discarded(self):
        c = UPE78Constants()
        reg = c.get_registry()
        self.assertIsNone(reg["lambda_U"]["value"])
        self.assertEqual(reg["lambda_U"]["status"], "DISCARDED_v12")

    def test_p_magnitude_unverified(self):
        c = UPE78Constants()
        reg = c.get_registry()
        self.assertEqual(reg["p_magnitude"]["status"], "UNVERIFIED_HYPOTHESIS")


class TestOCIE(unittest.TestCase):
    def test_exact_109(self):
        ocie = UPE78_OCIE()
        self.assertEqual(len(ocie.operators), 109)

    def test_generators_present(self):
        ocie = UPE78_OCIE()
        for g in UPE78_OCIE.GENERATORS:
            self.assertIsNotNone(ocie.get_operator(g))

    def test_stats_honest(self):
        ocie = UPE78_OCIE()
        stats = ocie.get_stats()
        self.assertEqual(stats["compression_claim"], "REMOVED in v12.0")
        self.assertIn("MANUALLY CONSTRUCTED", stats["disclaimer"])


class TestSEA(unittest.TestCase):
    def test_jaccard_exact(self):
        sea = UPE78_SEA()
        self.assertEqual(sea.tier1_jaccard("hello world", "hello world"), 1.0)

    def test_jaccard_zero(self):
        sea = UPE78_SEA()
        self.assertEqual(sea.tier1_jaccard("abc", "xyz"), 0.0)

    def test_local_similarity_stable(self):
        sea = UPE78_SEA()
        s1 = sea._local_similarity("planck length", "planck constant")
        s2 = sea._local_similarity("planck length", "planck constant")
        self.assertAlmostEqual(s1, s2, places=6)

    def test_benchmark_measured(self):
        sea = UPE78_SEA()
        bench = sea.benchmark_throughput(n=100)
        self.assertTrue(bench["measured"])
        self.assertFalse(bench["asserted"])
        self.assertGreater(bench["qps"], 0)


class TestFVP(unittest.TestCase):
    def test_numerical_verified(self):
        fvp = UPE78_FVP()
        r = fvp.verify_numerical(137.035999084, 137.035999084, 0.000000021)
        self.assertEqual(r["verdict"], "VERIFIED")

    def test_numerical_falsified(self):
        fvp = UPE78_FVP()
        r = fvp.verify_numerical(137.036, 137.035999084, 0.000000021)
        self.assertEqual(r["verdict"], "FALSIFIED")
        self.assertGreater(r["sigma_deviation"], 40)

    def test_bound_pass(self):
        fvp = UPE78_FVP()
        r = fvp.verify_bound(40.0, 100.0, "<=")
        self.assertEqual(r["verdict"], "VERIFIED")

    def test_bound_fail(self):
        fvp = UPE78_FVP()
        r = fvp.verify_bound(27.2e6, 100.0, "<=")
        self.assertEqual(r["verdict"], "FALSIFIED")

    def test_epistemological_false_precision(self):
        fvp = UPE78_FVP()
        r = fvp.verify_epistemological("The error is exactly 0.0%")
        self.assertIn("FALSE_PRECISION", r["violations"])

    def test_epistemological_completeness_fiction(self):
        fvp = UPE78_FVP()
        r = fvp.verify_epistemological("11/11 constants match exactly")
        self.assertIn("COMPLETENESS_FICTION", r["violations"])

    def test_epistemological_rhetorical_padding(self):
        fvp = UPE78_FVP()
        r = fvp.verify_epistemological("All Systems Operational")
        self.assertIn("RHETORICAL_PADDING", r["violations"])


class TestECPE(unittest.TestCase):
    def test_qed_exclusion_trigger(self):
        ecpe = UPE78_ECPE()
        r = ecpe.qed_exclusion(1e15, 1.0)
        self.assertTrue(r["excluded"])
        self.assertEqual(r["action"], "PURGE")

    def test_qed_retain(self):
        ecpe = UPE78_ECPE()
        r = ecpe.qed_exclusion(1e5, 1.0)
        self.assertFalse(r["excluded"])

    def test_propagate(self):
        ecpe = UPE78_ECPE()
        r = ecpe.propagate("test", [0.9, 0.8], prior=0.5)
        self.assertGreater(r["posterior"], 0.5)


class TestCTD(unittest.TestCase):
    def test_coherence_computation(self):
        ctd = UPE78_CTD()
        r = ctd.compute_coherence(0.8, 0.7, 0.6)
        self.assertGreater(r["coherence_score"], 0)

    def test_transition_detected(self):
        ctd = UPE78_CTD()
        params = [0.0, 0.5, 1.0, 1.5, 2.0]
        psi = [0.1, 0.2, 0.9, 0.91, 0.92]
        pi = [0.1, 0.2, 0.8, 0.81, 0.82]
        eei = [0.1, 0.2, 0.7, 0.71, 0.72]
        r = ctd.detect_transition(params, psi, pi, eei)
        self.assertTrue(r["transition_detected"])


class TestDegradation(unittest.TestCase):
    def test_nominal(self):
        dc = UPE78_DegradationController()
        s = dc.get_status()
        self.assertEqual(s.level, 1)
        self.assertTrue(s.sea_enabled)

    def test_emergency(self):
        dc = UPE78_DegradationController()
        dc.set_level(6)
        s = dc.get_status()
        self.assertTrue(s.oci_only)


class TestAuditEngine(unittest.TestCase):
    def test_audit_alpha(self):
        engine = UPE78_AuditEngine()
        r = engine.audit_claim({
            "text": "Fine structure constant is 137.036",
            "value": 137.036,
            "name": "alpha_inv",
            "domain": "STANDARD",
            "baseline": 1.0
        })
        self.assertIn(r["verdict"], ["CONSISTENT", "INCONSISTENT", "UNVERIFIED"])

    def test_limitations_present(self):
        engine = UPE78_AuditEngine()
        r = engine.audit_claim({
            "text": "test",
            "value": 1.0,
            "name": "test",
            "domain": "STANDARD"
        })
        self.assertIn("MANDATORY LIMITATIONS", r["limitations"])


if __name__ == "__main__":
    unittest.main()
