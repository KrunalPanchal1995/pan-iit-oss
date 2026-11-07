"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    B = L.BASE
    s = L.simulate()
    checks.append(("worked example: ram area 19.63 cm^2 and load pressure 60.0 bar for 1200 kg",
                   abs(L.A_CYL * 1e4 - 19.635) < 0.001 and abs(B["mass"] * L.G / L.A_CYL / 1e5 - 59.96) < 0.01))
    checks.append(("worked example: ideal lift speed Q / A = 50.93 mm/s", abs(B["Q"] / L.A_CYL * 1000 - 50.93) < 0.01))
    checks.append(("worked example: base case never opens the relief valve (peak below 80 bar)",
                   s["p"].max() < B["p_relief"] and s["q_relief"].max() == 0.0))
    # validation 1: analytic lift speed
    s0 = L.simulate(c_leak40=0.0)
    checks.append(("no leakage: simulated mean speed equals Q / A within 0.1 percent",
                   abs(L.mean_speed(s0, 3.0) / (B["Q"] / L.A_CYL) - 1.0) < 1e-3))
    v_th = L.lift_speed(c=s["c"])
    checks.append(("with leakage and friction: simulated speed matches the closed formula within 0.5 percent",
                   abs(L.mean_speed(s, 3.0) / v_th - 1.0) < 5e-3 and v_th < B["Q"] / L.A_CYL))
    squeeze = s0["p"][-1] * (B["V0"] + L.A_CYL * s0["x"][-1]) / B["B"] / L.A_CYL
    checks.append(("volume balance: lift = Q t / A minus the oil squeeze, within 3 mm",
                   abs(s0["x"][-1] - (B["Q"] * 6.0 / L.A_CYL - squeeze)) < 3e-3))
    # validation 2: energy accounting
    worst = max(abs(L.energy_residual(r)) / r["W_in"] for r in (s, L.simulate(wear=10.0, T=80.0), L.simulate(mass=1800.0, p_relief=7.0e6)))
    checks.append(("energy: input work = lift + friction + leakage + relief + oil squeeze + kinetic, residual under 0.1 percent", worst < 1e-3))
    checks.append(("energy: most of the pump work (over 90 percent) becomes lifted potential energy in the base case",
                   s["PE"] / s["W_in"] > 0.90))
    # validation 3: spring-mass behaviour of the oil
    k = L.stiffness(B["B"], L.A_CYL, B["V0"])
    checks.append(("hand calculation: oil spring k = B A^2 / V0 = 3.86 MN/m", abs(k / 1e6 - 3.855) < 0.01))
    r = L.simulate(t_end=3.0, Q=3.0e-5, c_f=1000.0)
    sl = slice(int(np.searchsorted(r["t"], 0.2)), None)
    kk = L.stiffness(B["B"], L.A_CYL, B["V0"] + L.A_CYL * r["x"][sl].mean())
    f_th = np.sqrt(kk / B["mass"]) / (2 * np.pi)
    checks.append(("ringing: pressure ripple frequency equals sqrt(k / m) / (2 pi) within 3 percent",
                   abs(L.ring_frequency(r["t"][sl], r["p"][sl]) / f_th - 1.0) < 0.03))
    # sensitivity
    base = L.lift_after()
    worn = L.lift_after(wear=10.0)
    hot = L.lift_after(wear=10.0, T=80.0)
    cold = L.lift_after(T=20.0)
    checks.append(("sensitivity: more leakage lifts less (new > worn > worn and hot), cold oil lifts a little more",
                   base > worn > hot and cold > base))
    checks.append(("sensitivity: worn seals at 80 C lose over half of the lift in 6 s", hot < 0.5 * base))
    # failure / limit cases
    f = L.simulate(mass=1800.0, p_relief=7.0e6)
    pp = L.plateau_pressure(B["Q"], f["kr"], 7.0e6, f["c"])
    checks.append(("failure: 1800 kg on a 70 bar relief valve does not lift (pressure plateau)",
                   f["x"].max() == 0.0 and abs(f["p"][-1] / pp - 1.0) < 5e-3 and f["p"][-1] > 7.0e6))
    checks.append(("failure: plateau is 76.8 bar, above the setting but below the 90 bar the load needs",
                   abs(pp / 1e5 - 76.8) < 0.1 and 1800.0 * L.G / L.A_CYL / 1e5 > pp / 1e5))
    c_bad = L.leak_coefficient(B["c_leak40"], 30.0, 80.0)
    checks.append(("failure: leakage above the critical value swallows the whole pump flow, no lift",
                   c_bad > L.critical_leak(B["Q"], L.A_CYL, B["mass"]) and L.lift_after(wear=30.0, T=80.0) == 0.0))
    z = L.simulate(Q=0.0, t_end=1.0)
    checks.append(("edge: with the pump off the pressure stays zero and the car stays on the floor",
                   z["p"].max() == 0.0 and z["x"].max() == 0.0))
    checks.append(("edge: relief valve gain makes the full pump flow pass at 10 percent over the setting",
                   abs(L.relief_gain(1e-4, 8e6) * 0.1 * 8e6 - 1e-4) < 1e-18))
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
