"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    CHENNAI = 13.0
    worst = 0.0
    for n, hr, f, dep in ((355, 12.0, 180, 0.6), (172, 15.0, 270, 0.6), (80, 9.0, 90, 0.6), (300, 10.5, 150, 0.6),
                          (30, 14.0, 200, 0.3), (200, 8.0, 60, 1.0)):
        d = float(L.declination(n))
        a, z = L.sun_position(CHENNAI, d, hr)
        worst = max(worst, abs(float(L.sunlit_fraction(a, z, f, dep, 1.5, 0.3)) - L.sunlit_fraction_raytrace(CHENNAI, d, hr, f, dep, 1.5, 0.3)))
    checks.append((f"overhang formula agrees with the independent 3D ray test (worst difference {worst:.4f})", worst < 1e-3))
    theta = L.visible_sky_angle(0.6)
    checks.append(("worked example: visible sky angle below a 0.6 m overhang is 60.26 degrees (atan(1.05 / 0.6))",
                   abs(theta - np.degrees(np.arctan(1.05 / 0.6))) < 1e-9 and abs(theta - 60.26) < 0.01))
    df = L.average_daylight_factor(3.0, theta)
    checks.append(("worked example: average daylight factor 1.79% (hand: 0.7 x 3 x 60.26 / (94 x 0.75))",
                   abs(df - 0.7 * 3.0 * 60.255 / (94.0 * 0.75)) < 1e-3 and abs(df - 1.795) < 0.002))
    r = L.simulate_year(CHENNAI, 180, 0.25, 0.6)
    checks.append(("worked example: south window WWR 0.25, 0.6 m overhang uses about 527 kWh per year",
                   abs(r["total_kwh"] - 526.8) < 1.0 and abs(r["light_kwh"] - 179.5) < 1.0))
    checks.append(("energy bookkeeping: total = lights + (solar + conduction + lights) / COP",
                   abs(r["total_kwh"] - (r["light_kwh"] + (r["solar_kwh"] + r["cond_kwh"] + r["light_kwh"]) / L.COP)) < 1e-9))
    checks.append(("conduction hand check: 3.8 W/(m2 K) x 3 m2 x 4 K x 8 h x 365 days = 133.2 kWh",
                   abs(r["cond_kwh"] - 3.8 * 3.0 * 4.0 * 8 * 365 / 1000) < 1e-6))
    checks.append(("monthly solar heat adds up to the yearly solar heat", abs(r["monthly_solar"].sum() - r["solar_all_kwh"]) < 1e-6))
    lights_max = L.LPD * L.ROOM_W * L.ROOM_D * 8 * 365 / 1000
    tiny = L.simulate_year(CHENNAI, 180, 0.01, 0.0)
    checks.append(("limit: a tiny window needs the lights almost all the time (within 5% of 467 kWh)",
                   tiny["light_kwh"] <= lights_max + 1e-9 and tiny["light_kwh"] > 0.95 * lights_max))
    checks.append(("a bigger window always means less lighting energy",
                   all(L.simulate_year(CHENNAI, 180, a, 0.6)["light_kwh"] >= L.simulate_year(CHENNAI, 180, b, 0.6)["light_kwh"] - 1e-9
                       for a, b in ((0.1, 0.2), (0.2, 0.3), (0.3, 0.4)))))
    checks.append(("an overhang never adds solar heat",
                   L.simulate_year(CHENNAI, 180, 0.3, 0.6)["solar_kwh"] <= L.simulate_year(CHENNAI, 180, 0.3, 0.0)["solar_kwh"]))
    _, _, tot = L.best_wwr(CHENNAI, 180, 0.6)
    k = int(np.argmin(tot))
    checks.append(("there is a best window size in between (not the smallest, not the largest)", 0 < k < len(tot) - 1))
    w_big = L.simulate_year(CHENNAI, 270, 0.5, 0.0)["total_kwh"]
    checks.append(("failure case: a large unshaded west window uses more than twice the planned south window",
                   w_big > 2.0 * r["total_kwh"]))
    checks.append(("in Chennai a north window beats a west window of the same size",
                   L.simulate_year(CHENNAI, 0, 0.25, 0.0)["total_kwh"] < L.simulate_year(CHENNAI, 270, 0.25, 0.0)["total_kwh"]))
    checks.append(("a smaller time step gives the same yearly total (within 0.1%)",
                   abs(L.simulate_year(CHENNAI, 180, 0.25, 0.6, step=0.1)["total_kwh"] - r["total_kwh"]) < 1e-3 * r["total_kwh"]))
    bad = 0
    for call in (lambda: L.simulate_year(CHENNAI, 180, 0.0), lambda: L.simulate_year(CHENNAI, 180, 0.8),
                 lambda: L.average_daylight_factor(3.0, refl=1.0)):
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
