"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("pH + pOH = 14 for pH 3.7", abs(L.poh_from_ph(3.7) + 3.7 - 14.0) < 1e-12))
    checks.append(("pOH of 1e-3 mol/L OH- is 3, so pH is 11", abs(L.poh_of_oh(1e-3) - 3.0) < 1e-12 and abs(L.poh_from_ph(3.0) - 11.0) < 1e-12))
    checks.append(("0.1 M HCl titrated with 0.1 M NaOH: pH 1 at the start", abs(L.strong_ph(0.1, 25.0, 0.1, 0.0) - 1.0) < 1e-6))
    ve = L.equivalence_volume(0.1, 25.0, 0.1)
    checks.append(("pH is 7 at the equivalence volume", abs(L.strong_ph(0.1, 25.0, 0.1, ve) - 7.0) < 1e-6))
    checks.append(("pH is high (above 11) well after equivalence", L.strong_ph(0.1, 25.0, 0.1, 30.0) > 11.0))
    # worked example: 25.00 mL of unknown HCl needs 20.00 mL of 0.1000 M NaOH
    c = L.unknown_concentration(0.1, 20.0, 25.0)
    checks.append((f"worked example: 20.00 mL of 0.1000 M NaOH for 25.00 mL of acid gives {c:.4f} mol/L and pH {-np.log10(c):.3f}",
                   abs(c - 0.08) < 1e-12 and abs(-np.log10(c) - 1.097) < 1e-3))
    # hand calculation: 0.1 mL before equivalence, leftover 0.01 mmol in 49.9 mL
    checks.append(("hand calculation: 24.9 mL gives pH = -log10(0.01/49.9) = 3.698",
                   abs(L.strong_ph(0.1, 25.0, 0.1, 24.9) - (-np.log10(0.01 / 49.9))) < 1e-5))
    checks.append(("hand calculation: 25.1 mL gives pH = 14 + log10(0.01/50.1) = 10.300",
                   abs(L.strong_ph(0.1, 25.0, 0.1, 25.1) - (14 + np.log10(0.01 / 50.1))) < 1e-5))
    checks.append(("inverse function: volume_at_ph undoes strong_ph",
                   all(abs(L.volume_at_ph(L.strong_ph(0.1, 25.0, 0.1, v), 0.1, 25.0, 0.1) - v) < 1e-6 for v in (5.0, 20.0, 24.9, 25.1, 30.0))))
    checks.append(("both dyes work for 0.1 M (error under 2 percent)", L.suitable("methyl orange", 0.1, 25.0, 0.1) and L.suitable("phenolphthalein", 0.1, 25.0, 0.1)))
    checks.append(("for 0.001 M neither dye is good enough", not L.suitable("methyl orange", 0.001, 25.0, 0.001) and not L.suitable("phenolphthalein", 0.001, 25.0, 0.001)))
    checks.append(("phenolphthalein tolerates a more dilute solution than methyl orange here",
                   L.lowest_concentration("phenolphthalein") < L.lowest_concentration("methyl orange")))
    checks.append(("dilution C1 V1 = C2 V2: 10 mL of 1.0 M to 0.1 M needs 100 mL", abs(L.final_volume(1.0, 10.0, 0.1) - 100.0) < 1e-12))
    checks.append(("finite at the exact boundary (Vb = Ve) and for a huge excess", bool(np.isfinite(L.strong_ph(0.3, 10.0, 0.3, 10.0)) and np.isfinite(L.strong_ph(0.1, 25.0, 0.5, 500.0)))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson2", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
