"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # ---- homography
    H0 = np.array([[1.0, 0.2, 10.0], [0.0, 1.0, 5.0], [0.001, 0.0, 1.0]])
    q = L.apply_h(H0, [[100.0, 50.0]])[0]
    checks.append((f"worked example: H sends (100, 50) to (109.09, 50.00) (got {q[0]:.2f}, {q[1]:.2f})",
                   abs(q[0] - 120.0 / 1.1) < 1e-9 and abs(q[1] - 50.0) < 1e-9))
    back = L.apply_h(np.linalg.inv(H0), q[None, :])[0]
    checks.append(("the inverse of H sends it back to (100, 50)", np.allclose(back, [100.0, 50.0], atol=1e-9)))
    src = np.array([[0.0, 0.0], [200.0, 0.0], [200.0, 150.0], [0.0, 150.0]])
    dst = L.apply_h(H0, src)
    H1 = L.homography_from_points(src, dst)
    checks.append(("solving the 8 x 8 system from 4 pairs recovers a known H", np.allclose(H1, H0, atol=1e-8)))
    checks.append(("four identical point pairs give the identity", np.allclose(L.homography_from_points(src, src), np.eye(3), atol=1e-9)))
    try:
        L.homography_from_points([[0, 0], [1, 1], [2, 2], [5, 0]], src)
        raised = False
    except ValueError:
        raised = True
    checks.append(("edge: three points on a line are reported as degenerate, not solved", raised))

    # ---- warping and sampling
    img = np.arange(30.0).reshape(5, 6)
    checks.append(("bilinear at a pixel centre returns that pixel", abs(L.bilinear(img, 2.0, 3.0) - img[3, 2]) < 1e-12))
    checks.append(("bilinear halfway between two pixels is their average", abs(L.bilinear(img, 2.5, 3.0) - 0.5 * (img[3, 2] + img[3, 3])) < 1e-12))
    checks.append(("edge: the last pixel column is inside, one step further is NaN",
                   abs(L.bilinear(img, 5.0, 4.0) - img[4, 5]) < 1e-12 and bool(np.isnan(L.bilinear(img, 5.01, 4.0)))))
    sp = L.speckle_image(40, 50, seed=3)
    shifted = L.warp_image(sp, np.array([[1.0, 0, 2.0], [0, 1.0, 0], [0, 0, 1.0]]), sp.shape)
    checks.append(("warping by a 2 pixel translation moves the image exactly", np.allclose(shifted[:, 2:], sp[:, :-2], atol=1e-9) and bool(np.isnan(shifted[0, 0]))))
    quad = np.array([[10.0, 8.0], [60.0, 14.0], [64.0, 50.0], [6.0, 46.0]])
    grid = np.array([[0.0, 0.0], [49.0, 0.0], [49.0, 39.0], [0.0, 39.0]])
    Hq = L.homography_from_points(quad, grid)
    checks.append(("the four quad corners land on the four grid corners", np.allclose(L.apply_h(Hq, quad), grid, atol=1e-8)))
    checks.append(("the speckle pattern has standard deviation about 1 (0.9 to 1.1)", 0.9 < float(L.speckle_image(120, 120).std()) < 1.1))

    # ---- aspect ratio
    c = L.aspect_costs(1280, 720, 640, 480)
    checks.append((f"worked example: 16:9 into 4:3 costs 25 percent (letterbox, crop) or a 1.333 stretch (got {c['letterbox_empty']:.3f}, {c['crop_lost']:.3f}, {c['stretch_ratio']:.3f})",
                   abs(c["letterbox_empty"] - 0.25) < 1e-12 and abs(c["crop_lost"] - 0.25) < 1e-12 and abs(c["stretch_ratio"] - 4 / 3) < 1e-12))
    checks.append(("hand calculation: letterboxing 1280 x 720 into 640 x 480 leaves bars of 0.25 * 480 / 2 = 60 px top and bottom", abs(c["letterbox_empty"] * 480 / 2 - 60) < 1e-9))
    c2 = L.aspect_costs(640, 480, 640, 480)
    checks.append(("edge: equal aspect ratios cost nothing", c2["letterbox_empty"] == 0 and c2["stretch_ratio"] == 1))
    c3 = L.aspect_costs(480, 640, 640, 480)
    checks.append(("a portrait source into a landscape grid also costs 1 - (3/4)/(4/3) = 43.75 percent", abs(c3["letterbox_empty"] - (1 - (3 / 4) / (4 / 3))) < 1e-12))

    # ---- resampling blur
    r5 = L.shift_std_ratio(0.5)
    checks.append((f"half-pixel bilinear shift keeps 0.7071 of the contrast on white noise (got {r5:.3f})", abs(r5 - np.sqrt(0.5)) < 0.01))
    checks.append(("a whole-pixel shift keeps all of it", abs(L.shift_std_ratio(0.0) - 1.0) < 1e-9))
    e = {s: L.resample_roundtrip_error(s)[0] for s in (0.5, 0.75, 0.9, 1.0, 2.0)}
    checks.append((f"scale 1.0 round trip is perfect and scale 0.5 loses about 0.30 of the pattern (got {e[0.5]:.3f})", e[1.0] < 1e-9 and abs(e[0.5] - 0.305) < 0.02))
    checks.append(("the smaller the image gets, the bigger the round-trip error (0.9 < 0.75 < 0.5)", e[0.9] < e[0.75] < e[0.5]))

    # ---- Makima: exactness, continuity, locality
    x = np.arange(11.0)
    xq = np.linspace(0, 10, 1001)
    ln = lambda v: 3 * v - 2
    checks.append(("Makima reproduces a straight line exactly (equal spacing)", np.max(np.abs(L.makima(x, ln(x), xq) - ln(xq))) < 1e-10))
    xn = np.array([0, 1.0, 2.5, 3, 4.6, 6, 7, 8.2, 9, 10])
    checks.append(("Makima reproduces a straight line exactly (uneven spacing)", np.max(np.abs(L.makima(xn, 2 * xn + 1, xq) - (2 * xq + 1))) < 1e-10))
    qd = lambda v: v ** 2
    em = float(np.max(np.abs(L.makima(x, qd(x), xq) - qd(xq))))
    es = float(np.max(np.abs(L.spline(x, qd(x), xq) - qd(xq))))
    ea = float(np.max(np.abs(L.akima(x, qd(x), xq) - qd(xq))))
    checks.append((f"spline and Akima reproduce x^2 exactly but Makima does not: its error is 2/27 = 0.074 (got {em:.4f})",
                   es < 1e-9 and ea < 1e-9 and abs(em - 2 / 27) < 1e-3))
    y = np.sin(x)
    jumps1 = [abs(L.makima(x, y, x[i] - 1e-7, 1) - L.makima(x, y, x[i] + 1e-7, 1)) for i in range(1, 10)]
    jumps2 = [abs(L.makima(x, y, x[i] - 1e-7, 2) - L.makima(x, y, x[i] + 1e-7, 2)) for i in range(1, 10)]
    checks.append(("Makima is C1: the slope has no jump at any knot (below 1e-5)", max(jumps1) < 1e-5))
    checks.append(("Makima is not C2: the curvature jumps at some knot (above 0.1)", max(jumps2) > 0.1))
    checks.append(("Makima passes through every sample", np.allclose(L.makima(x, y, x), y, atol=1e-12)))
    y2 = y.copy()
    y2[0] += 1.0
    cm = np.abs(L.makima(x, y, xq) - L.makima(x, y2, xq)) > 1e-12
    cs = np.abs(L.spline(x, y, xq) - L.spline(x, y2, xq)) > 1e-12
    checks.append(("Makima is local: changing the first sample changes nothing beyond x = 3; the spline changes up to x = 10",
                   xq[cm].max() <= 3.0 + 1e-9 and xq[cs].max() > 9.9))
    checks.append(("edge: flat data give zero slopes, not 0/0", np.allclose(L.akima_slopes(np.arange(5.0), np.ones(5)), 0.0)))
    checks.append(("edge: two samples give a straight line", abs(float(L.makima(np.array([0.0, 1.0]), np.array([0.0, 2.0]), 0.5)) - 1.0) < 1e-12))
    checks.append(("edge: outside the sampled range the answer is NaN unless extrapolation is asked for",
                   bool(np.isnan(L.makima(x, y, 10.5))) and bool(np.isfinite(L.makima(x, y, 10.5, extrapolate=True)))))
    dips = {m: L.corner_dip(m) for m in ("linear", "spline", "akima", "makima")}
    checks.append((f"hand calculation: Akima dips to -0.0741 where a flat run meets a ramp, Makima stays at 0 (got {dips['akima']:.4f}, {dips['makima']:.4f})",
                   abs(dips["akima"] + 0.0741) < 1e-3 and dips["makima"] > -1e-12))
    checks.append((f"the spline dips further to -0.103 (got {dips['spline']:.4f})", abs(dips["spline"] + 0.1026) < 1e-3))

    # ---- time base
    tl = L.timeline(120, 2.0)
    tA, tB = np.arange(61) / 30.0, np.arange(49) / 24.0
    checks.append(("120 fps is a multiple of 30 and 24: every real sample lies on a timeline tick",
                   np.allclose(tl[::4], tA) and np.allclose(tl[::5], tB)))
    sm = {m: L.rms_vs_truth(L.smooth_motion, m, 24) for m in ("linear", "spline", "makima")}
    checks.append((f"smooth motion at 24 fps: spline {sm['spline']:.4f} < Makima {sm['makima']:.4f} < linear {sm['linear']:.4f} px",
                   sm["spline"] < sm["makima"] < sm["linear"] and abs(sm["linear"] - 0.0394) < 0.002 and abs(sm["makima"] - 0.0083) < 0.001))
    st = {m: L.rms_vs_truth(L.step_motion, m, 24, L.STEP_WINDOW) for m in ("linear", "spline", "makima")}
    checks.append((f"step-like motion at 24 fps: Makima {st['makima']:.4f} < linear {st['linear']:.4f} < spline {st['spline']:.4f} px",
                   st["makima"] < st["linear"] < st["spline"] and abs(st["makima"] - 0.0554) < 0.003 and abs(st["spline"] - 0.1471) < 0.005))
    o = {m: L.max_overshoot(m, L.step_motion, 24) for m in ("linear", "spline", "makima")}
    checks.append((f"the spline overshoots the 4 px step by 0.38 px; linear and Makima by 0 (got {o['spline']:.3f}, {o['linear']:.3f}, {o['makima']:.3f})",
                   abs(o["spline"] - 0.383) < 0.01 and o["linear"] < 1e-9 and o["makima"] < 1e-9))

    # ---- offset
    ta, ya = L.camera_samples(L.wander_motion, 30)
    for tau in (0.0137, -0.021):
        yb = L.wander_motion(tB + tau)
        est = L.estimate_offset(ta, ya, tB, yb)
        checks.append((f"offset {tau * 1000:+.1f} ms recovered to within 0.1 ms (got {est * 1000:+.2f} ms)", abs(est - tau) < 1e-4))
    checks.append(("worked example: the worst gap between 30 fps and 24 fps frames is 1/60 s = 16.7 ms", abs(L.worst_gap_s(30, 24) - 1 / 60) < 1e-9))
    checks.append(("edge: cameras at 30 and 60 fps never disagree on frame times (gap 0)", L.worst_gap_s(30, 60) < 1e-12))
    ok_fps = [f for f in (24, 25, 30, 48, 50, 60) if L.worst_gap_s(30, f) <= 0.005]
    checks.append((f"design: of 24, 25, 30, 48, 50, 60 fps only 30 and 60 keep the gap under 5 ms (got {ok_fps})", ok_fps == [30, 60]))
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
