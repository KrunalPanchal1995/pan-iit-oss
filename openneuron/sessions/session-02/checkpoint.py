"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("tau = R C = 100 megaohm x 100 pF = 10 ms", abs(L.tau_ms() - 10.0) < 1e-12))
    checks.append(("rheobase = 15 mV / 100 megaohm = 0.15 nA", abs(L.rheobase_nA() - 0.15) < 1e-12))
    v10 = float(L.v_subthreshold(10.0, 0.1))
    checks.append(("after one tau the voltage has covered 63.2 percent of its climb (-63.679 mV for 0.1 nA)",
                   abs(v10 - (-70 + 10 * (1 - math.exp(-1)))) < 1e-9 and abs(v10 + 63.679) < 1e-3))
    checks.append(("V(0) is the resting value", abs(float(L.v_subthreshold(0.0, 0.1)) - L.V_REST) < 1e-12))
    # the closed form really solves V(T) = V_th
    for I in (0.16, 0.2, 0.5):
        T = L.climb_time_ms(I)
        checks.append((f"derivation: V(T) equals the threshold at I = {I} nA", abs(float(L.v_subthreshold(T, I)) - L.V_TH) < 1e-9))
    checks.append(("worked example: I = 0.2 nA gives T = 10 ln 4 = 13.863 ms", abs(L.climb_time_ms(0.2) - 10 * math.log(4)) < 1e-9 and abs(L.climb_time_ms(0.2) - 13.863) < 1e-3))
    checks.append(("worked example: with t_ref = 2 ms the closed-form rate at 0.2 nA is 63.04 Hz", abs(L.rate_hz(0.2) - 63.04) < 0.01))
    checks.append(("worked example: without refractory period it is 72.13 Hz", abs(L.rate_hz(0.2, t_ref=0.0) - 72.13) < 0.01))
    t, V, sp = L.simulate_lif(0.2, 1000.0, 0.01)
    checks.append((f"validation: simulation gives {L.measured_rate(sp):.2f} Hz, within 0.1 Hz of the closed form", abs(L.measured_rate(sp) - L.rate_hz(0.2)) < 0.1))
    checks.append(("the first spike of the 0.2 nA run is at 13.87 ms", abs(sp[0] - 13.87) < 0.011))
    checks.append(("every inter-spike interval of the 0.2 nA run is 15.87 ms", bool(np.all(np.abs(np.diff(sp) - 15.87) < 0.011))))
    # below / at the rheobase
    checks.append(("no firing below the rheobase (closed form and simulation, 0.149 nA)",
                   L.rate_hz(0.149) == 0.0 and len(L.simulate_lif(0.149, 500.0, 0.01)[2]) == 0))
    checks.append(("edge case: exactly at the rheobase (0.15 nA) the neuron never fires", L.rate_hz(0.15) == 0.0 and len(L.simulate_lif(0.15, 500.0, 0.01)[2]) == 0))
    checks.append(("just above the rheobase the rate jumps: 0.16 nA gives 33.64 Hz", abs(L.rate_hz(0.16) - 33.64) < 0.01))
    f = [L.rate_hz(c) for c in np.linspace(0.151, 2.0, 200)]
    checks.append(("the f-I curve rises with current", bool(np.all(np.diff(f) > 0))))
    checks.append(("a huge current saturates near 1 / t_ref = 500 Hz", abs(L.rate_hz(1e3) - 500.0) < 0.5 and L.rate_hz(1e6) < 500.0))
    # design problem
    I20 = L.current_for_rate(20.0)
    checks.append(("worked example: 20 spikes per second needs I = 0.1512 nA", abs(I20 - 0.1512) < 1e-4))
    checks.append(("design check: that current gives 20.00 Hz in the closed form and 20 Hz (within 0.1) in simulation",
                   abs(L.rate_hz(I20) - 20.0) < 1e-9 and abs(L.measured_rate(L.simulate_lif(I20, 2000.0, 0.01)[2]) - 20.0) < 0.1))
    checks.append(("design sensitivity: 0.151 nA gives 19.17 Hz and 0.152 nA gives 22.07 Hz", abs(L.rate_hz(0.151) - 19.17) < 0.01 and abs(L.rate_hz(0.152) - 22.07) < 0.01))
    checks.append(("scaling: doubling R halves the current needed (R = 200 megaohm, C = 50 pF: 0.0756 nA)",
                   abs(L.current_for_rate(20.0, R=200.0, C=50.0) - I20 / 2) < 1e-9 and abs(L.current_for_rate(20.0, R=200.0, C=50.0) - 0.0756) < 1e-4))
    checks.append(("a rate above 1 / t_ref cannot be reached", math.isinf(L.current_for_rate(600.0)) and L.current_for_rate(100.0) > 0))
    # Euler versus exact
    e1 = np.max(np.abs(L.simulate_lif(0.1, 60.0, 1.0, method="euler")[1] - L.v_subthreshold(np.arange(61) * 1.0, 0.1)))
    e2 = np.max(np.abs(L.simulate_lif(0.1, 60.0, 0.1, method="euler")[1] - L.v_subthreshold(np.arange(601) * 0.1, 0.1)))
    checks.append((f"Euler error shrinks about 10 times when dt shrinks 10 times ({e1:.3f} mV, {e2:.4f} mV)", 8 < e1 / e2 < 12))
    ex = np.max(np.abs(L.simulate_lif(0.1, 60.0, 5.0, method="exact")[1] - L.v_subthreshold(np.arange(13) * 5.0, 0.1)))
    checks.append(("the exact step has no time-step error even for dt = 5 ms", ex < 1e-9))
    checks.append(("question B: at 0.3 nA T = 10 ln 2 = 6.931 ms and the rate is 111.96 Hz", abs(L.climb_time_ms(0.3) - 10 * math.log(2)) < 1e-9 and abs(L.rate_hz(0.3) - 111.96) < 0.01))
    checks.append(("question A: halving C (50 pF) raises the 0.3 nA rate to 182.96 Hz; doubling C (200 pF) lowers it to 63.04 Hz",
                   abs(L.rate_hz(0.3, C=50.0) - 182.96) < 0.01 and abs(L.rate_hz(0.3, C=200.0) - 63.04) < 0.01))
    checks.append(("question D: 18 spikes per second needs 0.1507 nA and 22 needs 0.1520 nA", abs(L.current_for_rate(18.0) - 0.1507) < 1e-4 and abs(L.current_for_rate(22.0) - 0.1520) < 1e-4))
    checks.append(("bench experiment: R = 10 kohm and C = 1 uF give tau = 10 ms", abs(L.tau_ms(0.01, 1e6) - 10.0) < 1e-9))
    checks.append(("exercise 3: the simulated rate at 0.2 nA is 63.01 Hz against 63.04 Hz in the closed form (the threshold is checked on a time grid)", abs(L.measured_rate(sp) - 63.01) < 0.01 and abs(L.rate_hz(0.2) - 63.04) < 0.01))
    checks.append(("question D: for 20 per second T = 48 ms and R I = 15 / (1 - exp(-4.8)) = 15.12 mV", abs(1000 / 20.0 - L.T_REF - 48.0) < 1e-12 and abs(15 / (1 - math.exp(-4.8)) - 15.12) < 0.005))
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
