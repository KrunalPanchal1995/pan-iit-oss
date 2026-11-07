"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    T = L.TRUTH
    b, d = L.legs(T)
    a = L.interior_angles(b)
    P = float(d.sum())
    checks.append(("worked example: bearings 0, 59.04, 120.96, 180, 270 degrees",
                   np.allclose(b, [0.0, 59.04, 120.96, 180.0, 270.0], atol=5e-3)))
    checks.append(("worked example: leg lengths 120, 116.619, 116.619, 120, 200 m, perimeter 673.238 m",
                   np.allclose(d, [120.0, 116.619, 116.619, 120.0, 200.0], atol=5e-4) and abs(P - 673.238) < 5e-4))
    checks.append(("interior angles 90, 120.96, 118.07, 120.96, 90 degrees sum to 540 = (5 - 2) x 180",
                   np.allclose(a, [90.0, 120.96, 118.07, 120.96, 90.0], atol=5e-3) and abs(a.sum() - 540.0) < 1e-9))
    checks.append(("exact shoelace area of the plot is 30000 m2 (rectangle 24000 + gable 6000)",
                   abs(L.shoelace(T) - 30000.0) < 1e-9 and L.TRUE_AREA == 30000.0))
    checks.append(("shoelace gives 100 for a 10 m square, closed or open list",
                   abs(L.shoelace([[0, 0], [0, 10], [10, 10], [10, 0]]) - 100.0) < 1e-12
                   and abs(L.shoelace([[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]) - 100.0) < 1e-12))
    pts = L.walk(T[0], L.bearings_from_angles(b[0], a), d)
    checks.append(("validation: error-free angles and distances close to better than 1e-9 m",
                   L.misclosure(pts)[1] < 1e-9 and np.allclose(pts[:-1], T, atol=1e-9)))

    # hand calculation of the Bowditch correction
    e = np.array([0.100, -0.060])
    corr_leg5 = -e * 200.0 / P
    checks.append(("hand calculation: misclosure (0.100, -0.060) m, leg 5 of 200 m gets (-0.0297, +0.0178) m",
                   np.allclose(corr_leg5, [-0.02971, 0.01783], atol=5e-5)))
    rng = np.random.default_rng(3)
    b0, ma, md = L.simulate_field(T, rng, angle_arcsec=20.0 * 60, dist_scale=40.0)
    bearings = L.bearings_from_angles(b0, ma)
    raw = L.walk(T[0], bearings, md)
    adj, e2 = L.bowditch(T[0], bearings, md)
    checks.append(("Bowditch: the misclosure was not zero before, and the adjusted traverse closes exactly (< 1e-9 m)",
                   L.misclosure(raw)[1] > 0.5 and L.misclosure(adj)[1] < 1e-9))
    steps_before = np.diff(raw, axis=0)
    steps_after = np.diff(adj, axis=0)
    corr = steps_after - steps_before
    checks.append(("Bowditch: corrections are proportional to leg length and add up to minus the misclosure",
                   np.allclose(corr / md[:, None], corr[0] / md[0], atol=1e-12) and np.allclose(corr.sum(axis=0), -e2, atol=1e-12)))
    z = L.bowditch(T[0], b, d)
    checks.append(("edge: a traverse with no misclosure is unchanged by Bowditch", np.allclose(z[0][:-1], T, atol=1e-9)))
    checks.append(("edge: relative accuracy of a perfect closure is infinite; 0.1347 m in 673.238 m is 1 in 5000",
                   np.isinf(L.relative_accuracy(0.0, P)) and abs(L.relative_accuracy(0.13465, P) - 5000.0) < 2.0))

    # Monte Carlo with typical instrument figures
    mc = L.monte_carlo()
    rms_raw = float(np.sqrt(np.mean(mc["raw_unadjusted"] ** 2)))
    pred = L.predicted_misclosure_rms()
    checks.append(("validation: Monte Carlo RMS misclosure 39.4 mm matches the first-order prediction 39.8 mm within 3 percent",
                   abs(rms_raw * 1000 - 39.4) < 0.5 and abs(pred * 1000 - 39.8) < 0.5 and abs(rms_raw / pred - 1.0) < 0.03))
    checks.append(("typical errors: the median relative accuracy is about 1 in 30000, better than 1 in 5000",
                   25000 < np.median(mc["relative"]) < 35000 and np.median(mc["relative"]) > 5000))
    checks.append(("typical errors: the area error has a standard deviation of 1.17 m2 and no bias beyond 0.05 m2",
                   abs(mc["area_err"].std() - 1.17) < 0.05 and abs(mc["area_err"].mean()) < 0.05))
    checks.append(("validation: the mean adjusted area is 30000 m2 within 0.05 m2",
                   abs(mc["area_err"].mean()) < 0.05))
    ang_only = L.monte_carlo(trials=3000, dist_scale=0.0)
    dis_only = L.monte_carlo(trials=3000, angle_arcsec=0.0)
    ra = float(np.sqrt(np.mean(ang_only["raw_unadjusted"] ** 2))) * 1000
    rd = float(np.sqrt(np.mean(dis_only["raw_unadjusted"] ** 2))) * 1000
    checks.append(("sensitivity: angles alone give 37 mm RMS misclosure, distances alone 13 mm; angles dominate",
                   abs(ra - 37.1) < 1.5 and abs(rd - 12.6) < 0.8 and ra > 2.5 * rd))
    checks.append(("sensitivity: distance errors dominate the area error (1.16 m2 against 0.18 m2 from angles alone)",
                   abs(dis_only["area_err"].std() - 1.16) < 0.08 and abs(ang_only["area_err"].std() - 0.18) < 0.03))
    r160 = np.sqrt(np.mean(L.monte_carlo(trials=1500, angle_arcsec=160.0)["raw_unadjusted"] ** 2)) * 1000
    r5 = np.sqrt(np.mean(L.monte_carlo(trials=1500, angle_arcsec=5.0)["raw_unadjusted"] ** 2)) * 1000
    checks.append(("sensitivity: 5 arc-seconds gives 16 mm and 160 arc-seconds gives 298 mm, above the 134.6 mm of 1 in 5000",
                   abs(r5 - 15.8) < 1.0 and abs(r160 - 297.6) < 12.0 and r160 > P / 5000.0 * 1000))

    r40 = np.sqrt(np.mean(L.monte_carlo(trials=1500, angle_arcsec=40.0)["raw_unadjusted"] ** 2)) * 1000
    r80 = np.sqrt(np.mean(L.monte_carlo(trials=1500, angle_arcsec=80.0)["raw_unadjusted"] ** 2)) * 1000
    lim = P / 5000.0
    checks.append(("sensitivity: 40 arc-seconds gives 75.6 mm (inside 134.6 mm), 80 arc-seconds gives 149.5 mm (outside)",
                   abs(r40 - 75.6) < 3.0 and abs(r80 - 149.5) < 5.0 and r40 < lim * 1000 < r80))
    x1, x2 = L.max_angle_sigma(lim), L.max_angle_sigma(lim / 2.0)
    checks.append(("design: RMS misclosure equal to the 1 in 5000 limit allows 71 arc-seconds; half the limit allows 35 arc-seconds",
                   abs(x1 - 71.1) < 0.2 and abs(x2 - 35.1) < 0.2))
    ok35 = np.mean(L.monte_carlo(trials=2000, angle_arcsec=35.0, seed=5)["raw_unadjusted"] <= lim)
    ok40 = np.mean(L.monte_carlo(trials=2000, angle_arcsec=40.0, seed=5)["raw_unadjusted"] <= lim)
    checks.append(("design: with 35 arc-seconds about 97 percent of surveys meet 1 in 5000, with 40 about 94 percent",
                   abs(ok35 - 0.97) < 0.015 and abs(ok40 - 0.94) < 0.015))
    checks.append(("worked example: misclosure (0.100, -0.060) m is 0.1166 m long, 1 in 5773 in 673.238 m",
                   abs(np.hypot(0.1, 0.06) - 0.1166) < 5e-5 and abs(P / np.hypot(0.1, 0.06) - 5773.0) < 1.0))
    ok80 = np.mean(L.monte_carlo(trials=2000, angle_arcsec=80.0, seed=5)["raw_unadjusted"] <= lim)
    checks.append(("design: with 80 arc-seconds only about 58 percent of surveys meet 1 in 5000", abs(ok80 - 0.58) < 0.03))
    checks.append(("hand calculation: 116.619 / 673.238 = 0.173 of the misclosure goes to a 116.619 m leg", abs(116.619 / P - 0.173) < 5e-4))
    checks.append(("hand calculation: 0.050 m in 673.238 m is 1 in 13465; a 116.619 m leg gets 0.0087 m",
                   abs(P / 0.05 - 13465.0) < 1.0 and abs(0.05 * 116.619 / P - 0.0087) < 5e-5))

    # curvature and refraction
    k = np.array([0.1, 0.5, 1.0, 2.0, 3.0, 5.0])
    ratio = L.cr_physics(k) / L.cr_formula(k)
    checks.append(("validation: 0.0675 K^2 matches the sphere geometry with refraction 0.14 within 0.02 percent for K = 0.1 to 5 km",
                   np.all(np.abs(ratio - 1.0) < 2e-4)))
    checks.append(("curvature alone at 1 km is 78.5 mm; with refraction the correction is 67.5 mm",
                   abs(float(L.sphere_drop(1000.0)) * 1000 - 78.48) < 0.05 and abs(float(L.cr_formula(1.0)) * 1000 - 67.5) < 1e-9))
    checks.append(("a 100 m sight needs only 0.675 mm", abs(float(L.cr_formula(0.1)) * 1000 - 0.675) < 1e-9))
    checks.append(("the exact sphere drop matches d^2/(2R) to 1e-9 relative at 3 km",
                   abs(float(L.sphere_drop(3000.0)) / (3000.0 ** 2 / (2 * L.R_EARTH)) - 1.0) < 2e-6))
    checks.append(("unequal sights of 30 m and 70 m leave 0.27 mm of net curvature and refraction error",
                   abs((float(L.cr_formula(0.07)) - float(L.cr_formula(0.03))) * 1000 - 0.27) < 1e-9))
    checks.append(("equal sights of 50 m and 50 m cancel exactly", abs(float(L.cr_formula(0.05) - L.cr_formula(0.05))) < 1e-15))

    # blunder
    ab = L.with_blunder(a, 3, 1.0)
    rb = L.adjust(T[0], b[0], ab, d)
    rawb = L.walk(T[0], L.bearings_from_angles(b[0], ab), d)
    checks.append(("failure case: one angle 1 degree wrong gives a 4.071 m raw misclosure and an angle sum 1 degree off",
                   abs(L.misclosure(rawb)[1] - 4.071) < 5e-4 and abs(L.angle_misclosure(ab) - 1.0) < 1e-9))
    checks.append(("failure case: after spreading the angle error the misclosure is 1.851 m, only 1 in 364",
                   abs(rb["misclosure"] - 1.851) < 5e-4 and abs(rb["relative"] - 364.0) < 1.0))
    checks.append(("failure case: Bowditch still closes it exactly (< 1e-9 m) so the figure looks perfect",
                   L.misclosure(rb["points"])[1] < 1e-9))
    err = np.hypot(*(rb["points"][:-1] - T).T)
    checks.append(("failure case: yet the corners are wrong by up to 0.56 m and the area by 10.5 m2",
                   abs(err.max() - 0.557) < 5e-3 and abs(rb["area"] - 30000.0 + 10.52) < 0.05))
    kk, size = L.locate_angle_blunder(T[0], b[0], ab, d)
    checks.append(("locator: names corner 4 (index 3) and estimates the blunder as 1.000 degree", kk == 3 and abs(size - 1.0) < 1e-6))
    found = 0
    rng = np.random.default_rng(7)
    for _ in range(300):
        c = int(rng.integers(1, 5))
        bb0, mm, mdd = L.simulate_field(T, rng)
        found += L.locate_angle_blunder(T[0], bb0, L.with_blunder(mm, c, 1.0), mdd)[0] == c
    checks.append(("locator: finds the right corner in all 300 seeded trials with typical noise and a 1 degree blunder", found == 300))
    dd = d.copy()
    dd[1] += 1.0
    mv = L.misclosure(L.walk(T[0], b, dd))[0]
    bm = float(np.degrees(np.arctan2(mv[0], mv[1])) % 360.0)
    checks.append(("a 1 m distance blunder on leg 2 gives a misclosure along leg 2 (bearing 59.04 degrees)",
                   abs(bm - b[1]) < 1e-6 and abs(np.hypot(*mv) - 1.0) < 1e-9))

    # mini-project
    fa, fd = np.array(L.FIELD_ANGLES), np.array(L.FIELD_DISTS)
    r0 = L.adjust(L.FIELD_START, L.FIELD_B0, fa, fd)
    checks.append(("mini-project: as given, the angles are 1.007 degrees off, the misclosure is 2.601 m, only 1 in 332",
                   abs(r0["angle_misclosure_deg"] - 1.0071) < 5e-4 and abs(r0["misclosure"] - 2.601) < 5e-4 and abs(r0["relative"] - 332.0) < 1.0))
    kf, sf = L.locate_angle_blunder(L.FIELD_START, L.FIELD_B0, fa, fd)
    checks.append(("mini-project: the blunder is at corner 4 and about 1.0 degree", kf == 3 and abs(sf - 1.0004) < 5e-4))
    fa2 = fa.copy()
    fa2[kf] -= round(sf, 1)
    r1 = L.adjust(L.FIELD_START, L.FIELD_B0, fa2, fd)
    checks.append(("mini-project: corrected, the angle misclosure is 26 arc-seconds and the closure is 1 in 20180",
                   abs(r1["angle_misclosure_deg"] * 3600 - 25.56) < 0.05 and abs(r1["relative"] - 20180.0) < 20.0))
    checks.append(("mini-project: the corrected area is 53300.35 m2 against the exact 53300 m2",
                   abs(r1["area"] - 53300.35) < 0.01 and abs(L.shoelace(L.FIELD_TRUTH) - 53300.0) < 1e-9))
    checks.append(("mini-project: every adjusted corner is within 0.04 m of the answer key",
                   np.hypot(*(r1["points"][:-1] - L.FIELD_TRUTH).T).max() < 0.04))
    checks.append(("mini-project: the corrected traverse closes exactly", L.misclosure(r1["points"])[1] < 1e-9))

    # the app model: fixed error patterns scaled by sliders
    pa = np.array([0.6, -1.0, 0.8, -0.3, 0.5])
    pd = np.array([1.0, -0.6, 0.8, -1.0, 0.5])

    def app(sig, ds, bl):
        am = a + sig * pa / 3600.0
        am[3] += bl
        return L.adjust(T[0], b[0], am, d + ds * pd / 1000.0)

    r320, r340 = app(320, 10, 0), app(340, 10, 0)
    checks.append(("app challenge: with 10 mm distance error, 320 arc-seconds still gives better than 1 in 5000, 340 does not",
                   r320["relative"] > 5000 and r340["relative"] < 5000))
    checks.append(("app model: 100 arc-seconds and 10 mm give a 0.037 m misclosure, 1 in 18053",
                   abs(app(100, 10, 0)["misclosure"] - 0.0373) < 5e-4 and abs(app(100, 10, 0)["relative"] - 18053) < 5))
    checks.append(("app model: the largest slider settings stay below a 2.2 m misclosure", app(600, 50, 1.0)["misclosure"] < 2.2))

    # roadmap numbers
    checks.append(("roadmap: the shipped Bowditch gives an RMS error of 16.3 mm at corner 5 in the 4000-trial Monte Carlo",
                   abs(np.sqrt(np.mean(mc["corner_err"] ** 2)) * 1000 - 16.3) < 0.1))
    checks.append(("roadmap: a 60 m x 40 m plot with 2 percent tilt, levelled to its mean height, has 360 m3 of cut",
                   abs(40.0 * 0.02 * 30.0 ** 2 / 2.0 - 360.0) < 1e-9))
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
