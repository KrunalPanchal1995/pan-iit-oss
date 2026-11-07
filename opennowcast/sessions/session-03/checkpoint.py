"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # ---- building blocks
    f = L.scene_field([(50, 50, 5.0, 22.0, 0.0, 0.0, 0.08)], 12)
    checks.append(("a cell growing 8 % per frame has 22 x 1.08^12 = 55.4 mm/h at its centre after 12 frames",
                   abs(f[50, 50] - 22.0 * 1.08 ** 12) < 1e-9 and abs(22.0 * 1.08 ** 12 - 55.4) < 0.05))
    a = np.arange(16, dtype=float).reshape(4, 4)
    xs = np.array([[1.0, 1.5, 3.0]])
    ys = np.array([[2.0, 2.0, 3.0]])
    checks.append(("sampling at whole pixels returns the pixel, at a half pixel the average",
                   np.allclose(L.sample(a, xs, ys), [[9.0, 9.5, 15.0]])))
    checks.append(("sampling far outside the picture gives zero rain", float(L.sample(a, np.array([[50.0]]), np.array([[50.0]]))[0, 0]) == 0.0))

    # ---- global versus local motion on the two-region scene
    sc = L.TWO_REGION
    f0, f1 = L.scene_field(sc, -1), L.scene_field(sc, 0)
    gu, gv = L.global_motion(f0, f1)
    checks.append(("the single global vector is a useless compromise (-0.08, 1.10) px/frame; neither region moves like that",
                   abs(gu + 0.08) < 0.05 and abs(gv - 1.10) < 0.05))
    xc, yc, U, V = L.local_vectors(f0, f1)
    west = [(1, 0), (3, 0), (1, 1), (3, 1)]
    east = [(1, 4), (3, 4)]
    okw = all(abs(U[i, j] - 2.0) < 0.1 and abs(V[i, j] - 0.5) < 0.1 for i, j in west)
    oke = all(abs(U[i, j] + 1.5) < 0.1 and abs(V[i, j] - 1.5) < 0.1 for i, j in east)
    checks.append(("local vectors recover (2.0, 0.5) in the west and (-1.5, 1.5) in the east within 0.1 px/frame", bool(okw and oke)))
    checks.append(("blocks without rain have no vector (NaN)", bool(np.isnan(U[:, 2]).all())))
    checks.append(("global motion of two identical pictures is zero", max(abs(v) for v in L.global_motion(f1, f1)) < 1e-3))
    Up, Vp = L.vector_field(xc, yc, U, V)
    checks.append(("the pixel vector field has the size of the picture", Up.shape == (100, 100) and not np.isnan(Up).any() and not np.isnan(Vp).any()))
    z = L.vector_field(*L.local_vectors(np.zeros((100, 100)), np.zeros((100, 100))))
    checks.append(("a picture without rain gives zero vectors, not a crash", float(np.abs(z[0]).max()) == 0.0 and float(np.abs(z[1]).max()) == 0.0))
    checks.append(("advecting by 0 frames changes nothing", np.allclose(L.advect(f1, Up, Vp, 0), f1)))
    checks.append(("a uniform vector field gives the same result as a plain shift",
                   np.allclose(L.advect(f1, 2.0, 0.5, 6), L.shift_field(f1, 12.0, 3.0), atol=1e-9)))

    ob30 = L.scene_field(sc, 6)
    rm = (L.rmse(f1, ob30), L.rmse(L.advect(f1, gu, gv, 6), ob30), L.rmse(L.advect(f1, Up, Vp, 6), ob30))
    checks.append(("RMSE at 30 min: persistence 7.04, global 6.33, local 0.20 mm/h",
                   abs(rm[0] - 7.04) < 0.02 and abs(rm[1] - 6.33) < 0.02 and abs(rm[2] - 0.20) < 0.02))
    cv2 = L.nowcast_curves(sc)
    checks.append(("two regions, CSI at 30 min: global 0.13, local at least 0.99 (local vectors do better)",
                   abs(cv2["global"][5] - 0.13) < 0.01 and cv2["local"][5] >= 0.99))
    checks.append(("two regions, CSI at 60 min: local 0.90, global and persistence below 0.01",
                   abs(cv2["local"][11] - 0.90) < 0.01 and cv2["global"][11] < 0.01 and cv2["persistence"][11] < 0.01))
    cv1 = L.nowcast_curves(L.ONE_REGION)
    checks.append(("one region only: a global vector is already good (CSI at 60 min at least 0.95, about as good as local)",
                   cv1["global"][11] >= 0.95 and cv1["local"][11] >= 0.95 and abs(cv1["global"][11] - cv1["local"][11]) < 0.03))

    # ---- growth and decay; skill against lead time
    cvg = L.nowcast_curves(L.GROWTH)
    loc = cvg["local"]
    checks.append(("with growth and decay the local CSI never rises with lead time and drops from 0.91 (5 min) to 0.38 (60 min)",
                   all(loc[i + 1] <= loc[i] + 1e-12 for i in range(11)) and abs(loc[0] - 0.91) < 0.01 and abs(loc[11] - 0.38) < 0.01))
    checks.append(("persistence and global CSI also never rise with lead time",
                   all(cvg[k][i + 1] <= cvg[k][i] + 1e-12 for k in ("persistence", "global") for i in range(11))))
    checks.append(("two regions without growth: CSI at 60 min is lower than at 5 min (errors in the vectors add up)", cv2["local"][11] < cv2["local"][0]))
    ob12, ob4 = L.scene_field(L.GROWTH, 12), L.scene_field(L.GROWTH, 4)
    pure12 = L.csi(L.scene_field(L.without_growth(L.GROWTH), 12), ob12)
    pure4 = L.csi(L.scene_field(L.without_growth(L.GROWTH), 4), ob4)
    checks.append(("even with the true motion, ignoring growth costs skill: CSI 0.64 at 20 min and 0.24 at 60 min",
                   abs(pure4 - 0.636) < 0.01 and abs(pure12 - 0.236) < 0.01))
    checks.append(("with no growth the true motion gives CSI 1.0 at 60 min", L.csi(L.scene_field(L.without_growth(L.GROWTH), 12), L.scene_field(L.without_growth(L.GROWTH), 12)) == 1.0))
    checks.append(("lead time where CSI first drops below 0.5: persistence 10 min, global 15 min, local 45 min",
                   L.first_below(cvg["persistence"]) == 10 and L.first_below(cvg["global"]) == 15 and L.first_below(loc) == 45))
    checks.append(("first_below returns None when the curve never falls below the level", L.first_below([0.9, 0.8, 0.7]) is None))

    # ---- disc model for skill with displacement and growth
    s, pk, g, e = 6.0, 30.0, 0.05, 0.4
    r0 = s * math.sqrt(2 * math.log(pk / L.THR))
    good = True
    for k in (4, 8, 12):
        rt = s * math.sqrt(2 * math.log(pk * (1 + g) ** k / L.THR))
        fc = L.scene_field([(40, 50, s, pk, 0, 0, 0)], 0)
        ob = L.scene_field([(40 + e * k, 50, s, pk, 0, 0, g)], k)
        good &= abs(L.csi(fc, ob) - L.disc_overlap_csi(r0, rt, e * k)) < 0.02
    checks.append(("the two-disc formula with different radii matches the grid CSI at 20, 40 and 60 min", bool(good)))
    checks.append(("two discs: equal and on top of each other give 1, far apart 0, a small disc inside a big one gives the area ratio",
                   abs(L.disc_overlap_csi(5.0, 5.0, 0.0) - 1.0) < 1e-12 and L.disc_overlap_csi(5.0, 5.0, 10.0) == 0.0
                   and abs(L.disc_overlap_csi(2.0, 4.0, 1.0) - 0.25) < 1e-12 and L.disc_overlap_csi(0.0, 4.0, 1.0) == 0.0))

    # ---- numerical diffusion: 12 small shifts versus one big shift (worked example)
    cell = L.scene_field([(20, 50, 2.5, 30.0, 0, 0, 0)])
    rep = L.advect_repeated(cell, 0.7, 0.0, 12)
    one = L.shift_field(cell, 8.4, 0.0)
    v0 = L.second_moment_x(cell)
    checks.append(("worked example: each 0.7-pixel step adds f(1-f) = 0.21 pixel^2 of blur, so 12 steps add 2.52 and one 8.4-pixel shift only 0.24",
                   abs(L.second_moment_x(rep) - v0 - 2.52) < 0.01 and abs(L.second_moment_x(one) - v0 - 0.24) < 0.01
                   and abs(12 * 0.7 * 0.3 - 2.52) < 1e-12 and abs(0.4 * 0.6 - 0.24) < 1e-12))
    checks.append(("peak of a 30 mm/h cell after 60 min: 12 small steps 24.99, one step 29.08 (rep < one < start)",
                   abs(rep.max() - 24.99) < 0.02 and abs(one.max() - 29.08) < 0.02 and rep.max() < one.max() < cell.max()))
    checks.append(("both ways conserve total rain", abs(rep.sum() / cell.sum() - 1) < 1e-9 and abs(one.sum() / cell.sum() - 1) < 1e-9))

    # ---- ensemble and reliability
    rng = np.random.default_rng(1)
    fg = L.scene_field(L.ONE_REGION, 0)
    P, Pn, O = [], [], []
    for _ in range(40):
        du, dv = rng.normal(0, 0.35, 2)
        O.append(L.shift_field(fg, (2.0 + du) * 12, (0.5 + dv) * 12) >= L.THR)
        P.append(L.exceedance_probability(fg, 2.0, 0.5, 12, 0.35, 30, rng))
        Pn.append(L.exceedance_probability(fg, 2.0, 0.5, 12, 0.05, 30, rng))
    P, Pn, O = np.array(P), np.array(Pn), np.array(O, dtype=float)
    m = (P > 0) | (Pn > 0) | (O > 0)
    det = np.broadcast_to((L.shift_field(fg, 24.0, 6.0) >= L.THR).astype(float), O.shape)
    bs_p, bs_n, bs_d = L.brier(P[m], O[m]), L.brier(Pn[m], O[m]), L.brier(det[m], O[m])
    checks.append(("Brier score (lower is better): calibrated ensemble 0.140 < over-confident 0.179 < single answer 0.199",
                   abs(bs_p - 0.140) < 0.003 and abs(bs_n - 0.179) < 0.003 and abs(bs_d - 0.199) < 0.003 and bs_p < bs_n < bs_d))

    def wgap(rel):
        tot = sum(r[2] for r in rel)
        return sum(abs(r[0] - r[1]) * r[2] for r in rel if r[2] > 0) / tot

    checks.append(("reliability: the calibrated ensemble has a count-weighted gap below 0.03, the over-confident one above 0.1",
                   wgap(L.reliability(P[m], O[m])) < 0.03 and wgap(L.reliability(Pn[m], O[m])) > 0.1))
    p0 = L.exceedance_probability(fg, 2.0, 0.5, 12, 0.0, 5, np.random.default_rng(0))
    checks.append(("with zero wind uncertainty every member agrees: probabilities are only 0 or 1",
                   bool(np.all((p0 == 0.0) | (p0 == 1.0))) and np.array_equal(p0 >= 0.5, L.shift_field(fg, 24.0, 6.0) >= L.THR)))
    checks.append(("probabilities stay between 0 and 1", float(P.min()) >= 0.0 and float(P.max()) <= 1.0))

    # ---- failure cases
    ob0 = L.scene_field(sc, 12)
    ob1 = L.with_new_storm(ob0, 6, 12)
    fc = L.advect(f1, Up, Vp, 12)
    yy, xx = np.mgrid[0:100, 0:100]
    reg = (xx - 55) ** 2 + (yy - 10) ** 2 <= 12 ** 2
    hits = int(((fc >= L.THR) & (ob1 >= L.THR) & reg).sum())
    nobs = int(((ob1 >= L.THR) & reg).sum())
    checks.append(("a storm that starts at 30 min: 0 of its 193 rainy pixels are forecast; CSI falls from 0.90 to 0.72",
                   hits == 0 and nobs == 193 and abs(L.csi(fc, ob0) - 0.896) < 0.003 and abs(L.csi(fc, ob1) - 0.724) < 0.003))
    r0f, r1f = L.rotating_scene_fields(-1), L.rotating_scene_fields(0)
    ru, rv = L.global_motion(r0f, r1f)
    rob = L.rotating_scene_fields(12)
    ru_l, rv_l = L.vector_field(*L.local_vectors(r0f, r1f))
    c_pers, c_glob, c_loc = L.csi(r1f, rob), L.csi(L.advect(r1f, ru, rv, 12), rob), L.csi(L.advect(r1f, ru_l, rv_l, 12), rob)
    checks.append(("a rotating pattern has no mean motion: global vector about 0, so global = persistence = CSI 0.07; local 0.08 (all below 0.1)",
                   abs(ru) < 1e-3 and abs(rv) < 1e-3 and abs(c_pers - 0.073) < 0.003 and abs(c_glob - c_pers) < 1e-3
                   and abs(c_loc - 0.080) < 0.003 and max(c_pers, c_glob, c_loc) < 0.1))
    checks.append(("CSI is undefined (nan) for two pictures without rain", math.isnan(L.csi(np.zeros((5, 5)), np.zeros((5, 5))))))
    mp = {t: L.nowcast_curves(L.GROWTH, t) for t in (5.0, 15.0)}
    checks.append(("mini-project: lead time below CSI 0.5 at 5 mm/h is persistence 15, global 15, local never (CSI 0.62 at 60 min)",
                   L.first_below(mp[5.0]["persistence"]) == 15 and L.first_below(mp[5.0]["global"]) == 15
                   and L.first_below(mp[5.0]["local"]) is None and abs(mp[5.0]["local"][11] - 0.62) < 0.01))
    checks.append(("mini-project: at 10 mm/h it is 10, 15 and 45 minutes; at 15 mm/h it is 10, 10 and 25 minutes",
                   L.first_below(cvg["persistence"]) == 10 and L.first_below(cvg["global"]) == 15 and L.first_below(cvg["local"]) == 45
                   and L.first_below(mp[15.0]["persistence"]) == 10 and L.first_below(mp[15.0]["global"]) == 10 and L.first_below(mp[15.0]["local"]) == 25))
    r12 = L.advect_repeated(cell, 0.5, 0.0, 12)
    checks.append(("exercise: 12 steps of 0.5 pixel add 12 x 0.25 = 3.0 pixel^2 of blur; one 6-pixel shift adds 0",
                   abs(L.second_moment_x(r12) - v0 - 3.0) < 0.01 and abs(L.second_moment_x(L.shift_field(cell, 6.0, 0.0)) - v0) < 1e-9))
    r0g = 6.0 * math.sqrt(2 * math.log(30.0 / 10.0))
    rg = 6.0 * math.sqrt(2 * (math.log(3.0) + 12 * math.log(1.05)))
    checks.append(("app: growth of 5 % per frame, error 6 km/h at 60 min gives CSI 0.43; error 3 km/h gives 0.61; growth alone 0.65",
                   abs(L.disc_overlap_csi(r0g, rg, 6.0) - 0.430) < 0.002 and abs(L.disc_overlap_csi(r0g, rg, 3.0) - 0.614) < 0.002
                   and abs(L.disc_overlap_csi(r0g, rg, 0.0) - 0.652) < 0.002 and abs(r0g - 8.89) < 0.01 and abs(rg - 11.01) < 0.01))
    top = L.reliability(P[m], O[m])[-1]
    checks.append(("roadmap: the calibrated ensemble still has a gap of 0.12 in its highest bin (more than 1000 pixels)",
                   top[2] > 1000 and abs(abs(top[0] - top[1]) - 0.117) < 0.005))
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
