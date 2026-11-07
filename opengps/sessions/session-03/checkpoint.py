"""Checkpoint for Session 3. Prints PASS or FAIL."""
import itertools

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    rec = L.receiver_on_earth(19.0, 73.0)
    sats = L.toy_sats(rec, L.GOOD_SKY)
    bias = 0.35e-3 * L.C

    # noise-free recovery of position AND clock bias
    s4 = sats[:4]
    x, b, k, hist = L.gauss_newton(s4, L.pseudoranges(s4, rec, bias))
    checks.append(("noise-free fix recovers the position to 1 mm", np.linalg.norm(x - rec) < 1e-3))
    checks.append(("noise-free fix recovers the clock bias (0.35 ms = 104.9 km) to 1 mm", abs(b - bias) < 1e-3))
    checks.append((f"Gauss-Newton converges in 8 iterations or fewer from the Earth's centre (took {k})", k <= 8))
    checks.append(("the history starts at the Earth's centre", np.allclose(hist[0], 0.0)))

    # hand calculation: clock bias in ms to distance
    checks.append(("hand calculation: 0.35 ms of clock error is 104.9 km of range", abs(bias / 1e3 - 104.93) < 0.01))

    # DOP: prediction versus simulation
    sigma = 5.0
    d4 = L.dop(s4, rec)
    d8 = L.dop(sats, rec)
    rms4 = L.monte_carlo_error(s4, rec, sigma, trials=1500)
    checks.append((f"validation: simulated rms error {rms4:.1f} m matches sigma x PDOP = {sigma * d4['PDOP']:.1f} m within 10 percent",
                   abs(rms4 / (sigma * d4["PDOP"]) - 1.0) < 0.10))
    checks.append(("more well-spread satellites lower the PDOP (8 versus 4)", d8["PDOP"] < d4["PDOP"]))
    checks.append(("PDOP is consistent with HDOP and VDOP: PDOP^2 = HDOP^2 + VDOP^2",
                   abs(d4["PDOP"] ** 2 - d4["HDOP"] ** 2 - d4["VDOP"] ** 2) < 1e-6))
    checks.append(("GDOP^2 = PDOP^2 + TDOP^2", abs(d4["GDOP"] ** 2 - d4["PDOP"] ** 2 - d4["TDOP"] ** 2) < 1e-6))
    poor = L.dop(L.toy_sats(rec, L.POOR_SKY), rec)
    checks.append((f"six satellites clustered in one patch of sky are far worse (PDOP {poor['PDOP']:.0f} above 50)", poor["PDOP"] > 50))
    pdops = []
    for c in itertools.combinations(range(8), 4):
        pdops.append((L.dop(sats[list(c)], rec)["PDOP"], c))
    best = min(pdops)
    checks.append((f"best 4 of the 8 satellites are numbers 4, 5, 6, 7 with PDOP {best[0]:.2f}", best[1] == (3, 4, 5, 6) and abs(best[0] - 2.55) < 0.01))

    # relativity: worked example
    g, m, net = L.relativity_offsets()
    gus, mus, nus = (L.microseconds_per_day(v) for v in (g, m, net))
    checks.append((f"worked example: gravity +45.7, motion -7.2, net +38.5 microseconds per day (got {gus:.1f}, {mus:.1f}, {nus:.1f})",
                   abs(gus - 45.7) < 0.05 and abs(mus + 7.2) < 0.05 and abs(nus - 38.5) < 0.05))
    checks.append(("worked example: uncorrected, that is 11.5 km of range error per day", abs(L.drift_range_km(net, 1.0) - 11.5) < 0.05))
    v2 = L.GM / L.R_ORBIT                                        # hand calculation of the motion term
    checks.append(("hand calculation: v^2 / (2 c^2) x 86400 s = 7.21 microseconds per day",
                   abs(v2 / (2 * L.C**2) * 86400e6 - 7.21) < 0.01))
    checks.append(("higher orbit means a bigger gravity gain", L.relativity_offsets(r_sat=3e7)[0] > g))

    # a common satellite clock error is absorbed by the receiver bias; an uneven one is not
    common = np.full(4, L.C * net * L.SEC_PER_DAY)
    xa, _, _, _ = L.gauss_newton(s4, L.pseudoranges(s4, rec, bias, sat_clock_err_m=common))
    one = np.array([common[0], 0.0, 0.0, 0.0])
    xb, _, _, _ = L.gauss_newton(s4, L.pseudoranges(s4, rec, bias, sat_clock_err_m=one))
    checks.append(("a clock error shared by all four satellites does not move the fix", np.linalg.norm(xa - rec) < 1e-3))
    checks.append(("the same error on one satellite moves the fix by more than 10 km", np.linalg.norm(xb - rec) > 10e3))

    # edge: zero noise and zero bias also works
    x0, b0, _, _ = L.gauss_newton(s4, L.pseudoranges(s4, rec))
    checks.append(("zero bias, zero noise: bias estimate is 0", abs(b0) < 1e-3 and np.linalg.norm(x0 - rec) < 1e-3))
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
