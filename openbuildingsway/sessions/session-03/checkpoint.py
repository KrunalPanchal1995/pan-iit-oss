"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def _const_push_ok(L):
    """Constant ground acceleration a=1: u settles to -1/w^2; undamped it swings to -2/w^2."""
    w = 2 * np.pi
    a = np.ones(1001)
    q0, _ = L.sdof_response(w, 1e-9, a, 0.01)
    q1, _ = L.sdof_response(w, 0.1, a, 0.01)
    return abs(q0.min() + 2 / w ** 2) < 1e-4 and abs(q1[-1] + 1 / w ** 2) < 0.05 / w ** 2 and abs(q1.min()) > abs(q1[-1])


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # ---- worked example: a two-storey building by hand ------------------------------------------
    m, k = L.M_FLOOR, L.K_STOREY
    M2, K2 = L.shear_building(2, m, k)
    w2, p2 = L.modes(M2, K2)
    lam = np.array([(3 - np.sqrt(5)) / 2, (3 + np.sqrt(5)) / 2]) * k / m
    checks.append((f"worked example: 2 storeys give w^2 = (3 -/+ sqrt 5)/2 k/m, w = 25.854 and 67.687 rad/s, T = 0.2430 and 0.0928 s (got {w2[0]:.3f}, {w2[1]:.3f})",
                   np.allclose(w2 ** 2, lam) and abs(w2[0] - 25.854) < 5e-3 and abs(w2[1] - 67.687) < 5e-3
                   and abs(2 * np.pi / w2[0] - 0.2430) < 5e-5 and abs(2 * np.pi / w2[1] - 0.0928) < 5e-5))
    s1, s2 = p2[:, 0] / p2[0, 0], p2[:, 1] / p2[0, 1]
    checks.append((f"worked example: mode shapes (1, 1.618) and (1, -0.618) (got {s1[1]:.3f}, {s2[1]:.3f})",
                   abs(s1[1] - (1 + np.sqrt(5)) / 2) < 1e-9 and abs(s1[1] - 1.618) < 5e-4 and abs(s2[1] + 0.618) < 5e-4))
    _, me2 = L.participation(M2, p2)
    checks.append((f"worked example: effective mass fractions 94.7% and 5.3% (got {me2[0] / me2.sum():.3f}, {me2[1] / me2.sum():.3f})",
                   abs(me2[0] / me2.sum() - 0.9472) < 5e-4 and abs(me2[1] / me2.sum() - 0.0528) < 5e-4))

    # ---- matrices -------------------------------------------------------------------------------
    M, K = L.shear_building()
    checks.append(("K is symmetric and tridiagonal; K[0,0] = 2k, last diagonal = k",
                   np.allclose(K, K.T) and np.allclose(np.triu(K, 2), 0) and K[0, 0] == 2 * k and K[-1, -1] == k and K[0, 1] == -k))
    checks.append(("row sums of K are zero except the ground-connected first row (k)", np.allclose(K.sum(axis=1), [k] + [0.0] * 9)))
    w, phi = L.modes(M, K)
    checks.append(("mode shapes are mass-orthonormal: phi^T M phi = I", np.allclose(phi.T @ M @ phi, np.eye(10), atol=1e-9)))
    checks.append(("K phi = w^2 M phi holds for every mode", np.allclose(K @ phi, M @ phi @ np.diag(w ** 2), rtol=1e-8, atol=1e-3)))

    # ---- validation against the analytic uniform-building result --------------------------------
    wa, sa = L.uniform_analytic(10, m, k)
    T = 2 * np.pi / w
    checks.append((f"periods of the 10-storey building: T1 = 1.0049 s, T2 = 0.3375 s, T3 = 0.2056 s (got {T[0]:.4f}, {T[1]:.4f}, {T[2]:.4f})",
                   abs(T[0] - 1.0049) < 5e-5 and abs(T[1] - 0.3375) < 5e-5 and abs(T[2] - 0.2056) < 5e-5))
    checks.append(("numeric frequencies match 2 sqrt(k/m) sin((2i-1) pi / (2(2N+1))) to 1e-12 (relative)", np.allclose(w, wa, rtol=1e-12)))
    shapes = phi / phi[-1, :]
    checks.append(("numeric mode shapes match sin((2i-1) j pi / (2N+1)) to 1e-9", np.allclose(shapes, sa, atol=1e-9)))
    checks.append(("first mode has no sign change, mode 2 has one, mode 3 has two (nodes)",
                   [int((np.diff(np.sign(phi[np.abs(phi[:, i]) > 1e-9 * np.abs(phi[:, i]).max(), i])) != 0).sum()) for i in range(3)] == [0, 1, 2]))
    checks.append(("rule of thumb T = 0.1 N = 1.0 s is close to the computed T1 = 1.005 s", abs(0.1 * 10 - T[0]) < 0.01))

    # ---- participation and effective mass -------------------------------------------------------
    gamma, meff = L.participation(M, phi)
    frac = meff / np.trace(M)
    checks.append((f"effective masses add up to the total mass 2.0e6 kg (sum = {meff.sum():.6g})", abs(meff.sum() - np.trace(M)) < 1e-6 * np.trace(M)))
    checks.append((f"first mode carries 84.8%, second 9.1%, third 3.1% of the mass (got {frac[0]:.3f}, {frac[1]:.3f}, {frac[2]:.3f})",
                   abs(frac[0] - 0.848) < 5e-4 and abs(frac[1] - 0.0914) < 5e-4 and abs(frac[2] - 0.0309) < 5e-4))
    checks.append(("first three modes together carry more than 97 percent", frac[:3].sum() > 0.97))

    # ---- ground record --------------------------------------------------------------------------
    t, ag = L.synthetic_ground()
    dt = t[1] - t[0]
    ag_b = L.synthetic_ground()[1]
    checks.append(("synthetic record is repeatable (same seed gives the same numbers) and differs for another seed",
                   np.array_equal(ag, ag_b) and not np.allclose(ag, L.synthetic_ground(seed=8)[1])))
    checks.append((f"record: 24 s long, dt = 0.01 s, peak exactly 2.0 m/s^2 (got {np.abs(ag).max():.6f})",
                   abs(t[-1] - 24.0) < 1e-9 and abs(dt - 0.01) < 1e-12 and abs(np.abs(ag).max() - 2.0) < 1e-9))
    spec = np.abs(np.fft.rfft(ag))
    freq = np.fft.rfftfreq(ag.size, dt)
    fdom = freq[np.argmax(spec[1:]) + 1]
    checks.append((f"record energy peaks near 1 Hz (dominant period about 1 s): spectral peak at {fdom:.2f} Hz", 0.6 < fdom < 1.5))

    # ---- the two solvers ------------------------------------------------------------------------
    C = L.damping_matrix(M, phi, w)
    gen = phi.T @ C @ phi
    checks.append(("damping matrix gives zeta = 0.05 in every mode", np.allclose(np.diag(gen) / (2 * w), 0.05) and np.allclose(gen, np.diag(np.diag(gen)), atol=1e-6)))
    un, vn, an = L.newmark(M, C, K, ag, dt)
    um = L.modal_response(M, K, ag, dt)
    rel = np.abs(um - un).max() / np.abs(un).max()
    checks.append((f"modal superposition and Newmark agree to within 1 percent of the peak (got {100 * rel:.2f} percent)", rel < 0.01))
    checks.append(("exact one-mode step is right in a simple case: a constant push settles to -1/w^2 and (undamped) swings to -2/w^2", _const_push_ok(L)))
    t2, ag2 = L.synthetic_ground(dt=0.005)
    u2, _, _ = L.newmark(M, C, K, ag2, 0.005)
    diff = np.abs(u2[::2][:un.shape[0]] - un).max() / np.abs(un).max()
    checks.append((f"Newmark with half the time step changes the answer by only {100 * diff:.2f} percent", diff < 0.005))
    checks.append(("Newmark parameters: average acceleration beta = 1/4 and gamma = 1/2 are the defaults", L.newmark.__defaults__ == (0.25, 0.5)))
    C0 = 0 * C
    u0, v0, _ = L.newmark(M, C0, K, ag, dt)
    ein0, es0 = L.energy_balance(M, C0, K, u0, v0, ag, dt)
    checks.append((f"undamped: input energy equals stored energy to 0.5 percent ({ein0[-1]:.4g} J vs {es0[-1]:.4g} J)",
                   abs(ein0[-1] - es0[-1]) / abs(ein0[-1]) < 5e-3))
    ein, eacc = L.energy_balance(M, C, K, un, vn, ag, dt)
    checks.append((f"damped: input 3.641e6 J equals kinetic + strain + dissipated to 1e-4 (got {ein[-1]:.4g}, {eacc[-1]:.4g})",
                   abs(ein[-1] - eacc[-1]) / ein[-1] < 1e-4 and abs(ein[-1] - 3.641e6) < 5e3))

    # ---- responses ------------------------------------------------------------------------------
    roof = np.abs(un[:, -1]).max()
    drift = np.abs(L.storey_drift(un)).max(axis=0)
    shear = np.abs(L.base_shear(un, k)).max()
    checks.append((f"peak roof displacement 0.172 m (got {roof:.4f}); peak drift 25.1 mm in storey 1, 3.9 mm in storey 10 (got {1e3 * drift[0]:.1f}, {1e3 * drift[-1]:.1f})",
                   abs(roof - 0.1719) < 5e-4 and int(np.argmax(drift)) == 0 and abs(1e3 * drift[0] - 25.1) < 0.05 and abs(1e3 * drift[-1] - 3.9) < 0.05))
    checks.append((f"drift ratio 25.1 mm / 3.5 m = 0.72 percent; peak base shear 8.77 MN (got {shear / 1e6:.2f}), 0.45 of the weight 19.6 MN",
                   abs(drift[0] / L.STOREY_HEIGHT * 100 - 0.72) < 0.01 and abs(shear / 1e6 - 8.77) < 0.01
                   and abs(shear / (2e6 * 9.81) - 0.447) < 0.002))
    sm = np.abs(L.base_shear(um, k)).max()
    checks.append(("base shear from modal superposition is within 0.3 percent of Newmark", abs(sm - shear) / shear < 0.003))
    roof1 = np.abs(L.modal_response(M, K, ag, dt, nmodes=1)[:, -1]).max()
    checks.append((f"mode 1 alone gives the peak roof displacement within 1 percent (got {roof1:.4f} m)", abs(roof1 - roof) / roof < 0.01))
    sd1 = L.sdof_peak(1.0, 0.05, ag, dt)
    sd_short = L.sdof_peak(0.2, 0.05, ag, dt)
    checks.append((f"response spectrum: oscillator with T = 1.0 s moves {1e3 * sd1:.0f} mm, T = 0.2 s only {1e3 * sd_short:.0f} mm", sd1 > 10 * sd_short))

    # ---- sensitivity ----------------------------------------------------------------------------
    p_base = L.peaks()
    checks.append(("peaks() reproduces the Newmark run (roof, drift, T1 = 1.0049 s)",
                   abs(p_base["roof"] - roof) < 1e-12 and abs(p_base["T1"] - 1.0049) < 5e-5))
    z2, z10 = L.peaks(zeta=0.02), L.peaks(zeta=0.10)
    checks.append((f"damping sensitivity: roof peak {1e3 * z2['roof']:.0f} mm at 2%, {1e3 * p_base['roof']:.0f} mm at 5%, {1e3 * z10['roof']:.0f} mm at 10%",
                   z2["roof"] > p_base["roof"] > z10["roof"] and abs(1e3 * z2["roof"] - 259) < 1 and abs(1e3 * z10["roof"] - 163) < 1))
    s08, s12 = L.peaks(k=0.8 * k), L.peaks(k=1.2 * k)
    checks.append((f"stiffness sensitivity: 20 percent softer gives T1 = {s08['T1']:.3f} s and roof {1e3 * s08['roof']:.0f} mm; 20 percent stiffer gives T1 = {s12['T1']:.3f} s and roof {1e3 * s12['roof']:.0f} mm",
                   abs(s08["T1"] - 1.1235) < 5e-4 and abs(s12["T1"] - 0.9174) < 5e-4 and abs(1e3 * s08["roof"] - 274) < 1 and abs(1e3 * s12["roof"] - 191) < 1
                   and abs(s12["T1"] * np.sqrt(1.2) - p_base["T1"]) < 1e-9))

    # ---- failure case: soft storey --------------------------------------------------------------
    Ms, Ks = L.shear_building(k=L.soft_storey_stiffness())
    ws, ps = L.modes(Ms, Ks)
    Cs = L.damping_matrix(Ms, ps, ws)
    us, _, _ = L.newmark(Ms, Cs, Ks, ag, dt)
    ds = np.abs(L.storey_drift(us)).max(axis=0)
    checks.append((f"soft storey (storey 1 at 35 percent stiffness): storey-1 drift 95.3 mm, 3.8 times the uniform building (got {1e3 * ds[0]:.1f} mm, x{ds[0] / drift[0]:.2f})",
                   abs(1e3 * ds[0] - 95.3) < 0.1 and abs(ds[0] / drift[0] - 3.80) < 0.01 and int(np.argmax(ds)) == 0))
    shape1 = ps[:, 0] / ps[-1, 0]
    d1 = np.diff(np.r_[0, shape1])
    d0 = np.diff(np.r_[0, (lambda q: q[:, 0] / q[-1, 0])(phi)])
    checks.append((f"first-mode shape: storey 1 takes {100 * d1[0]:.1f} percent of the roof displacement when soft (against {100 * d0[0]:.1f} percent when uniform)",
                   abs(100 * d1[0] - 35.0) < 0.1 and abs(100 * d0[0] - 14.9) < 0.1))
    checks.append((f"the soft storey lengthens the first period (T1 1.0049 s -> {2 * np.pi / ws[0]:.3f} s)", abs(2 * np.pi / ws[0] - 1.176) < 0.001 and ws[0] < w[0]))

    # ---- stretch: tuned mass damper -------------------------------------------------------------
    tt, ah = L.resonant_ground(w[0])
    uh, _, _ = L.newmark(M, C, K, ah, 0.01)
    M3, C3, K3 = L.with_damper(M, K, w[0], 0.05, 0.15)
    u3, _, _ = L.newmark(M3, C3, K3, ah, 0.01)
    ratio = np.abs(u3[:, 9]).max() / np.abs(uh[:, 9]).max()
    checks.append((f"tuned mass damper (5 percent of the mass, tuned to mode 1) cuts the resonant roof sway to {100 * ratio:.0f} percent of the bare building",
                   ratio < 0.4 and abs(ratio - 0.31) < 0.02))
    checks.append(("damper adds one degree of freedom and keeps the matrices symmetric", M3.shape == (11, 11) and np.allclose(K3, K3.T) and np.allclose(C3, C3.T)))

    # ---- mini-project: stiffen the 10-storey frame ----------------------------------------------
    base = L.peaks()
    rows = {f: L.peaks(k=f * k) for f in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)}
    ok_f = [f for f, r in rows.items() if r["roof"] <= 0.5 * base["roof"] and r["drift"] / L.STOREY_HEIGHT <= 0.005]
    checks.append((f"mini-project: smallest stiffness factor (steps of 0.5) with roof sway at most half of the original and drift ratio at most 0.5 percent is 3.0 (got {min(ok_f) if ok_f else None})",
                   bool(ok_f) and min(ok_f) == 3.0 and 1.0 not in ok_f))
    r3 = rows[3.0]
    checks.append((f"mini-project: factor 3 gives T1 = 0.580 s, roof {1e3 * r3['roof']:.0f} mm, drift ratio {100 * r3['drift'] / L.STOREY_HEIGHT:.2f} percent, base shear {r3['shear'] / 1e6:.2f} MN",
                   abs(r3["T1"] - 0.5802) < 5e-4 and abs(1e3 * r3["roof"] - 63.3) < 0.1 and abs(100 * r3["drift"] / L.STOREY_HEIGHT - 0.28) < 0.005
                   and abs(r3["shear"] / 1e6 - 10.37) < 0.01))
    checks.append(("mini-project trade-off: the stiffer building has the larger base shear (10.37 against 8.77 MN)", r3["shear"] > base["shear"]))
    checks.append(("mini-project: factor 1.5 does not help (roof 173 mm, no lower than the original 172 mm): a record is not one frequency",
                   abs(1e3 * rows[1.5]["roof"] - 173.3) < 0.1 and rows[1.5]["roof"] > base["roof"]))
    cuts = [L.peaks(k=3 * k, seed=s)["roof"] < 0.5 * L.peaks(seed=s)["roof"] for s in (1, 2, 3, 4, 5, 6)]
    checks.append(("mini-project: factor 3 more than halves the roof sway for each of six other random seeds (1 to 6)", all(cuts)))
    r = base["T1"] / 1.0
    checks.append(("first-mode amplification D(T1 / Tg) for the original frame is 9.9 (near resonance), and 1.50 at factor 3",
                   abs(1 / np.sqrt((1 - r ** 2) ** 2 + (0.1 * r) ** 2) - 9.9) < 0.05
                   and abs(1 / np.sqrt((1 - r3["T1"] ** 2) ** 2 + (0.1 * r3["T1"]) ** 2) - 1.50) < 0.01))
    Mb, Kb = L.shear_building(2, 1e5, 1e8)
    wb, _ = L.modes(Mb, Kb)
    checks.append(("B: two storeys with m = 100000 kg, k = 1e8 N/m: w = 19.544 and 51.167 rad/s, T = 0.3215 and 0.1228 s",
                   abs(wb[0] - 19.544) < 5e-4 and abs(wb[1] - 51.167) < 5e-4 and abs(2 * np.pi / wb[0] - 0.3215) < 5e-5 and abs(2 * np.pi / wb[1] - 0.1228) < 5e-5))
    res = {}
    for f in (0.35, 0.6, 0.7, 1.0):
        Mf, Kf = L.shear_building(k=L.soft_storey_stiffness(factor=f))
        wf, pf = L.modes(Mf, Kf)
        uf, _, _ = L.newmark(Mf, L.damping_matrix(Mf, pf, wf), Kf, ag, dt)
        df = np.abs(L.storey_drift(uf)).max(axis=0)
        res[f] = (df[0], df[0] / df[1:].max())
    checks.append((f"D: weak storey at 0.7 gives storey-1 drift 43.5 mm, 1.46 times the largest other storey (within 1.5); at 0.6 it is 1.71 times",
                   abs(1e3 * res[0.7][0] - 43.5) < 0.1 and abs(res[0.7][1] - 1.46) < 0.01 and abs(res[0.6][1] - 1.71) < 0.01
                   and abs(1e3 * res[0.6][0] - 55.4) < 0.1 and abs(res[0.35][1] - 2.97) < 0.01 and abs(res[1.0][1] - 1.01) < 0.01))
    checks.append((f"frequency ratios: T1 / T2 = 2.98 for ten storeys and 2.62 for two storeys; storey-1 drift ratio {1e3 * ds[0] / 3.5:.0f} -> 2.7 percent with a soft storey",
                   abs(w[1] / w[0] - 2.977) < 5e-3 and abs(w2[1] / w2[0] - 2.618) < 5e-3 and abs(ds[0] / L.STOREY_HEIGHT * 100 - 2.72) < 0.01))
    M1, K1 = L.shear_building(1, m, k)
    w1, _ = L.modes(M1, K1)
    checks.append(("edge: one storey reduces to w = sqrt(k/m) from Session 2", abs(w1[0] - np.sqrt(k / m)) < 1e-9))
    # ---- Rayleigh damping -----------------------------------------------------------------------
    for pair in ((0, 2), (0, 9), (1, 4)):
        Cr, a0r, a1r = L.rayleigh_damping(M, K, w, pair)
        zr = L.rayleigh_ratio(w, a0r, a1r)
        checks.append((f"Rayleigh damping anchored at modes {pair[0] + 1} and {pair[1] + 1}: 5% at both (got {100 * zr[pair[0]]:.3f}%, {100 * zr[pair[1]]:.3f}%)",
                       abs(zr[pair[0]] - 0.05) < 1e-12 and abs(zr[pair[1]] - 0.05) < 1e-12))
    Cr, a0r, a1r = L.rayleigh_damping(M, K, w, (0, 2))
    D = phi.T @ Cr @ phi
    checks.append(("Rayleigh C is diagonal in the modes and phi^T C phi = 2 zeta(w) w (an independent check of the formula)",
                   np.abs(D - np.diag(np.diag(D))).max() < 1e-6 * np.diag(D).max()
                   and np.allclose(np.diag(D), 2 * w * L.rayleigh_ratio(w, a0r, a1r), rtol=1e-9)))
    zr = L.rayleigh_ratio(w, a0r, a1r)
    checks.append(("with modes 1 and 3 anchored, mode 2 is below 5% and every mode above 3 is above 5%",
                   zr[1] < 0.05 and np.all(zr[3:] > 0.05)))
    a0u, a1u = L.rayleigh_coefficients(10.0, 40.0, 0.02, 0.05)
    checks.append(("different targets work too: 2% at 10 rad/s and 5% at 40 rad/s",
                   abs(L.rayleigh_ratio(10.0, a0u, a1u) - 0.02) < 1e-12 and abs(L.rayleigh_ratio(40.0, a0u, a1u) - 0.05) < 1e-12))
    ag_ = L.synthetic_ground()
    dt_ = ag_[0][1] - ag_[0][0]
    u_mod = L.newmark(M, L.damping_matrix(M, phi, w), K, ag_[1], dt_)[0]
    u_ray = L.newmark(M, Cr, K, ag_[1], dt_)[0]
    pk_m, pk_r = np.abs(u_mod[:, -1]).max(), np.abs(u_ray[:, -1]).max()
    checks.append((f"same 5% in the dominant modes gives about the same roof peak: modal {pk_m * 1e3:.1f} mm, Rayleigh {pk_r * 1e3:.1f} mm (within 5%)",
                   abs(pk_r - pk_m) / pk_m < 0.05))
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
