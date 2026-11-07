"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    tau = L.ignition_delay(1000.0)
    hand = 8.314 * 1000.0 ** 2 / (150e3 * 1500.0 * 36.514)      # R T0^2 / (Ea DT k(T0)), by hand
    checks.append(("worked example: Frank-Kamenetskii by hand gives 1.01 ms at 1000 K",
                   abs(hand * 1e3 - 1.012) < 0.005 and abs(L.frank_kamenetskii(1000.0) - hand) < 2e-6))
    checks.append(("worked example: the integral gives 1.19 ms, so the estimate is 85 percent of it",
                   abs(tau * 1e3 - 1.192) < 0.002 and abs(hand / tau - 0.849) < 0.003))
    t, T, c = L.history(1000.0)
    k = int(np.argmax(T >= 1400.0))
    checks.append(("energy bookkeeping: T = T0 + 1500 (1 - c) and the trapezoid curve reaches +400 K at the same delay",
                   abs(T[0] - 1000.0) < 1e-9 and abs(t[k] / tau - 1) < 2e-3))
    checks.append(("the maximum-rate definition gives a slightly later delay (1.214 ms at 1000 K)",
                   0 < L.max_rate_delay(1000.0)[0] - tau < 0.05e-3 and abs(L.max_rate_delay(1000.0)[0] * 1e3 - 1.214) < 0.002))
    T0s = np.arange(800.0, 1201.0, 50.0)
    b, a, r2 = L.arrhenius_fit(T0s)
    checks.append(("ln(tau) against 1000/T0 is a straight line: R^2 above 0.9999, slope 15.96",
                   r2 > 0.9999 and abs(b - 15.96) < 0.02))
    checks.append(("the fitted slope is below Ea/(1000 R) = 18.04 because the gas heats during the delay",
                   0.85 * L.EA / (1000 * L.R_GAS) < b < L.EA / (1000 * L.R_GAS)))
    Td = L.design_T0(1.0e-3)
    checks.append(("design: T0 = 1011 K gives exactly a 1 ms delay",
                   abs(Td - 1011.2) < 0.2 and abs(L.ignition_delay(Td) - 1.0e-3) < 1e-9))
    checks.append(("design: 50 K cooler (961 K) more than doubles the delay (2.27 ms)",
                   abs(L.ignition_delay(Td - 50.0) * 1e3 - 2.27) < 0.01))
    checks.append(("doubling the pre-exponential factor halves the delay exactly",
                   abs(L.ignition_delay(1000.0, A=2 * L.A_PRE) / tau - 0.5) < 1e-9))
    checks.append(("a larger activation energy (all else equal) lengthens the delay",
                   L.ignition_delay(1000.0, Ea=160e3) > tau > L.ignition_delay(1000.0, Ea=140e3)))
    checks.append(("a hotter start always ignites sooner",
                   bool(np.all(np.diff([L.ignition_delay(T) for T in T0s]) < 0))))
    checks.append(("edge: with only 400 K available (rise = 400) or less there is no delay to report",
                   L.ignition_delay(1000.0, dT_ad=400.0) is None and L.ignition_delay(1000.0, dT_ad=300.0) is None))
    checks.append(("hand calculation: Frank-Kamenetskii at 1100 K is 0.2375 ms against 0.2829 ms exact (ratio 0.84)",
                   abs(L.frank_kamenetskii(1100.0) * 1e3 - 0.2375) < 0.0005 and abs(L.ignition_delay(1100.0) * 1e3 - 0.2829) < 0.0005))
    s1 = (np.log(L.ignition_delay(900.0)) - np.log(L.ignition_delay(1100.0))) / (1000 / 900.0 - 1000 / 1100.0)
    checks.append(("reading the graph: the slope between 900 K and 1100 K is 15.9", abs(s1 - 15.9) < 0.1))
    checks.append(("Ea = 140 and 160 kJ/mol give 0.387 ms and 3.69 ms at 1000 K; richer mixture (2000 K rise) gives 0.882 ms",
                   abs(L.ignition_delay(1000.0, Ea=140e3) * 1e3 - 0.387) < 0.002 and abs(L.ignition_delay(1000.0, Ea=160e3) * 1e3 - 3.687) < 0.01
                   and abs(L.ignition_delay(1000.0, dT_ad=2000.0) * 1e3 - 0.882) < 0.002))
    checks.append(("design variants for 1 ms: 992 K with a 2000 K rise, 940 K with Ea = 140, 1083 K with Ea = 160",
                   abs(L.design_T0(1e-3, dT_ad=2000.0) - 992.2) < 0.2 and abs(L.design_T0(1e-3, Ea=140e3) - 939.6) < 0.2
                   and abs(L.design_T0(1e-3, Ea=160e3) - 1083.0) < 0.2))
    checks.append(("a 10 times larger A lowers the T0 for 1 ms from 1011 K to 883 K; at 950 K the delay is 2.76 ms (A must grow 2.76 times)",
                   abs(L.design_T0(1e-3, A=10 * L.A_PRE) - 882.8) < 0.2 and abs(L.ignition_delay(950.0) * 1e3 - 2.759) < 0.002))
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
