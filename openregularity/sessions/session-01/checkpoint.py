"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: y' = y^2 with y0 = 2 blows up at t = 0.5", abs(L.blowup_time(2.0) - 0.5) < 1e-12))
    tn, yn = L.time_to_reach(2.0, 2.0, 1e6)
    checks.append(("RK4 reaches y = 1e6 at the exact crossing time 0.5 - 1/y (within 1e-5)",
                   abs(tn - (0.5 - 1.0 / yn)) < 1e-5 and yn >= 1e6))
    t1, _ = L.time_to_reach(1.0, 2.0, 1e6)
    checks.append(("y0 = 1 gives blow-up time 1 (RK4 within 1e-5)", abs(t1 - 1.0) < 1e-5))
    checks.append(("exact y(t) = y0/(1 - y0 t) agrees: y0 = 1, t = 0.9 gives 10", abs(L.exact_y(0.9, 1.0) - 10.0) < 1e-9))
    checks.append(("doubling y0 halves the blow-up time for p = 2", abs(L.blowup_time(2.0) * 2 - L.blowup_time(1.0)) < 1e-12))
    checks.append(("worked example: y(0.4) = 2 / (1 - 2 * 0.4) = 10 for y0 = 2", abs(L.exact_y(0.4, 2.0) - 10.0) < 1e-9))
    checks.append(("y0 = 4 blows up at 0.25 and y0 = 0.5 at 2", abs(L.blowup_time(4.0) - 0.25) < 1e-12 and abs(L.blowup_time(0.5) - 2.0) < 1e-12))
    checks.append(("p = 1.5 with y0 = 1 blows up at t = 2 (formula)", abs(L.blowup_time(1.0, 1.5) - 2.0) < 1e-12))
    t15, _ = L.time_to_reach(1.0, 1.5, 1e6)
    checks.append(("p = 1.5: RK4 time to reach 1e6 is within 0.01 of 2", abs(t15 - 2.0) < 0.01))
    checks.append(("p = 1 never blows up (infinite blow-up time) and y(10) = e^10 is finite",
                   L.blowup_time(1.0, 1.0) == float("inf") and abs(L.exact_y(10.0, 1.0, 1.0) - np.exp(10.0)) < 1e-6))
    checks.append(("p below 1 never blows up", L.blowup_time(1.0, 0.5) == float("inf")))
    x = np.linspace(0, 2 * np.pi, 7)
    checks.append(("at t = 0 the profile is sin x", np.allclose(L.characteristic_profile(x, 0.0), np.sin(x), atol=1e-12)))
    # hand check: the profile value at x must come from a foot point X with X + t sin X = x
    t = 0.5
    xs = np.linspace(0.1, 6.0, 9)
    u = L.characteristic_profile(xs, t)
    ok = True
    for xv, uv in zip(xs, u):
        cands = [np.arcsin(uv), np.pi - np.arcsin(uv)]
        ok &= any(abs(X + t * np.sin(X) - xv) < 1e-9 or abs(X + 2 * np.pi + t * np.sin(X) - xv) < 1e-9
                  or abs(X - 2 * np.pi + t * np.sin(X) - xv) < 1e-9 for X in cands)
    checks.append(("hand check: every profile value comes from a foot point with X + 0.5 sin X = x", ok))
    f0, f5, f9, f99 = (L.small_scale_fraction(v) for v in (0.0, 0.5, 0.9, 0.99))
    checks.append(("a pure sine wave has no energy at wavenumber >= 3", f0 < 1e-20))
    checks.append(("energy at small scales grows as the front steepens (t = 0, 0.5, 0.9, 0.99)", f0 < f5 < f9 < f99))
    checks.append(("about 7 percent of the energy is at k >= 3 when t = 0.9", abs(100 * f9 - 7.0) < 0.5))
    checks.append(("less than 1 percent at t = 0.5", 100 * f5 < 1.0))
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
