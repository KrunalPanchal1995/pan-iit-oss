"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("worked example: 0.8 px/frame at 1.5 mm/px and 200 fps is 0.24 m/s",
                   abs(L.speed_mps(0.8, 1.5, 200) - 0.24) < 1e-9))
    checks.append(("unit round trip: shift_per_frame undoes speed_mps",
                   abs(L.shift_per_frame(L.speed_mps(0.8, 1.5, 200), 1.5, 200) - 0.8) < 1e-9))
    ramp = np.fromfunction(lambda t, x: x - 0.5 * t, (20, 20))     # K = x - 0.5 t: gradient (1, -0.5) exactly
    v, coh = L.stripe_speed(ramp)
    checks.append(("hand calculation: the ramp x - 0.5 t has v = -nt/nx = 0.5", abs(v - 0.5) < 1e-9 and coh > 0.999))
    J = L.structure_tensor(ramp)
    checks.append(("hand calculation: for the ramp Jxx : Jxt : Jtt = 1 : -0.5 : 0.25",
                   abs(J[0, 1] / J[0, 0] + 0.5) < 1e-9 and abs(J[1, 1] / J[0, 0] - 0.25) < 1e-9))
    for vt in (-1.0, 0.3, 0.8):
        vm, c = L.stripe_speed(L.stripe_image(vt, x0=30.0 if vt < 0 else 10.0))
        checks.append((f"blob at {vt:+.1f} px/frame is measured within 0.03 (coherence above 0.95)", abs(vm - vt) < 0.03 and c > 0.95))
    v0, _ = L.stripe_speed(L.stripe_image(0.0))
    checks.append(("a standing blob gives slope 0 and angle 0 degrees", abs(v0) < 1e-9 and abs(L.stripe_angle_deg(v0)) < 1e-9))
    checks.append(("hand calculation: a stripe of 0.8 px/frame is tilted atan(0.8) = 38.7 degrees from the time axis", abs(L.stripe_angle_deg(0.8) - 38.66) < 0.01))
    checks.append(("a 45 degree stripe means 1 px/frame", abs(L.stripe_angle_deg(1.0) - 45.0) < 1e-9))
    vn, cn = L.stripe_speed(np.zeros((10, 10)))
    checks.append(("edge case: a blank image gives nan and coherence 0, not a crash", np.isnan(vn) and cn == 0.0))
    va, _ = L.stripe_speed(L.stripe_image(3.0, x0=5.0, n_x=300))
    checks.append(("limit: at 3 px/frame (blob width 2 px) the gradient method is off by more than 20 percent",
                   abs(va - 3.0) / 3.0 > 0.20))
    checks.append(("design: 0.5 m/s at 2 mm/px needs at least 500 fps", abs(L.min_fps(0.5, 2.0) - 500.0) < 1e-9))
    checks.append(("design: at 30 fps that object moves 8.33 px per frame (too much)",
                   abs(L.shift_per_frame(0.5, 2.0, 30) - 8.3333) < 1e-3))
    checks.append(("design: a 240 fps camera and 0.8 m/s need pixels of at least 6.67 mm",
                   abs(L.min_pixel_mm(0.8, 240) - 6.6667) < 1e-3))
    checks.append(("design: 0.5 px/frame over 40 frames needs a line of 20 pixels", L.min_line_pixels(0.5, 40) == 20))
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
