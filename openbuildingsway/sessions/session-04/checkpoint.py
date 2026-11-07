"""Checkpoint for Session 4. Prints PASS or FAIL."""
import numpy as np


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    M, K = L.shear_building()
    t, ag = L.synthetic_ground()
    dt = t[1] - t[0]
    T, w, phi, gamma, meff = L.modal_data(M, K)
    sd = L.spectrum_function(ag, dt)
    k1 = L.K_STOREY
    tot = float(np.trace(M))

    # ---- worked example: the first three modes of the ten-storey frame ---------------------------
    checks.append((f"worked example: periods 1.005, 0.337 and 0.206 s, effective mass shares 84.8, 9.1 and 3.1 percent (got {T[0]:.3f}, {T[1]:.3f}, {T[2]:.3f})",
                   np.allclose(T[:3], [1.005, 0.337, 0.206], atol=6e-4) and np.allclose(meff[:3] / tot, [0.848, 0.091, 0.031], atol=6e-4)))
    sdv = np.array([sd(T[i]) for i in range(3)])
    sav = w[:3] ** 2 * sdv
    checks.append((f"worked example: spectrum values S_a = 5.29, 2.73 and 2.19 m/s^2, that is {sav[0] / 2:.2f}, {sav[1] / 2:.2f} and {sav[2] / 2:.2f} times the peak ground acceleration",
                   np.allclose(sav, [5.286, 2.726, 2.188], atol=5e-3)))
    v = L.modal_base_shears(M, K, sd, 3)
    checks.append((f"worked example: modal base shears V = M* S_a = 8.964, 0.498 and 0.135 MN (got {v[0] / 1e6:.3f}, {v[1] / 1e6:.3f}, {v[2] / 1e6:.3f})",
                   np.allclose(v / 1e6, [8.964, 0.498, 0.135], atol=1e-3)))
    th = L.time_history_base_shear(M, K, k1, ag, dt)
    est = L.shortcut_base_shear(M, K, ag, dt, 3)
    err = est / th - 1
    checks.append((f"worked example: SRSS = {est / 1e6:.3f} MN (8.979) against the time history {th / 1e6:.3f} MN (8.775): {100 * err:+.1f} percent",
                   abs(est / 1e6 - 8.979) < 1e-3 and abs(th / 1e6 - 8.775) < 1e-3 and abs(err - 0.023) < 5e-4))
    checks.append((f"roadmap checkpoint: the first three modes by SRSS are within 5 percent of the full run (error {100 * err:+.1f} percent)",
                   abs(err) < 0.05))

    # ---- the base shear of one mode, two ways ----------------------------------------------------
    full = L.modal_base_shears(M, K, sd)
    chk = L.modal_base_shears_check(M, K, sd, k1)
    checks.append(("V_i = M*_i S_a equals k_1 Gamma_i phi_1,i S_d for all 10 modes (equilibrium of the lowest storey)",
                   full.shape == (10,) and np.allclose(full, chk, rtol=1e-9)))
    flat = lambda T_: 3.0 / (2 * np.pi / T_) ** 2          # flat pseudo-acceleration of 3 m/s^2
    vf = L.modal_base_shears(M, K, flat)
    checks.append(("flat spectrum S_a = 3 m/s^2: the effective masses add up to the whole mass, so the sum of the V_i is 3 m total",
                   abs(L.abs_sum(vf) - 3.0 * tot) < 1e-6 * 3.0 * tot))
    checks.append(("effective mass: first mode 84.8 percent, two modes reach 90 percent (modes_needed = 2), 95 percent needs 3, 100 percent needs 10",
                   L.modes_needed(meff) == 2 and L.modes_needed(meff, 0.95) == 3 and L.modes_needed(meff, 1.0) == 10))

    # ---- the combination rules -------------------------------------------------------------------
    checks.append(("SRSS(3, 4) = 5 and the sum of absolute values of (3, -4) = 7",
                   abs(L.srss([3, 4]) - 5.0) < 1e-12 and abs(L.abs_sum([3, -4]) - 7.0) < 1e-12))
    s3, a3 = L.srss(full[:3]), L.abs_sum(full[:3])
    checks.append((f"order: largest modal shear <= SRSS <= sum; sum of 3 modes is {100 * (a3 / th - 1):+.1f} percent from the time history",
                   full[0] <= s3 <= a3 and abs(a3 / th - 1 - 0.094) < 2e-3))
    checks.append(("CQC correlation: 1 for equal frequencies, small (< 0.01) for a frequency ratio of 3, and it depends only on the frequency ratio",
                   abs(L.cqc_correlation(5.0, 5.0) - 1.0) < 1e-12 and L.cqc_correlation(1.0, 3.0) < 0.01
                   and abs(L.cqc_correlation(2.0, 4.0) - L.cqc_correlation(1.0, 2.0)) < 1e-12))
    checks.append(("CQC of two modes with the same frequency equals their plain sum (they peak together)",
                   abs(L.cqc([3.0, 4.0], [7.0, 7.0]) - 7.0) < 1e-9))
    checks.append(("CQC of the well-separated modes of this frame agrees with SRSS within 0.5 percent",
                   abs(L.cqc(full[:3], w[:3]) / s3 - 1) < 5e-3))
    checks.append(("limit: an unknown rule, 0 modes, 11 modes or 2.5 modes is rejected",
                   _raises(lambda: L.shortcut_base_shear(M, K, ag, dt, 3, "abc")) and _raises(lambda: L.modal_base_shears(M, K, sd, 0))
                   and _raises(lambda: L.modal_base_shears(M, K, sd, 11)) and _raises(lambda: L.modal_base_shears(M, K, sd, 2.5))))

    # ---- the spectrum ----------------------------------------------------------------------------
    grid = np.linspace(0.1, 3.0, 146)
    sdg, sag = L.response_spectrum(grid, ag, dt)
    pga = float(np.abs(ag).max())
    checks.append((f"spectrum: very stiff oscillators follow the ground (S_a / PGA = {sag[0] / pga:.2f} at 0.1 s, within 5 percent of 1)",
                   abs(sag[0] / pga - 1.0) < 0.05 and abs(L.response_spectrum(0.05, ag, dt)[1][0] / pga - 1.0) < 0.05))
    imax = int(np.argmax(sag))
    checks.append((f"spectrum: the amplification peaks at {sag[imax] / pga:.1f} times the ground at T = {grid[imax]:.2f} s (between 0.6 and 0.85 s) and is only {sag[-1] / pga:.2f} at 3 s",
                   0.6 <= grid[imax] <= 0.85 and 4.0 < sag[imax] / pga < 4.8 and sag[-1] / pga < 0.3))
    checks.append(("spectrum: S_a = (2 pi / T)^2 S_d for every period", np.allclose(sag, (2 * np.pi / grid) ** 2 * sdg)))
    checks.append((f"the first mode (T = 1.00 s) sits in a dip of the spectrum: S_a/PGA = {sav[0] / pga:.2f}, well below the peak {sag[imax] / pga:.2f}",
                   sav[0] / pga < 0.65 * sag[imax] / pga))

    # ---- the shortcut is exact for one degree of freedom -----------------------------------------
    M1, K1 = L.shear_building(1)
    e1 = L.shortcut_error(M1, K1, L.K_STOREY, ag, dt, nmodes=1)
    checks.append((f"one storey, one mode: the shortcut is exact (error {100 * e1:+.3f} percent, within 0.5 percent; Newmark's own period error is the rest)",
                   abs(e1) < 5e-3))

    # ---- linearity and scaling -------------------------------------------------------------------
    checks.append(("linear: doubling the record doubles the shortcut and the time-history base shear",
                   abs(L.shortcut_base_shear(M, K, 2 * ag, dt) / est - 2.0) < 1e-9
                   and abs(L.time_history_base_shear(M, K, k1, 2 * ag, dt) / th - 2.0) < 1e-9))
    checks.append(("scaling: doubling every mass and every stiffness keeps the periods and doubles the shortcut",
                   abs(L.shortcut_base_shear(2 * M, 2 * K, ag, dt) / est - 2.0) < 1e-9))

    # ---- storey shears ---------------------------------------------------------------------------
    ssh = L.srss_storey_shears(M, K, ag, dt, 3)
    tsh = L.time_history_storey_shears(M, K, k1, ag, dt)
    checks.append(("storey shears: the lowest storey equals the base shear estimate and the shears decrease up the building",
                   abs(ssh[0] - est) < 1e-6 * est and np.all(np.diff(ssh) < 0)))
    checks.append((f"storey shears: top storey {ssh[-1] / 1e6:.3f} MN (SRSS) against {tsh[-1] / 1e6:.3f} MN (time history), within 5 percent",
                   abs(ssh[-1] / tsh[-1] - 1) < 0.05 and abs(ssh[0] / tsh[0] - 1) < 0.05))
    modal_rows = L.modal_storey_shears(M, K, sd, 2)
    checks.append(("storey shears: each mode's storey shear at the base is its V_i, and the table has one row per mode and one column per storey",
                   np.allclose(modal_rows[:, 0], full[:2], rtol=1e-9) and modal_rows.shape == (2, 10)))

    # ---- the screening test ----------------------------------------------------------------------
    rows = L.error_vs_stiffness(ag, dt)
    ok = L.passing(rows)
    checks.append((f"screening: 12 of 15 stiffnesses (300 to 1400 MN/m) are within 5 percent (got {len(ok)}: {[int(x) for x in ok]})",
                   len(rows) == 15 and len(ok) == 12 and ok == [float(x) for x in range(300, 1401, 100)]))
    by_k = {int(r[0]): r for r in rows}
    checks.append((f"screening: the softest frame (100 MN/m, T1 = {by_k[100][1]:.2f} s) is {100 * by_k[100][4]:+.1f} percent off, 200 MN/m {100 * by_k[200][4]:+.1f} percent, 1500 MN/m {100 * by_k[1500][4]:+.1f} percent",
                   abs(by_k[100][4] - 0.221) < 1.5e-3 and abs(by_k[200][4] - 0.061) < 1.5e-3 and abs(by_k[1500][4] + 0.054) < 1.5e-3))
    checks.append((f"stiffer is not safer: at 700 MN/m the time-history base shear is {by_k[700][2]:.1f} MN, {by_k[700][2] / (th / 1e6):.2f} times that of the 350 MN/m frame",
                   abs(by_k[700][2] - 15.29) < 0.01 and by_k[700][2] > 1.7 * th / 1e6))
    # ---- modal superposition against Newmark, and why the soft frame is overestimated -------------
    hist = L.modal_base_shear_histories(M, K, k1, ag, dt)
    checks.append((f"modal superposition: the modes' base shears add up to the Newmark history (peak {np.abs(hist.sum(axis=1)).max() / 1e6:.3f} MN against {th / 1e6:.3f} MN, within 0.5 percent), and each mode's peak is its V_i",
                   abs(np.abs(hist.sum(axis=1)).max() / th - 1) < 5e-3 and np.allclose(np.abs(hist).max(axis=0), full, rtol=1e-9)))
    Ms, Ks = L.shear_building(k=100e6)
    hs = L.modal_base_shear_histories(Ms, Ks, 100e6, ag, dt)
    i1 = int(np.abs(hs[:, 0]).argmax())
    checks.append((f"soft frame (100 MN/m): the full run ({np.abs(hs.sum(axis=1)).max() / 1e6:.2f} MN) is below mode 1's own peak ({np.abs(hs[:, 0]).max() / 1e6:.2f} MN), because at t = {t[i1]:.2f} s mode 2 pulls the other way ({hs[i1, 1] / 1e6:+.2f} MN)",
                   np.abs(hs.sum(axis=1)).max() < np.abs(hs[:, 0]).max() and hs[i1, 1] * hs[i1, 0] < 0 and abs(t[i1] - 12.28) < 1e-6 and abs(hs[i1, 1] / 1e6 + 0.80) < 5e-3))
    # ---- a hand-sized example: two storeys, made-up spectrum values -----------------------------
    M2, K2 = L.shear_building(2, 2.0e5, 3.5e8)
    T2, w2, p2, g2, me2 = L.modal_data(M2, K2)
    sd2 = lambda T_: (2.0 if abs(T_ - T2[0]) < 1e-9 else 1.0) / (2 * np.pi / T_) ** 2     # S_a = 2.0 at T1, 1.0 at T2
    v2 = L.modal_base_shears(M2, K2, sd2)
    checks.append((f"hand example: two storeys with S_a = 2.0 and 1.0 m/s^2 give V = {v2[0] / 1e3:.1f} and {v2[1] / 1e3:.1f} kN, SRSS {L.srss(v2) / 1e3:.1f} kN, sum {L.abs_sum(v2) / 1e3:.1f} kN",
                   abs(v2[0] / 1e3 - 757.8) < 0.05 and abs(v2[1] / 1e3 - 21.1) < 0.05 and abs(L.srss(v2) / 1e3 - 758.1) < 0.05 and abs(L.abs_sum(v2) / 1e3 - 778.9) < 0.05))
    # ---- other records ---------------------------------------------------------------------------
    errs = []
    for seed in range(1, 7):
        _, a_ = L.synthetic_ground(seed=seed)
        errs.append(L.shortcut_error(M, K, k1, a_, dt, 3))
    checks.append((f"six other records (seeds 1 to 6): the 3-mode SRSS error of the lesson frame is between {100 * min(errs):+.1f} and {100 * max(errs):+.1f} percent, all within 5 percent",
                   max(abs(e) for e in errs) < 0.05 and abs(min(errs) + 0.0284) < 5e-4 and abs(max(errs) - 0.0413) < 5e-4))
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
