"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    K = L.blob_kymo([(10, 0.7, 1.0)])
    checks.append(("noise-free blob at 0.7 px/frame: gradient (TLS) estimate within 0.005", abs(L.gradient_speed(K) - 0.7) < 0.005))
    checks.append(("noise-free blob at 0.7 px/frame: ridge fit within 0.002", abs(L.ridge_speed(K, 10)[0] - 0.7) < 0.002))
    checks.append(("worked example: a cosine of wavelength 8 px moving 5 px/frame looks like -3 px/frame",
                   abs(L.apparent_shift(5.0, 8.0) + 3.0) < 1e-12))
    checks.append(("worked example: the gradient method on that pattern reports about -3 (within 0.1)",
                   abs(L.gradient_speed(L.wave_kymo(5.0, 8.0), s=1.0) + 3.0) < 0.1))
    hand = 0.26 * np.sqrt(12.0 / (60 * (60 ** 2 - 1)))
    checks.append(("worked example: line-fit scatter 0.26 px over 60 points gives slope std 0.0019",
                   abs(hand - 0.001938) < 2e-6 and abs(L.slope_std_formula(0.26, 60) - hand) < 1e-12))
    rng = np.random.default_rng(7)
    tt = np.arange(60)
    sim = np.std([np.polyfit(tt, 0.7 * tt + 0.26 * rng.standard_normal(60), 1)[0] for _ in range(1500)])
    checks.append(("simulated line-fit scatter agrees with the formula within 10 percent", abs(sim / hand - 1) < 0.10))
    mk = lambda s: L.blob_kymo([(10, 0.7, 1.0)], noise=0.4, seed=s)
    ls = L.monte_carlo(L.gradient_speed_ls, mk, trials=25)[0]
    tls = L.monte_carlo(L.gradient_speed, mk, trials=25)[0]
    checks.append(("noise 0.4: least squares is biased low (below 0.5) while TLS stays within 0.05 of 0.7", ls < 0.5 and abs(tls - 0.7) < 0.05))
    K3 = L.blob_kymo([(10, 0.7, 1.0), (45, 0.7, 0.7), (75, 0.7, 0.5)])
    checks.append(("three parallel stripes are measured together (0.7 within 0.01)", abs(L.gradient_speed(K3) - 0.7) < 0.01))
    checks.append(("a texture sliding left gives a negative speed (-0.6 within 0.01)",
                   abs(L.gradient_speed(L.texture_kymo(-0.6, seed=2)) + 0.6) < 0.01))
    checks.append(("edge case: a flat image gives nan, not a crash", np.isnan(L.gradient_speed(np.zeros((30, 30))))))
    checks.append(("edge case: a shift of exactly half a wavelength folds to -wavelength/2, and a full wavelength to 0",
                   L.apparent_shift(4.0, 8.0) == -4.0 and L.apparent_shift(8.0, 8.0) == 0.0 and L.apparent_shift(0.0, 8.0) == 0.0))
    checks.append(("the folding is odd in the shift: apparent(-5) = +3", abs(L.apparent_shift(-5.0, 8.0) - 3.0) < 1e-12))
    mk3 = lambda v: L.blob_kymo([(5, v, 1.0)], n_x=700)
    checks.append(("blob sigma 1.5 px, 3 px/frame: still within 1 percent", abs(L.shift_error(3.0, mk3, L.gradient_speed)) < 0.01))
    checks.append(("failure: at 8 px/frame the gradient method is wrong by more than 100 percent",
                   abs(L.shift_error(8.0, mk3, L.gradient_speed)) > 1.0))
    checks.append(("failure: at 4 px/frame a ridge tracker with a 3 px window loses the blob (error below -90 percent)",
                   L.shift_error(4.0, mk3, lambda Kx: L.ridge_speed(Kx, 5)[0]) < -0.9))
    e100 = max(abs(L.belt_speed_mps(L.conveyor_kymo(0.8, 100, 2.0, seed=s), 100, 2.0) - 0.8) / 0.8 for s in range(3))
    e400 = max(abs(L.belt_speed_mps(L.conveyor_kymo(0.8, 400, 2.0, seed=s), 400, 2.0) - 0.8) / 0.8 for s in range(3))
    checks.append(("conveyor 0.8 m/s, 2 mm/px: 100 fps (4 px/frame) is off by more than 10 percent", e100 > 0.10))
    checks.append(("conveyor 0.8 m/s, 2 mm/px: 400 fps (1 px/frame) is within 1 percent", e400 < 0.01))
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
