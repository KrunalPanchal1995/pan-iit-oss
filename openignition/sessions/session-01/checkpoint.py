"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def _reference_delay(T0, dT_ad=1500.0, rise=400.0, A=2.5e9, Ea=150e3, R=8.314):
    """Independent reference: because T + dT_ad*c is constant, tau = integral of dc / (k c)."""
    x, w = np.polynomial.legendre.leggauss(100)
    cs = 1 - rise / dT_ad
    c = 0.5 * (1 - cs) * x + 0.5 * (1 + cs)
    k = A * np.exp(-Ea / (R * (T0 + dT_ad * (1 - c))))
    return 0.5 * (1 - cs) * float(np.sum(w / (k * c)))


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("hand calculation: Ea/(R T) = 18.04 and k(1000 K) = 36.5 per second",
                   abs(L.EA / (L.R_GAS * 1000.0) - 18.04) < 0.005 and abs(L.rate_const(1000.0) - 36.5) < 0.1))
    checks.append(("k(1400 K) is about 6300 per second, 170 times k(1000 K)",
                   abs(L.rate_const(1400.0) - 6330) < 30 and 170 < L.rate_const(1400.0) / L.rate_const(1000.0) < 175))
    t0, T0, c0 = L.euler_run(1000.0, 1.0e-3, 0.5e-6, heat=False)
    checks.append(("worked example: without heat feedback only 3.6 percent of the fuel is gone after 1 ms",
                   abs(c0[-1] - 0.964) < 0.001 and abs(T0[-1] - 1000.0) < 1e-9))
    t, T, c = L.euler_run(1000.0, 2.0e-3, 0.5e-6)
    tau = L.ignition_delay(t, T)
    checks.append(("worked example: with feedback the delay at 1000 K is 1.19 ms",
                   abs(tau * 1e3 - 1.19) < 0.02))
    checks.append(("Euler delay agrees with the independent reference within 1 percent",
                   abs(tau / _reference_delay(1000.0) - 1) < 0.01))
    checks.append(("energy bookkeeping: T + 1500 c stays equal to T0 + 1500",
                   np.allclose(T + L.DT_AD * c, 1000.0 + L.DT_AD, atol=1e-6)))
    i = int(round(1.0e-3 / 0.5e-6))
    j = int(round(1.3e-3 / 0.5e-6))
    checks.append(("flat then jump: T is below 1140 K at 1.0 ms and 2500 K at 1.3 ms",
                   T[i] < 1140 and abs(T[j] - 2500.0) < 1.0))
    checks.append(("at ignition 26.7 percent of the fuel is burnt (400/1500)",
                   abs((1 - c[np.argmax(T >= 1400.0)]) - 0.267) < 0.01))
    d = [L.euler_delay(x) for x in (850.0, 1000.0, 1150.0)]
    checks.append(("a hotter start ignites sooner, and 850 K waits over 100 times longer than 1150 K",
                   d[0] > d[1] > d[2] and d[0] / d[2] > 100))
    checks.append(("edge: if burning everything gives only 300 K, there is no ignition",
                   L.euler_delay(1000.0, 300.0) is None))
    checks.append(("k(1100 K) = 188 per second, 5.2 times k(1000 K); burning 10 percent of the fuel adds 150 K",
                   abs(L.rate_const(1100.0) - 188.27) < 0.1 and abs(L.rate_const(1100.0) / L.rate_const(1000.0) - 5.156) < 0.01
                   and abs(0.1 * L.DT_AD - 150.0) < 1e-9))
    checks.append(("the curve: T is 1134 K at 1.0 ms and 1458 K at 1.2 ms",
                   abs(T[i] - 1133.7) < 1.0 and abs(T[int(round(1.2e-3 / 0.5e-6))] - 1458.5) < 2.0))
    checks.append(("delays: 900 K gives 7.06 ms and 1100 K gives 0.284 ms; 1000 K to 1050 K cuts the delay by a factor of 2.1",
                   abs(L.euler_delay(900.0) * 1e3 - 7.062) < 0.02 and abs(L.euler_delay(1100.0) * 1e3 - 0.2843) < 0.002
                   and abs(L.euler_delay(1000.0) / L.euler_delay(1050.0) - 2.126) < 0.01))
    checks.append(("design: 1050 K is too slow for 0.5 ms (0.562 ms), 1060 K passes (0.488 ms); a 2000 K rise passes at 1050 K (0.416 ms)",
                   L.euler_delay(1050.0) > 0.5e-3 > L.euler_delay(1060.0) and abs(L.euler_delay(1060.0) * 1e3 - 0.488) < 0.002
                   and abs(L.euler_delay(1050.0, 2000.0) * 1e3 - 0.416) < 0.002))
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
