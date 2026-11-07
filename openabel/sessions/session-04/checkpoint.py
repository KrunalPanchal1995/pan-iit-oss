"""Checkpoint for Session 4. Prints PASS or FAIL."""
import inspect

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    N = 40

    # ---- the smoother and its hat matrix -------------------------------------------------------
    A0 = L.smoother(N, 0.0, 6.0)[1]
    A3 = L.smoother(N, 3.0, 6.0)[1]
    checks.append(("hat matrix is symmetric, and equals the identity when lam = 0 (the photo is copied)",
                   np.allclose(A3, A3.T, atol=1e-12) and np.allclose(A0, np.eye(N), atol=1e-9)))
    dfs = [L.effective_parameters(N, l, 6.0) for l in (0.0, 0.01, 0.3, 3.0, 100.0, 1e8)]
    checks.append((f"effective parameters fall from {dfs[0]:.0f} (lam = 0) to {dfs[-1]:.2f} (huge lam: only a straight line is left)",
                   all(a > b for a, b in zip(dfs, dfs[1:])) and abs(dfs[0] - N) < 1e-6 and abs(dfs[-1] - 2.0) < 0.01))

    # ---- noise size from the photo -------------------------------------------------------------
    rng = np.random.default_rng(5)
    white = 0.2 * rng.standard_normal((20, 400))
    checks.append(("pure noise of size 0.2: the curvature estimate gives 0.2 within 3%, the margin estimate within 8%",
                   abs(L.noise_sigma(white) / 0.2 - 1) < 0.03 and abs(L.noise_sigma_margin(white, 100) / 0.2 - 1) < 0.08))
    clean = L.clean_candle(N)
    checks.append((f"a noise-free candle photo reads as almost no noise ({L.noise_sigma(clean) / clean.max():.4f} of the peak): flame curvature does not fool the estimate",
                   L.noise_sigma(clean) < 0.002 * clean.max()))
    rng = np.random.default_rng(0)
    ratios = []
    for _ in range(20):
        img, sigma = L.noisy_candle(clean, 0.03, rng)
        ratios.append(L.noise_sigma(img) / sigma)
    ratios = np.array(ratios)
    checks.append((f"3% candle photo, 20 draws: estimated / true noise averages {ratios.mean():.3f} (0.97 to 1.03) and stays within 15% every time",
                   0.97 < ratios.mean() < 1.03 and ratios.min() > 0.85 and ratios.max() < 1.15))

    # ---- cross-validation shortcut: independent check by refitting -----------------------------
    I0 = L.photo_profile(lambda r: L.ring_eps(r, 1.5, 0.4), N, L.R_MM)
    rng = np.random.default_rng(2)
    Iy = I0 + 0.02 * I0.max() * rng.standard_normal(N)
    worst = 0.0
    for lam in (0.01, 0.3, 3.0):
        sc = L.loo_shortcut(Iy, lam, L.R_MM)
        brute = np.array([L.loo_refit(Iy, lam, i, L.R_MM) for i in range(N)])
        worst = max(worst, float(np.max(np.abs(sc - brute))))
    checks.append((f"leave-one-out shortcut r_i / (1 - A_ii) equals honest refitting for every pixel and 3 values of lam (largest difference {worst:.1e})",
                   worst < 1e-9))

    # ---- UPRE really is unbiased: Monte Carlo against the exact risk ----------------------------
    sig = 0.01 * I0.max()
    rng = np.random.default_rng(1)
    ok_up = True
    detail = []
    for lam in (0.01, 0.3, 3.0):
        A = L.smoother(N, lam, L.R_MM)[1]
        risk = np.sum(((A - np.eye(N)) @ I0) ** 2) + sig ** 2 * np.trace(A.T @ A)
        mean_up = np.mean([L.upre_score(I0 + sig * rng.standard_normal(N), lam, sig, L.R_MM) for _ in range(3000)])
        detail.append(mean_up / risk)
        ok_up &= abs(mean_up / risk - 1) < 0.03
    checks.append((f"UPRE averaged over 3000 noise draws matches the exact prediction error |A I - I_clean|^2 within 3% (ratios {', '.join(f'{d:.3f}' for d in detail)})", ok_up))

    # ---- the rules look at the photo only ------------------------------------------------------
    img, sigma = L.noisy_candle(clean, 0.03, np.random.default_rng(3))
    same = all(L.choose_lam(img, m) == L.choose_lam(7.0 * img, m) for m in ("gcv", "upre", "discrepancy"))
    checks.append(("choosing lam does not depend on the brightness units: a photo 7 times brighter gives the same lam for all three rules", same))
    params = set(inspect.signature(L.choose_lam).parameters)
    checks.append(("choose_lam takes only the photo (and the settings of the rule): no truth, no emission function among its inputs",
                   params <= {"img", "method", "sigma", "lams", "R"}))
    checks.append(("a photo with no noise (sigma = 0) is not smoothed: UPRE and the discrepancy rule pick the weakest lam in the grid",
                   L.choose_lam(clean, "upre", sigma=0.0) == L.LAMS[0] and L.choose_lam(clean, "discrepancy", sigma=0.0) == L.LAMS[0]))
    checks.append(("lam = 0 copies the photo, so GCV scores it as infinite instead of dividing by zero",
                   L.gcv_score(img, 0.0) == float("inf") and np.isfinite(L.gcv_score(img, 0.01))))
    checks.append(("a single profile and the same profile as one row of a table give the same lam",
                   L.choose_lam(img[7], "gcv") == L.choose_lam(img[7:8], "gcv")))

    # ---- the candle over 20 noise draws ---------------------------------------------------------
    res = L.compare_methods(clean, 0.03, 20, seed=0)
    up, gp, gr = res["UPRE, all rows"], res["GCV, all rows"], res["GCV, one row each"]
    orc, fx, dp = res["oracle (peeks at truth)"], res["fixed lam = 3"], res["discrepancy, all rows"]
    checks.append((f"UPRE on all rows, no peeking: mean worst-row error {up.mean():.3f} over 20 draws (limit 0.055), median {np.median(up):.3f} (limit 0.050)",
                   up.mean() <= 0.055 and np.median(up) <= 0.050))
    checks.append((f"it is within 25% of the oracle that looks at the truth ({orc.mean():.3f}) and no worse than the fixed lam = 3 tuned with the truth ({fx.mean():.3f})",
                   up.mean() <= 1.25 * orc.mean() and up.mean() <= fx.mean()))
    checks.append((f"GCV also works when it sees all rows ({gp.mean():.3f}); the same rule applied to one row at a time is worse and erratic (mean {gr.mean():.3f}, worst draw {gr.max():.3f} against {gp.max():.3f})",
                   gp.mean() <= 0.055 and gr.mean() > gp.mean() + 0.01 and gr.max() > 1.5 * gp.max()))
    rng = np.random.default_rng(0)
    larger = 0
    for _ in range(20):
        im, _s = L.noisy_candle(clean, 0.03, rng)
        larger += L.choose_lam(im, "discrepancy") > L.choose_lam(im, "upre")
    checks.append((f"the classical discrepancy rule over-smooths: its lam is larger than UPRE's on every draw and its mean error {dp.mean():.3f} is the worst of the rules that see all rows",
                   larger == 20 and dp.mean() > up.mean() + 0.015 and dp.mean() > gp.mean() + 0.015))
    n_up, n_or = int(np.sum(up <= 0.05)), int(np.sum(orc <= 0.05))
    checks.append((f"honest limit of the roadmap line: draws reaching 0.05 are {n_up} of 20 for UPRE and only {n_or} of 20 even for the oracle; no single lam can reach 0.05 every time",
                   n_or <= 16 and n_up >= n_or - 3 and up.max() <= 0.10))

    # ---- edge cases -----------------------------------------------------------------------------
    errs = 0
    for fn in (lambda: L.noise_sigma(np.zeros((3, 3))), lambda: L.noise_sigma_margin(np.zeros((5, 10)), 1),
               lambda: L.choose_lam(img, "bogus")):
        try:
            fn()
        except ValueError:
            errs += 1
    checks.append(("too few pixels, a silly margin width and an unknown rule are refused with a clear error", errs == 3))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson4", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
