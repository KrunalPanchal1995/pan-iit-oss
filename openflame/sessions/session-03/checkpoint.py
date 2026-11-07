"""Checkpoint for Session 3. Prints PASS or FAIL."""
import pathlib
import tempfile

import numpy as np

SCALE = 13.0                                          # mm per pixel of the synthetic camera
H_MM = (0.235 * 40 ** 0.4 - 1.02 * 0.30) * 1000       # Heskestad: Q = 40 kW, D = 0.30 m -> 721.8 mm
H0 = H_MM / SCALE


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    fs, f_true, amp = 30.0, 2.74, 2.0
    t, hs = L.flicker_heights(8.0, fs, H0, amp, f_true)
    video = L.render_video(hs, noise=0.15, seed=1)
    checks.append(("an 8 s clip at 30 fps is a stack of 240 pictures", video.shape == (240, L.ROWS, L.COLS)))

    r = L.measure_video(video, fs)
    checks.append((f"worked example: Heskestad gives {H_MM:.0f} mm = {H0:.1f} px at 13 mm/px; the video measures a mean of {r['mean']:.1f} px",
                   abs(H_MM - 721.8) < 0.5 and abs(r["mean"] - H0) < 0.5))
    err = r["trace"] - hs
    checks.append((f"worked example: height trace error has std {err.std():.2f} px (< 0.6) and no bias (|mean| < 0.2)",
                   err.std() < 0.6 and abs(err.mean()) < 0.2))
    checks.append((f"worked example: recovered flicker {r['f']:.4f} Hz is within 3 error bars (+/- {r['f_err']:.4f}) of 2.74 Hz",
                   abs(r["f"] - f_true) < 3 * r["f_err"] and r["f_err"] < 0.005))
    checks.append(("amplitude is recovered within 0.1 px", abs(r["amp"] - amp) < 0.1))

    sub = np.std(L.extract_heights(video, 0.5, True) - hs)
    pix = np.std(L.extract_heights(video, 0.5, False) - hs)
    checks.append((f"sub-pixel interpolation beats whole-pixel steps ({sub:.2f} < {pix:.2f} px)", sub < pix))

    # error bar against repeated experiments
    fh, er = L.repeat_experiments(20, 8.0, fs, H0, amp, f_true, 0.15)
    ratio = fh.std(ddof=1) / er.mean()
    checks.append((f"the Cramer-Rao error bar matches the scatter of 20 repeated experiments (ratio {ratio:.2f}, expected 0.7 to 1.4)",
                   0.7 < ratio < 1.4 and abs(fh.mean() - f_true) < 0.003))
    # hand calculation of the bar
    n = 240
    eta = amp ** 2 / (2 * 0.44 ** 2)
    hand = fs * np.sqrt(12 / ((2 * np.pi) ** 2 * eta * n * (n * n - 1)))
    checks.append((f"hand calculation: sigma_f = {hand:.4f} Hz for N = 240, A = 2 px, s = 0.44 px",
                   abs(L.frequency_error_bar(amp, 0.44, n, fs) - hand) < 1e-12 and 0.001 < hand < 0.003))
    longer = L.frequency_error_bar(amp, 0.44, 2 * n, fs)
    checks.append(("doubling the recording length shrinks the error bar by about 2^(3/2) = 2.8",
                   abs(L.frequency_error_bar(amp, 0.44, n, fs) / longer - 2 ** 1.5) < 0.03))

    # failure case: low signal-to-noise
    wh, _ = L.repeat_experiments(20, 8.0, fs, H0, 0.4, f_true, 0.35)
    bad = int(np.sum(np.abs(wh - f_true) > 0.1))
    checks.append((f"limit: with a 0.4 px flicker and noise 0.35, {bad} of 20 runs lock onto a noise peak (at least 3)", bad >= 3))

    # aliasing
    t9, h9 = L.flicker_heights(8.0, fs, H0, amp, 9.0)
    v9 = L.render_video(h9, noise=0.15, seed=2)
    r30 = L.measure_video(v9, fs)
    r15 = L.measure_video(L.decimate(v9, 2), fs / 2)
    checks.append((f"9 Hz at 30 fps is seen correctly ({r30['f']:.3f} Hz)", abs(r30["f"] - 9.0) < 0.02))
    checks.append((f"the same flame at 15 fps appears at 6 Hz, the alias (got {r15['f']:.3f} Hz)", abs(r15["f"] - 6.0) < 0.03))
    checks.append(("edge: alias of exactly the Nyquist frequency and of the frame rate",
                   abs(L.alias_frequency(7.5, 15.0) - 7.5) < 1e-12 and abs(L.alias_frequency(15.0, 15.0)) < 1e-12))

    # threshold sensitivity against the analytic shift
    ok, fok = True, True
    for th in (0.3, 0.4, 0.5, 0.6, 0.7):
        tr = L.extract_heights(video, th)
        shift = (tr - hs).mean()
        ok &= abs(shift - L.predicted_bias(th)) < 0.35
        fok &= abs(L.fit_flicker(tr, fs)["f"] - f_true) < 0.01
    checks.append(("measured height shift follows soft*ln((1-thr)/thr) within 0.35 px for thresholds 0.3 to 0.7", bool(ok)))
    checks.append(("the flicker frequency does not depend on the threshold (within 0.01 Hz)", bool(fok)))
    checks.append(("hand calculation: threshold 0.2 shifts the tip by 2 ln 4 = 2.77 px", abs(L.predicted_bias(0.2) - 2 * np.log(4)) < 1e-12))

    # mini-project clip
    cv, cfs, ct = L.candle_clip()
    cr = L.measure_video(cv, cfs)
    c3 = L.measure_video(L.decimate(cv, 3), cfs / 3)
    checks.append((f"mini-project clip: flicker {cr['f']:.3f} Hz within 0.01 of 7.3, height {cr['mean'] * 0.5:.1f} mm within 0.5 of 28",
                   abs(cr["f"] - ct["f"]) < 0.01 and abs(cr["mean"] * 0.5 - 28.0) < 0.5))
    checks.append((f"mini-project clip decimated to 10 fps shows the alias 2.7 Hz (got {c3['f']:.3f})", abs(c3["f"] - 2.7) < 0.02))

    # edge cases
    black = L.extract_heights(np.zeros((6, L.ROWS, L.COLS)), 0.5)
    checks.append(("edge: a black video gives height 0, not NaN", bool(np.all(np.isfinite(black)) and np.all(black == 0))))

    with tempfile.TemporaryDirectory() as d:
        import matplotlib.image as mpimg
        for k in range(3):
            mpimg.imsave(pathlib.Path(d) / f"f{k:04d}.png", video[k], cmap="gray", vmin=0, vmax=1)
        back = L.frames_from_pngs(d)
    checks.append(("frames_from_pngs reads a folder of pictures back into a stack", back.shape == (3, L.ROWS, L.COLS) and np.abs(back - video[:3]).max() < 0.02))
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
