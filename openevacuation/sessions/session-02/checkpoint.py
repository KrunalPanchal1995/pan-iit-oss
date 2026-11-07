"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("speed at 1.0 persons/m2 on the level: 1.40 x (1 - 0.266) = 1.028 m/s", abs(L.speed(1.0) - 1.0276) < 1e-4))
    checks.append(("free walking in a thin crowd (0.2 persons/m2): 0.85 x 1.40 = 1.19 m/s", abs(L.speed(0.2) - 1.19) < 1e-12))
    checks.append(("the speed law has no jump where the crowd starts to slow people down",
                   abs(L.speed(L.D_MIN + 1e-9) - L.speed(L.D_MIN - 1e-9)) < 1e-6))
    dd = np.linspace(0, 5, 5001)
    checks.append(("speed never rises as the crowd gets denser", np.all(np.diff(L.speed(dd)) <= 1e-12)))
    checks.append(("jammed crowd (1 / a = 3.76 persons/m2) does not move", abs(L.speed(L.D_JAM)) < 1e-12 and L.speed(5.0) == 0.0))
    checks.append(("specific flow is zero for an empty and for a jammed crowd",
                   L.specific_flow(0.0) == 0.0 and abs(L.specific_flow(L.D_JAM)) < 1e-12))
    d = np.linspace(0.6, 3.7, 31001)
    fs = L.specific_flow(d)
    checks.append((f"the peak of Fs is at D = 1 / (2a) = {L.optimal_density():.3f} persons/m2 (numerical search)",
                   abs(d[np.argmax(fs)] - L.optimal_density()) < 1e-3))
    checks.append(("max specific flow k / (4a) = 1.316 persons/(s m) on the level, 1.015 on the stair",
                   abs(L.max_specific_flow() - 1.3158) < 1e-4 and abs(L.max_specific_flow(L.stair_k(0.178, 0.279)) - 1.015) < 1e-3))
    checks.append(("no density on the curve beats the maximum", np.max(fs) <= L.max_specific_flow() + 1e-12))
    checks.append(("inverse: the density for a flow gives that flow back",
                   all(abs(L.specific_flow(L.density_for_flow(f)) - f) < 1e-9 for f in (0.3, 0.5, 0.9, 1.2, 1.3))))
    checks.append(("stairs are slower than level ground at the same density", L.speed(1.5, L.stair_k(0.178, 0.279)) < L.speed(1.5)))
    f_in = L.specific_flow(1.0) * L.effective_width(2.0, "corridor")
    tr = L.transition(f_in, 1.2)
    checks.append((f"worked example: 2 m corridor at 1.0 persons/m2 carries {f_in:.3f} persons/s", abs(f_in - 1.644) < 1e-3))
    checks.append((f"worked example: 1.2 m door passes {tr['flow_out']:.3f} and the queue grows at {tr['queue_rate']:.3f} persons/s",
                   tr["queue"] and abs(tr["flow_out"] - 1.184) < 1e-3 and abs(tr["queue_rate"] - 0.460) < 1e-3))
    checks.append(("conservation: flow out + queue growth = flow in", abs(tr["flow_out"] + tr["queue_rate"] - f_in) < 1e-12))
    wide = L.transition(f_in, 2.0)
    checks.append(("a door wider than needed passes everything and forms no queue", not wide["queue"] and abs(wide["flow_out"] - f_in) < 1e-12))
    checks.append(("after a wide door the crowd is thinner (flow spreads over more width)",
                   wide["density_out"] < 1.0 and abs(wide["fs_out"] * L.effective_width(2.0) - f_in) < 1e-12))
    bad = 0
    for call in (lambda: L.speed(-1.0), lambda: L.density_for_flow(1.5), lambda: L.effective_width(0.3),
                 lambda: L.stair_k(0.25, 0.20), lambda: L.transition(-1.0, 1.2)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 5))
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
