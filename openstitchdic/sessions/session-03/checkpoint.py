"""Checkpoint for Session 3. Prints PASS or FAIL."""
import pathlib
import tempfile

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # ---- hand calculations and the camera model
    pk = L.parabola_peak(0.80, 0.95, 0.90)
    checks.append((f"worked example: ZNCC scores 0.80, 0.95, 0.90 at shifts 2, 3, 4 give a peak at 3.25 px (got {3 + pk:.3f})", abs(3 + pk - 3.25) < 1e-9))
    pk2 = L.parabola_peak(0.60, 0.90, 0.85)
    checks.append((f"hand calculation: scores 0.60, 0.90, 0.85 put the peak 0.357 px beyond the best whole pixel (got {pk2:.3f})", abs(pk2 - 5 / 14) < 1e-9))
    checks.append(("hand calculation: at amplitude s = 3 the subset at x = 120 moves (3.48, 1.20) px",
                   np.allclose(L.true_displacement(3.0)[0, 2], [3.48, 1.2], atol=1e-9)))
    cams_ok = True
    for k in "AB":
        cam = L.CAMS[k]
        c = L.apply_h(L.camera_homography(cam), [[0, 0], [159, 0], [159, 119], [0, 119]])
        cams_ok &= bool(c.min() >= 0 and c[:, 0].max() < cam["cols"] and c[:, 1].max() < cam["rows"])
    checks.append(("both cameras see the whole sheet (A is 240 x 180 = 4:3, B is 320 x 180 = 16:9)", cams_ok))
    ok = True
    for k in "AB":
        H = L.to_grid_matrix(k, "homography", 0.0)
        pts = np.array([[80.0, 60.0], [30.0, 100.0], [150.0, 10.0]])
        ok &= bool(np.abs(L.apply_h(H, L.apply_h(L.camera_homography(L.CAMS[k]), pts)) - pts).max() < 1e-8)
    checks.append(("with exact corner clicks the homography puts any sheet point back on its grid pixel", ok))
    checks.append(("camera B is 28 degrees off axis, so its perspective is real: the affine fit misses a sheet point by more than 0.05 px",
                   np.abs(L.apply_h(L.to_grid_matrix("B", "affine", 0.0), L.apply_h(L.camera_homography(L.CAMS["B"]), [[150.0, 10.0]])) - [150.0, 10.0]).max() > 0.05))

    # ---- subset correlation
    gy, gx = np.mgrid[0:80, 0:80].astype(float)
    ref = L.speckle_at(gx, gy)
    errs = []
    for dx, dy in ((2.0, 0.0), (2.4, -1.3), (-3.7, 0.25), (0.15, 0.8)):
        d = L.track_subset(ref, L.speckle_at(gx - dx, gy - dy), 40, 40)
        errs.append(max(abs(d[0] - dx), abs(d[1] - dy)))
    checks.append((f"known sub-pixel shifts are recovered to within 0.07 px (worst {max(errs):.3f})", max(errs) < 0.07))
    d1 = L.track_subset(ref, L.speckle_at(gx - 2.4, gy - 1.3), 40, 40)
    d2 = L.track_subset(ref, 0.5 * L.speckle_at(gx - 2.4, gy - 1.3) + 0.3, 40, 40)
    checks.append(("ZNCC ignores brightness and contrast changes (same answer for 0.5 x + 0.3)", np.allclose(d1, d2, atol=1e-9)))
    far = L.track_subset(ref, L.speckle_at(gx - 9.0, gy), 40, 40)
    checks.append(("edge: a shift beyond the search window is reported as NaN, not guessed", bool(np.isnan(far[0]))))
    near = L.track_subset(ref, ref, 8, 40)
    checks.append(("edge: a subset too close to the picture border is reported as NaN", bool(np.isnan(near[0]))))

    # ---- the pipeline and its error budget
    good = L.run_pipeline("smooth", "homography", "makima")
    checks.append((f"smooth motion, homography + Makima: RMS error {good['rms']:.3f} px (below 0.03), worst {good['max']:.2f} px (below 0.12)",
                   good["rms"] < 0.03 and good["max"] < 0.12))
    checks.append(("the timeline is 120 fps from 0 to 0.75 s (91 points): the last time both cameras have data", len(good["timeline"]) == 91 and abs(good["timeline"][-1] - 0.75) < 1e-9))
    nr = L.run_pipeline("smooth", "homography", "nearest")["rms"]
    ln = L.run_pipeline("smooth", "homography", "linear")["rms"]
    checks.append((f"smooth motion, time alignment: nearest {nr:.3f} > linear {ln:.3f} > Makima {good['rms']:.3f} px, so skipping it costs 5 times the error", nr > ln > good["rms"] and nr / good["rms"] > 4.5))
    af = L.run_pipeline("smooth", "affine", "makima")["rms"]
    rz = L.run_pipeline("smooth", "resize", "nearest")["rms"]
    checks.append((f"smooth motion, geometry: homography {good['rms']:.3f} < affine {af:.3f} < plain resize {rz:.3f} px", good["rms"] < af < rz))
    sa = L.run_pipeline("step", "homography", "makima")
    sn = L.run_pipeline("step", "homography", "nearest")
    sf = L.run_pipeline("step", "affine", "makima")
    checks.append((f"step-like motion: homography + Makima {sa['rms']:.3f}, nearest time {sn['rms']:.3f}, affine {sf['rms']:.3f} px",
                   sa["rms"] < 0.05 and sn["rms"] > 2 * sa["rms"] and sf["rms"] > 1.5 * sa["rms"]))
    checks.append(("camera B alone suffers most from skipping the homography: affine error of B is 5 times the homography error",
                   sf["rms_b"] > 5 * sa["rms_b"]))
    b, a = L.before_after("step")
    checks.append((f"mini-project: error before {b:.3f} px, after {a:.3f} px, a factor of {b / a:.0f} (at least 10)", b / a > 10 and a < 0.05))
    cons = L.run_pipeline("smooth", "homography", "makima", "consecutive")
    checks.append((f"consecutive-frame correlation adds up small errors: RMS {cons['rms']:.3f} px against {good['rms']:.3f} px from the reference frame",
                   cons["rms"] > 3 * good["rms"]))

    # ---- edge cases
    masked = L.run_pipeline("smooth", "homography", "makima", shift_cx=L.OCCLUDE_SHIFT)
    zero = L.run_pipeline("smooth", "homography", "makima", shift_cx=L.OCCLUDE_SHIFT, nan_policy="zero")
    checks.append((f"occlusion: camera B loses 3 of 9 subsets, the merged data stay finite and accurate (RMS {masked['rms']:.3f} px)",
                   abs(masked["valid_b"] - 6 / 9) < 1e-9 and np.all(np.isfinite(masked["merged"])) and masked["rms"] < 0.03))
    checks.append((f"filling the missing pixels with zeros instead of masking them doubles the error ({zero['rms']:.3f} against {masked['rms']:.3f} px)", zero["rms"] > 1.8 * masked["rms"]))
    t = np.arange(int(L.DURATION * 24)) / 24
    tq = np.linspace(0, t[-1], 500)
    inside = float(np.sqrt(np.mean((L.resample("makima", t, L.motion_smooth(t), tq) - L.motion_smooth(tq)) ** 2)))
    ex = [L.extrapolation_error(L.motion_smooth, 24, k) for k in (1, 2, 3)]
    checks.append((f"extrapolation: {inside:.3f} px inside the range, but {ex[0]:.2f}, {ex[1]:.2f}, {ex[2]:.2f} px at 1, 2, 3 frames beyond it",
                   ex[0] > 10 * inside and ex[0] < ex[1] < ex[2]))
    checks.append(("by default values outside a camera's time range are NaN (never extrapolated)", bool(np.isnan(L.resample("makima", t, L.motion_smooth(t), np.array([t[-1] + 0.01]))[0]))))

    # ---- your own pictures
    with tempfile.TemporaryDirectory() as td:
        folder = pathlib.Path(td)
        none = L.load_user_pair(folder)
        a0, b0, pts0, src0 = L.get_pair(folder)
        checks.append(("without a data folder the lesson falls back to synthetic pictures", none is None and "synthetic" in src0))
        import matplotlib.image as mpimg
        mpimg.imsave(str(folder / "view_a.png"), a0, cmap="gray", vmin=-3, vmax=3)
        mpimg.imsave(str(folder / "view_b.png"), b0, cmap="gray", vmin=-3, vmax=3)
        np.savetxt(folder / "points.txt", pts0)
        ua, ub, up = L.load_user_pair(folder)
        a1, b1, pts1, src1 = L.get_pair(folder)
        warped = L.align_pair(ua, ub, up)
        checks.append((f"dropped-in PNG pictures with points.txt are loaded and aligned (correlation {L.ncc(ua, warped):.3f}, above 0.95)",
                       ua.shape == (180, 240) and ub.shape == (180, 320) and up.shape == (4, 4) and "your pictures" in src1 and L.ncc(ua, warped) > 0.95))
        (folder / "points.txt").unlink()
        ua2, ub2, up2 = L.load_user_pair(folder)
        crop = L.align_pair(ua2, ub2, up2)
        checks.append(("without points.txt picture B is scaled and cropped to the shape of A", up2 is None and crop.shape == ua2.shape))
    cc = L.ncc(a0, L.align_pair(a0, b0, pts0))
    checks.append((f"worked example: the synthetic pair, B warped onto A, correlates above 0.99 (got {cc:.3f})", cc > 0.99))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
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
