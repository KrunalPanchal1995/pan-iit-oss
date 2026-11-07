"""Checkpoint for Session 3. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    R = 100.0
    vflat = math.sqrt(0.4 * L.G * R)

    # validation against the Session 2 limits (flat and banked, with friction)
    sim_flat = L.sim_limit(R, 0.4, 0.0, "max")
    checks.append((f"worked example: flat wet curve, simulated top speed {sim_flat * 3.6:.1f} km/h is within 2% of sqrt(mu g R) = 71.3 km/h",
                   abs(sim_flat - vflat) / vflat < 0.02 and abs(vflat * 3.6 - 71.3) < 0.1))
    th = math.radians(30)
    lo_a, hi_a = L.analytic_limits(R, 0.3, th)
    lo_s, hi_s = L.sim_limit(R, 0.3, th, "min"), L.sim_limit(R, 0.3, th, "max")
    checks.append((f"banked 30 degrees, mu 0.3: simulated range {lo_s * 3.6:.1f} to {hi_s * 3.6:.1f} km/h is within 2% of {lo_a * 3.6:.1f} to {hi_a * 3.6:.1f}",
                   abs(lo_s - lo_a) / lo_a < 0.02 and abs(hi_s - hi_a) / hi_a < 0.02))
    checks.append(("slower than the limit holds, faster slides (flat, 0.9 and 1.1 times the limit)",
                   L.holds(0.9 * vflat, R, 0.4) and not L.holds(1.1 * vflat, R, 0.4)))
    checks.append(("ice is much worse than wet: sqrt(0.1/0.4) = 0.5 of the wet limit",
                   abs(L.sim_limit(R, 0.1, 0.0, "max") / sim_flat - 0.5) < 0.02))

    # frictionless banked curve: only the ideal speed holds, and energy is conserved
    t20 = math.radians(20)
    vi = math.sqrt(L.G * R * math.tan(t20))
    out = L.simulate(vi, R, 0.0, t20, 0.0, 10.0, 0.005)
    checks.append(("frictionless ideal bank: the car holds the lane at the ideal speed (drift < 0.01 m)", np.abs(out["rho"] - R).max() < 0.01))
    out2 = L.simulate(0.9 * vi, R, 0.0, t20, 0.0, 10.0, 0.005)
    e = out2["energy"]
    checks.append(("frictionless, 10% too slow: it slides down the bank (drift > 5 m) while energy stays constant to 1e-9",
                   np.abs(out2["rho"] - R).max() > 5.0 and (e.max() - e.min()) / e[0] < 1e-9))

    # accelerating and braking: the friction circle
    vs = L.grip_loss_speed(R, 0.4, 2.0)
    checks.append((f"accelerating at 2 m/s^2 the grip is lost at {vs * 3.6:.1f} km/h, formula {L.combined_slide_speed(R, 0.4, 2.0) * 3.6:.1f} km/h",
                   abs(vs - L.combined_slide_speed(R, 0.4, 2.0)) * 3.6 < 0.3))
    coast = L.simulate(0.9 * vflat, R, 0.4, 0.0, 0.0, 3.0, 0.01)
    brake = L.simulate(0.9 * vflat, R, 0.4, 0.0, -3.0, 3.0, 0.01)
    checks.append(("braking in the curve uses up grip: demand ratio rises above 1 where coasting stays below 0.85",
                   coast["ratio"].max() < 0.85 and brake["ratio"].max() > 1.0))
    checks.append(("braking never speeds the car up and it brakes at the commanded rate while gripping",
                   abs((L.simulate(0.5 * vflat, R, 0.4, 0.0, -3.0, 1.0, 0.01)["v"][-1]) - (0.5 * vflat - 3.0)) < 1e-6))

    # failure case: understeer slide follows a circle of radius v^2 / (mu g)
    v_in = 1.3 * vflat
    sl = L.simulate(v_in, R, 0.4, 0.0, 0.0, 6.0, 0.005)
    sp = L.skid_position(v_in, 0.4, R, 6.0)
    checks.append(("failure case: entering at 1.3 times the limit, the car follows the skid circle (position error < 1 m after 6 s)",
                   math.hypot(sl["x"][-1] - sp[0], sl["y"][-1] - sp[1]) < 1.0 and abs(sl["v"][-1] - v_in) < 1e-6))
    sl2 = L.simulate(v_in, R, 0.4, 0.0, 0.0, 6.0, 0.0025)
    checks.append(("time-step check: halving dt moves the end point by less than 0.05 m", math.hypot(sl["x"][-1] - sl2["x"][-1], sl["y"][-1] - sl2["y"][-1]) < 0.05))
    checks.append(("skid radius at 1.3 times the limit is 1.69 R", abs(L.skid_radius(v_in, 0.4) / R - 1.69) < 1e-9))
    nofric = L.simulate(10.0, R, 0.0, 0.0, 0.0, 3.0, 0.01)
    checks.append(("edge case: mu = 0 runs without error and the car goes straight (leaves the lane)", np.isfinite(nofric["x"]).all() and nofric["rho"][-1] > R + 1.0))

    # roller-coaster loop
    r = 10.0
    vb = L.loop_min_bottom_speed(r)
    checks.append((f"loop r = 10 m: simulated minimum bottom speed {vb:.2f} m/s equals sqrt(5 g r) = {math.sqrt(5 * L.G * r):.2f} m/s",
                   abs(vb - math.sqrt(5 * L.G * r)) / math.sqrt(5 * L.G * r) < 0.005))
    ok_run, _, vtop = L.loop_ride(1.001 * math.sqrt(5 * L.G * r), r)
    checks.append(("at that speed the top-of-loop speed is sqrt(g r) = 9.90 m/s", ok_run and abs(vtop - math.sqrt(L.G * r)) < 0.1))
    checks.append(("below the minimum the cart leaves the track; above it the cart stays on",
                   (not L.loop_ride(0.95 * vb, r)[0]) and L.loop_ride(1.05 * vb, r)[0]))

    # mini-project helper
    sign = L.posted_speed_limit(80.0, 4.0, 0.35)
    vwet = L.analytic_limits(80.0, 0.35, math.radians(4))[1] * 3.6
    checks.append((f"worked example: R = 80 m, bank 4 degrees, wet mu 0.35: wet top speed {vwet:.1f} km/h, margin 0.75, sign {sign} km/h",
                   sign == 45 and abs(vwet - 66.2) < 0.1))
    checks.append(("the sign is a multiple of 5 km/h and below margin times the wet limit", sign % 5 == 0 and sign <= 0.75 * vwet))
    checks.append(("simulation: the sign speed holds on wet road, and so does 99 percent of the wet limit",
                   L.holds(sign / 3.6, 80.0, 0.35, math.radians(4)) and L.holds(0.99 * vwet / 3.6, 80.0, 0.35, math.radians(4))))
    table = [L.posted_speed_limit(80.0, 4.0, 0.35, m) for m in (0.6, 0.7, 0.75, 0.8, 0.9)]
    checks.append((f"margin table 0.6 to 0.9 gives signs {table} (35, 45, 45, 50, 55)", table == [35, 45, 45, 50, 55]))
    checks.append(("the 45 km/h sign slides on ice (mu 0.1): a wet-road sign is not an ice-road sign", not L.holds(45 / 3.6, 80.0, 0.1, math.radians(4))))
    # ---- tall vehicles: tip speed and slide speed ------------------------------------------------
    car = L.slide_or_tip(100.0, 0.8, 1.5, 0.5)
    van = L.slide_or_tip(100.0, 0.8, 1.7, 1.3)
    van_wet = L.slide_or_tip(100.0, 0.4, 1.7, 1.3)
    kmh = lambda x: 3.6 * x
    checks.append((f"R = 100 m, flat: low car slides at {kmh(car['v_slide']):.1f} and tips at {kmh(car['v_tip']):.1f} km/h (100.9, 138.1) so it slides first",
                   abs(kmh(car['v_slide']) - 100.9) < 0.05 and abs(kmh(car['v_tip']) - 138.1) < 0.05 and car["first"] == "slides"))
    checks.append((f"tall van (T 1.7, h 1.3, s = {van['stability']:.3f}): tips at {kmh(van['v_tip']):.1f} km/h before it would slide at {kmh(van['v_slide']):.1f} on a dry road, but slides first at {kmh(van_wet['v_slide']):.1f} on a wet one",
                   abs(kmh(van['v_tip']) - 91.2) < 0.05 and van["first"] == "tips" and van_wet["first"] == "slides" and abs(kmh(van_wet['v_slide']) - 71.3) < 0.05))
    checks.append(("flat road: tip speed is sqrt(g R T / (2 h)) (hand formula)",
                   abs(L.tip_speed(80.0, 1.6, 0.9) - math.sqrt(L.G * 80.0 * 1.6 / 1.8)) < 1e-12))
    shares_ok = True
    for (Rr, T_, h_, th_) in ((100.0, 1.5, 0.5, 0.0), (60.0, 1.7, 1.3, 0.0), (80.0, 1.8, 1.0, math.radians(8)), (150.0, 2.0, 1.6, math.radians(15))):
        shares_ok &= abs(L.inner_wheel_share(L.tip_speed(Rr, T_, h_, th_), Rr, T_, h_, th_)) < 1e-9
        lo_, hi_ = 0.0, 100.0                                   # independent bisection on the load transfer
        for _ in range(100):
            mid = 0.5 * (lo_ + hi_)
            lo_, hi_ = (mid, hi_) if L.inner_wheel_share(mid, Rr, T_, h_, th_) > 0 else (lo_, mid)
        shares_ok &= abs(0.5 * (lo_ + hi_) - L.tip_speed(Rr, T_, h_, th_)) < 1e-6
    checks.append(("the inner-wheel load is exactly zero at the tip speed, and bisection on the wheel load finds the same speed (flat and banked)", shares_ok))
    checks.append(("at rest on a flat road each side carries half the load", abs(L.inner_wheel_share(0.0, 100.0, 1.5, 0.5) - 0.5) < 1e-12))
    rng_t = np.random.default_rng(2)
    rule_ok = True
    for _ in range(300):
        mu_, T_, h_, th_ = rng_t.uniform(0.1, 1.2), rng_t.uniform(1.2, 2.2), rng_t.uniform(0.4, 1.6), math.radians(rng_t.uniform(0, 12))
        so = L.slide_or_tip(rng_t.uniform(30, 250), mu_, T_, h_, th_)
        rule_ok &= (so["first"] == "tips") == (L.static_stability(T_, h_) < mu_)
    checks.append(("300 random vehicles, roads and banks: the vehicle tips first exactly when T / (2 h) < mu", rule_ok))
    eq = L.slide_or_tip(100.0, 0.75, 1.5, 1.0)
    checks.append(("when T / (2 h) = mu the two speeds are equal", abs(eq["v_slide"] - eq["v_tip"]) < 1e-9))
    checks.append(("banking raises the tip speed, and a track so wide that s tan(theta) >= 1 cannot tip at all",
                   L.tip_speed(100.0, 1.5, 0.9, math.radians(10)) > L.tip_speed(100.0, 1.5, 0.9) and L.tip_speed(100.0, 2.4, 0.3, math.radians(20)) == math.inf))
    bad = 0
    for args in ((0.0, 0.5), (1.5, 0.0), (-1.5, 0.5)):
        try:
            L.static_stability(*args)
        except ValueError:
            bad += 1
    checks.append(("a zero or negative track width or CG height is refused", bad == 3))
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
