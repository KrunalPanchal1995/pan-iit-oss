"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # Nernst limits
    checks.append((f"25 C: RT/F = 25.69 mV per e-fold (got {1000 * L.thermal_voltage():.2f})", abs(1000 * L.thermal_voltage() - 25.69) < 0.01))
    checks.append((f"25 C: 59.16 mV per decade for n = 1 (got {L.mv_per_decade(L.T0, 1):.2f}), 29.58 for n = 2",
                   abs(L.mv_per_decade(L.T0, 1) - 59.16) < 0.01 and abs(L.mv_per_decade(L.T0, 2) - 29.58) < 0.01))
    checks.append(("Nernst gives E0 exactly when Q = 1", abs(float(L.nernst(1.0)) - 1.10) < 1e-12))
    steps = L.nernst(np.array([0.01, 0.1, 1.0, 10.0, 100.0]))
    checks.append(("each decade of Q lowers E by the same 29.58 mV", np.allclose(-np.diff(steps) * 1000, L.mv_per_decade(L.T0, 2), atol=1e-6)))
    # worked example
    e0 = float(L.nernst(0.1))
    r0 = float(L.r_internal(0.0))
    i0 = float(L.current(0.0, 10.0))
    v0 = float(L.terminal_voltage(0.0, 10.0))
    checks.append((f"worked example: [Zn2+] = 0.1, [Cu2+] = 1.0 gives E = 1.1296 V, r = 0.84 ohm, I = 0.1042 A, V = 1.0420 V on 10 ohm (got {e0:.4f}, {r0:.2f}, {i0:.4f}, {v0:.4f})",
                   abs(e0 - 1.1296) < 5e-5 and abs(r0 - 0.84) < 1e-9 and abs(i0 - 0.1042) < 5e-5 and abs(v0 - 1.0420) < 5e-5))
    checks.append(("worked example: load power I^2 R = 0.1086 W and heat in the cell I^2 r = 0.0091 W",
                   abs(i0 ** 2 * 10 - 0.1086) < 5e-5 and abs(i0 ** 2 * r0 - 0.0091) < 5e-5))
    # concentrations conserve moles
    c_zn, c_cu = L.concentrations(1000.0)
    checks.append(("moles are conserved: Zn2+ gained equals Cu2+ lost", abs((c_zn - L.C_ZN0) - (L.C_CU0 - c_cu)) < 1e-12))
    # Faraday's law
    z1, z2 = L.zinc_from_concentration(1000.0), L.zinc_from_faraday(1000.0)
    checks.append((f"Faraday: zinc from concentrations = Q M / (n F) = 0.339 g for 1000 C (got {z1:.4f} and {z2:.4f})",
                   abs(z1 - z2) < 1e-12 and abs(z2 - 0.3388) < 5e-4))
    # RK4 against charge-domain integral
    c = L.discharge_curve(10.0)
    t_ref = float(np.interp(2000.0, c["q"], c["t"]))
    q_rk = L.rk4_charge(10.0, t_ref, steps=2000)
    checks.append((f"RK4 in time reaches the same charge as the integral of dq/I (2000 C vs {q_rk:.2f} C)", abs(q_rk - 2000.0) / 2000.0 < 1e-3))
    q_coarse = L.rk4_charge(10.0, t_ref, steps=200)
    checks.append(("RK4 result is step-size independent (200 versus 2000 steps)", abs(q_coarse - q_rk) / q_rk < 1e-6))
    # energy balance
    chem, deliv, heat = L.energy_balance(10.0)
    checks.append(("energy balance: chemical = delivered + heat", abs(chem - deliv - heat) / chem < 1e-9))
    checks.append(("a lighter load wastes less as heat (heat share 2 ohm > 40 ohm)",
                   (lambda a, b: a[2] / a[0] > b[2] / b[0])(L.energy_balance(2.0), L.energy_balance(40.0))))
    # discharge curve shape
    checks.append(("terminal voltage is below the open-circuit voltage and falls monotonically",
                   bool(np.all(c["v"] < c["e"]) and np.all(np.diff(c["v"]) <= 1e-12))))
    cap = [L.usable_capacity_ah(R) for R in (2.0, 10.0, 40.0)]
    checks.append((f"heavier loads give less usable capacity: {cap[0]:.3f} < {cap[1]:.3f} < {cap[2]:.3f} Ah, all below {L.Q_MAX / 3600:.3f} Ah",
                   cap[0] < cap[1] < cap[2] < L.Q_MAX / 3600.0))
    # maximum power
    Rs = np.linspace(0.05, 6.0, 1000)
    P = L.load_power(1.10, 0.8, Rs)
    checks.append(("maximum power is at R = r (0.8 ohm), P_max = E^2 / (4 r) = 0.378 W",
                   abs(Rs[np.argmax(P)] - 0.8) < 0.01 and abs(P.max() - 1.10 ** 2 / (4 * 0.8)) < 1e-4))
    checks.append(("hand calculation: at maximum power I = E / (2 r) = 0.6875 A", abs(1.10 / (2 * 0.8) - 0.6875) < 1e-12))
    rs = np.sqrt(2.0 / 0.05)
    checks.append((f"design: limiting the heat in a 0.05 ohm cell to 2 W needs I <= 6.32 A, R_s = 0.124 ohm (got {1.10 / rs - 0.05:.3f})",
                   abs(rs - 6.3246) < 1e-3 and abs(1.10 / rs - 0.05 - 0.1239) < 5e-4))
    checks.append(("Section F: the 40 ohm load starts at 1.106 V, the 2 ohm load at 0.795 V",
                   abs(float(L.terminal_voltage(0.0, 40.0)) - 1.106) < 5e-4 and abs(float(L.terminal_voltage(0.0, 2.0)) - 0.795) < 5e-4))
    tt, TT = L.short_circuit_heating(1.10, 0.05, 40.0, 0.15, 60.0)
    t8, T8 = L.short_circuit_heating(1.10, 0.8, 40.0, 0.15, 60.0)
    checks.append((f"short circuit after 60 s: 57.5 C for 0.05 ohm and 27.0 C for 0.8 ohm (got {TT[-1]:.1f}, {T8[-1]:.1f})", abs(TT[-1] - 57.5) < 0.05 and abs(T8[-1] - 27.0) < 0.05))
    checks.append(("efficiency is 50 percent at maximum power", abs(float(L.efficiency(0.8, 0.8)) - 0.5) < 1e-12))
    # temperature
    vs = [float(L.terminal_voltage(0.0, 10.0, T)) for T in (273.15, 298.15, 318.15)]
    checks.append(("cold cells sag more: V at 0 C < 25 C < 45 C", vs[0] < vs[1] < vs[2]))
    # failure case
    t, T = L.short_circuit_heating(1.10, 0.05, 40.0, 0.15, 300.0)
    exact = L.short_circuit_exact(1.10, 0.05, 40.0, 0.15, t)
    checks.append((f"short circuit: numerical heating matches the closed form (largest gap {np.abs(T - exact).max():.2f} K)", np.abs(T - exact).max() < 0.5))
    checks.append(("short circuit current is E / r = 22 A and heat 24.2 W", abs(1.10 / 0.05 - 22.0) < 1e-9 and abs(1.10 ** 2 / 0.05 - 24.2) < 1e-9))
    checks.append(("a dead short (R = 0) still gives a finite current E / r", abs(float(L.current(0.0, 0.0)) - float(L.ocv(0.0)) / 0.84) < 1e-12))
    bad = 0
    for f in (lambda: L.nernst(0.0), lambda: L.short_circuit_heating(1.1, 0.0, 40.0, 0.15, 10.0), lambda: L.pack_runtime_hours(0, 1, 30.0, 9.0)):
        try:
            f()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs (Q = 0, r = 0, empty pack) are rejected", bad == 3))
    # mini-project reference
    best = None
    for ns in range(5, 16):
        for npar in range(1, 6):
            if L.pack_runtime_hours(ns, npar, 30.0, 9.0) >= 5.0 and (best is None or ns * npar < best[0]):
                best = (ns * npar, ns, npar)
    checks.append((f"mini-project reference: smallest pack for a 30 ohm lamp at 9 V or more for 5 h is 10 x 2 = 20 cells (got {best})", best == (20, 10, 2)))
    # ---- many cycles, capacity fade -------------------------------------------------------------
    f50 = float(L.capacity_fraction(50))
    checks.append((f"0.2 percent loss per cycle gives 90.5 percent capacity after 50 cycles (got {100 * f50:.2f} %); a straight-line loss would give 90.0 %",
                   abs(100 * f50 - 90.5) < 0.05 and abs(1 - 0.002 * 50 - 0.90) < 1e-12 and f50 > 0.90))
    n80 = L.cycles_to_fraction(0.8)
    checks.append((f"end of life (80 percent) comes after {n80} cycles: 0.998^111 > 0.8 >= 0.998^112",
                   n80 == 112 and float(L.capacity_fraction(111)) > 0.8 >= float(L.capacity_fraction(112))))
    cl = L.cycle_life(10.0, n80)
    ah0, wh0 = L.usable_capacity_ah(10.0), L.energy_wh(10.0)
    checks.append(("the cycle-by-cycle simulation follows (1 - loss)^(k - 1) and cycle 1 is the fresh cell",
                   np.allclose(cl["fraction"], 0.998 ** np.arange(n80)) and abs(cl["ah"][0] - ah0) < 1e-12 and abs(cl["wh"][0] - wh0) < 1e-12))
    checks.append(("energy over the whole life to 80 percent equals the geometric series wh0 (1 - 0.998^n) / 0.002",
                   abs(cl["wh"].sum() - wh0 * (1 - 0.998 ** n80) / 0.002) < 1e-9))
    z = L.cycle_life(10.0, 5, loss=0.0)
    checks.append(("zero loss: every cycle is identical", np.allclose(z["ah"], ah0) and np.allclose(z["fraction"], 1.0)))

    def aged_capacity(f, R=10.0):
        """Independent check: an aged cell is the same cell with a solution volume f times smaller."""
        q = np.linspace(0.0, L.Q_MAX * f * (1 - 1e-4), 20001)
        xi = q / (L.N_E * L.FARADAY)
        cz, cc = L.C_ZN0 + xi / (f * L.VOL), np.maximum(L.C_CU0 - xi / (f * L.VOL), 1e-9)
        e = L.nernst(cz / cc)
        r = L.R_INT0 * (1 + L.K_DEP * L.C_CU0 / cc)
        v = e - e / (R + r) * r
        j = np.nonzero(v < 0.9 * v[0])[0][0]
        return np.interp(0.9 * v[0], [v[j], v[j - 1]], [q[j], q[j - 1]]) / 3600.0
    checks.append(("an aged cell behaves like a smaller cell: usable capacity of the 90.5 percent cell matches the independent small-volume calculation to 0.1 percent",
                   abs(aged_capacity(f50) - ah0 * f50) / (ah0 * f50) < 1e-3))
    bad = 0
    for args in ((0.8, -0.1), (0.8, 1.0), (1.2, 0.002)):
        try:
            L.cycles_to_fraction(*args)
        except ValueError:
            bad += 1
    checks.append(("a negative loss, a loss of 100 percent and an end-of-life target above 1 are refused", bad == 3))
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
