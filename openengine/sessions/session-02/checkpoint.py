"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    e9 = L.otto_eta(9.0)
    checks.append((f"worked example: Otto r = 9, gamma = 1.4 gives 0.585 (got {e9:.4f})", abs(e9 - 0.585) < 5e-4))
    checks.append(("hand calculation: 9**0.4 = 2.408 so eta = 1 - 1/2.408", abs(9 ** 0.4 - 2.408) < 1e-3 and abs(1 - 1 / 2.408 - e9) < 1e-3))
    d = L.diesel_eta(18.0, 2.0)
    checks.append((f"worked example: Diesel r = 18, rho = 2 gives 0.632 (got {d:.4f})", abs(d - 0.632) < 5e-4))
    checks.append(("worked example: Otto needs r = 9.88 for eta = 0.60", abs(L.otto_r_for_eta(0.60) - 9.88) < 5e-3))
    checks.append(("inverse then forward returns the target efficiency", abs(L.otto_eta(L.otto_r_for_eta(0.55)) - 0.55) < 1e-12))
    checks.append(("Carnot between 300 K and 2000 K is 0.85", abs(L.carnot_eta(300, 2000) - 0.85) < 1e-12))
    checks.append(("limit: Diesel with rho = 1 equals Otto", abs(L.diesel_eta(12.0, 1.0) - L.otto_eta(12.0)) < 1e-12))
    checks.append(("limit: Diesel with rho very close to 1 is stable and close to Otto",
                   abs(L.diesel_eta(12.0, 1.0 + 1e-9) - L.otto_eta(12.0)) < 1e-6))
    checks.append(("at equal r, Otto beats Diesel for every rho > 1", all(L.otto_eta(15) > L.diesel_eta(15, x) for x in (1.2, 2, 3, 5))))
    checks.append(("Diesel efficiency falls as the cut-off ratio grows",
                   all(L.diesel_eta(18, a) > L.diesel_eta(18, b) for a, b in ((1.5, 2), (2, 3), (3, 4)))))
    checks.append(("efficiency rises with r but with diminishing returns",
                   (L.otto_eta(10) - L.otto_eta(9)) > (L.otto_eta(20) - L.otto_eta(19)) > 0))
    (t1, t2, t3, t4), qo = L.otto_temperatures(9.0, 1100.0)
    checks.append(("Otto heats reproduce the formula: 1 - q_out / q_in", abs(1 - qo / 1100.0 - e9) < 1e-12))
    checks.append(("Otto Carnot bound with its own T3 and T1 holds", L.otto_eta(9.0) < L.carnot_eta(t1, t3)))
    (t1, t2, t3, t4), rho, qo = L.diesel_temperatures(18.0, 1100.0)
    checks.append(("Diesel heats reproduce the formula: 1 - q_out / q_in", abs(1 - qo / 1100.0 - L.diesel_eta(18.0, rho)) < 1e-12))
    checks.append(("Diesel Carnot bound with its own T3 and T1 holds", L.diesel_eta(18.0, rho) < L.carnot_eta(t1, t3)))
    rho2 = L.diesel_rho_for_eta(0.60, 18.0)
    checks.append(("design: cut-off ratio for eta = 0.60 at r = 18 reproduces 0.60",
                   rho2 is not None and abs(L.diesel_eta(18.0, rho2) - 0.60) < 1e-9))
    checks.append(("design: an efficiency above the Otto value at the same r is impossible for Diesel",
                   L.diesel_rho_for_eta(0.70, 18.0) is None))
    v, p = L.cycle_path("otto", 9.0, 1100.0)
    w = float(np.sum(0.5 * (p + np.roll(p, -1)) * (np.roll(v, -1) - v)))
    checks.append(("area of the Otto P-V loop equals q_in times eta (first law), within 1 percent",
                   abs(w - 1100.0 * e9) / (1100.0 * e9) < 0.01))
    bad = 0
    for call in (lambda: L.otto_eta(1.0), lambda: L.diesel_eta(9, 0.5), lambda: L.otto_r_for_eta(1.0), lambda: L.carnot_eta(500, 300)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 4))
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
