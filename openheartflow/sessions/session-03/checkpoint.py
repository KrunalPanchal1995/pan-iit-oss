"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R, C = 1.214, 1.251
    n = L.N_STEPS
    period = 60.0 / L.HR0
    ts = L.SYSTOLE_FRACTION * period
    t, P = L.last_beat(R, C)
    s, d, pp, m = L.bp_stats(P)

    # --- the inflow
    dt = 1e-4
    tt = np.arange(0.0, period, dt)
    q = np.array([L.inflow(x) for x in tt])
    checks.append(("one beat delivers the stroke volume 70 mL", abs(q.sum() * dt - 70.0) < 0.01))
    checks.append(("the inflow is zero in diastole and peaks at 427.6 mL/s",
                   float(q[tt > ts + 1e-9].max()) == 0.0 and abs(q.max() - 427.6) < 0.1))
    checks.append(("mean inflow is 81.67 mL/s (4.9 L/min)", abs(L.mean_inflow() - 81.667) < 1e-3))

    # --- worked example (Section E)
    rc = R * C
    checks.append(("worked example: time constant R C = 1.519 s", abs(rc - 1.5187) < 1e-3))
    factor = np.exp(-(period - ts) / rc)
    checks.append(("worked example: diastole lasts 0.600 s and the pressure falls by a factor 0.674",
                   abs((period - ts) - 0.6) < 1e-12 and abs(factor - 0.6736) < 1e-4))
    p_ts = P[int(round(L.SYSTOLE_FRACTION * n))]
    checks.append(("worked example: pressure 119.3 at the end of ejection becomes 80.4 at the end of the beat",
                   abs(p_ts - 119.29) < 0.02 and abs(p_ts * factor - 80.36) < 0.02 and abs(P[-1] - 80.36) < 0.02))
    checks.append(("worked example: R x mean flow = 1.214 x 81.67 = 99.1 mmHg equals the mean pressure",
                   abs(R * L.mean_inflow() - 99.15) < 0.01 and abs(m - 99.14) < 0.02))

    # --- the target waveform (mini-project values)
    checks.append(("R = 1.214 and C = 1.251 give systolic 120 and diastolic 80 within 0.1 mmHg",
                   abs(s - 120.0) < 0.1 and abs(d - 80.0) < 0.1))
    checks.append(("pulse pressure is 40 mmHg for the tuned model", abs(pp - 40.0) < 0.2))
    checks.append(("the minimum comes just after the next ejection starts, so it is below the end-of-beat value by 0.3",
                   abs(P[-1] - d - 0.33) < 0.05 and int(np.argmin(P[:-1])) < 10))
    checks.append(("the untuned guess R = 1.143, C = 1.0 misses the target (diastolic below 71)",
                   L.bp_stats(L.last_beat(1.143, 1.0)[1])[1] < 71.0))

    # --- validation 1: exact decay in diastole
    i0 = int(round(L.SYSTOLE_FRACTION * n))
    exact = L.diastolic_decay(P[i0], R, C, t[i0:] - ts)
    checks.append(("RK4 matches the exact diastolic decay to 1e-6 mmHg", float(np.abs(P[i0:] - exact).max()) < 1e-6))

    # --- validation 2: mean-flow balance for several (R, C, HR)
    ok = True
    for r_, c_, h_ in ((0.8, 0.5, 70), (1.6, 2.0, 70), (1.214, 1.251, 100)):
        _, Pb = L.last_beat(r_, c_, hr=h_)
        ok &= abs(L.bp_stats(Pb)[3] - r_ * L.mean_inflow(h_)) < 0.05
    checks.append(("mean P = R x mean Q for three different (R, C, heart rate) settings", bool(ok)))

    # --- order of the method: halving dt cuts the error by about 16
    _, Pr = L.last_beat(R, C, n=1200)
    errs = [float(np.abs(L.last_beat(R, C, n=k)[1] - Pr[::1200 // k]).max()) for k in (60, 120)]
    checks.append(("RK4 is fourth order: halving the step cuts the error by about 16",
                   12.0 < errs[0] / errs[1] < 20.0))

    # --- stiffer arteries
    stats = {c_: L.bp_stats(L.last_beat(R, c_)[1]) for c_ in (2.5, 1.251, 0.626)}
    checks.append(("stiffer arteries (smaller C) give a larger pulse pressure: 20.1, 40.0, 78.9 mmHg",
                   abs(stats[2.5][2] - 20.1) < 0.2 and abs(stats[1.251][2] - 40.0) < 0.2 and abs(stats[0.626][2] - 78.9) < 0.3))
    checks.append(("the mean pressure stays 99.1 mmHg whatever C is",
                   all(abs(v[3] - 99.14) < 0.03 for v in stats.values())))
    checks.append(("halving C gives 142.1 / 63.2 mmHg", abs(stats[0.626][0] - 142.1) < 0.2 and abs(stats[0.626][1] - 63.2) < 0.2))

    # --- heart rate and sensitivity
    h60 = L.bp_stats(L.last_beat(R, C, hr=60)[1])
    h90 = L.bp_stats(L.last_beat(R, C, hr=90)[1])
    checks.append(("heart rate 60 gives 106/66 (mean 85.0); 90 gives 148/108 (mean 127.5) at fixed stroke volume",
                   abs(h60[0] - 106.0) < 0.3 and abs(h60[1] - 66.0) < 0.3 and abs(h60[3] - 85.0) < 0.1
                   and abs(h90[0] - 148.2) < 0.3 and abs(h90[1] - 108.1) < 0.3 and abs(h90[3] - 127.5) < 0.1))
    base = L.bp_stats(L.last_beat(R, C)[1])
    rp = L.bp_stats(L.last_beat(R * 1.1, C)[1])
    cp = L.bp_stats(L.last_beat(R, C * 1.1)[1])
    sp = L.bp_stats(L.last_beat(R, C, sv=77.0)[1])
    checks.append(("sensitivity: R +10% raises the mean 10% (109.1) and leaves the pulse near 40",
                   abs(rp[3] / base[3] - 1.1) < 1e-3 and abs(rp[2] - 40.0) < 0.2))
    checks.append(("sensitivity: C +10% lowers the pulse pressure to 36.4 and leaves the mean",
                   abs(cp[2] - 36.4) < 0.1 and abs(cp[3] - base[3]) < 0.02))
    checks.append(("sensitivity: stroke volume +10% raises the pulse pressure to 44.0 and the mean to 109.1",
                   abs(sp[2] - 44.0) < 0.2 and abs(sp[3] - 109.06) < 0.1))

    # --- failure case and edge cases
    tiny = L.bp_stats(L.last_beat(R, 0.05)[1])
    checks.append(("failure case: C = 0.05 gives an unphysical pulse pressure of 430 mmHg and a fall to 0",
                   abs(tiny[2] - 430.0) < 1.0 and tiny[1] < 0.1))
    checks.append(("failure case: the mean is still 99.1, so the mean alone cannot reveal the failure",
                   abs(tiny[3] - 99.14) < 0.05))
    bad = 0
    for args in ((0.0, 1.0), (1.0, 0.0), (-1.0, 1.0)):
        try:
            L.windkessel(*args)
        except ValueError:
            bad += 1
    checks.append(("non-positive R or C is rejected", bad == 3))
    checks.append(("with no inflow (sv = 0) the pressure follows the exact decay 100 exp(-t/(R C))",
                   abs(float(L.windkessel(R, C, sv=0.0, beats=2, p0=100.0)[1][-1]) - 100.0 * np.exp(-2 * period / (R * C))) < 1e-6))

    # --- numbers used in the text
    checks.append(("worked example: beat 0.857 s, systole 0.257 s, diastole 0.600 s",
                   abs(period - 0.8571) < 1e-4 and abs(ts - 0.2571) < 1e-4))
    checks.append(("halving C multiplies the pulse pressure by 1.97", abs(stats[0.626][2] / stats[1.251][2] - 1.973) < 0.01))
    checks.append(("rule of thumb for 120/80 is 93.3 but the model's own mean is 99.1", abs(80 + 40 / 3 - 93.33) < 0.01 and abs(m - 99.14) < 0.02))
    r90 = 90.0 / L.mean_inflow()
    d90 = L.bp_stats(L.last_beat(r90, 1.7)[1])
    checks.append(("design: R = 1.102 and C = 1.7 give 105.3 / 75.8, pulse 29.5, mean 90.0",
                   abs(r90 - 1.102) < 1e-3 and abs(d90[0] - 105.27) < 0.1 and abs(d90[1] - 75.78) < 0.1 and abs(d90[2] - 29.49) < 0.1 and abs(d90[3] - 90.0) < 0.05))
    checks.append(("mean P at 60 beats/min is 85.0 from the balance 1.214 x 70", abs(1.214 * L.mean_inflow(60.0) - 84.98) < 0.01))
    checks.append(("in the first 0.02 s of ejection the two-element model's pressure falls by 0.2 mmHg", abs(P[7] - P[0] + 0.224) < 0.01 and abs(t[7] - 0.02) < 1e-9))
    pa = L.bp_stats(L.last_beat(1.592, C)[1])[2]
    pb = L.bp_stats(L.last_beat(1.102, C)[1])[2]
    checks.append(("a constant C gives the same pulse pressure at mean 130 and mean 90 (ratio 1.00)", abs(pa / pb - 1.0) < 0.01))
    hi = L.bp_stats(L.last_beat(R, C, sv=84.0)[1])[3]
    checks.append(("stroke volume +20% moves the mean by about 20 mmHg", abs(hi - base[3] - 19.8) < 0.3))
    pe = 80.0
    for _ in range(1000):
        pe += 0.001 * (0.0 - pe / 1.2) / 1.25
    checks.append(("snippet: Euler gives 41.1 and the exact decay gives 41.1", round(pe, 1) == 41.1 and round(80 * np.exp(-1.0 / 1.5), 1) == 41.1))
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
