"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    c = L.cycle_work(288, 10, 1400)
    checks.append((f"worked example: T2 = 556.0 K (got {c['t2']:.1f})", abs(c["t2"] - 556.0) < 0.1))
    checks.append((f"worked example: T4 = 725.1 K (got {c['t4']:.1f})", abs(c["t4"] - 725.1) < 0.1))
    checks.append((f"worked example: w_c = 269.4 kJ/kg (got {c['w_c']:.1f})", abs(c["w_c"] - 269.4) < 0.1))
    checks.append((f"worked example: w_t = 678.2 kJ/kg (got {c['w_t']:.1f})", abs(c["w_t"] - 678.2) < 0.1))
    checks.append((f"worked example: w_net = 408.9 kJ/kg (got {c['w_net']:.1f})", abs(c["w_net"] - 408.9) < 0.1))
    checks.append((f"worked example: power for 20 kg/s is 8.18 MW (got {L.power_mw(20, 288, 10, 1400):.2f})",
                   abs(L.power_mw(20, 288, 10, 1400) - 8.18) < 0.01))
    checks.append(("consistency with Session 1: eta = 1 - 1 / r^K",
                   all(abs(L.cycle_work(288, r, 1400)["eta"] - (1 - 1 / r ** L.K)) < 1e-12 for r in (2, 5, 10, 25))))
    checks.append(("energy balance: w_net = q_in - q_out with q_out = cp (T4 - T1)",
                   abs(c["w_net"] - (c["q_in"] - L.CP * (c["t4"] - 288))) < 1e-9))
    ro = L.best_ratio_for_work(288, 1400)
    checks.append((f"design: the best pressure ratio for work is 15.9 (got {ro:.1f})", abs(ro - 15.91) < 0.01))
    w_best = L.cycle_work(288, ro, 1400)["w_net"]
    checks.append(("design: the work at r_opt beats the work at 0.8 r_opt and 1.25 r_opt",
                   w_best > L.cycle_work(288, 0.8 * ro, 1400)["w_net"] and w_best > L.cycle_work(288, 1.25 * ro, 1400)["w_net"]))
    checks.append(("a hotter turbine inlet gives more work at the same r",
                   L.cycle_work(288, 10, 1600)["w_net"] > L.cycle_work(288, 10, 1400)["w_net"] > L.cycle_work(288, 10, 1200)["w_net"]))
    checks.append(("edge case: r = 1 gives zero net work", abs(L.cycle_work(288, 1, 1400)["w_net"]) < 1e-9))
    for bad, label in ((lambda: L.cycle_work(288, 0.5, 1400), "r below 1"),
                       (lambda: L.cycle_work(288, 300, 1400), "T2 above T3 (r far too large)")):
        try:
            bad()
            raised = False
        except ValueError:
            raised = True
        checks.append((f"edge case: {label} gives an error", raised))
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
