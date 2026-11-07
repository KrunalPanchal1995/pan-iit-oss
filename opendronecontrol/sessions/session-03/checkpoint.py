"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    # mixer and equations of motion
    fl, fr = L.mixer(11.772, 0.0)
    checks.append(("mixer: no torque splits the hover thrust equally (5.886 N each)", abs(fl - 5.886) < 1e-9 and abs(fr - 5.886) < 1e-9))
    fl, fr = L.mixer(12.0, 0.4)
    checks.append(("mixer: forces add back to the thrust and give back the torque (F_l - F_r) L",
                   abs(fl + fr - 12.0) < 1e-9 and abs((fl - fr) * L.ARM - 0.4) < 1e-9))
    d = L.derivatives(np.array([0, 0, 0, 0, 0, 0.0]), L.MASS * L.G / 2, L.MASS * L.G / 2)
    checks.append(("level drone at hover thrust: zero acceleration and zero angular acceleration", np.allclose(d[3:], 0.0)))
    d = L.derivatives(np.array([0, 0, np.radians(10), 0, 0, 0.0]), 6.0, 6.0)
    checks.append(("hand calculation: 12 N tilted 10 degrees gives a_y = 12 sin(10 deg) / 1.2 = 1.736 m/s^2",
                   abs(d[3] - 12 * np.sin(np.radians(10)) / 1.2) < 1e-12 and abs(d[3] - 1.7365) < 1e-3))

    # inner loop against the formulas
    wn, zeta = L.attitude_wn_zeta(1.2, 0.17)
    checks.append(("worked example: Kp_att = 1.2, Kd_att = 0.17, I = 0.012 gives wn = 10 rad/s, zeta = 0.708",
                   abs(wn - 10.0) < 1e-9 and abs(zeta - 0.7083) < 1e-3))
    t, ph = L.attitude_step(5.0, 0.0, t_end=3.0)
    over = (ph.max() - 5.0) / 5.0
    checks.append((f"attitude step with ideal motors: overshoot {over:.4f} matches the formula {L.overshoot_formula(zeta):.4f}",
                   abs(over - L.overshoot_formula(zeta)) < 0.005 and abs(ph[-1] - 5.0) < 0.01))
    checks.append(("worked example: motor-lag limit Kd / Kp = 0.142 s", abs(L.lag_limit(1.2, 0.17) - 0.14167) < 1e-4))
    t, ok_run = L.attitude_step(5.0, 0.10, t_end=8.0)
    t, bad_run = L.attitude_step(5.0, 0.17, t_end=8.0)
    checks.append(("Routh limit: tau_m = 0.10 s (below 0.142) settles, 0.17 s (above) keeps growing",
                   np.ptp(ok_run[t > 6]) < 0.05 and np.ptp(bad_run[t > 6]) > 10.0))
    t, a = L.attitude_step(5.0, 0.0, t_end=3.0)
    t, b = L.attitude_step(5.0, 0.06, t_end=3.0)
    checks.append(("motor lag raises the overshoot of the tilt", b.max() > a.max()))

    # full cascaded flight
    r = L.simulate(t_end=8.0)
    m = L.metrics(r)
    checks.append((f"worked example: 1 m sideways move ends at y = {m['final_y']:.4f} m, level (|phi| < 0.1 degree)",
                   abs(m["final_y"] - 1.0) < 2e-3 and abs(np.degrees(m["final_phi"])) < 0.1))
    checks.append((f"worked example: settles in {m['settling']:.2f} s (about 3.4 s), overshoot {100 * m['overshoot']:.1f} cm (about 5 cm)",
                   3.2 < m["settling"] < 3.7 and 0.03 < m["overshoot"] < 0.07))
    checks.append((f"first tilt is about Kp_y / g = 2.25 / 9.81 rad = 13.1 degrees (got {np.degrees(r['phi_des'].max()):.1f})",
                   abs(np.degrees(r["phi_des"].max()) - np.degrees(2.25 / 9.81)) < 0.05))
    hover = L.simulate(y_ref=0.0, t_end=3.0)
    checks.append(("no command: the drone stays exactly where it is", np.max(np.abs(hover["y"])) < 1e-9 and np.max(np.abs(hover["z"])) < 1e-9))
    left = L.simulate(y_ref=-1.0, t_end=8.0)
    checks.append(("symmetry: a move to the left mirrors the move to the right", np.allclose(left["y"], -r["y"], atol=1e-9)))
    no_tc = L.metrics(L.simulate(y_ref=3.0, t_end=8.0, tilt_comp=False), 3.0)
    tc = L.metrics(L.simulate(y_ref=3.0, t_end=8.0, tilt_comp=True), 3.0)
    checks.append((f"tilt compensation cuts the height dip of a 3 m move ({100 * no_tc['dip']:.1f} cm -> {100 * tc['dip']:.1f} cm)",
                   tc["dip"] < 0.2 * no_tc["dip"]))
    tilt = max(abs(np.degrees(L.simulate(y_ref=20.0, t_end=4.0, max_tilt_deg=20.0)["phi_des"])))
    checks.append(("the outer loop never asks for more than the tilt limit", tilt <= 20.0 + 1e-9))
    heavy = L.simulate(y_ref=0.0, t_end=20.0, mass=1.4)
    checks.append(("height PID (Session 2) still removes the error when the drone is 0.2 kg heavier", abs(heavy["z"][-1]) < 0.01))
    a1 = L.metrics(L.simulate(t_end=8.0, dt=0.001))
    a2 = L.metrics(L.simulate(t_end=8.0, dt=0.0005))
    checks.append(("a smaller time step gives the same answer (convergence)", abs(a1["overshoot"] - a2["overshoot"]) < 1e-3))

    # mini-project
    res = {name: L.check_design(kp, kd) for name, kp, kd in L.CANDIDATES}
    checks.append(("mini-project: the soft tuning (wn = 4 rad/s) is too slow for 4 s", not res["A soft"]["ok"] and res["A soft"]["settling"] > 4.0))
    checks.append(("mini-project: the stiff tuning (wn = 20 rad/s) fails the lag margin and the 15 degree tilt limit",
                   not res["D stiff"]["margin_ok"] and res["D stiff"]["max_tilt"] > 15.0))
    checks.append(("mini-project: medium (wn = 6) and default (wn = 10) tunings meet every requirement",
                   res["B medium"]["ok"] and res["C default"]["ok"]))
    bad = 0
    for call in (lambda: L.lag_limit(0.0, 0.1), lambda: L.simulate(dt=0.0), lambda: L.simulate(tau_m=-0.1)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 3))
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
