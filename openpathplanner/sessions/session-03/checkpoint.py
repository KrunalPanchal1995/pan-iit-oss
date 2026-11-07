"""Checkpoint for Session 3. Prints PASS or FAIL."""
import itertools
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []

    # --- collision tests on known cases
    circ = ("circle", 5.0, 5.0, 1.0)
    cases_c = [((0, 5), (10, 5), True, "through the middle"), ((0, 6), (10, 6), False, "tangent line only touches"),
               ((0, 6.5), (10, 6.5), False, "passes 1.5 away"), ((0, 5), (3, 5), False, "stops 1 short of the circle"),
               ((4.5, 5), (5.5, 5), True, "starts inside"), ((0, 0), (10, 10), True, "diagonal through the centre"),
               ((5, 5), (5, 5), True, "a point at the centre")]
    checks.append(("segment-circle: 7 known cases", all(L.seg_circle_hit(p, q, circ) == want for p, q, want, _ in cases_c)))
    rect = ("rect", 4.0, 4.0, 6.0, 6.0)
    cases_r = [((0, 5), (10, 5), True), ((0, 4), (10, 4), False), ((5, 7), (7, 5), False), ((3, 7), (7, 3), True),
               ((0, 5), (3, 5), False), ((4.5, 5), (5.5, 5), True), ((0, 7), (10, 7), False), ((5, 0), (5, 10), True),
               ((3, 0), (3, 10), False), ((6, 5), (8, 5), False), ((5, 7), (7, 5.0001), False), ((0, 0), (10, 10), True)]
    checks.append(("segment-rectangle: 12 known cases (edge-sliding and corner-touching are free, crossing is a hit)",
                   all(L.seg_rect_hit(p, q, rect) == want for p, q, want in cases_r)))
    checks.append(("a reversed segment gives the same answer", L.seg_rect_hit((10, 5), (0, 5), rect) and not L.seg_rect_hit((10, 4), (0, 4), rect)))
    checks.append(("point_free: centre of circle blocked, map corner free",
                   not L.point_free((5, 5), [circ]) and L.point_free((0, 0), [circ]) and not L.point_free((11, 5), [])))

    # --- validation: exact shortest path around the wall
    exact = L.wall_corner_path(L.WALL)
    d = math.sqrt(3.8 ** 2 + 5.0 ** 2)
    ln = L.path_length(exact)
    checks.append((f"worked example: exact path = 2 sqrt(3.8^2 + 5^2) + 0.4 = 12.960 m (got {ln:.4f})", abs(ln - (2 * d + 0.4)) < 1e-12 and round(ln, 3) == 12.960))
    checks.append(("exact path is collision-free at 4 x 50 sampled points", L.path_is_free(exact, L.WALL["obstacles"])))
    checks.append(("the straight line start-goal (8 m) is blocked by the wall", not L.segment_free(L.WALL["start"], L.WALL["goal"], L.WALL["obstacles"])))
    vg = L.visibility_graph_path(L.WALL)
    checks.append(("visibility-graph Dijkstra finds the same corner path and length", abs(L.path_length(vg) - ln) < 1e-9 and len(vg) == 4))

    ln3 = 2 * math.sqrt(3.8 ** 2 + 3.0 ** 2) + 0.4
    checks.append((f"practice question: start (1, 3) gives 10.083 m (got {ln3:.3f})",
                   abs(ln3 - 10.083) < 6e-4 and abs(L.path_length(L.wall_corner_path({"obstacles": L.WALL["obstacles"], "start": (1.0, 3.0), "goal": (9.0, 3.0)})) - ln3) < 1e-12))
    checks.append(("worked example: the wall adds 4.960 m to the 8 m straight line; sqrt(39.44) = 6.280", abs(ln - 8 - 4.960) < 5e-4 and round(math.sqrt(39.44), 3) == 6.280))

    # --- RRT
    r = L.rrt(L.CLUTTER, seed=1)
    raw = L.path_length(r["path"])
    checks.append((f"RRT seed 1 finds a path in 186 iterations, length 16.130 m (got {r['iterations']}, {raw:.3f})",
                   r["found"] and r["iterations"] == 186 and abs(raw - 16.130) < 6e-4))
    checks.append(("RRT path starts at the start, ends at the goal", r["path"][0] == L.CLUTTER["start"] and r["path"][-1] == L.CLUTTER["goal"]))
    checks.append(("RRT path is collision-free at every sampled point and every tree edge is free",
                   L.path_is_free(r["path"], L.CLUTTER["obstacles"])
                   and all(L.segment_free(r["nodes"][r["parent"][k]], r["nodes"][k], L.CLUTTER["obstacles"]) for k in range(1, len(r["nodes"])))))
    checks.append(("RRT tree edges are at most one step (0.5 m) long",
                   all(math.dist(r["nodes"][r["parent"][k]], r["nodes"][k]) <= 0.5 + 1e-9 for k in range(1, len(r["nodes"]) - 1))))
    r_again, r_other = L.rrt(L.CLUTTER, seed=1), L.rrt(L.CLUTTER, seed=2)
    checks.append(("the same seed gives the same tree; another seed gives a different one", r_again["nodes"] == r["nodes"] and r_other["nodes"] != r["nodes"]))
    sm = L.shortcut(r["path"], L.CLUTTER["obstacles"], seed=1)
    ls = L.path_length(sm)
    checks.append((f"shortcut smoothing: 16.130 m becomes 12.829 m, still collision-free (got {ls:.3f})",
                   abs(ls - 12.829) < 6e-4 and L.path_is_free(sm, L.CLUTTER["obstacles"]) and sm[0] == r["path"][0] and sm[-1] == r["path"][-1]))
    checks.append(("no path is ever lengthened by shortcutting (10 seeds)",
                   all(L.path_length(L.shortcut(L.rrt(L.CLUTTER, seed=s)["path"], L.CLUTTER["obstacles"], seed=s)) <= L.path_length(L.rrt(L.CLUTTER, seed=s)["path"]) + 1e-9 for s in range(10))))
    checks.append(("the straight-line lower bound (start to goal, 11.314 m) is below every path length",
                   abs(math.dist(L.CLUTTER["start"], L.CLUTTER["goal"]) - 8 * math.sqrt(2)) < 1e-12 and 11.314 < ls < raw))

    # --- RRT*
    star = L.rrt_star(L.WALL, iterations=3000, seed=2)
    tr = dict(star["trace"])
    finite = [c for _, c in star["trace"] if math.isfinite(c)]
    opt = L.path_length(exact)
    checks.append(("RRT* best-path cost never increases with iterations", all(a >= b - 1e-9 for a, b in zip(finite, finite[1:])) and len(finite) > 20))
    checks.append((f"RRT* wall, seed 2: 14.792 m at 500, 13.265 at 1000, 13.158 at 3000 iterations (got {tr[500]:.3f}, {tr[1000]:.3f}, {tr[3000]:.3f})",
                   abs(tr[500] - 14.792) < 6e-4 and abs(tr[1000] - 13.265) < 6e-4 and abs(tr[3000] - 13.158) < 6e-4))
    checks.append(("worked example: grid A* is 5 percent and RRT* (3000 iterations) 1.5 percent above the exact length",
                   round(100 * (13.607 / opt - 1)) == 5 and round(100 * (tr[3000] / opt - 1), 1) == 1.5))
    checks.append(("RRT* never beats the exact optimum 12.960 and ends within 2 percent of it", min(finite) >= opt - 1e-9 and tr[3000] <= 1.02 * opt))
    checks.append(("RRT* final path is collision-free and equals the reported best cost",
                   L.path_is_free(star["path"], L.WALL["obstacles"]) and abs(L.path_length(star["path"]) - star["best"]) < 1e-6))
    plain = L.rrt(L.WALL, seed=2)
    checks.append(("plain RRT on the same wall is longer than RRT* after 3000 iterations", plain["found"] and L.path_length(plain["path"]) > star["best"]))

    # --- grid A* versus RRT versus RRT* on the clutter map
    blocked = L.rasterize(L.CLUTTER["obstacles"])
    ga = L.grid_astar(blocked, L.CLUTTER["start"], L.CLUTTER["goal"])
    checks.append((f"grid A* on the clutter map: 12.685 m, 1565 expanded cells (got {ga['cost']:.3f}, {ga['expanded']})",
                   abs(ga["cost"] - 12.685) < 6e-4 and ga["expanded"] == 1565))
    checks.append(("grid A* path is collision-free", L.path_is_free(ga["path"], L.CLUTTER["obstacles"])))
    rs = L.rrt_star(L.CLUTTER, iterations=2000, seed=1)
    lr = L.path_length(rs["path"])
    checks.append((f"RRT* on the clutter map (2000 iterations, seed 1): 12.136 m, 1493 nodes (got {lr:.3f}, {rs['nodes']})",
                   abs(lr - 12.136) < 6e-4 and rs["nodes"] == 1493 and L.path_is_free(rs["path"], L.CLUTTER["obstacles"])))
    checks.append(("ordering on the clutter map: RRT* (12.136) < smoothed RRT (12.829) and < raw RRT (16.130); grid A* is 12.685", lr < ls < raw and lr < ga["cost"] < ls))
    gw = L.grid_astar(L.rasterize(L.WALL["obstacles"]), L.WALL["start"], L.WALL["goal"])
    checks.append((f"grid A* on the wall: 13.607 m, 5 percent above the exact 12.960 (got {gw['cost']:.3f})", abs(gw["cost"] - 13.607) < 6e-4 and gw["cost"] > opt))

    # --- an inadmissible heuristic: faster but longer
    gwt = L.grid_astar(blocked, L.CLUTTER["start"], L.CLUTTER["goal"], weight=3.0)
    checks.append((f"heuristic multiplied by 3: path 13.130 m instead of 12.685, expanded 117 instead of 1565 (got {gwt['cost']:.3f}, {gwt['expanded']})",
                   abs(gwt["cost"] - 13.130) < 6e-4 and gwt["expanded"] == 117 and gwt["cost"] > ga["cost"]))

    # --- failure case: narrow passage
    rates = {gap: L.success_rate(L.narrow_map(gap), 0.5, 1000, 100) for gap in (0.05, 0.1, 0.3, 1.0, 3.0)}
    checks.append((f"success rate over 100 seeds (1000 iterations) for gaps 0.05, 0.1, 0.3, 1.0, 3.0 m: 0.12, 0.33, 0.82, 1.00, 1.00 (got {list(rates.values())})",
                   [rates[g] for g in (0.05, 0.1, 0.3, 1.0, 3.0)] == [0.12, 0.33, 0.82, 1.0, 1.0]))
    checks.append(("more iterations help (probabilistic completeness): gap 0.1 succeeds 0.24 of the time at 500 iterations and 0.33 at 1000",
                   L.success_rate(L.narrow_map(0.1), 0.5, 500, 100) == 0.24))

    # --- step size
    got = {st: L.step_study(L.CLUTTER, st) for st in (0.25, 0.5, 1.0, 2.0)}
    checks.append(("step sensitivity: mean iterations 440, 204, 105, 60 for steps 0.25, 0.5, 1.0, 2.0 m (20 seeds, all succeed)",
                   all(abs(got[st]["mean_iterations"] - v) < 0.5 and got[st]["success"] == 1.0 for st, v in zip(got, (440, 204, 105, 60)))))
    checks.append(("step sensitivity: mean raw path length 15.28, 15.39, 15.93, 15.97 m, longer for bigger steps",
                   all(abs(got[st]["mean_length"] - v) < 0.006 for st, v in zip(got, (15.28, 15.39, 15.93, 15.97)))))

    # --- mini-project warehouse
    wh = L.warehouse_grid()
    checks.append(("warehouse: 36 x 18 cells, 9 shelf blocks of 16 cells = 144 shelf cells; dock and picks are free",
                   wh.shape == (18, 36) and int(wh.sum()) == 144 and not wh[L.DOCK[1], L.DOCK[0]] and all(not wh[y, x] for x, y in L.PICKS)))
    stops = [L.DOCK] + L.PICKS + [L.DOCK]
    total, exp = L.pick_route(wh, stops)
    checks.append((f"mini-project: the given order has length 82.97 and 244 expanded nodes (got {total:.2f}, {exp})", abs(total - 82.97) < 6e-3 and exp == 244))
    straight = sum(math.dist(a, b) for a, b in zip(stops, stops[1:]))
    checks.append((f"the straight-line sum over the legs, 70.39, is a lower bound (got {straight:.2f})", abs(straight - 70.39) < 6e-3 and straight < total))
    dj = sum(L.astar_cells(wh, a, b, weight=0.0)["expanded"] for a, b in zip(stops, stops[1:]))
    checks.append((f"Dijkstra (weight 0) expands 1209 nodes on the same legs against 244 for A* (got {dj})", dj == 1209 and exp < dj))
    best = min(L.pick_route(wh, [L.DOCK] + list(p) + [L.DOCK])[0] for p in itertools.permutations(L.PICKS))
    checks.append((f"best of all 24 pick orders is 77.31, the given order is 82.97 (got best {best:.2f})", abs(best - 77.31) < 6e-3))

    # --- edge cases
    checks.append(("zero-length segment inside a rectangle is a hit; outside is not", L.seg_rect_hit((5, 5), (5, 5), rect) and not L.seg_rect_hit((1, 1), (1, 1), rect)))
    sealed = np.zeros((5, 5), dtype=bool)
    sealed[:, 2] = True
    checks.append(("grid A* on a sealed grid returns no path", L.astar_cells(sealed, (0, 0), (4, 4))["cells"] is None))
    checks.append(("RRT with a goal inside a closed box reports found = False after the iteration limit",
                   not L.rrt({"obstacles": [("rect", 7.0, 7.0, 9.5, 9.5)], "start": (1.0, 1.0), "goal": (8.0, 8.0)}, max_iter=300, seed=0)["found"]))
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
