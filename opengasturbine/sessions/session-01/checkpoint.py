"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e = L.ideal_efficiency(10)
    checks.append((f"worked example: ideal efficiency at r = 10 is 0.482 (got {e:.3f})", abs(e - 0.4821) < 1e-3))
    w, q_out = L.energy_balance(600, 10)
    checks.append((f"worked example: net work 289 kJ/kg (got {w:.0f})", abs(w - 289.2) < 0.2))
    checks.append((f"worked example: heat out 311 kJ/kg (got {q_out:.0f})", abs(q_out - 310.8) < 0.2))
    checks.append(("energy balance: w_net + q_out = q_in for several r and q_in",
                   all(abs(sum(L.energy_balance(q, r)) - q) < 1e-9 for r in (1, 2, 10, 30) for q in (100, 600, 1000))))
    checks.append(("more pressure ratio means more efficiency", L.ideal_efficiency(5) < L.ideal_efficiency(10) < L.ideal_efficiency(20)))
    checks.append(("diminishing returns: doubling r from 10 to 20 gains less than from 2 to 4",
                   L.ideal_efficiency(20) - L.ideal_efficiency(10) < L.ideal_efficiency(4) - L.ideal_efficiency(2)))
    checks.append(("efficiency is always between 0 and 1", all(0 <= L.ideal_efficiency(r) < 1 for r in (1, 1.5, 10, 100, 1e6))))
    checks.append(("edge case: r = 1 gives efficiency exactly 0", L.ideal_efficiency(1) == 0))
    try:
        L.ideal_efficiency(0.5)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge case: r below 1 gives an error", raised))
    checks.append(("design: r = 17 reaches 55 percent, r = 16 does not",
                   L.ideal_efficiency(17) >= 0.55 > L.ideal_efficiency(16)))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
