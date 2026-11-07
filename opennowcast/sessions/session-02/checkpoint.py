"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    cell = L.make_field([(50, 50, 3.0, 30.0)])
    checks.append(("a cell has its peak (30 mm/h) at its centre pixel", abs(cell[50, 50] - 30.0) < 1e-9 and cell.shape == (100, 100)))

    # ---- shifting
    si = L.shift_int(cell, 5, -3)
    checks.append(("integer shift moves the peak to pixel (x=55, y=47) and keeps the peak value",
                   abs(si[47, 55] - 30.0) < 1e-9 and abs(si.max() - 30.0) < 1e-9))
    checks.append(("rain pushed off the picture is lost by an integer shift", L.shift_int(cell, 100, 0).sum() == 0.0 and L.shift_int(cell, 60, 0).sum() < 0.01 * cell.sum()))
    checks.append(("a bilinear shift by whole pixels equals the integer shift",
                   np.allclose(L.shift_bilinear(cell, 5.0, -3.0), si, atol=1e-12)))
    half = L.shift_bilinear(cell, 0.5, 0.0)
    checks.append(("interpolation conserves total rain (shift by 5.5 pixels)",
                   abs(L.shift_bilinear(cell, 5.5, 0.0).sum() / cell.sum() - 1.0) < 1e-12))
    checks.append(("a half-pixel shift keeps 0.973 of the peak of a sigma = 3 cell (smoothing)",
                   abs(half.max() / cell.max() - 0.973) < 0.001))
    gain = L.x_variance(half) - L.x_variance(cell)
    checks.append(("hand calculation: the added blur is f(1-f) = 0.25 pixel^2 for f = 0.5",
                   abs(gain - 0.25) < 1e-3))
    g25 = L.x_variance(L.shift_bilinear(cell, 0.25, 0.0)) - L.x_variance(cell)
    checks.append(("the blur at f = 0.25 is 0.1875 and at f = 0.75 is the same", abs(g25 - 0.1875) < 1e-3
                   and abs(L.x_variance(L.shift_bilinear(cell, 0.75, 0.0)) - L.x_variance(cell) - 0.1875) < 1e-3))
    checks.append(("a shift of 0 changes nothing", np.allclose(L.shift_bilinear(cell, 0.0, 0.0), cell, atol=1e-12)))

    # ---- motion estimation
    f0 = L.make_field(L.CELLS)
    f1 = L.shift_bilinear(f0, *L.TRUE_SHIFT)
    ex, ey = L.estimate_shift(f0, f1)
    checks.append(("known shift (2.4, 1.3) pixels per frame is recovered within 0.1 pixel",
                   abs(ex - 2.4) < 0.1 and abs(ey - 1.3) < 0.1))
    rng = np.random.default_rng(7)
    ok = True
    for tr in [(2.4, 1.3), (-1.7, 0.6), (0.35, -2.85)]:
        a = np.clip(f0 + rng.normal(0, 0.5, f0.shape), 0, None)
        b = np.clip(L.shift_bilinear(f0, *tr) + rng.normal(0, 0.5, f0.shape), 0, None)
        sx, sy = L.estimate_shift(a, b)
        ok &= abs(sx - tr[0]) < 0.1 and abs(sy - tr[1]) < 0.1
    checks.append(("shifts recovered within 0.1 pixel even with 0.5 mm/h seeded noise on both frames", bool(ok)))
    px, py = L.xcorr_peak(f0, f1)
    checks.append(("the FFT cross-correlation peak gives the whole-pixel part (2, 1)", (px, py) == (2, 1)))

    # ---- worked example: unit conversion and CSI from counts
    u, v = ex * 12.0, ey * 12.0
    checks.append(("worked example: (2.4, 1.3) px per 5 min is (28.8, 15.6) km/h, speed 32.76 km/h",
                   abs(u - 28.8) < 1.2 and abs(v - 15.6) < 1.2 and abs(np.hypot(28.8, 15.6) - 32.76) < 0.01))
    checks.append(("worked example: in 60 minutes the field moves (28.8, 15.6) km", abs(2.4 * 12 - 28.8) < 1e-9 and abs(1.3 * 12 - 15.6) < 1e-9))
    checks.append(("worked example: 80 hits, 10 misses, 10 false alarms give CSI 0.8", abs(L.csi_counts(80, 10, 10) - 0.8) < 1e-12))

    # ---- scores on the 60-minute forecast
    obs = L.make_field(L.moved_cells(L.CELLS, *L.TRUE_SHIFT, 12))
    pers, adv = f0, L.advect_forecast(f0, ex, ey, 12)
    checks.append(("60 min persistence: RMSE 5.83 mm/h, CSI 0.074",
                   abs(L.rmse(pers, obs) - 5.83) < 0.01 and abs(L.csi(pers, obs) - 0.074) < 0.002))
    checks.append(("60 min advection: RMSE 0.03 mm/h, CSI 0.996",
                   abs(L.rmse(adv, obs) - 0.03) < 0.01 and abs(L.csi(adv, obs) - 0.996) < 0.002))
    beats = True
    for k in range(1, 13):
        ob = L.make_field(L.moved_cells(L.CELLS, *L.TRUE_SHIFT, k))
        a = L.advect_forecast(f0, ex, ey, k)
        beats &= L.csi(a, ob) > L.csi(f0, ob) and L.rmse(a, ob) < L.rmse(f0, ob)
    checks.append(("advection beats persistence in CSI and RMSE at every lead from 5 to 60 minutes", bool(beats)))
    checks.append(("a perfect forecast scores CSI 1, RMSE 0, FSS 1", L.csi(obs, obs) == 1.0 and L.rmse(obs, obs) == 0.0 and abs(L.fss(obs, obs, n=5) - 1.0) < 1e-12))
    checks.append(("CSI counts a pixel exactly at the threshold as rain", L.csi(np.array([[5.0]]), np.array([[5.0]])) == 1.0))
    checks.append(("no rain in either picture: CSI and FSS are undefined (nan), not 1 or a crash",
                   np.isnan(L.csi(np.zeros((4, 4)), np.zeros((4, 4)))) and np.isnan(L.fss(np.zeros((4, 4)), np.zeros((4, 4)), n=3))))

    # ---- FSS forgives displacement; box_mean is right
    o = L.make_field(L.CELLS)
    f = L.shift_int(o, 3, 0)
    fs = [L.fss(f, o, n=n) for n in (1, 7, 31)]
    checks.append(("a forecast displaced by 3 pixels: CSI 0.677, FSS 0.807 (n=1), 0.929 (n=7), 0.987 (n=31)",
                   abs(L.csi(f, o) - 0.677) < 0.002 and abs(fs[0] - 0.807) < 0.002 and abs(fs[1] - 0.929) < 0.002 and abs(fs[2] - 0.987) < 0.002))
    checks.append(("FSS grows with the window size", fs[0] < fs[1] < fs[2]))
    a = np.arange(25, dtype=float).reshape(5, 5)
    bm = L.box_mean(a, 3)
    pad = np.pad(a, 1)
    checks.append(("box_mean equals a direct 3 x 3 average with zeros outside",
                   all(abs(bm[i, j] - pad[i:i + 3, j:j + 3].mean()) < 1e-9 for i in range(5) for j in range(5))))

    # ---- two-disc model
    r = L.edge_radius(5.0, 30.0)
    checks.append(("a sigma = 5, 30 mm/h cell has a 5 mm/h edge at 9.47 km", abs(r - 9.465) < 0.001))
    c0 = L.make_field([(40, 50, 5.0, 30.0)])
    good = True
    for d in (0, 2, 5, 9):
        good &= abs(L.csi(L.make_field([(40 + d, 50, 5.0, 30.0)]), c0) - L.disc_csi(r, d)) < 0.02
    checks.append(("the two-disc formula matches the grid CSI for displacements of 0, 2, 5 and 9 pixels", bool(good)))
    checks.append(("two discs: CSI 1 at d = 0, 0 at d = 2r, 0.50 at d = 5 km for r = 9.47 km",
                   L.disc_csi(r, 0.0) == 1.0 and L.disc_csi(r, 2 * r) == 0.0 and abs(L.disc_csi(r, 5.0) - 0.501) < 0.002))
    checks.append(("a cell weaker than the threshold has radius 0", L.edge_radius(5.0, 4.0) == 0.0))
    checks.append(("exercise: (1.5, 0.5) pixels per 5 min is (18, 6) km/h, speed 18.97 km/h",
                   abs(1.5 * 12 - 18.0) < 1e-9 and abs(0.5 * 12 - 6.0) < 1e-9 and abs(np.hypot(18.0, 6.0) - 18.97) < 0.01))
    checks.append(("two discs: only the ratio d/r matters (doubling both leaves CSI unchanged)", abs(L.disc_csi(2 * r, 10.0) - L.disc_csi(r, 5.0)) < 1e-12))
    checks.append(("design: wind error 5 km/h over 60 min is 5 km (CSI 0.50); over 30 min 10 km/h is also 5 km",
                   abs(5.0 * 60 / 60 - 5.0) < 1e-12 and abs(10.0 * 30 / 60 - 5.0) < 1e-12))
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
