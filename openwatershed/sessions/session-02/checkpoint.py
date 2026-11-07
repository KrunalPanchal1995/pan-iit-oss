"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("unit factor 3.6: C = 1, i = 1 mm/h, A = 1 km2 gives 1000 m3/h = 0.2778 m3/s",
                   abs(L.rational_peak(1.0, 1.0, 1.0) - 1000.0 / 3600.0) < 1e-12 and abs(1.0 / 3.6 - 0.2778) < 1e-4))
    checks.append(("rational peak scales linearly with C, i and A",
                   abs(L.rational_peak(0.5, 20.0, 3.0) - 2 * L.rational_peak(0.25, 20.0, 3.0)) < 1e-12
                   and abs(L.rational_peak(0.5, 40.0, 3.0) - 2 * L.rational_peak(0.5, 20.0, 3.0)) < 1e-12))
    # worked example: P = 100 mm, CN = 80
    S, Ia, Q = float(L.scs_S(80)), 0.2 * float(L.scs_S(80)), float(L.scs_runoff(100.0, 80))
    hand = (100 - 12.7) ** 2 / (100 - 12.7 + 63.5)
    checks.append((f"worked example: CN 80, P 100 mm gives S 63.5, Ia 12.7, Q 50.54 mm (got {S:.1f}, {Ia:.1f}, {Q:.2f})",
                   abs(S - 63.5) < 1e-9 and abs(Ia - 12.7) < 1e-9 and abs(Q - hand) < 1e-9 and abs(Q - 50.54) < 0.005))
    vol = Q / 1000.0 * 4.5e6
    checks.append((f"run-off volume over 4.5 km2 is about 227 thousand m3 (got {vol:,.0f})", abs(vol - 227426) < 5))
    checks.append(("no run-off for P at or below Ia (exact boundary 12.7 mm gives 0)",
                   float(L.scs_runoff(12.7, 80)) == 0.0 and float(L.scs_runoff(5.0, 80)) == 0.0 and float(L.scs_runoff(0.0, 98)) == 0.0))
    checks.append(("just above Ia the run-off is tiny but positive", 0.0 < float(L.scs_runoff(13.0, 80)) < 0.01))
    P = np.linspace(0, 300, 301)
    checks.append(("run-off grows with P (monotonic) and stays below P", bool(np.all(np.diff(L.scs_runoff(P, 80)) >= 0)
                                                                      and np.all(L.scs_runoff(P[1:], 80) < P[1:]))))
    cns = np.arange(40, 99, 2)
    checks.append(("run-off never falls as CN rises (60 mm storm; zero for very low CN)", bool(np.all(np.diff(L.scs_runoff(60.0, cns)) >= 0) and L.scs_runoff(60.0, 98) > L.scs_runoff(60.0, 60))))
    big = 1.0e6
    qb = float(L.scs_runoff(big, 80))
    checks.append(("huge storm: Q / (P - Ia) tends to 1 and the water kept after Ia tends to S = 63.5 mm",
                   abs(qb / (big - 12.7) - 1) < 1e-4 and abs((big - 12.7 - qb) - 63.5) < 0.01))
    checks.append(("CN 100 means S = 0: all rain runs off", float(L.scs_S(100)) == 0.0 and abs(float(L.scs_runoff(60.0, 100)) - 60.0) < 1e-12))
    q3 = L.scs_runoff(60.0, [60, 75, 90])
    checks.append((f"60 mm storm: CN 60, 75, 90 give 3.49, 14.52, 35.78 mm (got {q3[0]:.2f}, {q3[1]:.2f}, {q3[2]:.2f})",
                   np.allclose(q3, [3.49, 14.52, 35.78], atol=0.005)))
    tc = L.kirpich_tc_min(3200.0, 64.0 / 3200.0)
    checks.append((f"Kirpich Tc for Mango Creek is about 44.0 min (got {tc:.1f})", abs(tc - 44.0) < 0.05))
    checks.append(("doubling the slope cuts Tc by 2^-0.385 = 0.766 (about 23 percent)",
                   abs(L.kirpich_tc_min(3200.0, 0.04) / tc - 2 ** -0.385) < 1e-12 and abs(2 ** -0.385 - 0.766) < 5e-4))
    i = float(L.idf_made_up(tc))
    pk = L.rational_peak(0.45, i, 4.5)
    checks.append((f"design: i(Tc) = 33.9 mm/h and rational peak = 19.1 m3/s (got {i:.1f}, {pk:.1f})",
                   abs(i - 33.9) < 0.05 and abs(pk - 19.1) < 0.05))
    D = np.concatenate([np.linspace(5, 150, 2000), [tc]])
    q = L.peak_for_duration(0.45, D, 4.5, tc)
    checks.append(("the peak over all storm durations is largest at D = Tc", abs(D[q.argmax()] - tc) < 1e-9))
    q20, q90 = float(L.peak_for_duration(0.45, 20.0, 4.5, tc)), float(L.peak_for_duration(0.45, 90.0, 4.5, tc))
    checks.append((f"a 20 min storm gives 14.6 m3/s and a 90 min storm 10.7 m3/s, both below the Tc storm (got {q20:.1f}, {q90:.1f})",
                   abs(q20 - 14.6) < 0.05 and abs(q90 - 10.7) < 0.05 and max(q20, q90) < pk))
    tc2 = L.kirpich_tc_min(3200.0, 0.04)
    i2 = float(L.idf_made_up(tc2))
    pk2 = L.rational_peak(0.45, i2, 4.5)
    checks.append((f"straightening the channel (slope doubled): Tc 33.7 min, i 41.1 mm/h, peak 23.1 m3/s, 21 percent more (got {tc2:.1f}, {i2:.1f}, {pk2:.1f})",
                   abs(tc2 - 33.7) < 0.05 and abs(i2 - 41.1) < 0.05 and abs(pk2 - 23.1) < 0.05 and abs(pk2 / pk - 1.21) < 0.005))
    v75 = float(L.scs_runoff(60.0, 75)) * 4.5
    checks.append((f"60 mm on CN 75 over 4.5 km2 gives 65.3 thousand m3 (got {v75:.1f}); Ia is 33.9 mm for CN 60 and 5.6 mm for CN 90",
                   abs(v75 - 65.3) < 0.05 and abs(0.2 * float(L.scs_S(60)) - 33.9) < 0.05 and abs(0.2 * float(L.scs_S(90)) - 5.6) < 0.05))
    checks.append(("100 mm on CN 60 gives 18.6 mm of run-off", abs(float(L.scs_runoff(100.0, 60)) - 18.6) < 0.05))
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
