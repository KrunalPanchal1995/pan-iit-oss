"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    xg = np.linspace(0, 2 * np.pi, 2001)
    checks.append(("worked example: u0 = sin x has shock time t* = 1 / max(-cos x) = 1",
                   abs(L.shock_time(np.cos(xg)) - 1.0) < 1e-9))
    checks.append(("hand check: u0 = 2 sin x steepens twice as fast, t* = 0.5", abs(L.shock_time(2 * np.cos(xg)) - 0.5) < 1e-9))
    checks.append(("a profile that never decreases (u0' >= 0) has no shock time", L.shock_time(np.ones(10)) == float("inf")))

    h = 1e-5
    for t, want, tol in ((0.5, -2.0, 1e-3), (0.9, -10.0, 1e-2), (0.99, -100.0, 0.5)):
        fd = (L.characteristic_profile(np.array([np.pi + h]), t)[0] - L.characteristic_profile(np.array([np.pi - h]), t)[0]) / (2 * h)
        checks.append((f"inviscid slope at x = pi, t = {t}: finite difference equals -1/(1-t) = {want}",
                       abs(fd - want) < tol and abs(L.inviscid_slope_at_pi(t) - want) < 1e-9))

    x = np.linspace(0, 2 * np.pi, 7)
    checks.append(("Cole-Hopf at t = 0 returns sin x", np.allclose(L.cole_hopf(x, 0.0, 0.1), np.sin(x), atol=1e-9)))
    checks.append(("Cole-Hopf stays bounded by 1 (the maximum principle) at t = 1.5, nu = 0.05",
                   float(np.max(np.abs(L.cole_hopf(np.linspace(0, 2 * np.pi, 400), 1.5, 0.05)))) <= 1.0 + 1e-12))
    for nu, n, t in ((0.1, 128, 1.0), (0.05, 256, 1.5)):
        r = L.solve_burgers(nu, n, t, dt=0.002)
        err = float(np.max(np.abs(r["u"] - L.cole_hopf(r["x"], t, nu))))
        checks.append((f"pseudo-spectral solver matches exact Cole-Hopf (nu = {nu}, N = {n}, t = {t}): error {err:.1e} below 1e-6", err < 1e-6))
        if n == 128:
            e128 = err
    e64 = float(np.max(np.abs(L.solve_burgers(0.1, 64, 1.0, dt=0.005)["u"] - L.cole_hopf(2 * np.pi * np.arange(64) / 64, 1.0, 0.1))))
    checks.append(("error shrinks with resolution: N = 64 has error above 1e-5, N = 128 below 1e-7", 1e-5 < e64 and e128 < 1e-7))

    s4 = L.solve_burgers(0.04, 512, 1.7)
    checks.append(("exact slope at x = pi (nu = 0.04, t = 1.7) is -10.78 and equals the solver's peak gradient",
                   abs(L.cole_hopf_slope_at_pi(1.7, 0.04) + 10.78) < 0.005 and abs(-L.cole_hopf_slope_at_pi(1.7, 0.04) - s4["peak"][-1]) < 1e-4))
    checks.append(("exact slope at x = pi stays below -9 for nu = 0.04 at t = 1.4, 1.7, 2.0 and is above -9 for nu = 0.1 at t = 1.0",
                   all(L.cole_hopf_slope_at_pi(t, 0.04) < -9 for t in (1.4, 1.7, 2.0)) and L.cole_hopf_slope_at_pi(1.0, 0.1) > -9))
    rb = L.solve_burgers(0.02, 1024, 1.5)
    with np.errstate(all="ignore"):
        bad = np.abs(L.cole_hopf(rb["x"], 1.5, 0.02) - rb["u"])
    checks.append(("limit case: in double precision the Cole-Hopf formula is wrong (error above 1) at nu = 0.02",
                   bool(np.nanmax(bad) > 1.0 or np.any(np.isnan(bad)))))
    r = L.solve_burgers(0.05, 256, 3.0)
    lost = r["energy"][0] - r["energy"][-1]
    gained = L.trapezoid(r["diss"], r["t"])
    checks.append(("initial energy E(0) = 0.25", abs(r["energy"][0] - 0.25) < 1e-12))
    checks.append(("energy balance: E(0) - E(T) equals the time integral of nu * mean(u_x^2) (relative error < 1e-4)",
                   abs(lost - gained) / lost < 1e-4))
    checks.append(("energy never increases", bool(np.all(np.diff(r["energy"]) <= 1e-14))))
    i = 300
    dEdt = (r["energy"][i + 1] - r["energy"][i - 1]) / (r["t"][i + 1] - r["t"][i - 1])
    checks.append(("dE/dt = -nu mean(u_x^2) at t = 1.2 (relative error < 1e-3)", abs(dEdt + r["diss"][i]) / abs(dEdt) < 1e-3))

    res = {nu: L.peak_gradient(nu, 1024) for nu in (0.08, 0.04, 0.02, 0.01)}
    checks.append(("peak |u_x| at nu = 0.04 is 10.78 and at nu = 0.02 is 23.31",
                   abs(res[0.04] - 10.78) < 0.02 and abs(res[0.02] - 23.31) < 0.05))
    checks.append(("halving nu multiplies the peak gradient by 2.0 to 2.3",
                   all(2.0 < res[a] / res[b] < 2.3 for a, b in ((0.04, 0.08), (0.02, 0.04), (0.01, 0.02)))))
    checks.append(("nu * peak is 0.385, 0.431, 0.466, 0.484 for nu = 0.08, 0.04, 0.02, 0.01 and stays below 0.5",
                   all(abs(nu * res[nu] - w) < 0.002 for nu, w in zip((0.08, 0.04, 0.02, 0.01), (0.385, 0.431, 0.466, 0.484)))))

    dpeak, tpeak = {}, {}
    for nu in (0.08, 0.04, 0.02, 0.01):
        rr = L.solve_burgers(nu, 1024, 3.0)
        dpeak[nu], tpeak[nu] = float(rr["diss"].max()), float(rr["t"][rr["diss"].argmax()])
    checks.append(("peak dissipation rate is 0.079, 0.089, 0.098, 0.102 for nu = 0.08, 0.04, 0.02, 0.01: it grows by only 30 percent while the peak gradient grows 10 times",
                   all(abs(dpeak[nu] - w) < 0.002 for nu, w in zip((0.08, 0.04, 0.02, 0.01), (0.079, 0.089, 0.098, 0.102)))
                   and dpeak[0.01] / dpeak[0.08] < 1.35 and res[0.01] / res[0.08] > 10))
    checks.append(("the dissipation spike happens between t = 1.5 and t = 1.7 for every nu", all(1.5 < tpeak[nu] < 1.7 for nu in tpeak)))
    table, ref = L.convergence_table(0.02)
    err = {n: e for n, _, e in table}
    checks.append(("nu = 0.02: reference peak is 23.31", abs(ref - 23.31) < 0.01))
    checks.append(("nu = 0.02: N = 64 is more than 40 percent off, N = 256 is 1.7 percent off, N = 512 is below 0.2 percent",
                   err[64] > 0.40 and 0.015 < err[256] < 0.02 and err[512] < 0.002))
    checks.append(("nu = 0.02 needs N = 512 for 1 percent accuracy", L.smallest_resolved(0.02, sizes=(256, 512, 1024)) == 512))
    checks.append(("nu = 0.04 needs N = 256 and nu = 0.01 needs N = 1024 (N doubles when nu halves)",
                   L.smallest_resolved(0.04, sizes=(128, 256)) == 256 and L.smallest_resolved(0.01, sizes=(512, 1024)) == 1024))
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
