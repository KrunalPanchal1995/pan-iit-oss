"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    p = L.demo_planet()
    # transit model basics
    far = L.transit_model(np.array([p["t0"] + p["period"] / 2]), p["period"], p["t0"], p["k"], p["a_rs"], p["b"])[0]
    mid = L.transit_model(np.array([p["t0"]]), p["period"], p["t0"], 0.1, p["a_rs"], 0.0)[0]
    checks.append(("transit model: flux is exactly 1 half an orbit away (planet behind the star)", far == 1.0))
    checks.append(("transit model: central depth for k = 0.1 is 0.01", abs((1 - mid) - 0.01) < 1e-12))
    checks.append(("overlap area at the boundary z = 1 + k is 0", L.overlap_area(np.array([1.1]), 0.1)[0] == 0.0))

    # synthetic data and detrending
    t, f = L.demo_lightcurve()
    checks.append(("demo run has gaps: fewer points than 40 d at 30 min cadence (1920)", len(t) < 1920 and np.diff(t).max() > 0.5))
    checks.append(("the demo light curve is the same on every run (seeded)", np.allclose(f[:5], L.demo_lightcurve()[1][:5])))
    r_short, r_long = L.depth_retained(0.15), L.depth_retained(1.0)
    checks.append((f"WRONG window 0.15 d keeps only {r_short:.0%} of the transit depth (below 10 percent)", r_short < 0.10))
    checks.append((f"RIGHT window 1.0 d keeps {r_long:.0%} of the depth (above 90 percent)", r_long > 0.90))
    flat, trend = L.detrend(t, f, 1.0)
    checks.append(("detrending leaves flux near 1 out of transit (median within 100 ppm of 1)", abs(np.median(flat) - 1.0) < 1e-4))
    checks.append(("moving median of a constant is that constant", np.allclose(L.moving_median(t, np.full(len(t), 2.0), 1.0), 2.0)))

    # BLS recovers the planet
    res = L.run_bls(t, flat)
    snr, per, t0, dur, depth = res["best"]
    checks.append((f"BLS recovers the injected period 4.2 d within 1 percent (got {per:.3f})", abs(per / 4.2 - 1) < 0.01))
    checks.append((f"BLS signal-to-noise {snr:.1f} is above the detection threshold 7", snr > 7))
    sn, pr, t0r, dr, dep = L.refine(t, flat, res)
    checks.append((f"refined period {pr:.4f} d is within 0.5 percent of 4.2", abs(pr / 4.2 - 1) < 0.005))
    ph = (t0r - p["t0"] + 2.1) % 4.2 - 2.1
    checks.append((f"mid-transit time found within 0.05 d of the truth (off by {abs(ph):.3f} d)", abs(ph) < 0.05))
    checks.append((f"box depth {dep * 1e6:.0f} ppm is between 80 and 100 percent of the true 4900 ppm", 0.80 * 4900e-6 < dep < 1.0 * 4900e-6))
    # aliases
    s1, shalf, s2 = L.alias_snr(res, per), L.alias_snr(res, per / 2), L.alias_snr(res, 2 * per)
    checks.append((f"alias peaks exist but are lower: SNR at P/2 {shalf:.1f} and at 2P {s2:.1f} are both below 0.8 of {s1:.1f}",
                   shalf < 0.8 * s1 and s2 < 0.8 * s1 and shalf > 7 and s2 > 7))
    # edge: constant flux does not crash
    flat_res = L.bls(t, np.ones(len(t)), L.period_grid(1.0, 5.0, 40.0, 0.06), (0.1,), 0.001)
    checks.append(("BLS on a perfectly constant star gives SNR 0 and no crash", float(flat_res["snr"].max()) <= 1e-9))

    # fit and radius
    k, b, t0f, rms = L.fit_transit(t, flat, pr, t0r, L.a_over_rs(pr, 1.0, 1.0))
    checks.append((f"model fit radius ratio {k:.3f} is within 10 percent of the true 0.07", abs(k / 0.07 - 1) < 0.10))
    checks.append(("hand calculation: k = 0.07 around a 1 solar-radius star is a 7.6 Earth-radius planet", abs(L.planet_radius_earth(0.07, 1.0) - 7.64) < 0.01))

    # odd-even
    o, e, sg = L.odd_even(t, flat, pr, t0f, 0.08, 0.0008)
    checks.append((f"planet: odd and even depths agree (difference {sg:.1f} sigma, below 3)", sg < 3))
    eb = L.eclipsing_binary(t)
    eres = L.run_bls(t, eb)
    eper, et0 = L.refine(t, eb, eres)[1:3]
    checks.append((f"binary: BLS locks on half the true orbit (got {eper:.3f} d, orbit is 6.0 d)", abs(eper / 3.0 - 1) < 0.01))
    o2, e2, sg2 = L.odd_even(t, eb, eper, et0, 0.08, 0.0008)
    checks.append((f"binary: odd and even depths differ by {sg2:.1f} sigma (above 5)", sg2 > 5))

    # false alarms (seeded Monte Carlo)
    mx = L.noise_max_snr(100)
    checks.append((f"false alarms: {L.false_alarm_rate(mx, 5):.0%} of 100 noise runs exceed SNR 5 (expect 7 percent)", abs(L.false_alarm_rate(mx, 5) - 0.07) < 1e-9))
    checks.append((f"false alarms: none of 100 noise runs exceed SNR 6 (largest {mx.max():.1f})", L.false_alarm_rate(mx, 6) == 0.0))
    checks.append(("false-alarm rate is non-increasing with the threshold", L.false_alarm_rate(mx, 4) >= L.false_alarm_rate(mx, 5) >= L.false_alarm_rate(mx, 7)))

    # failure cases
    ta, fa, _ = L.alias_case()
    ra = L.run_bls(ta, L.detrend(ta, fa, 1.0)[0])
    sp, s2p = L.alias_snr(ra, 4.2), L.alias_snr(ra, 8.4)
    checks.append((f"failure case: odd transits lost, SNR at P ({sp:.1f}) and 2P ({s2p:.1f}) differ by under 5 percent", abs(sp - s2p) / sp < 0.05))
    to, fo, _ = L.one_transit_case()
    ro = L.run_bls(to, fo, pmin=2.0, pmax=14.0)
    good = ro["periods"][ro["snr"] >= 0.9 * ro["snr"].max()]
    checks.append((f"failure case: one transit, periods {good.min():.1f} to {good.max():.1f} d all fit (span at least 3.5 d)", good.min() >= 9.5 and good.max() - good.min() >= 3.5))

    # mini-project: the worked example
    tp, fp = L.project_lightcurve()
    found = L.find_planets(tp, fp)
    truth = L.project_planets()
    ok_p = [abs(a["period"] / b_["period"] - 1) < 0.01 for a, b_ in zip(found, truth)]
    checks.append((f"worked example: mini-project finds P = {found[0]['period']:.3f} d and {found[1]['period']:.3f} d (truth 6.43 and 2.71, within 1 percent)", all(ok_p)))
    rt = [L.planet_radius_earth(x["k"], L.R_STAR_PROJECT) for x in truth]
    checks.append((f"mini-project radii {found[0]['radius_earth']:.1f} and {found[1]['radius_earth']:.1f} Earth radii are within 10 percent of the truth {rt[0]:.1f} and {rt[1]:.1f}",
                   all(abs(x["radius_earth"] / r - 1) < 0.10 for x, r in zip(found, rt))))
    checks.append(("mini-project: both candidates pass the odd-even check (below 3 sigma)", all(x["oe_sigma"] < 3 for x in found)))
    checks.append(("mini-project: both detections have SNR above 7", all(x["snr"] > 7 for x in found)))
    # numbers quoted in the text
    checks.append((f"text: SNR at P/2, P, 2P rounds to 26, 37, 27 (got {shalf:.1f}, {s1:.1f}, {s2:.1f})", (round(shalf), round(s1), round(s2)) == (26, 37, 27)))
    checks.append(("text: window 0.15 d keeps 3 percent and 1.0 d keeps 94 percent", round(r_short * 100) == 3 and round(r_long * 100) == 94))
    checks.append(("text: the fitted k is 0.068, which is 2.9 percent below 0.07", abs(k - 0.068) < 1e-9 and abs((k / 0.07 - 1) * 100 + 2.9) < 0.05))
    checks.append(("text: largest noise SNR 5.2; alias case SNR 28.2 and 28.1", round(float(mx.max()), 1) == 5.2 and (round(sp, 1), round(s2p, 1)) == (28.2, 28.1)))
    checks.append(("text: one Earth radius is 695700 / 6371 = 109.2 per solar radius and depth 0.0025 on 0.9 Rsun gives 4.91", abs(695700 / 6371 - 109.2) < 0.05 and abs(L.planet_radius_earth(np.sqrt(0.0025), 0.9) - 4.91) < 0.005))
    w1, w2 = found
    checks.append((f"worked example: planet 1 depth {w1['depth'] * 1e6:.0f} ppm, k {np.sqrt(w1['depth']):.4f}, radius {np.sqrt(w1['depth']) * 0.9 * 695700 / 6371:.2f} Earth radii, SNR {w1['snr']:.0f}, odd-even {w1['oe_sigma']:.1f} sigma",
                   round(w1["depth"] * 1e6) == 2311 and abs(np.sqrt(w1["depth"]) - 0.0481) < 5e-5 and abs(np.sqrt(w1["depth"]) * 0.9 * 695700 / 6371 - 4.73) < 0.01 and round(w1["snr"]) == 25 and round(w1["oe_sigma"], 1) == 0.5))
    checks.append((f"worked example: planet 2 SNR {w2['snr']:.1f}, radius {w2['radius_earth']:.1f} Earth radii, odd-even {w2['oe_sigma']:.1f} sigma", round(w2["snr"], 1) == 9.5 and round(w2["radius_earth"], 1) == 2.6 and round(w2["oe_sigma"], 1) == 1.7))
    # roadmap claim: a 600 ppm planet is not detected by the shipped search
    weak = dict(p, k=np.sqrt(6e-4))
    f6 = L.synthetic_star(t, [weak])
    r6 = L.run_bls(t, L.detrend(t, f6, 1.0)[0])
    checks.append((f"roadmap: a 600 ppm planet gives only SNR {L.alias_snr(r6, 4.2):.1f} at the true period (below 7)", 4.7 < L.alias_snr(r6, 4.2) < 4.9))
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
