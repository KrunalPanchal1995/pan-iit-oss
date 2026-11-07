"""Checkpoint for Session 5. Prints PASS or FAIL."""
import inspect

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    N, dr = L.N_RINGS, L.R_CANDLE / L.N_RINGS

    # ---- the forward model, checked independently --------------------------------------------------
    xg, wg = np.polynomial.legendre.leggauss(400)

    def gauss_legendre(z, y, R=6.0):  # = 2 * int_0^U eps du
        if abs(y) >= R:
            return 0.0
        U = np.sqrt(R * R - y * y)
        u = 0.5 * U * (xg + 1.0)
        return U * np.sum(wg * L.candle_emission(np.sqrt(y * y + u * u), z))

    worst = 0.0
    for z in (3, 8, 15):
        for y in (0.0, 0.37, 1.9, 4.2, 5.9, 6.2):
            a = L.photo_at(lambda r, z=z: L.candle_emission(r, z), [y])[0]
            b = gauss_legendre(z, y)
            worst = max(worst, abs(a - b) / max(abs(b), 1e-3))
    checks.append((f"photo_at (trapezoid) agrees with an independent Gauss-Legendre line integral at 18 places (largest relative difference {worst:.1e}); lines of sight beyond R see nothing",
                   worst < 1e-5))
    rng = np.random.default_rng(0)
    eps = rng.uniform(0.2, 1.0, N)
    offs = np.array([0.0, 0.4, 1.7, 3.3, 5.5])
    pred = L.ring_matrix_at(offs) @ eps
    num = L.photo_at(lambda r: eps[np.minimum((r / dr).astype(int), N - 1)], offs, n_fine=200000)
    checks.append(("ring_matrix_at (chord lengths for pixels at any offset) matches a brute-force integral of a ring-by-ring emission",
                   np.max(np.abs(pred - num) / num) < 1e-4))
    c0 = L.clean_candle_full(0.0)
    c2 = L.clean_candle_full(2.0)
    c07 = L.clean_candle_full(-0.7)
    checks.append(("a photo with the axis in the middle is its own mirror image; with the axis 2 pixels right it is mirror-symmetric about column 39 + 2",
                   np.allclose(c0, c0[:, ::-1], atol=1e-12) and np.allclose(c2[:, 42:72], c2[:, 11:41][:, ::-1], atol=1e-12)))

    # ---- what a wrong axis costs -------------------------------------------------------------------
    dmg = L.axis_damage()
    checks.append((f"noise-free, assuming the middle: error {dmg[0.0]:.3f} / {dmg[0.25]:.3f} / {dmg[0.5]:.3f} / {dmg[1.0]:.3f} / {dmg[2.0]:.3f} for an axis 0 / 0.25 / 0.5 / 1 / 2 pixels off: 1 pixel costs 0.050, 2 pixels about 0.096",
                   dmg[0.0] < 0.02 and dmg[0.25] < 0.02 and dmg[0.25] < dmg[0.5] < dmg[1.0] < dmg[2.0]
                   and abs(dmg[1.0] - 0.050) < 0.003 and dmg[2.0] > 0.09))

    # ---- finders on noise-free photos -------------------------------------------------------------
    shifts = (-2.0, -0.7, 0.0, 0.5, 1.0, 2.3)
    clean = {s: L.clean_candle_full(s) for s in shifts}
    em0 = max(abs(L.axis_mirror(clean[s]) - s) for s in shifts)
    ec0 = {s: abs(L.axis_centroid(clean[s]) - s) for s in shifts}
    checks.append((f"noise-free, mirror matching finds the axis to within 0.005 pixel at 6 positions (largest error {em0:.4f})", em0 < 0.005))
    checks.append((f"the centroid is exact when the axis sits on a column or half way between two, but biased by up to {max(ec0.values()):.3f} pixel at awkward positions (its column window is cut off-centre); mirror matching is not",
                   ec0[0.0] < 0.002 and ec0[1.0] < 0.002 and ec0[-0.7] > 0.03 and ec0[2.3] > 0.03 and max(ec0.values()) < 0.06))

    # ---- finders on noisy photos ---------------------------------------------------------------
    sd_m, sd_c, mean_m, max_m, max_c = [], [], [], [], []
    for s in (-2.0, -1.0, 0.0, 0.5, 1.0, 2.0):
        cl = L.clean_candle_full(s)
        r = np.random.default_rng(100 + int(10 * s))
        ec, em = [], []
        for _ in range(20):
            im = L.noisy(cl, 0.03, r)
            ec.append(L.axis_centroid(im) - s)
            em.append(L.axis_mirror(im) - s)
        ec, em = np.array(ec), np.array(em)
        sd_m.append(em.std())
        sd_c.append(ec.std())
        mean_m.append(abs(em.mean()))
        max_m.append(np.abs(em).max())
        max_c.append(np.abs(ec).max())
    checks.append((f"3% noise, 6 axis positions x 20 draws: mirror matching is within 0.3 pixel every time (largest error {max(max_m):.3f}), unbiased (|mean| <= {max(mean_m):.3f}) with scatter at most {max(sd_m):.3f} pixel",
                   max(max_m) < 0.15 and max(mean_m) < 0.03 and max(sd_m) < 0.06))
    checks.append((f"the centroid is also within 0.3 pixel (largest {max(max_c):.3f}) but scatters more than mirror matching at every one of the 6 positions",
                   max(max_c) < 0.3 and all(a < b for a, b in zip(sd_m, sd_c))))
    # pixel locking: interpolation without smoothing
    cl = L.clean_candle_full(0.5)
    r = np.random.default_rng(3)
    e_raw, e_blur = [], []
    for _ in range(20):
        im = L.noisy(cl, 0.03, r)
        e_raw.append(L.axis_mirror(im, blur=0.01) - 0.5)
        e_blur.append(L.axis_mirror(im) - 0.5)
    checks.append((f"without the smoothing step mirror matching scatters {np.std(e_raw):.3f} pixel (pixel locking), with it {np.std(e_blur):.3f}: at least 2.5 times better",
                   np.std(e_raw) > 2.5 * np.std(e_blur)))
    cl = L.clean_candle_full(1.0)
    r = np.random.default_rng(3)
    e_one, e_all = [], []
    for _ in range(20):
        im = L.noisy(cl, 0.03, r)
        e_one.append(L.axis_mirror(im[7]) - 1.0)
        e_all.append(L.axis_mirror(im) - 1.0)
    checks.append((f"one row alone finds the axis to only {np.std(e_one):.3f} pixel, all 20 rows together to {np.std(e_all):.3f}: the axis is a property of the whole flame, so pool the rows",
                   np.std(e_one) > 2.5 * np.std(e_all)))

    # ---- the finders look at the photo only -----------------------------------------------------------
    checks.append(("the finders take only the photo (and their settings): no shift, no truth among their inputs",
                   set(inspect.signature(L.axis_mirror).parameters) <= {"img", "blur", "search", "steps"}
                   and set(inspect.signature(L.axis_centroid).parameters) <= {"img", "window"}))

    # ---- inversion with the axis found ---------------------------------------------------------------
    cl1 = L.clean_candle_full(1.0)
    e_fix = L.worst_row_error(cl1, L.axis_mirror(cl1), both=True)
    checks.append((f"noise-free, axis 1 pixel off, inverted with the axis found and both halves: error {e_fix:.3f} (only the smoothing bias, 0.02 or less)", e_fix < 0.02))
    res = L.compare_axis_methods(1.0, 0.03, 20, seed=0)
    mid = res["assume the axis is in the middle (one half)"]
    mb = res["mirror axis, both halves"]
    mo = res["mirror axis, one half"]
    tb = res["true axis, both halves (not known in practice)"]
    cb = res["centroid axis, both halves"]
    checks.append((f"roadmap line: with the true axis 1 pixel (0.15 mm) off and 3% noise, the mean worst-row error over 20 draws is {mb.mean():.3f} (limit 0.045) after finding the axis, against {mid.mean():.3f} when the middle is assumed (at least 0.06)",
                   mb.mean() <= 0.045 and mid.mean() >= 0.06))
    checks.append((f"finding the axis costs nothing measurable: {mb.mean():.3f} against {tb.mean():.3f} for the true axis; the centroid version gives {cb.mean():.3f}",
                   mb.mean() <= 1.05 * tb.mean() and cb.mean() <= 1.1 * tb.mean()))
    checks.append((f"the roadmap line needs both halves: one half only gives {mo.mean():.3f} even with the axis found (more than 0.008 worse than both halves)",
                   mo.mean() > mb.mean() + 0.008 and mo.mean() > 0.045))
    n_mb, n_tb = int(np.sum(mb <= 0.045)), int(np.sum(tb <= 0.045))
    checks.append((f"draws at or below 0.045: {n_mb} of 20 with the axis found, {n_tb} of 20 with the true axis, only {int(np.sum(mid <= 0.045))} of 20 with the middle assumed; the noise sets the rest",
                   abs(n_mb - n_tb) <= 2 and np.sum(mid <= 0.045) <= 4))

    # ---- edge cases ---------------------------------------------------------------------------
    errs = 0
    for fn in (lambda: L.axis_centroid(np.zeros((3, 20))),
               lambda: L.mirror_cost(c0, 60.0),
               lambda: L.axis_mirror(L.clean_candle_full(5.0))):
        try:
            fn()
        except ValueError:
            errs += 1
    checks.append(("a photo with no light, an axis far outside the picture and an axis outside the search range are refused with a clear error", errs == 3))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson5", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
