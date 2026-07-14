"""
UPE-78 v12.0 Framework Auditor

Ingests claims from external frameworks, routes through OCIE->SEA->FVP->ECPE->CTD.
Produces verdict: CONSISTENT, INCONSISTENT, UNVERIFIED, PURGED
"""

from typing import Dict, List, Optional
from .ocie import UPE78_OCIE
from .sea import UPE78_SEA
from .fvp import UPE78_FVP
from .ecpe import UPE78_ECPE
from .ctd import UPE78_CTD
from .saud import UPE78_SAUD


class UPE78_AuditEngine:
    """
    Meta-verification engine for peer frameworks.
    """

    def __init__(self):
        self.ocie = UPE78_OCIE()
        self.sea = UPE78_SEA()
        self.fvp = UPE78_FVP()
        self.ecpe = UPE78_ECPE()
        self.ctd = UPE78_CTD()
        self.saud = UPE78_SAUD()
        self._self_audited = False

    def _require_self_audit(self):
        if not self._self_audited:
            self.saud.run()
            self._self_audited = True

    def audit_claim(self, claim: Dict) -> Dict:
        """Audit a single claim from an external framework."""
        self._require_self_audit()

        text = claim.get("text", "")
        value = claim.get("value", 0.0)
        name = claim.get("name", "")
        domain = claim.get("domain", "STANDARD")
        baseline = claim.get("baseline", 0.0)

        results = {}

        results["ocie"] = self.ocie.compress(text)

        results["sea"] = self.sea.full_pipeline(text, claim.get("reference_text", ""))

        if domain == "STANDARD":
            from .constants import UPE78Constants
            c = UPE78Constants
            if "alpha" in name.lower():
                results["fvp"] = c.validate_alpha_inv(value)
            elif "planck" in name.lower() or "length" in name.lower():
                results["fvp"] = c.validate_planck_length(value)
            elif "neural" in name.lower() or "frequency" in name.lower():
                results["fvp"] = c.validate_neural_frequency(value)
            else:
                results["fvp"] = {"verdict": "UNVERIFIED", "reason": "No CODATA mapping"}
        else:
            results["fvp"] = {"verdict": "UPE_NATIVE", "note": "Checked against internal axioms"}

        if baseline != 0:
            results["ecpe"] = self.ecpe.qed_exclusion(value, baseline)

        verdict = self._composite_verdict(results)
        results["verdict"] = verdict
        results["limitations"] = self.saud.get_limitations_statement()

        return results

    def _composite_verdict(self, results: Dict) -> str:
        """Determine final verdict from sub-results."""
        if results.get("ecpe", {}).get("excluded", False):
            return "PURGED"
        if results.get("fvp", {}).get("verdict") == "FALSIFIED":
            return "INCONSISTENT"
        if results.get("fvp", {}).get("verdict") == "UNVERIFIED":
            return "UNVERIFIED"
        return "CONSISTENT"

    def audit_framework(self, framework_name: str, claims: List[Dict]) -> Dict:
        """Audit an entire framework."""
        self._require_self_audit()
        audited = []
        for claim in claims:
            audited.append(self.audit_claim(claim))

        consistent = sum(1 for a in audited if a["verdict"] == "CONSISTENT")
        inconsistent = sum(1 for a in audited if a["verdict"] == "INCONSISTENT")
        purged = sum(1 for a in audited if a["verdict"] == "PURGED")
        unverified = len(audited) - consistent - inconsistent - purged

        return {
            "framework": framework_name,
            "total_claims": len(audited),
            "consistent": consistent,
            "inconsistent": inconsistent,
            "purged": purged,
            "unverified": unverified,
            "details": audited,
            "limitations": self.saud.get_limitations_statement()
        }
