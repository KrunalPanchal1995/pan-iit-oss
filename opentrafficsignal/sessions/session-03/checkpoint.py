"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    q = [0.20, 0.10]
    plan60 = L.FixedPlan((27.0, 27.0))

    # --- arrivals
    counts = [len(L.poisson_arrivals(np.random.default_rng(sd), 0.2, 3600.0)) for sd in range(5, 25)]
    checks.append(("Poisson arrivals: the mean over 20 seeds is about q T = 720 cars an hour (within 3 percent)",
                   abs(np.mean(counts) - 720) < 0.03 * 720))
    checks.append(("even arrivals: exactly 720 cars at 0.2 cars/s", len(L.regular_arrivals(0.2, 3600.0)) == 720))
    a1 = L.simulate(q, plan60, seed=3, T=600.0)
    a2 = L.simulate(q, plan60, seed=3, T=600.0)
    a3 = L.simulate(q, plan60, seed=4, T=600.0)
    checks.append(("same seed gives the same result", a1["avg_delay"] == a2["avg_delay"] and a1["arrived"] == a2["arrived"]))
    checks.append(("different seeds give different arrivals", a1["arrived"] != a3["arrived"] or a1["avg_delay"] != a3["avg_delay"]))

    # --- validation 1: even arrivals against the formula (worked example)
    reg = L.simulate(q, plan60, poisson=False, T=7200.0)
    d_formula = L.fixed_plan_uniform_delay(q, plan60)
    checks.append((f"worked example: formula gives 13.86 s (got {d_formula:.2f})", abs(d_formula - 13.8646) < 1e-3))
    checks.append((f"worked example: even-arrival simulation {reg['avg_delay']:.2f} s is within 5 percent of 13.86 s",
                   abs(reg["avg_delay"] / d_formula - 1.0) < 0.05))
    checks.append(("even arrivals: largest queue about q r = 0.2 x 33 = 6.6, so 7 cars", reg["max_queue"] == 7))

    # --- validation 2: conservation, for random arrivals, both controllers, two and four approaches
    ok = True
    for ctrl in (plan60, L.Actuated()):
        r = L.simulate(q, ctrl, seed=2, T=1800.0)
        ok &= L.conservation_gap(r) == [0, 0]
    r4 = L.simulate([0.4, 0.3, 0.35, 0.25], L.Actuated(), s=1.0, seed=2, T=1800.0)
    ok &= L.conservation_gap(r4) == [0, 0, 0, 0]
    checks.append(("conservation: arrived = departed + still waiting (fixed, actuated, four approaches)", bool(ok)))

    # --- validation 3: total delay equals the area under the queue curve
    area = reg["qlen"].sum() * reg["dt"]
    checks.append(("sum of car delays equals area under the queue curve within 3 percent", abs(reg["total_delay"] / area - 1.0) < 0.03))

    # --- randomness
    pois = L.mean_over_seeds(q, lambda: plan60, seeds=range(1, 7), T=3600.0)
    checks.append(("random arrivals give more delay and longer queues than even arrivals",
                   pois[0] > reg["avg_delay"] + 2.0 and pois[1] > reg["max_queue"]))

    # --- edge cases
    z = L.simulate([0.0, 0.0], plan60, T=300.0)
    checks.append(("no cars: zero delay and zero queue, no crash", z["avg_delay"] == 0.0 and z["max_queue"] == 0.0))

    # --- Webster formula and plan
    checks.append(("Webster cycle: (1.5 x 6 + 5) / (1 - 0.6) = 35 s", abs(L.webster_cycle(0.6) - 35.0) < 1e-9))
    wp = L.webster_plan(q)
    checks.append(("Webster plan greens 19.33 s and 9.67 s", abs(wp.g[0] - 58.0 / 3) < 1e-9 and abs(wp.g[1] - 29.0 / 3) < 1e-9))
    try:
        L.webster_plan([0.35, 0.20])
        raised = False
    except ValueError:
        raised = True
    checks.append(("Y >= 1: no fixed plan exists (edge case raises ValueError)", raised))

    # --- sensitivity to cycle length
    def delay_at(Cc):
        spare = Cc - L.LOST
        return L.mean_over_seeds(q, lambda: L.FixedPlan((spare * 2 / 3, spare / 3)), seeds=range(1, 7))[0]
    d35, d100 = delay_at(35.0), delay_at(100.0)
    checks.append((f"a cycle of 100 s gives much more delay than Webster's 35 s ({d100:.1f} against {d35:.1f} s)", d100 > 1.5 * d35))
    d15 = L.mean_over_seeds(q, lambda: L.FixedPlan((6.0, 3.0)), seeds=range(1, 4))[0]
    checks.append((f"a 15 s cycle (x = 1 on both roads, the shortest possible) is worse than 35 s ({d15:.1f} against {d35:.1f} s)",
                   d15 > 1.05 * d35))

    # --- fixed against actuated
    d_act = L.mean_over_seeds(q, L.Actuated, seeds=range(1, 7))[0]
    checks.append((f"actuated rule lowers the delay of the Webster fixed plan by at least 20 percent ({d_act:.1f} against {d35:.1f} s)",
                   d_act < 0.8 * d35))

    # --- actuated rule: first green of phase 0 under two scripted queue situations
    def first_green(queues):
        ctl = L.Actuated(min_green=8.0, max_green=45.0)
        t, length = 0.0, 0.0
        while t < 200.0:
            ph, green = ctl(t, queues)
            if not (ph == 0 and green):
                return length
            length += 0.5
            t += 0.5
        return length
    checks.append(("actuated: empty queue on green and a car waiting on the other road -> green lasts the minimum, 8 s",
                   abs(first_green([0, 4]) - 8.0) <= 0.5))
    checks.append(("actuated: both roads busy -> green stops at the maximum, 45 s", abs(first_green([5, 5]) - 45.0) <= 0.5))
    checks.append(("actuated: nobody waiting on the other road -> green is kept", first_green([0, 0]) >= 199.0))

    # --- failure case: oversaturation
    r = L.simulate([0.35, 0.20], plan60, T=7200.0)
    half = len(r["qlen"]) // 2
    w1, w2 = r["qlen"][half - 1].sum(), r["qlen"][-1].sum()
    checks.append((f"oversaturation: queue grows without bound ({w1:.0f} cars after 1 h, {w2:.0f} after 2 h)", w2 > 1.8 * w1 and w1 > 100))
    ra = L.simulate([0.30, 0.10], plan60, poisson=False, T=3600.0)
    rate = ra["qlen"][-1, 0] / 3600.0
    checks.append((f"overloaded approach grows near q - s g / C = 0.075 cars/s (got {rate:.3f})", abs(rate - 0.075) < 0.012))

    # --- four-approach mini-project numbers
    q4 = [360 / 900, 270 / 900, 315 / 900, 225 / 900]
    plan4 = L.webster_plan(q4, s=1.0)
    checks.append(("mini-project: Webster cycle for 360/270/315/225 cars per 15 min is 46.7 s",
                   abs(plan4.cycle - 46.6667) < 1e-3 and abs(plan4.g[0] - 23.2381) < 1e-3 and abs(plan4.g[1] - 17.4286) < 1e-3))
    dw = L.mean_over_seeds(q4, lambda: plan4, seeds=range(1, 7), s=1.0)[0]
    de = L.mean_over_seeds(q4, lambda: L.FixedPlan((27.0, 27.0)), seeds=range(1, 7), s=1.0)[0]
    checks.append((f"mini-project: Webster timing cuts delay by at least 15 percent against 27/27 ({dw:.1f} against {de:.1f} s)", dw < 0.85 * de))
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
