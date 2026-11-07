"""Checkpoint for Session 2. Prints PASS or FAIL."""
import math

import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    s2 = math.sqrt(2.0)

    # hand-checkable: empty 3 x 3 floor, corner to corner
    empty = np.zeros((3, 3), dtype=bool)
    checks.append(("3x3 empty, 4-connected: every method gives cost 4",
                   all(abs(f(empty, (0, 0), (2, 2), False)["cost"] - 4.0) < 1e-12 for f in (L.bfs, L.dijkstra, L.astar))))
    checks.append(("3x3 empty, 8-connected: Dijkstra and A* give 2 sqrt 2 = 2.828",
                   all(abs(f(empty, (0, 0), (2, 2), True)["cost"] - 2 * s2) < 1e-12 for f in (L.dijkstra, L.astar))))

    # worked example: the 5 x 3 hand grid
    blocked, start, goal = L.from_text(L.HAND_GRID)
    d4 = L.dijkstra(blocked, start, goal, False)
    d8 = L.dijkstra(blocked, start, goal, True)
    checks.append((f"worked example: 4-connected cost is 7 (got {d4['cost']:.3f})", abs(d4["cost"] - 7.0) < 1e-12))
    checks.append((f"worked example: 8-connected cost is 3 + 2 sqrt 2 = 5.828 (got {d8['cost']:.3f})", abs(d8["cost"] - (3 + 2 * s2)) < 1e-12))
    checks.append(("worked example: Manhattan lower bound is 5, less than 7", L.manhattan(start, goal) == 5 < d4["cost"]))
    checks.append(("worked example: A* agrees with Dijkstra in both modes",
                   abs(L.astar(blocked, start, goal, False)["cost"] - 7.0) < 1e-12
                   and abs(L.astar(blocked, start, goal, True)["cost"] - (3 + 2 * s2)) < 1e-12))
    # no corner cutting: (1,1) -> (2,2) is forbidden because (2,1) is a wall
    nb = [n for n, _ in L.neighbors(blocked, (1, 1), True)]
    checks.append(("a diagonal move may not cut a corner", (2, 2) not in nb and (2, 0) not in nb and (0, 0) in nb))
    checks.append(("path cost helper: 1 per straight move, sqrt 2 per diagonal", abs(L.path_cost([(0, 0), (1, 0), (2, 1)]) - (1 + s2)) < 1e-12))

    # BFS minimises moves, not cost, when diagonals are allowed
    tb, ts, tg = L.from_text(L.BFS_TRAP)
    bf, dj = L.bfs(tb, ts, tg, True), L.dijkstra(tb, ts, tg, True)
    checks.append((f"BFS trap grid: BFS costs 2 + 3 sqrt 2 = 6.243, Dijkstra 6.0 (got {bf['cost']:.3f}, {dj['cost']:.3f})",
                   abs(bf["cost"] - (2 + 3 * s2)) < 1e-9 and abs(dj["cost"] - 6.0) < 1e-9 and len(bf["path"]) < len(dj["path"])))
    checks.append(("with 4-connection BFS equals Dijkstra", abs(L.bfs(tb, ts, tg, False)["cost"] - L.dijkstra(tb, ts, tg, False)["cost"]) < 1e-12))

    # heuristics by hand
    checks.append(("octile((0,0),(3,1)) = 4 + (sqrt 2 - 2) * 1 = 2 + sqrt 2", abs(L.octile((0, 0), (3, 1)) - (2 + s2)) < 1e-12))
    checks.append(("Euclidean (0,0)-(3,1) = sqrt 10 = 3.162; Manhattan 4 exceeds the true 8-connected cost 3.414",
                   abs(L.euclidean((0, 0), (3, 1)) - math.sqrt(10)) < 1e-12 and round(L.euclidean((0, 0), (3, 1)), 3) == 3.162
                   and L.manhattan((0, 0), (3, 1)) > L.octile((0, 0), (3, 1)) and round(L.octile((0, 0), (3, 1)), 3) == 3.414))
    checks.append(("Manhattan((0,0),(3,1)) = 4", L.manhattan((0, 0), (3, 1)) == 4))

    # admissibility, numerically, on 25 random grids
    ok4 = ok8 = True
    for seed in range(25):
        b = L.random_grid(20, 14, 0.2, seed)
        goal_ = (19, 13)
        for diag, h in ((False, L.manhattan), (True, L.octile)):
            true = L.cost_map(b, goal_, diag)
            for r in range(14):
                for c in range(20):
                    if np.isfinite(true[r, c]) and h((c, r), goal_) > true[r, c] + 1e-9:
                        if diag:
                            ok8 = False
                        else:
                            ok4 = False
    checks.append(("Manhattan never overestimates on 4-connected grids (25 grids)", ok4))
    checks.append(("octile never overestimates on 8-connected grids (25 grids)", ok8))
    checks.append(("Manhattan DOES overestimate on an 8-connected grid: (0,0)->(1,1) is 2 but the true cost is sqrt 2",
                   L.manhattan((0, 0), (1, 1)) > L.cost_map(np.zeros((2, 2), dtype=bool), (1, 1), True)[0, 0]))

    # A* equals Dijkstra in cost and expands fewer nodes
    same, d_tot, a_tot, n = True, 0, 0, 0
    for seed in range(40):
        b = L.random_grid(30, 20, 0.2, seed)
        rd = L.dijkstra(b, (0, 0), (29, 19), True)
        ra = L.astar(b, (0, 0), (29, 19), True)
        if rd["path"] is None:
            same &= ra["path"] is None
            continue
        n += 1
        same &= abs(rd["cost"] - ra["cost"]) < 1e-9
        d_tot += rd["expanded"]
        a_tot += ra["expanded"]
    checks.append((f"A* and Dijkstra return the same cost on all {n} solvable 20%-density grids", same and n == 35))
    checks.append((f"A* expands fewer nodes in total ({a_tot} versus {d_tot})", a_tot < d_tot and d_tot == 16776 and a_tot == 6339))
    rg = L.random_grid(30, 20, 0.25, 0)
    rd, ra = L.dijkstra(rg, (0, 0), (29, 19), True), L.astar(rg, (0, 0), (29, 19), True)
    checks.append((f"25% grid, seed 0: cost 40.971 for both; expanded 463 versus 148 (got {rd['expanded']}, {ra['expanded']})",
                   abs(rd["cost"] - 40.971) < 5e-4 and abs(ra["cost"] - rd["cost"]) < 1e-9 and rd["expanded"] == 463 and ra["expanded"] == 148))
    ra0 = L.astar(rg, (0, 0), (29, 19), True, h=lambda a, b: 0.0)
    checks.append(("A* with h = 0 is Dijkstra: same expanded count", ra0["expanded"] == rd["expanded"]))
    rw = L.astar(rg, (0, 0), (29, 19), True, weight=3.0)
    checks.append(("an inflated (inadmissible) heuristic expands fewer nodes but may cost more", rw["expanded"] < ra["expanded"] and rw["cost"] >= rd["cost"] - 1e-9))

    # empty-floor facts used in the text
    e = np.zeros((20, 30), dtype=bool)
    de = L.dijkstra(e, (0, 0), (29, 19), True)
    checks.append((f"empty 30 x 20 floor, corner to corner: 19 diagonals + 10 straights = 36.87 (got {de['cost']:.2f})",
                   abs(de["cost"] - (19 * s2 + 10)) < 1e-9 and round(de["cost"], 2) == 36.87))

    # design table: serpentine warehouse 30 x 25
    exp = {1: (464, 285.00), 2: (290, 192.73), 3: (232, 161.97), 4: (174, 131.21), 5: (116, 100.46)}
    ok = True
    for a_w, (cells, cost) in exp.items():
        b, s, g, n_cells = L.serpentine(30, 25, a_w)
        r = L.dijkstra(b, s, g, True)
        ok &= n_cells == cells and abs(r["cost"] - cost) < 6e-3 and abs(L.astar(b, s, g, True)["cost"] - r["cost"]) < 1e-9
    checks.append(("serpentine 30 x 25: shelf cells 464/290/232/174/116 and costs 285.00/192.73/161.97/131.21/100.46 for aisles 1..5", ok))
    feasible = [a_w for a_w, (cells, cost) in exp.items() if cells >= 200 and cost <= 170]
    checks.append(("design answer: aisle 3 is the only width with at least 200 shelf cells and cost at most 170", feasible == [3]))
    b1, s1, g1, _ = L.serpentine(30, 25, 1)
    r1d, r1a = L.dijkstra(b1, s1, g1, True), L.astar(b1, s1, g1, True)
    checks.append(("aisle 1 is a single corridor: Dijkstra and A* both expand 286 nodes", r1d["expanded"] == r1a["expanded"] == 286))

    # density table
    st = {d: L.density_stats(d) for d in (0.0, 0.1, 0.2, 0.3, 0.4)}
    checks.append(("solvable grids out of 40 at densities 0, 0.1, 0.2, 0.3, 0.4: 40, 40, 35, 19, 1",
                   [st[d]["solvable"] for d in sorted(st)] == [40, 40, 35, 19, 1]))
    costs = [round(st[d]["mean_cost"], 2) for d in sorted(st)]
    checks.append((f"mean cost rises with density: 36.87, 37.82, 39.77, 43.76, 48.49 (got {costs})", costs == [36.87, 37.82, 39.77, 43.76, 48.49]))
    checks.append(("Dijkstra's mean expanded nodes: 600 with no obstacles, 188 at density 0.4",
                   round(st[0.0]["mean_dijkstra"]) == 600 and round(st[0.4]["mean_dijkstra"]) == 188))
    checks.append(("A* expands fewer nodes than Dijkstra at every density",
                   all(st[d]["mean_astar"] < st[d]["mean_dijkstra"] for d in st)))

    # edge cases
    sealed = np.zeros((3, 3), dtype=bool)
    sealed[:, 1] = True
    for f in (L.bfs, L.dijkstra, L.astar):
        if f(sealed, (0, 0), (2, 2), True)["path"] is not None:
            checks.append(("a sealed wall gives no path", False))
            break
    else:
        checks.append(("a sealed wall gives no path (path None, cost inf) in all three methods", True))
    one = L.astar(empty, (1, 1), (1, 1), True)
    checks.append(("start equals goal: cost 0, one expanded node", one["cost"] == 0.0 and one["expanded"] == 1))
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
