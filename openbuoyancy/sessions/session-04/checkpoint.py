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
    tank = L.make_tank(10.0, 5.0, 120000.0, 2.5)
    m_tot = L.LIGHT + tank["mass"]
    solid = L.gm_loaded(tank["mass"], tank["cg"])
    i5 = L.tank_inertia(tank)
    fsc = L.free_surface_correction(tank, m_tot)
    gm_eff = L.gm_effective(tank)

    # ---- worked example ------------------------------------------------------------------------
    checks.append((f"worked example: i = l w^3 / 12 = 104.17 m^4, FSC = rho_l i / m = {fsc:.4f} m, GM = 0.7500 - {fsc:.4f} = {gm_eff:.4f} m",
                   abs(solid - 0.75) < 1e-12 and abs(i5 - 10 * 125 / 12) < 1e-12 and abs(fsc - 0.5787) < 5e-5 and abs(gm_eff - 0.1713) < 5e-5))
    checks.append((f"roadmap checkpoint: the effective GM of the 180 t barge with a 10 x 5 m tank is {gm_eff:.4f} m, which is 0.17 m to two decimals (the shipped code gives {solid:.2f} m)",
                   round(gm_eff, 2) <= 0.17 and solid > 0.7))
    t2 = L.make_tank(10.0, 5.0, 120000.0, 2.5, n_long=2)
    checks.append((f"worked example: one longitudinal divider gives i = 26.04 m^4 and GM = {L.gm_effective(t2):.4f} m (0.6053)",
                   abs(L.tank_inertia(t2) - i5 / 4) < 1e-12 and abs(L.gm_effective(t2) - 0.6053) < 5e-5))

    # ---- formula against the exact geometry --------------------------------------------------------
    ex = L.effective_gm_exact(tank)
    checks.append((f"exact geometry of the heeled tank gives GM_eff = {ex:.4f} m, within 0.002 m of the formula {gm_eff:.4f} m",
                   abs(ex - gm_eff) < 2e-3))
    checks.append((f"the same for two and three compartments (exact {L.effective_gm_exact(t2):.4f} and {L.effective_gm_exact(L.make_tank(10.0, 5.0, 120000.0, 2.5, n_long=3)):.4f} m)",
                   abs(L.effective_gm_exact(t2) - L.gm_effective(t2)) < 2e-3
                   and abs(L.effective_gm_exact(L.make_tank(10.0, 5.0, 120000.0, 2.5, n_long=3)) - L.gm_effective(L.make_tank(10.0, 5.0, 120000.0, 2.5, n_long=3))) < 2e-3))
    moms = []
    for f in (0.2, 0.4, 0.6, 0.8):
        tk = L.make_tank(10.0, 5.0, f * 1000.0 * 10.0 * 5.0 * 4.0, 2.0)
        moms.append(L.free_surface_moment_exact(tk))
    checks.append((f"the free-surface moment does not depend on the fill: {', '.join(f'{m / 1e3:.1f}' for m in moms)} tonne m at 20, 40, 60 and 80 percent against rho_l i = {1000 * i5 / 1e3:.1f}",
                   all(abs(m / (1000 * i5) - 1) < 5e-3 for m in moms)))
    checks.append(("with the liquid frozen the exact GZ equals the Session 3 solid-cargo GZ at 5, 15 and 30 degrees",
                   all(abs(L.righting_arm_tank(np.radians(d), tank, frozen=True)
                           - L.righting_arm(np.radians(d), m_tot, L.kg_loaded(tank["mass"], tank["cg"]))) < 1e-9 for d in (5, 15, 30))))

    # ---- scaling ---------------------------------------------------------------------------------------
    half = L.make_tank(10.0, 2.5, 120000.0, 2.5, height=8.0)
    checks.append((f"width cubed: halving the tank width divides FSC by 8 (formula {L.free_surface_correction(tank, m_tot) / L.free_surface_correction(half, m_tot):.3f})",
                   abs(L.free_surface_correction(tank, m_tot) / L.free_surface_correction(half, m_tot) - 8.0) < 1e-9))
    checks.append(("length: doubling the tank length doubles FSC; density: 1250 kg/m^3 liquid gives 1.25 times FSC and the exact moment agrees within 0.5 percent",
                   abs(L.free_surface_correction(L.make_tank(20.0, 5.0, 120000.0, 2.5), m_tot) / fsc - 2.0) < 1e-9
                   and abs(L.free_surface_correction(L.make_tank(10.0, 5.0, 120000.0, 2.5, rho_l=1250.0), m_tot) / fsc - 1.25) < 1e-9
                   and abs(L.free_surface_moment_exact(L.make_tank(10.0, 5.0, 120000.0, 2.5, rho_l=1250.0)) / (1250 * i5) - 1) < 5e-3))
    checks.append((f"mass: the same tank on a heavier barge (light 160 t) loses less: FSC = {L.free_surface_correction(tank, 280000.0):.4f} m against {fsc:.4f} m",
                   abs(L.free_surface_correction(tank, 280000.0) - 1000 * i5 / 280000.0) < 1e-12 and L.free_surface_correction(tank, 280000.0) < fsc))
    checks.append(("equivalent view: GM_eff = KM - (KG + FSC), so the free surface acts like raising G by FSC",
                   abs(gm_eff - (L.kb_box(L.draft_for(m_tot)) + L.bm_box(L.draft_for(m_tot)) - L.kg_loaded(tank["mass"], tank["cg"]) - fsc)) < 1e-12))

    # ---- dividers -----------------------------------------------------------------------------------------
    t3 = L.make_tank(10.0, 5.0, 120000.0, 2.5, n_long=3)
    checks.append((f"longitudinal dividers: 2 compartments give 1/4 of i and 3 give 1/9 (i = {L.tank_inertia(t2):.2f} and {L.tank_inertia(t3):.2f} m^4)",
                   abs(L.tank_inertia(t3) - i5 / 9) < 1e-12 and abs(L.divided_inertia(10.0, 5.0, 2, 1) - i5 / 4) < 1e-12))
    tt = L.make_tank(10.0, 5.0, 120000.0, 2.5, n_trans=3)
    checks.append((f"transverse bulkheads do not help: 3 compartments across the length still have i = {L.tank_inertia(tt):.2f} m^4 and GM_eff = {L.gm_effective(tt):.4f} m",
                   abs(L.tank_inertia(tt) - i5) < 1e-12 and abs(L.divided_inertia(10.0, 5.0, 1, 3) - i5) < 1e-12 and abs(L.gm_effective(tt) - gm_eff) < 1e-12))

    # ---- full tank and the exact curve ---------------------------------------------------------------------
    full = L.make_tank(10.0, 5.0, 1000.0 * 10.0 * 5.0 * 4.0, 2.0, height=4.0)
    checks.append(("a full tank has no free surface: FSC = 0 and the exact GZ equals the frozen GZ at 15 degrees",
                   L.is_full(full) and L.free_surface_correction(full, L.LIGHT + full["mass"]) == 0.0
                   and abs(L.righting_arm_tank(np.radians(15), full) - L.righting_arm_tank(np.radians(15), full, frozen=True)) < 1e-9))
    d10, d20 = np.radians(10), np.radians(20)
    g10, g20 = L.righting_arm_tank(d10, tank), L.righting_arm_tank(d20, tank)
    checks.append((f"exact GZ with the free surface: {g10:.4f} m at 10 degrees and {g20:.4f} m at 20 (solid: {L.righting_arm_tank(d10, tank, frozen=True):.4f} and {L.righting_arm_tank(d20, tank, frozen=True):.4f} m)",
                   abs(g10 - 0.0336) < 5e-4 and abs(g20 - 0.0866) < 5e-4
                   and abs(L.righting_arm_tank(d10, tank, frozen=True) - 0.1356) < 5e-4))
    checks.append(("the free surface lowers the righting arm at every heel angle from 1 to 40 degrees",
                   all(L.righting_arm_tank(np.radians(d), tank) < L.righting_arm_tank(np.radians(d), tank, frozen=True) for d in range(1, 41))))
    checks.append(("symmetry: GZ(-phi) = -GZ(phi) with the free surface", abs(L.righting_arm_tank(np.radians(12), tank) + L.righting_arm_tank(-np.radians(12), tank)) < 1e-9))
    checks.append((f"the liquid is a clean wedge up to {L.surface_touches_deg(tank):.1f} degrees for the 10 x 5 m tank (2.4 m of liquid in a 4 m tank)",
                   abs(L.surface_touches_deg(tank) - np.degrees(np.arctan(2 * 1.6 / 5.0))) < 1e-9))

    # ---- the wide tank and design --------------------------------------------------------------------------
    wide = L.make_tank(10.0, 5.8, 120000.0, 2.5)
    gw = L.gm_effective(wide)
    checks.append((f"a 10 x 5.8 m tank (the widest that fits) makes GM_eff = {gw:+.4f} m: negative, although the solid-cargo GM is 0.75 m",
                   abs(gw + 0.1533) < 5e-4 and gw < 0))
    gz_wide = [L.righting_arm_tank(np.radians(d), wide) for d in range(1, 61)]
    checks.append(("for that tank GZ is negative at every heel angle from 1 to 60 degrees, so there is no angle of loll: the model has it capsize",
                   max(gz_wide) < 0 and np.isnan(L.angle_of_loll_tank(wide))))
    w2 = L.make_tank(10.0, 5.8, 120000.0, 2.5, n_long=2)
    w3 = L.make_tank(10.0, 5.8, 120000.0, 2.5, n_long=3)
    checks.append((f"one longitudinal divider rescues it: GM_eff = {L.gm_effective(w2):+.3f} m with 2 compartments and {L.gm_effective(w3):+.3f} m with 3",
                   abs(L.gm_effective(w2) - 0.524) < 5e-4 and abs(L.gm_effective(w3) - 0.650) < 5e-4))
    widths = [L.max_tank_width(10.0, 120000.0, 2.5, 0.15, n) for n in (1, 2, 3)]
    ok = all(abs(L.gm_effective(L.make_tank(10.0, w, 120000.0, 2.5, height=8.0, n_long=n)) - 0.15) < 1e-9 for w, n in zip(widths, (1, 2, 3)))
    checks.append((f"widest tank for GM >= 0.15 m: {widths[0]:.2f} m undivided, {widths[1]:.2f} m with 2 compartments, {widths[2]:.2f} m with 3 (the hull is only 6 m wide)",
                   ok and abs(widths[0] - 5.061) < 5e-4 and abs(widths[1] - 8.033) < 5e-4 and abs(widths[2] - 10.526) < 5e-4))
    v_free, v_solid = L.vanishing_angle_deg(tank), L.vanishing_angle_deg(tank, frozen=True)
    checks.append((f"range of stability: GZ vanishes at {v_free:.1f} degrees with the free surface against {v_solid:.1f} degrees for a solid cargo; one divider on the wide tank gives {L.vanishing_angle_deg(w2):.1f}",
                   abs(v_free - 30.7) < 0.05 and abs(v_solid - 53.6) < 0.05 and abs(L.vanishing_angle_deg(w2) - 42.2) < 0.05 and np.isnan(L.vanishing_angle_deg(wide))))
    checks.append(("limit: a tank that cannot hold its liquid, a zero width or a zero compartment count is rejected; a margin larger than the solid GM gives width 0",
                   _raises(lambda: L.make_tank(10.0, 1.0, 120000.0, 2.5)) and _raises(lambda: L.make_tank(10.0, 0.0, 1e5, 2.5))
                   and _raises(lambda: L.make_tank(10.0, 5.0, 1e5, 2.5, n_long=0)) and L.max_tank_width(10.0, 120000.0, 2.5, gm_min=0.9) == 0.0))
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
