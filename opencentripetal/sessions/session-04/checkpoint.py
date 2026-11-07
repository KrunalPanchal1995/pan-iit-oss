"""Checkpoint for Session 4. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R, v = 100.0, 20.0
    # the roadmap checkpoint and the worked example
    jerk = L.lateral_jerk(v, R, 40.0)
    checks.append((f"roadmap checkpoint: spiral 40 m, R = 100 m, 20 m/s: lateral jerk v^3 / (R L) = {jerk:.2f} m/s^3 (2.0); the step of Session 3 jumps by v^2 / R = {v * v / R:.1f} m/s^2 at once",
                   abs(jerk - 2.0) < 1e-12 and abs(v * v / R - 4.0) < 1e-12))
    p = L.build_path(R, 40.0)
    t = np.arange(0.0, 2.0 + 1e-9, 0.01)
    a = L.lateral_acceleration(v, L.clothoid_curvature(v * t, R, 40.0))
    checks.append((f"acceleration along the spiral rises from {a[0]:.1f} to {a[-1]:.1f} m/s^2 in {L.spiral_time(v, 40.0):.1f} s at a steady {np.diff(a)[0] / 0.01:.2f} m/s^3",
                   abs(a[0]) < 1e-12 and abs(a[-1] - 4.0) < 1e-9 and np.allclose(np.diff(a) / 0.01, 2.0, atol=1e-6) and abs(L.spiral_time(v, 40.0) - 2.0) < 1e-12))
    checks.append(("heading at the end of the spiral is L / (2 R) = 0.2 rad (11.46 degrees)", abs(float(L.clothoid_heading(40.0, R, 40.0)) - 0.2) < 1e-12))
    # the clothoid against a numerical integral
    s = np.linspace(0.0, 40.0, 9)
    xs, ys = L.clothoid_xy(s, R, 40.0)
    tt, ww = np.polynomial.legendre.leggauss(20)
    gx = [sum(w * math.cos((q * 0.5 * (1 + z)) ** 2 / (2 * R * 40.0)) for z, w in zip(tt, ww)) * q * 0.5 for q in s]
    gy = [sum(w * math.sin((q * 0.5 * (1 + z)) ** 2 / (2 * R * 40.0)) for z, w in zip(tt, ww)) * q * 0.5 for q in s]
    err = max(float(np.max(np.abs(xs - gx))), float(np.max(np.abs(ys - gy))))
    checks.append((f"series for the clothoid position agrees with a 20-point Gauss integral to {err:.0e}", err < 1e-11))
    # geometry of the path
    dth = np.diff(p["theta"]) / np.diff(p["s"])
    checks.append(("the heading changes at the rate of the curvature along the whole path", float(np.max(np.abs(dth - p["kappa"][1:]))) < 1e-4))
    step = np.hypot(np.diff(p["x"]), np.diff(p["y"]))
    checks.append(("the path has no jump: every 0.05 m of arc length is 0.05 m of distance", float(np.max(np.abs(step - 0.05))) < 1e-6))
    cx, cy = p["centre"]
    on_arc = p["s"] >= p["s_arc"]
    rr = np.hypot(p["x"][on_arc] - cx, p["y"][on_arc] - cy)
    checks.append(("after the spiral the path is a circle of radius 100 m (to 1e-9)", float(np.max(np.abs(rr - R))) < 1e-9))
    checks.append((f"shift of the circle {p['shift']:.4f} m against L^2 / (24 R) = {L.spiral_shift_formula(R, 40.0):.4f} m (within 0.2 percent); no spiral gives 0",
                   abs(p["shift"] - 0.6657) < 1e-3 and abs(L.spiral_shift_formula(R, 40.0) - 2 / 3) < 1e-12 and abs(p["shift"] - L.spiral_shift_formula(R, 40.0)) < 0.002 * 0.6667 + 1e-3
                   and abs(L.build_path(R, 0.0)["shift"]) < 1e-12))
    # design rule
    checks.append(("shortest spiral for a jerk limit: v^3 / (R j) = 40 m for 2.0 m/s^3 and 80 m for 1.0 m/s^3",
                   abs(L.min_spiral_length(v, R, 2.0) - 40.0) < 1e-9 and abs(L.min_spiral_length(v, R, 1.0) - 80.0) < 1e-9))
    checks.append(("round_up goes up to a multiple of 5 m: 8.9 -> 10, 25 -> 25, 52.1 -> 55", L.round_up(8.9) == 10 and L.round_up(25.0) == 25 and L.round_up(52.1) == 55))
    # the car
    m0 = {Ls: L.entry_metrics(R, Ls, v) for Ls in (0, 10, 20, 40, 80)}
    checks.append((f"car with slow tyres, entering at 20 m/s: peak jerk {m0[0]['peak_jerk']:.1f} (step) falls to {m0[40]['peak_jerk']:.2f} with a 40 m spiral and {m0[80]['peak_jerk']:.2f} with 80 m",
                   15.0 < m0[0]["peak_jerk"] < 16.5 and 2.3 < m0[40]["peak_jerk"] < 2.7 and 1.1 < m0[80]["peak_jerk"] < 1.4))
    checks.append((f"peak sideways acceleration {m0[0]['peak_a']:.2f} -> {m0[40]['peak_a']:.2f} -> {m0[80]['peak_a']:.2f} m/s^2 (steady 4.0) and distance from the path {m0[0]['max_dev']:.2f} -> {m0[40]['max_dev']:.2f} -> {m0[80]['max_dev']:.2f} m",
                   4.85 < m0[0]["peak_a"] < 5.0 and 4.4 < m0[40]["peak_a"] < 4.6 and 4.1 < m0[80]["peak_a"] < 4.25
                   and 0.5 < m0[0]["max_dev"] < 0.6 and 0.4 < m0[40]["max_dev"] < 0.47 and 0.22 < m0[80]["max_dev"] < 0.3))
    ls = (0, 10, 20, 40, 80)
    checks.append(("longer spiral, smaller peak jerk, smaller peak acceleration and no larger distance from the path (L = 0, 10, 20, 40, 80)",
                   all(m0[ls[i]]["peak_jerk"] > m0[ls[i + 1]]["peak_jerk"] and m0[ls[i]]["peak_a"] > m0[ls[i + 1]]["peak_a"] and m0[ls[i]]["max_dev"] >= m0[ls[i + 1]]["max_dev"] for i in range(4))))
    # validation of the car model
    q = {Ls: L.entry_metrics(R, Ls, v, tau=0.01) for Ls in (0, 40)}
    checks.append((f"validation: with almost instant tyres (tau = 0.01 s) the car tracks the path to {q[40]['max_dev']:.3f} m and its peak jerk on the spiral is {q[40]['peak_jerk']:.2f}, the ideal v^3 / (R L) = 2.0",
                   q[40]["max_dev"] < 0.02 and abs(q[40]["peak_jerk"] - 2.0) < 0.05 and q[0]["peak_jerk"] > 100))
    longp = L.build_path(R, 40.0, arc=250.0)
    out = L.follow_path(longp, v)
    checks.append((f"validation: on the long circle the car settles at a = {out['a'][-1]:.4f} m/s^2 = v^2 / R = 4.0, on the path to {abs(out['d'][-1]):.3f} m",
                   abs(out["a"][-1] - 4.0) < 0.005 and abs(out["d"][-1]) < 0.02))
    # limits and failure cases
    fast = {Ls: L.entry_metrics(R, Ls, 29.0) for Ls in (0, 40, 80)}
    checks.append((f"failure: at 29 m/s the circle needs {29.0 ** 2 / R:.2f} m/s^2 but friction gives mu g = {0.8 * L.G:.2f}: the car runs {fast[80]['max_dev']:.1f} m off the path even with an 80 m spiral",
                   all(fast[k]["peak_ratio"] > 0.999 for k in fast) and fast[80]["max_dev"] > 2.0 and fast[0]["max_dev"] > 4.0))
    checks.append(("limits: L > 2 R, a zero spiral length for the jerk, R <= 0 or a negative jerk limit are rejected",
                   all(_raises(f) for f in (lambda: L.lateral_jerk(v, R, 0.0), lambda: L.clothoid_xy(1.0, R, 300.0), lambda: L.build_path(0.0, 10.0),
                                            lambda: L.min_spiral_length(v, R, -1.0), lambda: L.follow_path(L.build_path(R, 10.0), -1.0)))))
    # mini-project reference numbers
    des = [L.design_spiral(k, 150.0, 2.0) for k in (50, 70, 90)]
    ml = [L.entry_metrics(150.0, d["L"], d["v"]) for d in des]
    m_step = [L.entry_metrics(150.0, 0.0, d["v"]) for d in des]
    checks.append((f"mini-project: R = 150 m, jerk limit 2.0: spirals {[d['L'] for d in des]} m, jerk {[round(d['jerk'], 2) for d in des]}, shifts {[round(d['shift'], 2) for d in des]} m, times {[round(d['time'], 1) for d in des]} s",
                   [d["L"] for d in des] == [10.0, 25.0, 55.0] and [round(d["jerk"], 2) for d in des] == [1.79, 1.96, 1.89]
                   and [round(d["shift"], 2) for d in des] == [0.03, 0.17, 0.84] and [round(d["time"], 1) for d in des] == [0.7, 1.3, 2.2]))
    checks.append((f"mini-project: peak jerk of the car with the designed spiral {[round(m['peak_jerk'], 1) for m in ml]} against the step {[round(m['peak_jerk'], 1) for m in m_step]}",
                   [round(m["peak_jerk"], 1) for m in ml] == [2.2, 2.4, 2.3] and [round(m["peak_jerk"], 1) for m in m_step] == [5.0, 9.7, 16.3]))
    return checks


def _raises(f):
    try:
        f()
    except ValueError:
        return True
    return False


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
