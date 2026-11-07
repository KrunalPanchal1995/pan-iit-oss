"""Checkpoint for Session 1. Prints PASS or FAIL."""
import numpy as np


def run_checks(L):
    """L is the lesson module (or notebook namespace). Returns a list of (label, passed)."""
    checks = []
    shelf = (10, 2)
    # worked example: door in row 6
    floor = L.make_floor(6)
    steps = L.bfs_steps(floor, L.START, shelf)
    checks.append((f"worked example: door in row 6 gives a route of 18 steps (got {steps})", steps == 18))
    straight = L.straight_line(L.START, shelf)
    checks.append((f"straight line is sqrt(9^2 + 1^2) = 9.06 (got {straight:.2f})", abs(straight - np.sqrt(82)) < 1e-12 and round(straight, 2) == 9.06))
    path = L.bfs_path(floor, L.START, shelf)
    checks.append(("path has steps + 1 cells and starts and ends correctly", len(path) == steps + 1 and path[0] == L.START and path[-1] == shelf))
    checks.append(("path never enters a blocked cell", all(not floor[r, c] for c, r in path)))
    checks.append(("every move in the path is one cell up, down, left or right",
                   all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:]))))
    checks.append(("the route is longer than the straight line", steps > straight))

    # hand calculation on an empty floor
    empty = np.zeros((8, 12), dtype=bool)
    checks.append(("empty floor: route = dx + dy = 9 + 1 = 10 steps", L.bfs_steps(empty, L.START, shelf) == 10))

    # the closed formula agrees with BFS for every door and shelf row
    ok = all(L.bfs_steps(L.make_floor(d), L.START, (10, s)) == L.route_formula(d, s) for d in range(8) for s in range(8))
    checks.append(("formula 9 + |1 - door| + |door - shelf row| equals BFS for all 64 door/shelf rows", ok))
    steps_all = [L.bfs_steps(L.make_floor(d), L.START, shelf) for d in range(8)]
    checks.append((f"door rows 0..7 give 12, 10, 10, 12, 14, 16, 18, 20 steps (got {steps_all})", steps_all == [12, 10, 10, 12, 14, 16, 18, 20]))
    checks.append(("best doors are rows 1 and 2 with 10 steps, the empty-floor value", min(steps_all) == 10 and steps_all[1] == steps_all[2] == 10))

    both = [sum(L.route_formula(d, row) for row in (2, 6)) for d in range(8)]
    checks.append((f"two shelves in rows 2 and 6: total steps per door row 0..7 are 28, 24, 24, 26, 28, 30, 32, 36 (got {both})", both == [28, 24, 24, 26, 28, 30, 32, 36]))
    checks.append(("door row 4 with the shelf in row 2 gives 14 steps (practice question)", L.bfs_steps(L.make_floor(4), L.START, shelf) == 14))

    # edge cases: start equals goal, unreachable goal
    checks.append(("start equals goal needs 0 steps", L.bfs_steps(empty, L.START, L.START) == 0))
    sealed = L.make_floor(6)
    sealed[:, 6] = True
    checks.append(("a fully sealed wall means no route (None)", L.bfs_steps(sealed, L.START, shelf) is None and L.bfs_path(sealed, L.START, shelf) is None))
    return checks


# --- runner ---
if __name__ == "__main__":
    import importlib.util
    import pathlib
    import sys

    path = pathlib.Path(__file__).resolve().parent / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    ok = True
    for label, passed in run_checks(lesson):
        print(("PASS  " if passed else "FAIL  ") + label)
        ok &= bool(passed)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
