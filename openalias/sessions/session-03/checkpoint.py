"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # validation against the exact folding formula
    x = L.sampled_signal(22.5, 30.0, 300)
    checks.append(("worked example: 22.5 Hz at 30 Hz shows its FFT peak at the alias 7.5 Hz",
                   abs(L.peak_frequency(x, 30.0) - 7.5) < 1e-9 and abs(L.alias_frequency(22.5, 30.0) - 7.5) < 1e-9))
    freqs, amp = L.spectrum(x, 30.0)
    checks.append(("the peak has height 1 (amplitude of the sine) and bin spacing 0.1 Hz",
                   abs(amp.max() - 1.0) < 1e-6 and abs(freqs[1] - 0.1) < 1e-9))
    rng = np.random.default_rng(1)
    f_rand = rng.uniform(1.0, 89.0, 60)
    err = L.max_alias_error(30.0, 300, f_rand)
    checks.append(("FFT peak matches the exact alias formula for 60 random frequencies (error under one bin, 0.1 Hz)", err < 0.1))
    # two rates
    a1, a2 = L.signed_alias(22.5, 30.0), L.signed_alias(22.5, 24.0)
    checks.append(("hand calculation: apparent speeds are -7.5 rev/s (30 fps) and -1.5 rev/s (24 fps)",
                   abs(a1 + 7.5) < 1e-9 and abs(a2 + 1.5) < 1e-9))
    checks.append(("worked example: -7.5 + 30 k and -1.5 + 24 m meet at 22.5 (k = 1, m = 1)",
                   L.recover_frequency(a1, 30, a2, 24, 0, 100, 1e-6) == [22.5]))
    checks.append(("unsigned sizes only: the answer is 22.5 or 97.5 below 100",
                   L.recover_frequency(7.5, 30, 1.5, 24, 0, 100, 1e-6, signed=False) == [22.5, 97.5]))
    checks.append(("unambiguous range: lcm(30, 24) = 120 and lcm(30, 25) = 150",
                   L.ambiguity_period(30, 24) == 120 and L.ambiguity_period(30, 25) == 150))
    checks.append(("beyond the range the answer repeats: 142.5 looks like 22.5 on both clips",
                   abs(L.signed_alias(142.5, 30) - a1) < 1e-9 and abs(L.signed_alias(142.5, 24) - a2) < 1e-9))
    checks.append(("failure case: the same rate twice cannot separate speeds (period 30; 22.5 and 52.5 stay candidates)",
                   L.ambiguity_period(30, 30) == 30 and L.recover_frequency(a1, 30, a1, 30, 0, 100, 1e-6) == [22.5, 52.5, 82.5]))
    # rendered clips
    c30 = L.render_clip(22.5, 30.0, 40)
    checks.append(("a rendered clip filmed at 30 fps is measured at -7.5 rev/s", abs(L.measure_apparent(c30, 30.0) + 7.5) < 0.05))
    c_slow = L.render_clip(4.0, 30.0, 40)
    checks.append(("a slow wheel (4 rev/s) is measured correctly, forward", abs(L.measure_apparent(c_slow, 30.0) - 4.0) < 0.05))
    # mystery fan -> mini-project answer
    m1 = L.measure_apparent(L.mystery_fan(30), 30.0)
    m2 = L.measure_apparent(L.mystery_fan(24), 24.0)
    rec = L.recover_frequency(m1, 30, m2, 24, 0.0, 60.0, 0.3)
    checks.append(("mini-project: the two mystery clips give 22.5 rev/s (1350 rpm) below 60 rev/s",
                   len(rec) == 1 and abs(rec[0] - 22.5) < 0.1))
    # jitter and exposure against their formulas
    s = 0.002
    meas = np.mean([L.projected_amplitude(L.sampled_signal(40, 50, 20000, jitter_std=s, seed=sd), 50, -10) for sd in range(4)])
    checks.append(("jitter of 2 ms at f = 40 Hz: peak shrinks by exp(-(2 pi f s)^2 / 2) = 0.881",
                   abs(L.jitter_factor(40, s) - 0.8812) < 1e-3 and abs(meas - L.jitter_factor(40, s)) < 0.02))
    xe = L.sampled_signal(22.5, 30.0, 3000, exposure=0.5)
    ge = L.projected_amplitude(xe, 30.0, -7.5)
    checks.append(("exposure at 22.5 Hz and 30 fps: gain |sinc(f tau)| is 0.784 (half frame) and 0.300 (full frame), and the simulation matches",
                   abs(ge - L.exposure_gain(22.5, 0.5, 30.0)) < 0.01 and abs(L.exposure_gain(22.5, 1.0, 30.0) - abs(np.sinc(0.75))) < 1e-12))
    checks.append(("full-frame exposure of a wheel turning exactly fs rev/s blurs the marker to a ring (gain 0)",
                   L.exposure_gain(30.0, 1.0, 30.0) < 1e-12))
    _, r = L.marker_polar(L.render_clip(22.5, 30.0, 6, exposure=1.0))
    checks.append(("rendered blur agrees: marker radius ratio 0.30 at full exposure (sinc(0.75))", abs(r.mean() / 20.0 - abs(np.sinc(0.75))) < 0.03))
    # edge: peak at exactly Nyquist
    xn = L.sampled_signal(15.0, 30.0, 300, phase=np.pi / 2)
    checks.append(("edge: a 15 Hz signal at 30 Hz sits exactly on the Nyquist bin", abs(L.peak_frequency(xn, 30.0) - 15.0) < 1e-9))
    checks.append(("design: a partner rate for 30 fps must have lcm above 100: 24 (120), 25 (150) work; 20 (60), 60 (60), 15 (30) fail",
                   all(L.ambiguity_period(30, r) > 100 for r in (24, 25)) and all(L.ambiguity_period(30, r) <= 100 for r in (20, 60, 15))))
    checks.append(("jitter of 1 ms at f = 40 Hz costs only 3.1 percent of the peak (factor 0.969)", abs(L.jitter_factor(40, 0.001) - 0.9689) < 1e-4))
    checks.append(("with two clips only, speeds up to 400 rev/s still leave 4 candidates (22.5, 142.5, 262.5, 382.5)",
                   L.recover_frequency(a1, 30, a2, 24, 0, 400, 1e-6) == [22.5, 142.5, 262.5, 382.5]))
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
