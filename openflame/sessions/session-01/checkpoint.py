"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    f = L.flame_frame(60)
    checks.append(("a picture has the expected shape and brightness range",
                   f.shape == (L.ROWS, L.COLS) and f.min() >= 0 and f.max() <= 1))
    m = L.flame_mask(f, 0.5)
    hp = L.flame_height_px(m)
    checks.append((f"worked example: a 60 px flame at threshold 0.5 measures 60 px, i.e. 30 mm at 0.5 mm/px (got {hp} px)",
                   hp == 60 and abs(L.height_mm(hp, L.scale_mm_per_px(50, 100)) - 30.0) < 1e-9))
    checks.append(("hand calculation: a 100 px ruler covering 50 mm gives 0.5 mm per pixel",
                   abs(L.scale_mm_per_px(50, 100) - 0.5) < 1e-12))
    # the threshold moves the tip exactly as the closed form says
    ok = True
    for h in (20, 40, 60, 80):
        for t in (0.2, 0.35, 0.5, 0.8):
            ok &= L.flame_height_px(L.flame_mask(L.flame_frame(h), t)) == L.predicted_height_px(h, t)
    checks.append(("measured height equals the closed-form prediction for 16 height/threshold pairs", bool(ok)))
    checks.append(("a lower threshold gives a taller flame, a higher one a shorter flame",
                   L.predicted_height_px(60, 0.2) > L.predicted_height_px(60, 0.5) > L.predicted_height_px(60, 0.8)))
    # edge cases
    checks.append(("edge: threshold 1.0 finds no flame (height 0)", L.flame_height_px(L.flame_mask(f, 1.0)) == 0))
    checks.append(("edge: an empty (black) picture has height 0", L.flame_height_px(L.flame_mask(np.zeros((L.ROWS, L.COLS)), 0.5)) == 0))
    checks.append(("edge: threshold 0 fills the whole column up to the top of the picture",
                   L.flame_height_px(L.flame_mask(f, 0.0)) == L.BASE_ROW and L.predicted_height_px(60, 0.0) == L.BASE_ROW))
    # a video is a stack
    heights = [50, 55, 60, 55, 50]
    stack = L.video_stack(heights)
    checks.append(("a 5-frame video is an array of shape (5, rows, cols)", stack.shape == (5, L.ROWS, L.COLS)))
    checks.append(("the height trace of the stack returns the true heights", list(L.height_trace(stack, 0.5)) == heights))
    # noise: a few stray pixels fool a naive count at a low threshold
    noisy = L.flame_frame(60, noise=0.12, seed=3)
    naive = L.flame_height_px(L.flame_mask(noisy, 0.2), 1)
    guarded = L.flame_height_px(L.flame_mask(noisy, 0.2), 3)
    checks.append((f"noise specks inflate the naive height ({naive} px) more than the guarded one ({guarded} px)",
                   naive > guarded >= 60))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
