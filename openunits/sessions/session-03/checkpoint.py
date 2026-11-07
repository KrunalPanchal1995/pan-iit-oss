"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    n, number = 12, 0.2
    times = L.firing_times(n)
    _, y_true = L.offset_simulated(L.dv_from_file(number, L.LBF_S_TO_NS), times)
    _, y_bug = L.offset_simulated(L.dv_from_file(number, 1.0), times)
    miss_sim = (y_true[-1] - y_bug[-1]) / 1000.0
    checks.append(("worked example: 12 firings of 0.2 lbf*s miss by 119.17 km (toy model)",
                   abs(miss_sim - 119.17) < 0.01))
    one = L.miss_distance(1.0, 1) / 1000.0
    hand = 1.0 * (L.LBF_S_TO_NS - 1.0) / 600.0 * (180 - 10) * 86400.0 / 1000.0
    checks.append(("hand calculation: one 1 lbf*s firing on day 10 misses by 84.4 km",
                   abs(one - hand) < 1e-6 and abs(one - 84.4) < 0.05))
    closed = n * number * (L.LBF_S_TO_NS - 1.0) / 600.0 * (L.T_END - times.mean()) / 1000.0
    checks.append(("simulation agrees with the closed form n*dv_err*(T - mean firing time)",
                   abs(miss_sim - closed) < 1e-6))
    checks.append(("real path is 4.4482 times the predicted one", abs(y_true[-1] / y_bug[-1] - 4.448222) < 1e-6))
    checks.append(("with the right factor the miss is zero",
                   abs(L.miss_distance(0.2, 12, factor_used=L.LBF_S_TO_NS)) < 1e-9))
    m2, m1 = L.miss_distance(0.2, 12, mass=1200.0), L.miss_distance(0.2, 12, mass=600.0)
    checks.append(("sensitivity: doubling the mass halves the miss", abs(m2 / m1 - 0.5) < 1e-9))
    checks.append(("sensitivity: doubling the impulse doubles the miss",
                   abs(L.miss_distance(0.4, 12) / m1 - 2.0) < 1e-9))
    late = (L.LBF_S_TO_NS - 1.0) / 600.0 * (180 - 179) * 86400.0
    checks.append(("limit: a firing one day before arrival barely matters (about 0.5 km)",
                   abs(late / 1000.0 - 0.497) < 0.01))
    q = L.total_miss(L.Quantity(0.2, "lbf*s"), 12, L.Quantity(600.0, "kg"))
    checks.append(("wrapper reproduces the miss and returns a length", abs(q.to("km") - 119.17) < 0.01))
    checks.append(("wrapper converts: 1 lbf*s is 4.448222 N*s", abs(L.Quantity(1, "lbf*s").to("N*s") - 4.448222) < 1e-6))

    def raises(f):
        try:
            f()
        except L.DimensionError:
            return True
        return False

    checks.append(("force + impulse is refused", raises(lambda: L.Quantity(5, "N") + L.Quantity(5, "N*s"))))
    checks.append(("a bare number is refused at the gate", raises(lambda: L.require(0.2, "N*s"))))
    checks.append(("a length cannot be asked for in N*s", raises(lambda: L.Quantity(2, "m").to("N*s"))))
    checks.append(("force * time has the dimension of impulse",
                   bool(np.array_equal((L.Quantity(5, "N") * L.Quantity(2, "s")).dim, L.Quantity(1, "N*s").dim))))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson3", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
