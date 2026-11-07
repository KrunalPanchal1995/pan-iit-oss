"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("0.1 mol/L HCl has pH 1", abs(L.ph_strong_acid(0.1) - 1.0) < 1e-9))
    checks.append(("each step of 1 in pH is a factor 10 in [H+]", abs(L.ph_from_h(1e-3) - L.ph_from_h(1e-2) - 1.0) < 1e-9))
    checks.append(("0.001 mol/L NaOH has pH 11", abs(L.ph_strong_base(1e-3) - 11.0) < 1e-9))
    checks.append(("pure water (1e-7 mol/L) is neutral", L.kind(L.ph_from_h(1e-7)) == "neutral"))
    checks.append(("the flask starts at pH 1 (0 mL base)", abs(L.strong_ph(0.1, 25.0, 0.1, 0.0) - 1.0) < 1e-6))
    ve = L.equivalence_volume(0.1, 25.0, 0.1)
    checks.append((f"worked example: 25 mL of 0.1 M HCl needs {ve:.1f} mL of 0.1 M NaOH, and the pH there is 7",
                   abs(ve - 25.0) < 1e-12 and abs(L.strong_ph(0.1, 25.0, 0.1, ve) - 7.0) < 1e-6))
    # hand calculation: 10 mL base -> acid left 1.5 mmol in 35 mL -> [H+] = 0.04286 -> pH 1.368
    checks.append(("hand calculation: after 10 mL base pH = -log10(1.5/35) = 1.368",
                   abs(L.strong_ph(0.1, 25.0, 0.1, 10.0) - (-np.log10(1.5 / 35.0))) < 1e-9))
    checks.append(("30 mL of base: pH is above 11", L.strong_ph(0.1, 25.0, 0.1, 30.0) > 11.0))
    vb, ph = L.titration_curve(0.1, 25.0, 0.1, 50.0)
    checks.append(("adding base never lowers the pH", bool(np.all(np.diff(ph) >= -1e-12))))
    checks.append(("the steepest part is at the equivalence volume", abs(vb[np.argmax(np.diff(ph))] - 25.0) < 0.2))
    checks.append(("a 0.2 M base needs only half the volume", abs(L.equivalence_volume(0.1, 25.0, 0.2) - 12.5) < 1e-12))
    checks.append(("finite at the exact boundary and far past it",
                   bool(np.isfinite(L.strong_ph(0.1, 25.0, 0.1, 25.0)) and np.isfinite(L.strong_ph(0.1, 25.0, 0.5, 200.0)))))
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
