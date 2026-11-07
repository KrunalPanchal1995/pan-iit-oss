"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("LJ force is zero at r = 2^(1/6) = 1.1225", abs(float(L.lj_force(L.R_MIN))) < 1e-9))
    checks.append(("LJ well depth at the minimum is -1 epsilon", abs(float(L.lj_potential(L.R_MIN)) + 1.0) < 1e-9))
    checks.append(("LJ potential is zero at r = 1 sigma", abs(float(L.lj_potential(1.0))) < 1e-12))

    # worked example: LJ at r = 1.5
    v, f = float(L.lj_potential(1.5)), float(L.lj_force(1.5))
    checks.append((f"worked example: LJ at r=1.5 gives V = -0.3203 and F = -1.158 (got {v:.4f}, {f:.3f})",
                   abs(v + 0.3203) < 1e-3 and abs(f + 1.158) < 2e-3))

    # force = minus slope of V (central difference), for both laws
    h = 1e-6
    for name, V, F in (("LJ", L.lj_potential, L.lj_force), ("spring", L.spring_potential, L.spring_force)):
        r = 1.4
        slope = (float(V(r + h)) - float(V(r - h))) / (2 * h)
        checks.append((f"{name}: force equals minus the slope of the potential", abs(float(F(r)) + slope) < 1e-4))

    # hand calculation: spring at r = 1.3 with k = 10, r0 = 1: V = 0.5*10*0.09 = 0.45, F = -3
    checks.append(("hand calculation: spring k=10, r0=1, r=1.3 gives V=0.45 and F=-3.0",
                   abs(float(L.spring_potential(1.3, 10.0, 1.0)) - 0.45) < 1e-9 and abs(float(L.spring_force(1.3, 10.0, 1.0)) + 3.0) < 1e-9))

    # the matched spring has the same curvature as the LJ well
    h = 1e-4
    curv = (float(L.lj_potential(L.R_MIN + h)) - 2 * float(L.lj_potential(L.R_MIN)) + float(L.lj_potential(L.R_MIN - h))) / h ** 2
    checks.append((f"spring constant matches the LJ curvature (57.15, got {curv:.2f})", abs(curv - L.K_MATCH) < 0.05))

    # simulated spring period equals 2 pi sqrt(mu/k)
    t, r, _ = L.simulate_pair(L.spring_force, L.R_MIN + 0.1)
    checks.append(("simulated spring period matches 2 pi sqrt(mu/k) within 1 percent",
                   abs(L.measured_period(t, r) / L.spring_period(L.K_MATCH) - 1) < 0.01))

    # edge case: released exactly at the minimum, nothing moves
    t, r, _ = L.simulate_pair(L.lj_force, L.R_MIN, steps=200)
    checks.append(("edge case: a pair at the bottom of the well stays put", float(np.max(np.abs(r - L.R_MIN))) < 1e-9))
    # limit: far apart the LJ force is tiny and attractive
    checks.append(("limit: at r = 5 sigma the LJ force is attractive and below 0.01",
                   -0.01 < float(L.lj_force(5.0)) < 0))
    # LJ is anharmonic: a big swing takes longer than a small one
    t1, r1, _ = L.simulate_pair(L.lj_force, L.R_MIN + 0.1)
    t2, r2, _ = L.simulate_pair(L.lj_force, L.R_MIN + 0.5, steps=4000)
    checks.append(("LJ period grows with the size of the swing", L.measured_period(t2, r2) > 1.5 * L.measured_period(t1, r1)))
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
