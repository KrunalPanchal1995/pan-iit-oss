"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    fs = 1000.0
    a = L.alpha_exact(20.0, fs)
    checks.append(("alpha for fc = 20 Hz at fs = 1000 Hz is 0.11809 (exact) and 0.11164 (backward Euler)",
                   abs(a - 0.11809) < 1e-5 and abs(L.alpha_euler(20.0, fs) - 0.11164) < 1e-5))
    checks.append(("exact and Euler alpha agree when fc is much smaller than fs",
                   abs(L.alpha_exact(0.1, fs) / L.alpha_euler(0.1, fs) - 1.0) < 1e-3))
    # the exact discretisation reproduces the analog step response at every sample
    tau = 1.0 / (2 * np.pi * 20.0)
    step = L.ema(np.ones(50), a)
    analog = 1.0 - np.exp(-(np.arange(1, 51) / fs) / tau)
    checks.append(("exact alpha: digital step response equals 1 - exp(-t/tau) at every sample", np.allclose(step, analog, atol=1e-12)))
    checks.append(("EMA edge cases: alpha = 1 copies the input, alpha = 0 never moves",
                   np.allclose(L.ema(np.array([1.0, 5.0, -2.0]), 1.0), [1.0, 5.0, -2.0])
                   and np.allclose(L.ema(np.array([1.0, 5.0]), 0.0, y0=3.0), [3.0, 3.0])))

    # frequency response: sweep and FFT against theory
    freqs = np.array([2.0, 10.0, 20.0, 80.0, 320.0])
    meas = np.array([L.sweep_gain(f, a, fs) for f in freqs])
    th = L.digital_gain(freqs, a, fs)
    checks.append(("sine-sweep gain matches the digital theory within 0.001", float(np.max(np.abs(meas - th))) < 1e-3))
    ff, gf = L.fft_gain(a, fs)
    band = (ff > 3.0) & (ff < 200.0)
    checks.append(("FFT gain from white noise matches the digital theory within 5 percent (3 to 200 Hz)",
                   float(np.max(np.abs(gf[band] / L.digital_gain(ff[band], a, fs) - 1.0))) < 0.05))
    checks.append(("digital and analog Bode agree below fc/2 (within 0.2 percent) but not near Nyquist (320 Hz: 0.0743 versus 0.0624)",
                   abs(float(L.digital_gain(10.0, a, fs) / L.analog_gain(10.0, 20.0)) - 1.0) < 0.002
                   and abs(float(L.digital_gain(320.0, a, fs)) - 0.0743) < 5e-4 and abs(float(L.analog_gain(320.0, 20.0)) - 0.0624) < 5e-4))

    # noise versus lag
    worst = max(abs(L.variance_ratio_measured(al) / L.variance_ratio_theory(al) - 1.0) for al in (0.5, 0.1, 0.02))
    checks.append(("measured white-noise variance ratio matches alpha / (2 - alpha) within 3 percent", worst < 0.03))
    a2 = L.alpha_exact(2.0, 500.0)
    checks.append(("worked example: fc = 2 Hz at 500 Hz gives alpha 0.0248, noise power x0.0126 (rms 0.0056 C from 0.05 C), lag 39.3 samples",
                   abs(a2 - 0.02482) < 1e-4 and abs(L.variance_ratio_theory(a2) - 0.01257) < 1e-4
                   and abs(0.05 * np.sqrt(L.variance_ratio_theory(a2)) - 0.0056) < 1e-4 and abs(L.lag_samples(a2) - 39.3) < 0.1))
    checks.append(("worked example: that filter leaves 0.0203 C of 50 Hz hum (0.5 C in)",
                   abs(0.5 * float(L.digital_gain(50.0, a2, 500.0)) - 0.0203) < 2e-4))
    e15 = L.ema_filter(1.5)
    checks.append(("worked example: fc = 1.5 Hz leaves 0.0152 C of hum, reaches 90 percent in 0.244 s, noise 0.0049 C",
                   abs(L.ripple_after(e15) - 0.0152) < 3e-4 and abs(L.time_to_90(e15) - 0.244) < 0.003
                   and abs(0.05 * np.sqrt(L.variance_ratio_theory(L.alpha_exact(1.5, 500.0))) - 0.0049) < 1e-4))
    checks.append(("lag matches a hand count: alpha = 0.5 gives 1 sample, alpha = 0.1 gives 9 samples",
                   L.lag_samples(0.5) == 1.0 and abs(L.lag_samples(0.1) - 9.0) < 1e-12))
    h = a * (1 - a) ** np.arange(4000)
    checks.append(("lag is the mean of the impulse response: sum k h[k] = (1 - alpha) / alpha",
                   abs(float(np.sum(np.arange(4000) * h)) - L.lag_samples(a)) < 1e-6))
    checks.append(("samples_to_90 hand check: alpha = 0.5 needs 4 samples (1 - 0.5^4 = 0.9375), alpha = 0.1 needs 22",
                   L.samples_to_90(0.5) == 4 and L.samples_to_90(0.1) == 22))
    prod = [L.variance_ratio_theory(al) * L.lag_samples(al) for al in (0.02, 0.01)]
    checks.append(("trade-off: noise power x lag is (1 - alpha) / (2 - alpha), close to 1/2 for small alpha",
                   all(abs(p - (1 - al) / (2 - al)) < 1e-12 for p, al in zip(prod, (0.02, 0.01))) and abs(prod[1] - 0.5) < 0.005))

    # Butterworth biquad
    b, ba = L.butter2_coeffs(20.0, fs)
    checks.append(("Butterworth biquad is exactly -3.01 dB (gain 0.70711) at fc", abs(float(L.biquad_gain(20.0, b, ba, fs)) - 2 ** -0.5) < 1e-9))
    checks.append(("Butterworth DC gain is 1 and the poles are inside the unit circle",
                   abs(float(np.sum(b) / np.sum(ba)) - 1.0) < 1e-12 and float(np.max(np.abs(np.roots(ba)))) < 1.0))
    g10 = 20 * np.log10(float(L.biquad_gain(200.0, b, ba, fs)))
    g1 = 20 * np.log10(float(L.biquad_gain(2.0, b, ba, fs)))
    checks.append(("Butterworth falls about 40 dB per decade (-42.5 dB at 10 fc; passband flat within 0.001 dB at fc/10)",
                   -44.0 < g10 < -40.0 and abs(g1) < 1e-3))
    t = np.arange(4000) / fs
    y = L.biquad(np.sin(2 * np.pi * 20.0 * t), b, ba)
    checks.append(("time-domain run of the biquad at fc measures gain 0.7071 (within 0.002)",
                   abs(L.fit_amplitude(y[1000:], t[1000:], 20.0) - 2 ** -0.5) < 2e-3))
    f1 = L.cascade_stage_fc(20.0)
    cas = float(1.0 / (1.0 + (20.0 / f1) ** 2))
    checks.append(("two buffered RC stages set to fc/0.6436 are -3.01 dB at fc (each stage alone is -6 dB at its own cutoff)",
                   abs(f1 - 31.07) < 0.01 and abs(cas - 2 ** -0.5) < 1e-3))

    # failure cases
    checks.append(("aliasing: 50 Hz sampled at 55 Hz looks like 5 Hz; below Nyquist nothing changes; 70 Hz at 100 Hz becomes 30 Hz",
                   L.alias_frequency(50.0, 55.0) == 5.0 and L.alias_frequency(30.0, 100.0) == 30.0
                   and L.alias_frequency(70.0, 100.0) == 30.0 and L.alias_frequency(100.0, 100.0) == 0.0))
    fb = L.ema_minus3db_hz(a, fs)
    checks.append(("digital -3 dB frequency of the fc = 20 Hz EMA is just above 20 Hz and really has gain 0.7071",
                   20.0 < fb < 20.2 and abs(float(L.digital_gain(fb, a, fs)) - 2 ** -0.5) < 1e-9))
    checks.append(("cutoff above Nyquist: fc = 40 Hz at fs = 60 Hz has no -3 dB point (alpha = 0.985); fc = 30 Hz at fs = 60 Hz has none either",
                   L.ema_minus3db_hz(L.alpha_exact(40.0, 60.0), 60.0) is None and L.ema_minus3db_hz(L.alpha_exact(30.0, 60.0), 60.0) is None))
    checks.append(("aliased hum is hard to remove: EMA (fc = 2 Hz, fs = 55 Hz) passes 0.376 of the 5 Hz alias, the analog filter would pass 0.040 of 50 Hz",
                   abs(float(L.digital_gain(5.0, L.alpha_exact(2.0, 55.0), 55.0)) - 0.376) < 2e-3 and abs(float(L.analog_gain(50.0, 2.0)) - 0.040) < 1e-3))

    # temperature mini-project helpers
    checks.append(("temperature design: EMA fc = 1.5 Hz passes all three requirements, fc = 2.0 Hz fails the hum limit, fc = 0.5 Hz is too slow",
                   L.passes(L.ema_filter(1.5)) and not L.passes(L.ema_filter(2.0)) and not L.passes(L.ema_filter(0.5))))
    checks.append(("temperature design: Butterworth fc = 4 Hz passes, fc = 6 Hz fails the noise limit, fc = 0.75 Hz is too slow",
                   L.passes(L.butter_filter(4.0)) and not L.passes(L.butter_filter(6.0)) and not L.passes(L.butter_filter(0.75))))
    checks.append(("a filter that never reaches 90 percent reports infinite time", L.time_to_90(L.ema_filter(0.02)) == float("inf")))
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
