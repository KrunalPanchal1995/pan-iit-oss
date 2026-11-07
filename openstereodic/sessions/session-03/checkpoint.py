"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    dots = L.make_dots(L.SIZE, L.SIZE, seed=1)
    ref = L.render(dots, deformed=False)
    checks.append(("grey levels stay between 20 and 240", float(ref.min()) >= 19.99 and float(ref.max()) <= 240.01))
    yy, xx = np.mgrid[0:L.SIZE, 0:L.SIZE].astype(float)
    moved = L.texture(dots, xx - 2.5, yy + 1.25)
    u, v, c = L.track_subset(ref, moved, 80, 80, 10, 6)
    checks.append((f"a known shift (2.5, -1.25) px is recovered within 0.02 px (got {u:.3f}, {v:.3f})", abs(u - 2.5) < 0.02 and abs(v + 1.25) < 0.02))
    checks.append(("the whole-pixel correlation of a good match is above 0.9", c > 0.9))

    # worked example: strain from two tracked points, by hand 0.96 / 48 = 0.02
    cur = L.render(dots, deformed=True)
    u1, _, _ = L.track_subset(ref, cur, 56, 80, 10, 6)
    u2, _, _ = L.track_subset(ref, cur, 104, 80, 10, 6)
    exx = (u2 - u1) / 48.0
    checks.append((f"worked example: u(56) = -0.4224, u(104) = 0.5376 exactly; strain = 0.96 / 48 = 0.0200 (measured {exx:.4f})",
                   abs(L.displacement(56.0, 80.0)[0] + 0.4224) < 1e-9 and abs(L.displacement(104.0, 80.0)[0] - 0.5376) < 1e-9 and abs(exx - 0.02) < 0.0015))
    ex_exact, ey_exact = L.exact_strain(80.0, 80.0)
    checks.append(("exact strain at the centre is 0.02 in x and -0.009 in y", abs(ex_exact - 0.02) < 1e-12 and abs(ey_exact + 0.009) < 1e-12))

    r = L.run_dic(noise=0.0)
    eu, ev = L.rms(r["U"] - r["ue"]), L.rms(r["V"] - r["ve"])
    checks.append((f"noise-free: RMS displacement error below 0.02 px (u {eu:.4f}, v {ev:.4f})", eu < 0.02 and ev < 0.02))
    ex, ey = L.rms(r["exx"] - r["exx_exact"]), L.rms(r["eyy"] - r["eyy_exact"])
    checks.append((f"noise-free: RMS strain error below 0.001 (e_xx {ex:.5f}, e_yy {ey:.5f})", ex < 0.001 and ey < 0.001))
    checks.append(("the measured strain map rises from left to right like the exact one",
                   float(np.nanmean(r["exx"][:, -1]) - np.nanmean(r["exx"][:, 0])) > 0.5 * float(np.mean(r["exx_exact"][:, -1] - r["exx_exact"][:, 0]))))

    G2 = L.mean_gradient_sq(ref)
    sig = float(L.predicted_noise_error(4.0, 10, G2))
    checks.append((f"worked example: predicted noise error sqrt(2) * 4 / sqrt(441 * G2) = {sig:.4f} px (G2 = {G2:.0f})",
                   abs(sig - np.sqrt(2) * 4 / np.sqrt(441 * G2)) < 1e-12 and 0.005 < sig < 0.03))
    s6 = float(L.predicted_noise_error(6.0, 14, G2))
    e6 = float(L.predicted_strain_noise(s6, 8, 2))
    w1 = float(L.predicted_strain_noise(s6, 8, 1))
    checks.append((f"hand calculation: noise 6, h = 14 gives {s6:.4f} px; strain error {e6:.5f} (w = 2) and {w1:.5f} (w = 1)",
                   abs(s6 - 0.0135) < 5e-4 and abs(e6 - 0.00024) < 2e-5 and abs(w1 - 0.00069) < 3e-5))
    checks.append(("a bigger subset has a smaller noise error", L.predicted_noise_error(4.0, 20, G2) < L.predicted_noise_error(4.0, 10, G2)))
    checks.append(("bias formula b h (h + 1) / 3 for h = 10 and b = 1e-4 is 0.0037 px", abs(L.predicted_bias(10) - 0.00367) < 1e-4))
    rn = L.run_dic(noise=4.0)
    du = L.rms(rn["U"] - r["U"])
    pred = float(L.predicted_noise_error(4.0, 10, G2))
    checks.append((f"noise-only displacement error {du:.4f} px agrees with the prediction {pred:.4f} px within 25 percent", abs(du - pred) < 0.25 * pred))
    de = L.rms(rn["exx"] - r["exx"])
    pe = float(L.predicted_strain_noise(pred, 8, 2))
    checks.append((f"noise-only strain error {de:.5f} is within a factor 1.6 of the independent-noise formula {pe:.5f}", pe / 1.6 < de < pe * 1.6))
    checks.append(("strain noise falls as the window grows", L.predicted_strain_noise(0.0124, 8, 3) < L.predicted_strain_noise(0.0124, 8, 1)))

    flat = np.full((60, 60), 100.0)
    un, vn, cn = L.track_subset(flat, flat, 30, 30, 8, 3)
    checks.append(("edge: a blank patch cannot be tracked and returns NaN", bool(np.isnan(un) and np.isnan(vn))))
    checks.append(("edge: ZNCC of a patch with its brightness-scaled copy is 1", abs(L.zncc(ref[10:30, 10:30], 0.5 * ref[10:30, 10:30] + 7) - 1.0) < 1e-12))

    # the stereo pair used by the mini-project
    sd = L.strip_dots()
    l0, r0 = L.stereo_pair(sd)
    cx, cy = L.IMG_W // 2, L.IMG_H // 2
    du, dv, _ = L.track_subset(l0, r0, cx, cy, 11, 5, guess=(-80, 0))
    checks.append((f"stereo pair: the strip at 0.5 m has disparity 80 px (got {-du:.2f})", abs(-du - 80.0) < 0.1 and abs(dv) < 0.1))
    l1, _ = L.stereo_pair(sd, exx=0.03, dz=0.01)
    u30, _, _ = L.track_subset(l0, l1, cx + 30, cy, 11, 6)
    checks.append((f"loaded strip pulled 10 mm nearer: a point 30 px right of centre moves 30 * (1.03 * 0.5 / 0.49 - 1) = 1.53 px (got {u30:.2f})", abs(u30 - 1.531) < 0.06))
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
