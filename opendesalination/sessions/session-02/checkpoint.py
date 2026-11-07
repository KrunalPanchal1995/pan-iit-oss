"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    pf = L.osmotic_pressure(35.0)
    checks.append(("salt balance: at r = 0.5 the brine is 70 g/L", abs(L.brine_concentration(35.0, 0.5) - 70.0) < 1e-12))
    w = L.w_reversible(35.0, 0.5)
    checks.append((f"worked example: least work at r = 0.5 is {w:.3f} kWh/m3 (hand value 1.143)", abs(w - 1.1433) < 1e-3))
    checks.append(("hand calculation: 2969 x ln 2 / 0.5 / 3600", abs(w - pf * np.log(2.0) / 0.5 / 3600.0) < 1e-12))
    checks.append(("adding up 2000 strips agrees with the ln formula within 0.01 percent",
                   abs(L.batch_piston_work(35.0, 0.5) - w) / w < 1e-4))
    checks.append(("limit: least work at tiny recovery tends to the Session 1 value pi_f / 3600",
                   abs(L.w_reversible(35.0, 1e-6) - pf / 3600.0) < 1e-5))
    ws = L.w_single_stage(35.0, 0.5)
    checks.append((f"worked example: one stage, no ERD, r = 0.5 needs {ws:.3f} kWh/m3 = 4 pi_f",
                   abs(ws - 4 * pf / 3600.0) < 1e-12 and abs(ws - 3.299) < 2e-3))
    rr = np.linspace(0.05, 0.95, 181)
    best = rr[int(np.argmin([L.w_single_stage(35.0, r) for r in rr]))]
    checks.append(("one stage without ERD is cheapest at r = 0.5", abs(best - 0.5) < 0.006))
    checks.append(("perfect ERD: one stage needs pi_b / 3600 = 1.650 kWh/m3",
                   abs(L.w_single_stage(35.0, 0.5, 1.0) - 2 * pf / 3600.0) < 1e-12))
    checks.append(("ERD 0.9 at r = 0.5 gives 1.815 kWh/m3", abs(L.w_single_stage(35.0, 0.5, 0.9) - 1.8146) < 1e-3))
    checks.append(("one ideal stage equals the one-stage plant with a perfect ERD",
                   abs(L.w_staged(35.0, 0.5, 1) - L.w_single_stage(35.0, 0.5, 1.0)) < 1e-12))
    checks.append(("staged model with n = 1 equals the one-stage plant for any ERD (here 0.9 and 0)",
                   abs(L.w_staged(35.0, 0.5, 1, 0.9) - L.w_single_stage(35.0, 0.5, 0.9)) < 1e-12
                   and abs(L.w_staged(35.0, 0.6, 1, 0.0) - L.w_single_stage(35.0, 0.6, 0.0)) < 1e-12))
    checks.append(("3 stages with ERD 0.95 at r = 0.5 need 1.375 kWh/m3", abs(L.w_staged(35.0, 0.5, 3, 0.95) - 1.3746) < 1e-3))
    ws3 = [L.w_staged(35.0, 0.5, n) for n in (1, 2, 3, 10, 1000)]
    checks.append(("more stages always use less energy", bool(np.all(np.diff(ws3) < 0))))
    checks.append(("1000 stages approach the least work within 0.1 percent", abs(ws3[-1] - w) / w < 1e-3))
    order = [L.w_reversible(35.0, r) <= L.w_staged(35.0, r, 3) <= L.w_single_stage(35.0, r, 1.0)
             <= L.w_single_stage(35.0, r, 0.9) <= L.w_single_stage(35.0, r) for r in rr]
    checks.append(("second law: no process ever beats the least work (at every recovery)", all(order)))
    checks.append(("a 6000 kPa pump reaches at most 50.5 percent recovery on seawater",
                   abs(L.recovery_for_pressure(35.0, 6000.0) - (1 - pf / 6000.0)) < 1e-12
                   and abs(L.recovery_for_pressure(35.0, 6000.0) - 0.505) < 1e-3))
    checks.append(("a pump below the feed osmotic pressure gives no water", L.recovery_for_pressure(35.0, 2000.0) == 0.0))
    bad = 0
    for call in (lambda: L.w_reversible(35.0, 1.0), lambda: L.w_single_stage(35.0, 0.5, 1.5), lambda: L.w_staged(35.0, 0.5, 0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
