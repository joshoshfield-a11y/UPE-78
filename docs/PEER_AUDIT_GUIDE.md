# UPE-78 Peer Audit Guide

## Mandatory First Step

Run SAUD before ANY peer audit:

```python
from upe78 import UPE78_SAUD
saud = UPE78_SAUD()
report = saud.run()
print(report["limitations"])
```

This is **not optional**. The audit engine will refuse to run without it.

## Auditing a Peer Framework

```python
from upe78 import UPE78_AuditEngine

engine = UPE78_AuditEngine()

claims = [
    {
        "text": "H0 = 67.4 km/s/Mpc",
        "value": 67.4,
        "name": "hubble_constant",
        "domain": "STANDARD",
        "baseline": 1.0
    },
    {
        "text": "Shear modulus of space is 4.62e34 Pa",
        "value": 4.62e34,
        "name": "shear_modulus_space",
        "domain": "STANDARD",
        "baseline": 1.0
    }
]

result = engine.audit_framework("Peer Framework", claims)
print(result["consistent"], result["inconsistent"], result["purged"])
```

## Verdicts

| Verdict | Meaning |
|---------|---------|
| CONSISTENT | Passes FVP checks against CODATA or UPE_NATIVE axioms |
| INCONSISTENT | Falsified by FVP (sigma-deviation > 5 or bound violation) |
| UNVERIFIED | No CODATA mapping available |
| PURGED | QED exclusion triggered (>10^12 orders deviation) |

## Auto-Appended Limitations

Every audit output includes the UPE-78 v12.0 limitations statement. This cannot be bypassed or edited. It discloses:
- Unverified operators (55%)
- Unmeasured SEA benchmarks
- Synthetic ECPE calibration
- Discarded constants
- Development-stage status
