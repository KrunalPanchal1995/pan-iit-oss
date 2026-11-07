"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    cargo, h = 120000.0, 2.5
    mass = L.LIGHT + cargo
    d = L.draft_for(mass)
    kg = L.kg_loaded(cargo, h)
    gm = L.gm_loaded(cargo, h)
    bm = L.bm_box(d)
    checks.append((f"worked example: draft 1.500 m, KB 0.750, BM 2.000 (got {d:.3f}, {L.kb_box(d):.3f}, {bm:.3f})",
                   abs(d - 1.5) < 1e-12 and abs(L.kb_box(d) - 0.75) < 1e-12 and abs(bm - 2.0) < 1e-12))
    checks.append((f"worked example: KG = 2.000 m and GM = 0.750 m (got {kg:.3f}, {gm:.3f})", abs(kg - 2.0) < 1e-12 and abs(gm - 0.75) < 1e-12))

    # exact geometry in the small-angle limit equals GM sin(phi)
    p = np.radians(0.5)
    ratio = L.righting_arm(p, mass, kg) / np.sin(p)
    checks.append((f"validation: GZ / sin(phi) tends to GM at small angle (got {ratio:.4f})", abs(ratio - gm) < 2e-3))
    p10 = np.radians(10)
    checks.append(("validation: exact GZ matches the wall-sided formula at 10 degrees",
                   abs(L.righting_arm(p10, mass, kg) - L.wall_sided_gz(p10, gm, bm)) < 1e-6))
    checks.append(("validation: small-angle GM sin(phi) is within 5 percent at 10 degrees",
                   abs(L.righting_arm(p10, mass, kg) - gm * np.sin(p10)) / L.righting_arm(p10, mass, kg) < 0.05))
    checks.append(("exact geometry: zero heel gives zero righting arm", abs(L.righting_arm(0.0, mass, kg)) < 1e-9))
    checks.append(("exact geometry: righting arm is odd in the heel angle",
                   abs(L.righting_arm(-p10, mass, kg) + L.righting_arm(p10, mass, kg)) < 1e-9))
    level, yb, zb = L.wet_section(0.0, mass / (L.RHO * L.LEN))
    checks.append(("upright: waterline at the draft and B at half the draft", abs(level - d) < 1e-9 and abs(zb - d / 2) < 1e-9 and abs(yb) < 1e-9))
    a_wet = mass / (L.RHO * L.LEN)
    lv, _, _ = L.wet_section(np.radians(15), a_wet)
    checks.append(("heeled water line leaves the same wet area (weight is carried)",
                   abs(L.area_centroid(L.clip_below([(y * np.cos(np.radians(15)) - z * np.sin(np.radians(15)),
                                                        y * np.sin(np.radians(15)) + z * np.cos(np.radians(15)))
                                                       for y, z in [(-3, 0), (3, 0), (3, 2.5), (-3, 2.5)]], lv))[0] - a_wet) < 1e-6))

    # loading height
    checks.append(("raising the cargo lowers GM", L.gm_loaded(cargo, 3.0) < L.gm_loaded(cargo, 2.0)))
    hmax = L.max_cargo_height(cargo)
    checks.append((f"hand calculation: highest cargo centre for GM = 0.15 m is 3.40 m (got {hmax:.3f})", abs(hmax - 3.4) < 1e-9))
    checks.append(("GM is above 0.15 m at 3.39 m and negative at 3.7 m",
                   L.gm_loaded(cargo, 3.39) > 0.15 and L.gm_loaded(cargo, 3.7) < 0))

    # failure case
    gm_bad = L.gm_loaded(cargo, 3.8)
    kg_bad = L.kg_loaded(cargo, 3.8)
    checks.append((f"failure case: cargo at 3.8 m gives negative GM (got {gm_bad:.3f})", gm_bad < 0))
    checks.append(("failure case: a small heel makes the arm point the wrong way (GZ < 0)", L.righting_arm(np.radians(3), mass, kg_bad) < 0))
    loll = np.degrees(L.angle_of_loll(mass, kg_bad))
    analytic = np.degrees(np.arctan(np.sqrt(-2 * gm_bad / bm)))
    checks.append((f"failure case: angle of loll {loll:.1f} deg is near the analytic {analytic:.1f} deg", abs(loll - analytic) < 0.5))

    # cargo shift
    heel = np.degrees(L.heel_after_shift(cargo, h, 0.1))
    est = np.degrees(np.arctan(cargo * 0.1 / mass / gm))
    checks.append((f"cargo shift of 0.1 m: heel {heel:.1f} deg close to the small-angle estimate {est:.1f} deg", abs(heel - est) < 0.3))
    checks.append(("no shift gives no heel", L.heel_after_shift(cargo, h, 0.0) == 0.0))
    checks.append(("a bigger shift gives a bigger heel", L.heel_after_shift(cargo, h, 0.2) > L.heel_after_shift(cargo, h, 0.1)))

    # mini-project (the lever really matters): both limits, the heel limit governs
    best_gm = max(k * 0.05 for k in range(20, 100) if L.gm_loaded(cargo, k * 0.05) >= 0.15 - 1e-9)
    best_heel = max(k * 0.05 for k in range(20, 100)
                    if L.gm_loaded(cargo, k * 0.05) >= 0.15 - 1e-9 and np.degrees(L.heel_after_shift(cargo, k * 0.05, 0.2)) <= 10.0)
    checks.append((f"mini-project: GM limit allows cargo up to {best_gm:.2f} m, heel limit only up to {best_heel:.2f} m",
                   abs(best_gm - 3.4) < 1e-9 and abs(best_heel - 2.5) < 1e-9))
    # any hull polygon (issue: generalise the wet-section function)
    def grid_wet(hull, phi, level, n=1600):
        """Independent check: area and centroid of the wet part by counting grid points (no clipping code)."""
        c_, s_ = np.cos(phi), np.sin(phi)
        wp = np.array([(y * c_ - z * s_, y * s_ + z * c_) for y, z in hull])
        lo, hi = wp.min(axis=0), wp.max(axis=0)
        gy, gz_ = np.meshgrid(np.linspace(lo[0], hi[0], n), np.linspace(lo[1], min(hi[1], level), n))
        inside = np.zeros(gy.shape, dtype=bool)
        for k in range(len(wp)):
            (y1, z1), (y2, z2) = wp[k], wp[(k + 1) % len(wp)]
            cond = (z1 > gz_) != (z2 > gz_)
            with np.errstate(divide="ignore", invalid="ignore"):
                x_at = y1 + (gz_ - z1) * (y2 - y1) / (z2 - z1)
            inside ^= cond & (gy < x_at)
        inside &= gz_ <= level
        cell = (hi[0] - lo[0]) * (min(hi[1], level) - lo[1]) / (n * n)
        return inside.sum() * cell, gy[inside].mean(), gz_[inside].mean()

    box = L.rectangle_hull()
    def reference_box(phi, area, beam=6.0, depth=2.5):
        """The original rectangle-only algorithm, kept unchanged as a regression reference."""
        cc, ss = np.cos(phi), np.sin(phi)
        world = [(y * cc - z * ss, y * ss + z * cc)
                 for y, z in [(-beam / 2, 0.0), (beam / 2, 0.0), (beam / 2, depth), (-beam / 2, depth)]]
        lo = min(q[1] for q in world)
        hi = max(q[1] for q in world)
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if L.area_centroid(L.clip_below(world, mid))[0] < area:
                lo = mid
            else:
                hi = mid
        lv = 0.5 * (lo + hi)
        return (lv,) + tuple(L.area_centroid(L.clip_below(world, lv))[1:])

    for phi_deg in (0.0, 10.0, 25.0):
        r_old = reference_box(np.radians(phi_deg), 3.0)
        r_new = L.wet_polygon(np.radians(phi_deg), 3.0, box)
        r_sec = L.wet_section(np.radians(phi_deg), 3.0)
        checks.append((f"polygon code gives the same result as the original rectangle code at {phi_deg:.0f} degrees",
                       all(abs(u - v) < 1e-12 for u, v in zip(r_old, r_new))
                       and all(abs(u - v) < 1e-12 for u, v in zip(r_old, r_sec))))
    lvl, yb_, zb_ = L.wet_polygon(0.0, 3.0, L.v_hull())
    d_v = np.sqrt(2 * 3.0 * L.DEPTH / L.BEAM)
    checks.append((f"V hull upright, analytic: draft sqrt(2 A depth / beam) = {d_v:.4f} m and B at 2/3 of the draft",
                   abs(lvl - d_v) < 1e-9 and abs(zb_ - 2 * d_v / 3) < 1e-9 and abs(yb_) < 1e-9))
    for name, hull in (("box", box), ("V hull", L.v_hull()), ("round bilge", L.round_bilge_hull())):
        for phi_deg in (12.0, 30.0):
            lv_, yb2, zb2 = L.wet_polygon(np.radians(phi_deg), 3.0, hull)
            a_g, yg_, zg_ = grid_wet(hull, np.radians(phi_deg), lv_)
            checks.append((f"{name} at {phi_deg:.0f} degrees: wet area and B agree with an independent grid count",
                           abs(a_g - 3.0) < 0.01 and abs(yg_ - yb2) < 0.01 and abs(zg_ - zb2) < 0.01))
    checks.append(("righting_arm_hull for the box equals righting_arm",
                   abs(L.righting_arm_hull(np.radians(20), mass, kg, box) - L.righting_arm(np.radians(20), mass, kg)) < 1e-12))
    try:
        L.wet_polygon(0.1, 8.0, L.v_hull())
        rejected = False
    except ValueError:
        rejected = True
    checks.append(("a hull that cannot hold the weight (8 m^2 in a 7.5 m^2 V section) is rejected", rejected))
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
