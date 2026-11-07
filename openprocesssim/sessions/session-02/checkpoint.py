"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    P = L.P_ATM
    z = np.array([0.5, 0.5, 0.0])
    Tb, yb = L.bubble_T(z, P)
    Td, xd = L.dew_T(z, P)
    checks.append((f"equimolar benzene-toluene at 1 atm: bubble point near 365 K (got {Tb:.1f})", abs(Tb - 365.0) < 0.5 and round(Tb, 1) == 365.3))
    checks.append((f"dew point of the equimolar mixture is 371.9 K (got {Td:.1f})", round(Td, 1) == 371.9))
    checks.append(("first vapour at the bubble point is 0.714 benzene", round(float(yb[0]), 3) == 0.714))
    pure = [round(L.bubble_T(np.eye(3)[i], P)[0], 1) for i in range(3)]
    checks.append((f"pure boiling points: benzene 353.2, toluene 383.8, ethanol 351.5 K (got {pure})", pure == [353.2, 383.8, 351.5]))
    # worked example at 368 K
    T = 368.0
    ps = L.psat(T)
    K = L.k_values(T, P)
    V, _ = L.rr_newton(z, K)
    x = z / (1.0 + V * (K - 1.0))
    y = K * x
    checks.append((f"worked example: P_sat at 368 K is 156.2 kPa (benzene) and 63.3 kPa (toluene) (got {ps[0]:.1f}, {ps[1]:.1f})", round(float(ps[0]), 1) == 156.2 and round(float(ps[1]), 1) == 63.3))
    checks.append((f"worked example: K = 1.542 and 0.6245 (got {K[0]:.3f}, {K[1]:.4f})", round(float(K[0]), 3) == 1.542 and round(float(K[1]), 4) == 0.6245))
    checks.append((f"worked example: V = 0.409, x_benzene = 0.409, y_benzene = 0.631 (got {V:.3f}, {x[0]:.3f}, {y[0]:.3f})",
                   round(V, 3) == 0.409 and round(float(x[0]), 3) == 0.409 and round(float(y[0]), 3) == 0.631))
    f_hand = 0.5 * 0.542 / (1 + 0.542 * V) + 0.5 * (-0.3755) / (1 - 0.3755 * V)
    checks.append(("hand calculation: the Rachford-Rice sum f(V) is zero at the root", abs(f_hand) < 1e-3 and abs(L.rr_f(V, z, K)) < 1e-10))
    # mass balance closure of the flash block
    feed = L.Stream(np.array([50.0, 50.0, 0.0]), 300.0, P)
    vap, liq, Vf, duty = L.flash_TP(feed, T, P)
    checks.append(("flash closes the component balance to 1e-12", float(np.max(np.abs(vap.n + liq.n - feed.n))) < 1e-12))
    checks.append(("flash energy: duty = H(vapour) + H(liquid) - H(feed) and is positive", abs(duty - (vap.enthalpy() + liq.enthalpy() - feed.enthalpy())) < 1e-6 and duty > 0))
    checks.append(("vapour is richer in benzene than the liquid (y > x)", vap.n[0] / vap.total() > liq.n[0] / liq.total()))
    # limits V = 0 at bubble and V = 1 at dew
    Vlo = L.rr_newton(z, L.k_values(Tb - 1e-6, P))[0]
    Vbub = L.rr_newton(z, L.k_values(Tb + 1e-6, P))[0]
    Vdew = L.rr_newton(z, L.k_values(Td - 1e-6, P))[0]
    Vhi = L.rr_newton(z, L.k_values(Td + 1e-6, P))[0]
    checks.append(("limit: V = 0 just below the bubble point and tiny just above it", Vlo == 0.0 and 0.0 < Vbub < 1e-4))
    checks.append(("limit: V = 1 just above the dew point and close to 1 just below it", Vhi == 1.0 and 1 - 1e-4 < Vdew < 1.0))
    # solvers
    Vb, nb = L.rr_bisection(z, K)
    Vn, nn = L.rr_newton(z, K)
    checks.append((f"bisection needs 40 iterations, Newton 4, and agree within 1e-9 (got {nb}, {nn})", nb == 40 and nn == 4 and abs(Vb - Vn) < 1e-9))
    # design problem
    Th = L.flash_T_for_vapour_fraction(z, P, 0.5)
    Kh = L.k_values(Th, P)
    Vh, _ = L.rr_newton(z, Kh)
    xh = z / (1 + Vh * (Kh - 1))
    checks.append((f"design: 50 percent vapour at 368.6 K (got {Th:.1f}), vapour 0.611 benzene, liquid 0.389",
                   round(Th, 1) == 368.6 and abs(Vh - 0.5) < 1e-9 and round(float((Kh * xh)[0]), 3) == 0.611 and round(float(xh[0]), 3) == 0.389))
    T30 = L.flash_T_for_vapour_fraction(z, P, 0.3)
    K30 = L.k_values(T30, P)
    x30 = z / (1 + 0.3 * (K30 - 1))
    checks.append((f"design window: 30 percent vapour needs 367.2 K and then y = 0.655 (got {T30:.1f}, {(K30 * x30)[0]:.3f})",
                   round(T30, 1) == 367.2 and round(float((K30 * x30)[0]), 3) == 0.655))
    def y_of(Tx):
        Kx = L.k_values(Tx, P)
        Vx, _ = L.rr_newton(z, Kx)
        return float((Kx * (z / (1 + Vx * (Kx - 1))))[0])
    checks.append(("design window: y stays at or above 0.65 up to 367.39 K but not at 367.45 K", y_of(367.39) >= 0.65 > y_of(367.45)))
    checks.append(("no single flash of the equimolar feed can exceed y = 0.714 benzene (the first-vapour value)", all(y_of(t) <= 0.7141 for t in np.linspace(365.4, 371.8, 40))))
    # blocks
    h, q = L.heater(feed, 350.0)
    checks.append((f"heater: 100 mol/s equimolar from 300 to 350 K takes 732.5 kW (got {q / 1000:.1f})", abs(q - 732500.0) < 1e-6))
    pm, w = L.pump(feed, P + 400.0)
    checks.append((f"pump: 400 kPa rise on 100 mol/s at 70 percent efficiency needs 5.71 kW (got {w / 1000:.2f})", round(w / 1000, 2) == 5.71))
    m = L.mixer([L.Stream(np.array([60.0, 0.0, 0.0]), 300.0, P), L.Stream(np.array([0.0, 40.0, 0.0]), 340.0, P)])
    checks.append((f"mixer: 60 mol/s benzene at 300 K + 40 mol/s toluene at 340 K leaves at 317.4 K (got {m.T:.1f})", round(m.T, 1) == 317.4 and abs(m.total() - 100.0) < 1e-12))
    a, b = L.splitter(feed, [0.3, 0.7])
    checks.append(("splitter keeps composition and conserves flow", abs(a.total() - 30.0) < 1e-12 and abs(a.total() + b.total() - 100.0) < 1e-12 and np.allclose(a.z(), feed.z())))
    bad = 0
    for fn in (lambda: L.splitter(feed, [0.5, 0.6]), lambda: L.valve(feed, P + 10.0)):
        try:
            fn()
        except ValueError:
            bad += 1
    checks.append(("edge: a splitter that does not sum to 1 and a valve that raises pressure are refused", bad == 2))
    v = L.valve(feed, 50.0)
    checks.append(("valve lowers pressure, keeps temperature and flow", v.P == 50.0 and v.T == feed.T and abs(v.total() - 100.0) < 1e-12))
    # edge: feed below its bubble point and above its dew point
    cold = L.flash_TP(feed, 340.0, P)
    hot = L.flash_TP(feed, 400.0, P)
    checks.append(("edge: at 340 K all liquid, at 400 K all vapour", cold[2] == 0.0 and cold[1].total() == 100.0 and hot[2] == 1.0 and abs(hot[0].total() - 100.0) < 1e-12))
    checks.append((f"the boiling window of the equimolar mixture is 6.7 K wide (got {Td - Tb:.1f})", round(Td - Tb, 1) == 6.7))
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
