"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # resting state
    checks.append((f"resting potential is -65.0 mV (found {L.V_REST:.3f})", abs(L.V_REST + 65.0) < 0.01))
    m0, h0, n0 = L.gate_steady(L.V_REST)
    checks.append(("gates at rest: m = 0.053, h = 0.596, n = 0.318", abs(m0 - 0.0530) < 5e-4 and abs(h0 - 0.5960) < 5e-4 and abs(n0 - 0.3177) < 5e-4))
    t, V, m, h, n = L.simulate(lambda t: 0.0, 50.0, 0.01)
    checks.append(("validation 1: with no stimulus the voltage stays at rest to 1e-3 mV for 50 ms", float(np.max(np.abs(V - L.V_REST))) < 1e-3))
    am, bm, ah, bh, an, bn = L.rates(-40.0)
    checks.append(("edge case: rate alpha_m is finite at V = -40 mV where 0/0 appears (value 1.0 per ms)", abs(am - 1.0) < 1e-6))
    checks.append(("edge case: rate alpha_n is finite at V = -55 mV (value 0.1 per ms)", abs(L.rates(-55.0)[4] - 0.1) < 1e-6))

    # one action potential
    t, V, m, h, n = L.simulate(L.pulse(10.0, 1.0, 1.0), 30.0, 0.01)
    st = L.spike_times(t, V)
    checks.append((f"worked example: a 10 uA/cm2, 1 ms pulse gives one spike peaking at 39.1 mV (got {V.max():.1f})", len(st) == 1 and abs(V.max() - 39.1) < 0.1))
    checks.append(("the spike peaks 3.5 ms after the start and undershoots to -76.2 mV (below rest, near E_K = -77)",
                   abs(t[V.argmax()] - 3.51) < 0.02 and abs(V[t > 5].min() + 76.2) < 0.1))
    checks.append(("spike width at half height is 1.45 ms at 6.3 C", abs(L.spike_width(t, V) - 1.45) < 0.02))
    checks.append(("peak stays between E_K and E_Na (the voltage cannot pass the reversal potentials)", float(V.min()) > L.E_K and float(V.max()) < L.E_NA))
    # gating variables
    ok = True
    for g in (m, h, n):
        ok &= bool(g.min() >= 0.0 and g.max() <= 1.0)
    checks.append(("conservation-like check 1: m, h, n stay inside [0, 1] during a spike", ok))
    checks.append(("m peaks at 0.994 (fast), h dips to 0.076, n reaches 0.768", abs(m.max() - 0.9937) < 5e-4 and abs(h.min() - 0.0764) < 5e-4 and abs(n.max() - 0.7681) < 5e-4))
    # numerical convergence
    t2, V2, *_ = L.simulate(L.pulse(10.0, 1.0, 1.0), 30.0, 0.005)
    checks.append(("validation 2: halving dt to 0.005 ms changes the peak by less than 0.01 mV", abs(V2.max() - V.max()) < 0.01))
    t3, V3, *_ = L.simulate(L.pulse(10.0, 1.0, 1.0), 30.0, 0.05)
    checks.append(("RK4 with dt = 0.05 ms is still within 0.2 mV on the peak", abs(V3.max() - V.max()) < 0.2))
    # charge balance
    qna, qk, ql, qs, dv = L.charge_balance()
    checks.append((f"conservation-like check 2: Na carries {qna:.0f} (inward), K {qk:.0f}, leak {ql:.0f} nC/cm2; their sum equals the 10 nC/cm2 stimulus",
                   qna < 0 < qk and abs(qna + qk + ql - qs + L.C_M * dv) < 0.05 and abs(qna + qk + ql - 10.0) < 0.1))
    checks.append(("Na inward charge is about 1427 nC/cm2, K outward 1535 nC/cm2", abs(qna + 1426.6) < 1.0 and abs(qk - 1535.5) < 1.0))
    checks.append(("after the spike the voltage is back within 0.02 mV of rest at 40 ms", abs(dv) < 0.02))

    # LIF closed form for the subthreshold response
    g0 = L.instant_conductance()
    checks.append(("instantaneous conductance at rest is 0.678 mS/cm2, so tau = C/g = 1.476 ms", abs(g0 - 0.6775) < 5e-4 and abs(L.C_M / g0 - 1.476) < 0.002))
    t4, V4, *_ = L.simulate(L.step_current(0.1, 0.0), 0.2, 0.01)
    hh, lif = V4[-1] - L.V_REST, float(L.lif_subthreshold(t4[-1:], 0.1)[0] - L.V_REST)
    checks.append((f"validation 3: after 0.2 ms the HH response ({hh:.5f} mV) matches the LIF closed form ({lif:.5f} mV) within 2 percent", abs(hh / lif - 1) < 0.02))
    t5, V5, *_ = L.simulate(L.step_current(0.1, 0.0), 1.0, 0.01)
    ratio = (V5[-1] - L.V_REST) / float(L.lif_subthreshold(t5[-1:], 0.1)[0] - L.V_REST)
    checks.append((f"by 1 ms the gates have moved and HH is {100 * (ratio - 1):.0f} percent above the LIF curve (the limit of the leaky model)", 1.09 < ratio < 1.13))

    # threshold behaviour
    thr = L.threshold_pulse(1.0)
    checks.append((f"worked example: the threshold of a 1 ms pulse is 6.92 uA/cm2 (found {thr:.2f})", abs(thr - 6.92) < 0.02))
    peaks = []
    for amp in (6.5, 7.5, 15.0, 30.0):
        tt, VV, *_ = L.simulate(L.pulse(amp, 1.0, 1.0), 20.0, 0.02)
        peaks.append(float(VV.max()))
    checks.append((f"all or nothing: 6.5 uA/cm2 peaks at {peaks[0]:.1f} mV (no spike); 7.5, 15 and 30 all peak between 36 and 42 mV",
                   abs(peaks[0] + 59.1) < 0.2 and all(36 < p < 42 for p in peaks[1:])))
    # refractory
    checks.append(("refractory: 4 ms after the first pulse no second spike is possible even with 400 uA/cm2", math.isnan(L.second_pulse_threshold(4.0))))
    s5, s10 = L.second_pulse_threshold(5.0), L.second_pulse_threshold(10.0)
    checks.append((f"relative refractory: the second pulse needs {s5:.0f} uA/cm2 at 5 ms and {s10:.1f} at 10 ms, far above the threshold 6.92",
                   abs(s5 - 275.1) < 1.0 and abs(s10 - 23.6) < 0.3 and s10 > 3 * thr))
    # repetitive firing
    onset = L.onset_current()
    checks.append((f"worked example: sustained firing starts at {onset:.2f} uA/cm2 (literature: about 6)", abs(onset - 6.27) < 0.02))
    t6, V6, *_ = L.simulate(L.step_current(5.0, 1.0), 300.0, 0.05)
    checks.append(("between the rheobase and the onset (5 uA/cm2) the cell fires exactly once and then rests", len(L.spike_times(t6, V6)) == 1 and L.firing_rate(5.0) == 0.0))
    f8, f10 = L.firing_rate(8.0), L.firing_rate(10.0)
    checks.append((f"just above onset the rate jumps to about 60 Hz (8 uA/cm2: {f8:.1f}, 10: {f10:.1f})", abs(f8 - 62.5) < 0.5 and abs(f10 - 68.3) < 0.5))
    rates = {i: L.firing_rate(float(i)) for i in range(10, 66, 5)}
    best_i = max(rates, key=rates.get)
    checks.append((f"maximum firing rate: about 126 Hz near 60 to 65 uA/cm2 (scan best {rates[best_i]:.1f} Hz at {best_i})", 122 < max(rates.values()) < 128 and best_i in (60, 65)))
    checks.append(("depolarisation block: at 66 uA/cm2 the cell stops firing repetitively", L.firing_rate(66.0) == 0.0))

    # mini-project helpers
    sd = L.strength_duration((0.2, 1.0, 50.0))
    checks.append((f"mini-project: lowest current for a long pulse (rheobase) is {sd[2][1]:.2f} uA/cm2; 1 ms needs 6.92; 0.2 ms needs 32.66",
                   abs(sd[2][1] - 2.25) < 0.02 and abs(sd[1][1] - 6.92) < 0.02 and abs(sd[0][1] - 32.66) < 0.05))
    checks.append(("mini-project: the smallest charge is for the shortest pulse (6.53 nC/cm2 at 0.2 ms, 6.92 at 1 ms, 112 at 50 ms)",
                   abs(sd[0][2] - 6.53) < 0.02 and sd[0][2] < sd[1][2] < sd[2][2] and abs(sd[2][2] - 112.3) < 0.5))
    best = L.max_rate_scan(range(55, 66))
    checks.append((f"mini-project: scanning 55 to 65 uA/cm2 the highest rate is {best[0]:.1f} Hz at {best[1]:.0f} uA/cm2", abs(best[0] - 125.87) < 0.1 and best[1] == 63.0))

    # temperature and g_Na
    thr18 = L.threshold_pulse(1.0, temp=18.5)
    tt, VV, *_ = L.simulate(L.pulse(20.0, 1.0, 1.0), 30.0, 0.01, temp=18.5)
    w18 = L.spike_width(tt, VV)
    checks.append((f"Q10: at 18.5 C the spike is {w18:.2f} ms wide (1.45 at 6.3 C) and the 1 ms threshold rises to {thr18:.2f}", abs(w18 - 0.42) < 0.02 and abs(thr18 - 8.91) < 0.03))
    r18 = L.firing_rate(20.0, temp=18.5, t_end=200.0)
    checks.append((f"Q10: at 20 uA/cm2 the rate goes from 86.5 Hz (6.3 C) to {r18:.0f} Hz (18.5 C)", abs(L.firing_rate(20.0, t_end=200.0) - 86.5) < 0.5 and abs(r18 - 254.0) < 2.0))
    checks.append(("the rate factor is 3^1.22 = 3.8 between 6.3 and 18.5 C", abs(L.Q10 ** ((18.5 - 6.3) / 10) - 3.82) < 0.01))
    th = {g: L.threshold_pulse(1.0, gna=g) for g in (120.0, 100.0, 80.0, 40.0)}
    checks.append(("g_Na sensitivity: the threshold rises as g_Na falls (120: 6.92, 100: 8.56, 80: 10.61, 40: 17.86 uA/cm2)",
                   th[120.0] < th[100.0] < th[80.0] < th[40.0] and abs(th[100.0] - 8.56) < 0.03 and abs(th[80.0] - 10.61) < 0.03 and abs(th[40.0] - 17.86) < 0.05))
    tg, Vg, *_ = L.simulate(L.pulse(30.0, 1.0, 1.0), 30.0, 0.01, gna=20.0)
    checks.append(("with g_Na = 20 mS/cm2 even a 30 uA/cm2 pulse gives no spike (peak -16.7 mV)", len(L.spike_times(tg, Vg)) == 0 and abs(Vg.max() + 16.7) < 0.3))

    # a step that is too large
    checks.append(("failure case: RK4 with dt = 0.05 ms is fine but dt = 0.1 ms blows up (voltage beyond 200 mV or gates outside 0..1)", not L.blows_up(0.05) and L.blows_up(0.1)))
    checks.append(("failure case: larger steps 0.5, 1 and 2 ms also fail", all(L.blows_up(d) for d in (0.5, 1.0, 2.0))))

    # conduction speed
    v = [10.0 * L.cable_speed(a) for a in (0.005, 0.01, 0.02)]
    checks.append((f"cable simulation: speeds {v[0]:.2f}, {v[1]:.2f}, {v[2]:.2f} m/s for radii 50, 100, 200 um (6.3 C)", abs(v[0] - 5.64) < 0.05 and abs(v[1] - 7.97) < 0.05 and abs(v[2] - 11.30) < 0.05))
    checks.append((f"scaling: doubling the radius multiplies the speed by {v[1] / v[0]:.3f} and {v[2] / v[1]:.3f}, close to sqrt 2 = 1.414", abs(v[1] / v[0] - 1.414) < 0.02 and abs(v[2] / v[1] - 1.414) < 0.02))
    checks.append(("scaling formula: 4 times the radius gives 2 times the speed", abs(L.velocity_scaling(4.0, 1.0, 5.64) - 11.28) < 1e-9))
    T = 1000.0
    ta, Va, *_ = L.simulate(lambda t: 20.0 * t / T, T, 0.05)
    sta = L.spike_times(ta, Va)
    checks.append((f"accommodation: a slow ramp 0 to 20 uA/cm2 over 1000 ms has its first spike at {20 * sta[0] / T:.2f} uA/cm2, far above the steady onset 6.27", len(sta) > 0 and abs(20 * sta[0] / T - 18.06) < 0.1))
    T2 = 2000.0
    tri = lambda t: 30.0 * t / (T2 / 2) if t < T2 / 2 else 30.0 * (T2 - t) / (T2 / 2)
    tb, Vb, *_ = L.simulate(tri, T2, 0.05)
    stb = L.spike_times(tb, Vb)
    cb = [tri(x) for x in stb]
    checks.append((f"hysteresis: on a triangle ramp 0-30-0 uA/cm2 over 2000 ms the first spike is at {cb[0]:.2f} on the way up and the last at {cb[-1]:.2f} on the way down",
                   abs(cb[0] - 19.79) < 0.3 and abs(cb[-1] - 6.88) < 0.3))
    checks.append(("charge of the 1 ms threshold pulse is 6.92 nC/cm2, which raises V by about 6.9 mV on a 1 uF/cm2 membrane", abs(thr * 1.0 / L.C_M - 6.92) < 0.02))
    hand = 0.1 / g0 * (1 - math.exp(-g0 * 0.2))
    checks.append(("question B: hand calculation (0.1 / 0.6775) x (1 - exp(-0.1355)) = 0.1476 x 0.1267 = 0.01870 mV",
                   abs(0.1 / g0 - 0.1476) < 5e-4 and abs(1 - math.exp(-g0 * 0.2) - 0.1267) < 5e-4 and abs(hand - 0.01870) < 5e-5))
    radius = 100.0 * (50.0 / v[1]) ** 2
    checks.append((f"question D: reaching 50 m/s by diameter alone needs a radius of about {radius:.0f} um (scaling from 7.97 m/s at 100 um)", abs(radius - 3936.0) < 20.0))
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
