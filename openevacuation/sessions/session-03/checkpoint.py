"""Checkpoint for Session 3. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    checks.append(("stair capacity of a 1.2 m stair: 1.015 x 0.9 = 0.914 persons/s", abs(L.capacity(1.2, L.K_STAIR) - 0.9135) < 1e-3))
    # 1. one room, one door: the network model must reproduce the Session 1 formula
    links = {"door": {"cap": 1.17, "tau": 0.0, "next": None}}
    r = L.simulate(links, [("door", 76.7, 240)], dt=0.1)
    checks.append((f"limit: one room and one door reproduces Session 1 (76.7 + 240 / 1.17 = 281.8 s): {r['t_evac']:.1f} s",
                   abs(r["t_evac"] - (76.7 + 240 / 1.17)) < 0.3))
    # 2. conservation of people
    one = L.evacuate(floors=3, per_floor=120, exit_width=1.5)
    total_in_links = one["inside"]
    checks.append(("conservation: everyone (480 people) comes out, nobody is lost or created",
                   abs(one["outside"][-1] - 480) < 1e-6 and np.all(np.diff(one["outside"]) >= -1e-12)))
    checks.append(("people inside never go up after the alarm", np.all(np.diff(total_in_links) <= 1e-9)))
    # 3. bottleneck bound
    b = L.bottleneck_bound(floors=3, per_floor=120)
    checks.append((f"worked example: one 1.2 m stair empties in {one['t_evac']:.1f} s, just above the hand bound {b:.1f} s",
                   b <= one["t_evac"] <= b + 5.0 and abs(b - 480.7) < 0.2))
    checks.append(("the final exit never passes more people per step than its capacity allows",
                   np.all(np.diff(one["outside"]) <= (L.capacity(1.5, L.K_LEVEL)) * 0.5 + 1e-9)))
    # 4. convergence in the time step
    t1 = L.evacuate(floors=3, per_floor=120, exit_width=1.5, dt=0.1)["t_evac"]
    t2 = L.evacuate(floors=3, per_floor=120, exit_width=1.5, dt=1.0)["t_evac"]
    checks.append((f"a smaller time step gives the same answer (dt 0.1 s: {t1:.1f} s, dt 1 s: {t2:.1f} s)", abs(t1 - t2) < 5.0))
    # 5. behaviour
    two = L.evacuate(floors=3, per_floor=120, n_stairs=2, exit_width=1.5)
    checks.append((f"two stairs: {two['t_evac']:.1f} s, faster than one but not twice as fast (pre-movement stays)",
                   two["t_evac"] < one["t_evac"] and two["t_evac"] > one["t_evac"] / 2))
    checks.append(("a narrow final exit (0.9 m) becomes the new bottleneck and slows everything",
                   L.evacuate(floors=3, per_floor=120, exit_width=0.9)["t_evac"] > one["t_evac"] + 100))
    checks.append(("a longer pre-movement time delays the end by the same amount",
                   abs(L.evacuate(floors=3, per_floor=120, exit_width=1.5, t_pre=120.0)["t_evac"] - one["t_evac"] - 60.0) < 1.0))
    checks.append(("only a ground floor: no stair, same as the Session 1 formula",
                   abs(L.evacuate(floors=0, per_floor=120, exit_width=1.2)["t_evac"] - (60 + 20 / 1.19 + 120 / L.capacity(1.2, L.K_LEVEL))) < 1.0))
    # 6. RSET, ASET and the plan
    checks.append(("RSET = detection + evacuation", abs(L.rset(t_detect=30.0, floors=3, per_floor=120, exit_width=1.5) - (30 + one["t_evac"])) < 1e-9))
    checks.append(("is_safe uses the 1.5 safety factor: 600 s is safe with ASET 900 s, 601 s is not",
                   L.is_safe(900, 600) and not L.is_safe(900, 601)))
    plan = L.plan_stairs(900.0)
    checks.append((f"design: ASET 900 s needs two stairs of {plan[0]} m (RSET {plan[1]:.0f} s, one blocked {plan[2]:.0f} s)",
                   plan[0] == 1.2 and L.is_safe(900, plan[2]) and not L.is_safe(900, L.stair_rset(1, 1.0))))
    mp = L.plan_stairs(1200.0, floors=5, per_floor=150)
    checks.append((f"mini-project: 6-storey hostel, ASET 1200 s needs two stairs of {mp[0]} m (one blocked: {mp[2]:.0f} s)",
                   mp[0] == 1.5 and not L.is_safe(1200, L.stair_rset(1, 1.2, floors=5, per_floor=150))))
    bad = 0
    for call in (lambda: L.capacity(0.2, L.K_LEVEL), lambda: L.simulate({"a": {"cap": 0, "tau": 0, "next": None}}, []),
                 lambda: L.simulate({"a": {"cap": 1, "tau": 0, "next": "b"}}, []), lambda: L.is_safe(0, 100),
                 lambda: L.building(n_stairs=0)):
        try:
            call()
        except ValueError:
            bad += 1
    checks.append(("invalid inputs raise ValueError", bad == 5))
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
