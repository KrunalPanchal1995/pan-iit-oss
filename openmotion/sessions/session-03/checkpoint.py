"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    x, v, a = (float(q) for q in L.true_motion(5.0))
    checks.append(("hand calculation at t = 5 s: x = 39.16 m, v = 11.46 m/s, a = 1.21 m/s^2",
                   abs(x - 39.162) < 0.001 and abs(v - 11.456) < 0.001 and abs(a - 1.207) < 0.001))
    dt, sigma = 0.05, 0.02
    t, xn = L.sample(dt, sigma)
    xt, vt, at = L.true_motion(t)
    ev = L.rms_error(L.central_velocity(xn, dt), vt)
    ea = L.rms_error(L.second_difference(xn, dt), at)
    pv, pa = sigma / (np.sqrt(2) * dt), sigma * np.sqrt(6) / dt ** 2
    checks.append(("worked example: noise-only prediction 0.283 m/s and 19.6 m/s^2 matches the measured errors within 10%",
                   abs(ev / pv - 1) < 0.1 and abs(ea / pa - 1) < 0.1))
    tc, xc = L.sample(dt, 0.0)
    bound = dt ** 2 / 6 * L.A_WAVE * L.W ** 3
    checks.append(("noise-free central difference error stays below the dt^2/6 bound",
                   float(np.nanmax(np.abs(L.central_velocity(xc, dt) - L.true_motion(tc)[1]))) <= bound * 1.01))
    ev_s = L.rms_error(L.smooth_derivative(xn, dt, 8, 3, 1), vt)
    ea_s = L.rms_error(L.smooth_derivative(xn, dt, 8, 3, 2), at)
    checks.append(("local cubic fit beats finite differences: velocity error 3 times smaller, acceleration under 1 m/s^2",
                   ev_s < ev / 3 and ea_s < 1.0))
    tq = np.arange(0, 3.0, 0.1)
    xq = 2 + 3 * tq + 2 * tq ** 2
    vq, aq = L.smooth_derivative(xq, 0.1, 5, 3, 1), L.smooth_derivative(xq, 0.1, 5, 3, 2)
    checks.append(("edge: a quadratic motion is differentiated exactly (v = 3 + 4t, a = 4)",
                   np.allclose(vq[5:-5], 3 + 4 * tq[5:-5], atol=1e-8) and np.allclose(aq[5:-5], 4.0, atol=1e-7)))
    e1 = L.mean_error(lambda tt, xx, d: L.rms_error(L.central_velocity(xx, d), L.true_motion(tt)[1]), 0.05, 0.02, seeds=range(6))
    e2 = L.mean_error(lambda tt, xx, d: L.rms_error(L.central_velocity(xx, d), L.true_motion(tt)[1]), 0.1, 0.02, seeds=range(6))
    checks.append(("sensitivity: halving dt doubles the velocity noise error (ratio 1.8 to 2.2)", 1.8 < e1 / e2 < 2.2))
    t2, x2 = L.sample(2.0, 0.0)
    checks.append(("limit: sampling every 2 s misses the 5.2 s wiggle even without noise (error above 1.5 m/s)",
                   L.rms_error(L.central_velocity(x2, 2.0), L.true_motion(t2)[1]) > 1.5))
    tp, xp, vp = L.phone_dataset()
    ints = L.cumulative_integral(vp, tp[1] - tp[0])
    checks.append(("phone dataset: integrating the exact velocity gives 180 m, and the noisy x ends within 0.1 m",
                   abs(ints[-1] - 180.0) < 1e-6 and abs(xp[-1] - 180.0) < 0.1))
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
