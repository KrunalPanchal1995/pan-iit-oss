"""Checkpoint for Session 2. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    kj, ke = L.radius_ratio(L.R_JUP_KM), L.radius_ratio(L.R_EARTH_KM)
    checks.append((f"Jupiter around the Sun: depth {L.depth(kj):.4f} is about 1.06 percent", abs(L.depth(kj) - 0.01056) < 5e-5))
    checks.append((f"Earth around the Sun: depth {L.depth(ke) * 1e6:.1f} ppm is about 84 ppm", abs(L.depth(ke) * 1e6 - 83.9) < 0.1))

    # exact overlap against known geometry
    checks.append(("overlap: planet fully inside the star gives pi k^2", abs(L.overlap_area(0.0, 0.1)[0] - np.pi * 0.01) < 1e-12))
    checks.append(("overlap: planet fully outside gives 0", L.overlap_area(1.2, 0.1)[0] == 0.0))
    # brute force: count tiny squares that lie inside both circles (planet radius 0.5 centred on the star's edge)
    g = (np.arange(2000) + 0.5) / 2000 * 3.0 - 1.5
    X, Y = np.meshgrid(g, g)
    brute = np.sum((X ** 2 + Y ** 2 < 1.0) & ((X - 1.0) ** 2 + Y ** 2 < 0.25)) * (3.0 / 2000) ** 2
    checks.append((f"overlap: k = 0.5, z = 1 matches a brute-force count of squares ({brute:.4f})", abs(L.overlap_area(1.0, 0.5)[0] - brute) < 2e-3))
    checks.append(("overlap grows continuously to pi k^2 at z = 1 - k", abs(L.overlap_area(0.5 + 1e-9, 0.5)[0] - L.overlap_area(0.5, 0.5)[0]) < 1e-6))

    # numerical grid integral
    checks.append(("grid integral of the whole star matches pi(1 - u1/3 - u2/6) within 0.01 percent",
                   abs(L.disk_integral() / L.total_light_exact() - 1) < 1e-4))
    zs = np.linspace(0.0, 1.3, 14)
    err = np.max(np.abs(L.ld_flux(zs, 0.1, 0.0, 0.0) - L.uniform_flux(zs, 0.1)))
    checks.append((f"no limb darkening: grid light curve matches exact overlap (max error {err:.1e} < 1e-4)", err < 1e-4))
    d0 = 1 - L.ld_flux(np.array([0.0]), 0.1)[0]
    checks.append(("flat star: depth at the centre is (Rp/Rs)^2 = 0.01", abs(1 - L.uniform_flux(np.array([0.0]), 0.1)[0] - 0.01) < 1e-12))
    hand_ld = 0.01 / (1 - L.U1 / 3 - L.U2 / 6)
    checks.append((f"limb darkening: centre depth {d0:.5f} is about 0.01212, deeper than k^2 (hand: k^2 / (1 - u1/3 - u2/6))", abs(d0 - hand_ld) < 5e-5 and d0 > 0.0115))
    checks.append(("limb darkening law: I = 1 at the centre (mu = 1) and 1 - u1 - u2 at the edge (mu = 0)",
                   abs(L.ld_intensity(1.0) - 1.0) < 1e-12 and abs(L.ld_intensity(0.0) - (1 - L.U1 - L.U2)) < 1e-12))

    # Kepler and duration
    checks.append(("Earth: a = 1 AU = 149.6 million km", abs(L.a_metres(365.25) / 1e9 - 149.6) < 0.2))
    aR = L.a_over_rs(3.0)
    checks.append((f"P = 3 d around the Sun: a/Rs = {aR:.2f} is about 8.75", abs(aR - 8.75) < 0.01))
    app, ex, num = (L.duration_approx(3.0, aR, 0.1, 0.3) * 24, L.duration_exact(3.0, aR, 0.1, 0.3) * 24, L.duration_numeric(3.0, aR, 0.1, 0.3) * 24)
    checks.append((f"duration formula {app:.3f} h is within 1 percent of the numerical light curve {num:.3f} h", abs(app / num - 1) < 0.01))
    checks.append(("exact duration formula matches the numerical light curve within 0.1 percent", abs(ex / num - 1) < 1e-3))
    checks.append(("the impact parameter b = (a/Rs) cos i round-trips through the inclination", abs(L.impact_parameter(aR, L.inclination_deg(aR, 0.3)) - 0.3) < 1e-9))
    checks.append(("a grazing orbit (b = 1.2 > 1 + k) has no transit: duration 0", L.duration_approx(3.0, aR, 0.1, 1.2) == 0.0 and L.duration_numeric(3.0, aR, 0.1, 1.2) == 0.0))
    checks.append(("exact boundary b = 1 + k gives duration 0 (no crash)", L.duration_approx(3.0, aR, 0.1, 1.1) == 0.0 or L.duration_approx(3.0, aR, 0.1, 1.1) < 1e-6))
    checks.append(("higher impact parameter gives a shorter transit", L.duration_approx(3.0, aR, 0.1, 0.8) < L.duration_approx(3.0, aR, 0.1, 0.0)))

    # period
    rng = np.random.default_rng(4)
    ep = np.arange(8)
    p, _ = L.fit_period(ep, 2.0 + 4.2 * ep + rng.normal(0, 0.003, 8))
    checks.append((f"period from 8 noisy mid-times {p:.4f} is 4.2 within 0.005", abs(p - 4.2) < 0.005))
    checks.append(("period fit is exact for noise-free times", abs(L.fit_period([0, 1, 2], [1.0, 3.5, 6.0])[0] - 2.5) < 1e-12))

    # design problem
    aE = L.a_over_rs(365.25)
    TE = L.duration_approx(365.25, aE, ke, 0.0) * 24
    checks.append((f"Earth: a/Rs = {aE:.1f} is about 215 and the central transit lasts {TE:.2f} h (about 13.1)", abs(aE - 215.0) < 0.2 and abs(TE - 13.10) < 0.02))
    nE = L.points_per_transit(TE / 24, 0.5 / 24)
    checks.append(("30-minute cadence gives 26 points in one Earth transit", nE == 26))
    sig = L.sigma_needed(L.depth(ke), 3 * nE, 7.0)
    checks.append((f"worked example: noise needed for SNR 7 over 3 transits is {sig * 1e6:.1f} ppm (about 105.8)", abs(sig * 1e6 - 105.8) < 0.1))
    checks.append(("with that noise the SNR is exactly 7", abs(L.snr(L.depth(ke), sig, 3 * nE) - 7.0) < 1e-9))
    rng = np.random.default_rng(8)
    means = rng.normal(0.0, sig, (4000, 3 * nE)).mean(axis=1)
    checks.append((f"Monte Carlo: depth / scatter of the in-transit mean is {L.depth(ke) / means.std():.2f}, near 7 (within 5 percent)", abs(L.depth(ke) / means.std() / 7.0 - 1) < 0.05))
    checks.append(("more transits relax the noise limit by sqrt(N): 12 transits allow twice the noise of 3",
                   abs(L.sigma_needed(L.depth(ke), 12 * nE) / sig - 2.0) < 1e-9))
    checks.append(("radius ratios: Jupiter 0.1028 and Earth 0.009158", abs(kj - 0.10276) < 1e-5 and abs(ke - 0.009158) < 1e-6))
    # question B: 2 Earth radii around a 0.5 solar-radius star
    kb = L.radius_ratio(2 * L.R_EARTH_KM, 0.5 * L.R_SUN_KM)
    checks.append((f"question B: k = {kb:.5f} and depth {L.depth(kb) * 1e6:.0f} ppm (1342)", abs(kb - 0.03663) < 1e-5 and abs(L.depth(kb) * 1e6 - 1342) < 1))
    # question C: durations at b = 0 and 0.8 (k = 0.1, P = 3 d)
    d0, d8 = L.duration_approx(3.0, aR, 0.1, 0.0) * 24, L.duration_approx(3.0, aR, 0.1, 0.8) * 24
    checks.append((f"question C: durations {d0:.2f} h at b = 0 and {d8:.2f} h at b = 0.8 (2.88 and 1.98)", abs(d0 - 2.88) < 0.005 and abs(d8 - 1.98) < 0.005))
    checks.append(("worked example text: duration 2.77 h (approx) and 2.78 h (exact) for P = 3 d, b = 0.3", round(app, 2) == 2.77 and round(ex, 2) == 2.78))
    # question D: noise 200 ppm
    n_in = (7 * 200e-6 / L.depth(ke)) ** 2
    checks.append((f"question D: n_in = {n_in:.0f} points and {int(np.ceil(n_in / nE))} transits (279 and 11)", round(n_in) == 279 and int(np.ceil(n_in / nE)) == 11))
    checks.append(("app constant: 3 / pi / (a/Rs) x 24 = 2.6182 hours per unit", abs(3 / np.pi / aR * 24 - 2.6182) < 1e-3))
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
