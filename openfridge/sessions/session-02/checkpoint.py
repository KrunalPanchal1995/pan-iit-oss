"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.cop_carnot(4, 25)
    checks.append((f"worked example: Carnot COP between 4 C and 25 C is 277.15/21 = 13.20 (got {c:.2f})", abs(c - 277.15 / 21) < 1e-9))
    cr = L.cop_real(4, 25, 0.25)
    checks.append((f"worked example: real COP with eta2 = 0.25 is 3.30 (got {cr:.2f})", abs(cr - 3.2994) < 1e-3))
    w = L.electric_power(60, 4, 25, 0.25)
    checks.append((f"worked example: leak 60 W needs W = 18.2 W (got {w:.1f})", abs(w - 18.18) < 0.01))
    qh = L.room_heating(60, 4, 25, 0.25)
    checks.append(("energy balance: Q_hot = Q_cold + W", abs(qh - (60 + w)) < 1e-12))
    checks.append(("Q_hot is 78.2 W in the worked example", abs(qh - 78.19) < 0.01))
    checks.append(("kelvin(0) = 273.15 and kelvin(-273.15) = 0", abs(L.kelvin(0) - 273.15) < 1e-12 and abs(L.kelvin(-273.15)) < 1e-12))
    checks.append(("hotter room means a lower COP", L.cop_carnot(4, 35) < L.cop_carnot(4, 25) < L.cop_carnot(4, 15)))
    checks.append(("colder inside means a lower COP", L.cop_carnot(-18, 25) < L.cop_carnot(4, 25)))
    checks.append(("real COP never exceeds Carnot", all(L.cop_real(4, t, e) <= L.cop_carnot(4, t) + 1e-12 for t in (10, 25, 40) for e in (0.1, 0.5, 1.0))))
    # design problem: round trip of the inverse formula
    th = L.max_room_temp_c(60, 4, 0.30, 15)
    checks.append((f"design: warmest room for 15 W is 24.8 C (got {th:.1f})", abs(th - 24.786) < 0.01))
    checks.append(("design: round trip, power at that room temperature is exactly 15 W", abs(L.electric_power(60, 4, th, 0.30) - 15.0) < 1e-9))
    checks.append(("design: eta2 = 0.30 at 32 C fails the 15 W limit, eta2 = 0.45 passes",
                   L.electric_power(60, 4, 32, 0.30) > 15 and L.electric_power(60, 4, 32, 0.45) < 15))
    for bad, label in ((lambda: L.cop_carnot(25, 25), "equal temperatures"), (lambda: L.cop_carnot(30, 25), "room colder than inside"),
                       (lambda: L.cop_real(4, 25, 0.0), "eta2 = 0")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
    checks.append(("edge case: room just above the inside gives a very large but finite COP", np.isfinite(L.cop_carnot(4, 4.001)) and L.cop_carnot(4, 4.001) > 1e4))
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
