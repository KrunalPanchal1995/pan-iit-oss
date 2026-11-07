"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    nu = 0.05
    w0 = L.taylor_green_vorticity(32)
    t, E, Z, W, wend, P = L.run_ns2d(w0, nu, 2.0, dt=0.01)
    err = float(np.max(np.abs(wend - w0 * np.exp(-2 * nu * 2.0))))
    checks.append((f"Taylor-Green matches the exact decay exp(-2 nu t) (error {err:.0e} below 1e-10)", err < 1e-10))
    checks.append(("worked example: nu = 0.05, t = 2 gives max|w| = 2 exp(-0.2) = 1.637",
                   abs(W[-1] - 2 * np.exp(-0.2)) < 1e-9 and abs(W[-1] - 1.637) < 0.001))
    checks.append(("Taylor-Green energy decays like exp(-4 nu t): E(2)/E(0) = 0.670",
                   abs(E[-1] / E[0] - np.exp(-0.4)) < 1e-9 and abs(E[-1] / E[0] - 0.670) < 0.001))
    checks.append(("Taylor-Green energy starts at 0.25 and enstrophy at 0.5", abs(E[0] - 0.25) < 1e-12 and abs(Z[0] - 0.5) < 1e-12))

    k2 = 2
    wk, = (L.taylor_green_vorticity(32, k2),)
    tk, Ek, Zk, Wk, wendk, Pk = L.run_ns2d(wk, nu, 0.5, dt=0.01)
    checks.append(("wavenumber k = 2: decay exp(-2 nu k^2 t) (error below 1e-10), enstrophy starts at k^2/2 = 2 and energy at 0.25",
                   np.max(np.abs(wendk - wk * np.exp(-2 * nu * 4 * 0.5))) < 1e-10 and abs(Zk[0] - 2.0) < 1e-12 and abs(Ek[0] - 0.25) < 1e-12))
    nu2 = 0.01
    wr =L.random_vorticity(64)
    t2, E2, Z2, W2, wend2, P2 = L.run_ns2d(wr, nu2, 3.0)
    checks.append(("random initial vorticity has max|w| = 3 and enstrophy 0.356", abs(W2[0] - 3.0) < 1e-9 and abs(Z2[0] - 0.356) < 0.001))
    checks.append(("2-D enstrophy never increases (random start, nu = 0.01)", bool(np.all(np.diff(Z2) <= 1e-12))))
    checks.append(("enstrophy at t = 3 is 52 percent of its initial value", abs(Z2[-1] / Z2[0] - 0.52) < 0.005))
    lost = E2[0] - E2[-1]
    checks.append(("energy balance: E(0) - E(3) = 2 nu * integral of Z (relative error < 1e-5)",
                   abs(lost - 2 * nu2 * L.trapezoid(Z2, t2)) / lost < 1e-5))
    zl = Z2[0] - Z2[-1]
    checks.append(("enstrophy balance: Z(0) - Z(3) = 2 nu * integral of P (relative error < 1e-4)",
                   abs(zl - 2 * nu2 * L.trapezoid(P2, t2)) / zl < 1e-4))
    checks.append(("max|w| stays at or below its initial value (within 0.1 percent)", bool(W2.max() <= W2[0] * 1.001)))
    bkm = L.bkm_integral(t2, W2)
    checks.append(("BKM integral of max|w| over [0, 3] is 7.27 and below 3 * max|w0| = 9",
                   abs(bkm - 7.27) < 0.02 and bkm < 3 * W2[0]))

    u3 = L.taylor_green_3d(16)
    w3, adv, wSw = L.stretching_fields(u3)
    checks.append(("hand check: at (pi/4, pi/4, pi/2) the 3-D vorticity is (-0.5, -0.5, 0)",
                   np.allclose(w3[:, 2, 2, 4], [-0.5, -0.5, 0.0], atol=1e-9)))
    checks.append(("3-D Taylor-Green: enstrophy mean(|w|^2)/2 = 0.375", abs(0.5 * np.mean((w3 ** 2).sum(0)) - 0.375) < 1e-9))
    checks.append(("3-D Taylor-Green: w.S.w ranges over -0.125 to 0.125", abs(wSw.min() + 0.125) < 1e-9 and abs(wSw.max() - 0.125) < 1e-9))
    checks.append(("w.S.w has mean zero: stretching and compression balance", abs(wSw.mean()) < 1e-12))
    checks.append(("about half of the points (49.6 percent) are stretching", abs(100 * np.mean(wSw > 0) - 49.6) < 0.1))
    checks.append(("identity: w . ((w.grad)u) = w.S.w", np.allclose(np.einsum("i...,i...->...", w3, adv), wSw, atol=1e-12)))
    _, adv2, wSw2 = L.stretching_fields(L.taylor_green_3d(16, with_z=False))
    checks.append(("a 2-D flow has no stretching: (w.grad)u = 0 and w.S.w = 0", np.max(np.abs(adv2)) < 1e-12 and np.max(np.abs(wSw2)) < 1e-12))

    inf16 = L.burgers_run(0.01, 16, dealias=False)
    inf32 = L.burgers_run(0.01, 32, dealias=False)
    checks.append(("failure case: nu = 0.01 without dealiasing overflows at N = 16 and N = 32", (not inf16[2]) and (not inf32[2])))
    want = {64: 51.1, 128: 48.8, 256: 48.4}
    got = {n: L.burgers_run(0.01, n, dealias=False) for n in want}
    checks.append(("without dealiasing N = 64, 128, 256 stay finite with peaks 51.1, 48.8, 48.4",
                   all(got[n][2] and abs(got[n][0] - want[n]) < 0.1 for n in want)))
    good = L.burgers_run(0.01, 1024)
    checks.append(("with enough resolution the peak is 48.4 and the energy never exceeds its initial 0.25",
                   good[2] and abs(good[0] - 48.38) < 0.05 and good[1] <= 0.25 + 1e-9))
    coarse = L.burgers_run(0.01, 16)
    checks.append(("a coarse dealiased run does not blow up but reports a false peak of 4.9 (true: 48.4)",
                   coarse[2] and abs(coarse[0] - 4.89) < 0.05))

    rows, first = L.convergence_report(0.015)
    ch = {n: c for n, _, c in rows}
    pk = {n: p for n, p, _ in rows}
    checks.append(("mini-project: nu = 0.015 changes by 5.4 percent from N = 256 to 512 but only 0.2 percent from 512 to 1024",
                   abs(100 * ch[256] - 5.4) < 0.2 and 100 * ch[512] < 0.3))
    checks.append(("mini-project: converged at N = 512 with peak gradient 31.6", first == 512 and abs(pk[512] - 31.63) < 0.05))
    checks.append(("convergence_report returns None when no size converges", L.convergence_report(0.015, sizes=(32, 64))[1] is None))
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
