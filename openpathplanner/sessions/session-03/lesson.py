"""Session 3 (Level 3): continuous space, RRT, RRT*, and a comparison with grid A*.

Run:  python start.py 3
"""
# %% [markdown]
# # Session 3: planning without a grid
# **A. Real-world problem.** A robot arm or a drone does not live on a grid. Its map is
# continuous, with round and rectangular obstacles, and a grid either loses detail (coarse) or
# is slow (fine). *Sampling-based* planners such as RRT (rapidly-exploring random tree) throw
# random points at the map and grow a tree of collision-free moves. Today you build RRT,
# smooth its path, improve it with RRT*, and measure all of it against a case with an exact
# answer.
#
# **Plan.** (1) collision tests for a segment against circles and rectangles, (2) RRT,
# (3) shortcut smoothing, (4) RRT*, (5) validation against the exact shortest path around a
# wall, (6) comparison with grid A*, failure cases, and the mini-project.

# %%
import heapq
import math
import pathlib
import time

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
EPS = 1e-9
SIZE = 10.0                                  # every map is the square 0..10 by 0..10 (metres)


# %% [markdown]
# ## Step 1: maps and collision checks
# An obstacle is `("circle", cx, cy, r)` or `("rect", x0, y0, x1, y1)`. A segment is in
# collision if it enters the INSIDE of an obstacle; touching an edge or a corner is allowed
# (the shortest path around a wall must touch its corners).
#
# * Segment and circle: find the point of the segment closest to the centre; collision if it is
#   closer than r.
# * Segment and rectangle (Liang-Barsky): clip the segment to the rectangle's four sides. If a
#   piece is left, its midpoint tells whether it runs through the inside or only along an edge.

# %%
def seg_circle_hit(p, q, circle):
    _, cx, cy, r = circle
    dx, dy = q[0] - p[0], q[1] - p[1]
    length2 = dx * dx + dy * dy
    t = 0.0 if length2 < EPS else max(0.0, min(1.0, ((cx - p[0]) * dx + (cy - p[1]) * dy) / length2))
    nx, ny = p[0] + t * dx, p[1] + t * dy
    return math.hypot(nx - cx, ny - cy) < r - EPS


def seg_rect_hit(p, q, rect):
    _, x0, y0, x1, y1 = rect
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pk) < EPS:
            if qk < 0:
                return False                 # parallel to this side and outside it
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    if t0 > t1:
        return False
    tm = 0.5 * (t0 + t1)
    mx, my = p[0] + tm * dx, p[1] + tm * dy
    return x0 + EPS < mx < x1 - EPS and y0 + EPS < my < y1 - EPS


def point_free(p, obstacles):
    for o in obstacles:
        if o[0] == "circle":
            if math.hypot(p[0] - o[1], p[1] - o[2]) < o[3] - EPS:
                return False
        elif o[1] + EPS < p[0] < o[3] - EPS and o[2] + EPS < p[1] < o[4] - EPS:
            return False
    return 0.0 <= p[0] <= SIZE and 0.0 <= p[1] <= SIZE


def segment_free(p, q, obstacles):
    for o in obstacles:
        if (seg_circle_hit(p, q, o) if o[0] == "circle" else seg_rect_hit(p, q, o)):
            return False
    return True


def path_length(path):
    return float(sum(math.dist(a, b) for a, b in zip(path, path[1:])))


def path_is_free(path, obstacles, per_segment=50):
    """Sample many points along every segment and check each lies outside all obstacles."""
    for a, b in zip(path, path[1:]):
        for t in np.linspace(0.0, 1.0, per_segment):
            if not point_free((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), obstacles):
                return False
    return True


# %% [markdown]
# ## The maps
# * `WALL`: one thin wall (x from 4.8 to 5.2, from below the map up to y = 6). Start (1, 1), goal (9, 1). The exact
#   shortest path is a polyline through the wall's top corners (we compute it below).
# * `CLUTTER`: three circles and two rectangles between (1, 1) and (9, 9).
# * `narrow_map(gap)`: a wall with a gap of width `gap` in the middle, the failure case.

# %%
WALL = {"obstacles": [("rect", 4.8, -1.0, 5.2, 6.0)], "start": (1.0, 1.0), "goal": (9.0, 1.0)}
CLUTTER = {"obstacles": [("circle", 3.0, 7.0, 1.3), ("circle", 7.0, 3.0, 1.3), ("circle", 5.0, 5.0, 1.0),
                         ("rect", 1.5, 3.5, 4.0, 4.5), ("rect", 6.0, 5.5, 8.5, 6.5)],
           "start": (1.0, 1.0), "goal": (9.0, 9.0)}


def narrow_map(gap):
    lo, hi = 5.0 - gap / 2, 5.0 + gap / 2
    return {"obstacles": [("rect", 4.8, -1.0, 5.2, lo), ("rect", 4.8, hi, 5.2, SIZE + 1.0)],
            "start": (1.0, 5.0), "goal": (9.0, 5.0)}


# %% [markdown]
# ## Step 2: RRT
# Repeat: pick a random point (5% of the time the goal itself, "goal bias"); find the nearest
# tree node; step from it toward the sample by at most `step`; if that short segment is free,
# add the new node. Stop when the goal can be reached from the new node in a free segment.
# The random numbers come from a seeded generator, so the same seed gives the same tree.

# %%
def rrt(world, step=0.5, max_iter=3000, seed=0, goal_bias=0.05):
    rng = np.random.default_rng(seed)
    obs, start, goal = world["obstacles"], world["start"], world["goal"]
    nodes = [start]
    parent = [-1]
    arr = np.zeros((max_iter + 2, 2))        # the same points as `nodes`, kept as an array for fast nearest search
    arr[0] = start
    for it in range(1, max_iter + 1):
        sample = goal if rng.random() < goal_bias else (rng.uniform(0, SIZE), rng.uniform(0, SIZE))
        m = len(nodes)
        i = int(np.argmin((arr[:m, 0] - sample[0]) ** 2 + (arr[:m, 1] - sample[1]) ** 2))
        d = math.dist(nodes[i], sample)
        if d < EPS:
            continue
        s = min(step, d)
        new = (nodes[i][0] + s * (sample[0] - nodes[i][0]) / d, nodes[i][1] + s * (sample[1] - nodes[i][1]) / d)
        if not segment_free(nodes[i], new, obs):
            continue
        arr[len(nodes)] = new
        nodes.append(new)
        parent.append(i)
        if math.dist(new, goal) <= step and segment_free(new, goal, obs):
            nodes.append(goal)
            parent.append(len(nodes) - 2)
            return {"nodes": nodes, "parent": parent, "path": _trace(nodes, parent, len(nodes) - 1), "iterations": it, "found": True}
    return {"nodes": nodes, "parent": parent, "path": None, "iterations": max_iter, "found": False}


def _trace(nodes, parent, k):
    path = []
    while k != -1:
        path.append(nodes[k])
        k = parent[k]
    return path[::-1]


# %% [markdown]
# ## Step 3: smoothing by shortcutting
# An RRT path wiggles. Repeatedly pick two points on the path; if the straight segment between
# them is free, cut out everything in between. The path can only get shorter.

# %%
def shortcut(path, obstacles, seed=0, tries=300):
    rng = np.random.default_rng(seed)
    path = list(path)
    for _ in range(tries):
        if len(path) < 3:
            break
        i, j = sorted(rng.choice(len(path), size=2, replace=False))
        if j - i >= 2 and segment_free(path[i], path[j], obstacles):
            path = path[:i + 1] + path[j:]
    return path


# %% [markdown]
# ## Step 4: RRT* (stretch)
# RRT* adds two ideas. (1) When a new node is added, choose as its parent the nearby node
# that gives the lowest cost-from-start (not just the nearest). (2) Rewire: if the new node
# gives a nearby node a cheaper route, make the new node its parent. Keep sampling after the
# goal is first reached: the best path keeps improving toward the optimum.

# %%
def rrt_star(world, step=0.5, iterations=2000, seed=0, radius=1.5, goal_bias=0.05, every=100):
    rng = np.random.default_rng(seed)
    obs, start, goal = world["obstacles"], world["start"], world["goal"]
    pts = np.zeros((iterations + 1, 2))
    pts[0] = start
    parent = [-1]
    cost = [0.0]
    kids = {0: []}
    n = 1
    trace = []

    def best_goal_link():
        best, who = math.inf, -1
        near = np.where(np.hypot(pts[:n, 0] - goal[0], pts[:n, 1] - goal[1]) <= radius)[0]
        for k in near:
            c = cost[k] + math.dist(pts[k], goal)
            if c < best and segment_free(tuple(pts[k]), goal, obs):
                best, who = c, int(k)
        return best, who

    def push_cost(k, delta):
        stack = [k]
        while stack:
            u = stack.pop()
            cost[u] += delta
            stack.extend(kids[u])

    for it in range(1, iterations + 1):
        sample = goal if rng.random() < goal_bias else (rng.uniform(0, SIZE), rng.uniform(0, SIZE))
        d2 = (pts[:n, 0] - sample[0]) ** 2 + (pts[:n, 1] - sample[1]) ** 2
        i = int(np.argmin(d2))
        d = math.sqrt(d2[i])
        if d > EPS:
            s = min(step, d)
            new = (pts[i][0] + s * (sample[0] - pts[i][0]) / d, pts[i][1] + s * (sample[1] - pts[i][1]) / d)
            if segment_free(tuple(pts[i]), new, obs):
                dn = np.hypot(pts[:n, 0] - new[0], pts[:n, 1] - new[1])
                near = [int(k) for k in np.where(dn <= radius)[0]]
                best_k, best_c = i, cost[i] + float(dn[i])
                for k in near:
                    c = cost[k] + float(dn[k])
                    if c < best_c and segment_free(tuple(pts[k]), new, obs):
                        best_k, best_c = k, c
                pts[n] = new
                parent.append(best_k)
                cost.append(best_c)
                kids[n] = []
                kids[best_k].append(n)
                for k in near:                       # rewire the neighbours through the new node
                    c = best_c + float(dn[k])
                    if k != best_k and c < cost[k] - EPS and segment_free(new, tuple(pts[k]), obs):
                        kids[parent[k]].remove(k)
                        push_cost(k, c - cost[k])
                        parent[k] = n
                        kids[n].append(k)
                n += 1
        if it % every == 0:
            trace.append((it, best_goal_link()[0]))
    best, who = best_goal_link()
    path = None
    if who >= 0:
        path = _trace([tuple(p) for p in pts[:n]], parent, who) + [goal]
    return {"path": path, "best": best, "trace": trace, "nodes": n, "pts": pts[:n].copy(), "parent": list(parent)}


# %% [markdown]
# ## Step 5: validation with an exact answer
# Around a single wall the shortest path is a polyline through the wall's corners. We compute it
# in two independent ways: directly for the wall, and with a *visibility graph* (connect the
# start, the goal and every obstacle corner that can see each other, then run Dijkstra).

# %%
def wall_corner_path(world):
    """Exact shortest path over the top of the single rectangular wall in `world`."""
    (_, x0, _, x1, top) = world["obstacles"][0]
    return [world["start"], (x0, top), (x1, top), world["goal"]]


def visibility_graph_path(world):
    corners = [(o[1], o[2]) for o in world["obstacles"] if o[0] == "rect"]
    corners += [(o[3], o[2]) for o in world["obstacles"] if o[0] == "rect"]
    corners += [(o[1], o[4]) for o in world["obstacles"] if o[0] == "rect"]
    corners += [(o[3], o[4]) for o in world["obstacles"] if o[0] == "rect"]
    corners = [c for c in corners if 0.0 <= c[0] <= SIZE and 0.0 <= c[1] <= SIZE]   # corners outside the map are not reachable
    nodes = [world["start"], world["goal"]] + corners
    obs = world["obstacles"]
    dist = {0: 0.0}
    prev = {}
    heap = [(0.0, 0)]
    while heap:
        c, u = heapq.heappop(heap)
        if c > dist.get(u, math.inf):
            continue
        if u == 1:
            break
        for v in range(len(nodes)):
            if v != u and segment_free(nodes[u], nodes[v], obs):
                nc = c + math.dist(nodes[u], nodes[v])
                if nc < dist.get(v, math.inf) - 1e-12:
                    dist[v] = nc
                    prev[v] = u
                    heapq.heappush(heap, (nc, v))
    path, k = [], 1
    while k != 0:
        path.append(nodes[k])
        k = prev[k]
    return [nodes[0]] + path[::-1]


# %% [markdown]
# ## Step 6: grid A* on the same map, for comparison
# We lay a grid of cells of side `res` over the map (a cell is blocked if its centre is inside
# an obstacle), then run 8-connected A* with the octile heuristic as in Session 2.

# %%
def rasterize(obstacles, res=0.1):
    n = int(round(SIZE / res))
    blocked = np.zeros((n, n), dtype=bool)
    for r in range(n):
        for c in range(n):
            blocked[r, c] = not point_free(((c + 0.5) * res, (r + 0.5) * res), obstacles)
    return blocked


def astar_cells(blocked, s, g, weight=1.0):
    """8-connected A* between cells s and g (column, row). Cost is in cell widths."""
    n_r, n_c = blocked.shape
    sq2 = math.sqrt(2.0)

    def h(a):
        dx, dy = abs(a[0] - g[0]), abs(a[1] - g[1])
        return weight * ((dx + dy) + (sq2 - 2.0) * min(dx, dy))

    best = {s: 0.0}
    parent = {s: None}
    heap = [(h(s), 0.0, s)]
    done = set()
    while heap:
        _, c, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        if u == g:
            cells = []
            while u is not None:
                cells.append(u)
                u = parent[u]
            return {"cells": cells[::-1], "cost": c, "expanded": len(done)}
        x, y = u
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            vx, vy = x + dx, y + dy
            if 0 <= vx < n_c and 0 <= vy < n_r and not blocked[vy, vx]:
                if dx and dy and (blocked[y, vx] or blocked[vy, x]):
                    continue
                nc = c + (sq2 if dx and dy else 1.0)
                if nc < best.get((vx, vy), math.inf):
                    best[(vx, vy)] = nc
                    parent[(vx, vy)] = u
                    heapq.heappush(heap, (nc + h((vx, vy)), nc, (vx, vy)))
    return {"cells": None, "cost": math.inf, "expanded": len(done)}


def grid_astar(blocked, start, goal, res=0.1, weight=1.0):
    """A* on the rasterized map; returns {"path": cell-centre points, "cost": length (m), "expanded": n}."""
    r = astar_cells(blocked, (int(start[0] / res), int(start[1] / res)), (int(goal[0] / res), int(goal[1] / res)), weight)
    path = None if r["cells"] is None else [((a + 0.5) * res, (b + 0.5) * res) for a, b in r["cells"]]
    return {"path": path, "cost": r["cost"] * res, "expanded": r["expanded"]}


# %% [markdown]
# ## Step 7: success rate, step size, and the mini-project warehouse
# `success_rate` runs RRT with many seeds. The mini-project uses a grid warehouse: shelf blocks,
# a dock and four pick points; the robot visits them in the given order and returns to the dock.

# %%
def success_rate(world, step=0.5, max_iter=1000, seeds=100):
    return sum(rrt(world, step, max_iter, seed=s)["found"] for s in range(seeds)) / seeds


def step_study(world, step, seeds=20, max_iter=3000):
    """RRT with a given step size over many seeds: success rate, mean iterations used, mean raw path length."""
    runs = [rrt(world, step, max_iter, seed=s) for s in range(seeds)]
    ok = [r for r in runs if r["found"]]
    return {"success": len(ok) / seeds, "mean_iterations": float(np.mean([r["iterations"] for r in ok])),
            "mean_length": float(np.mean([path_length(r["path"]) for r in ok]))}


def warehouse_grid():
    """36 x 18 cells. Three rows of three shelf blocks (8 x 2 cells each), True = shelf."""
    blocked = np.zeros((18, 36), dtype=bool)
    for y in (3, 7, 11):
        for x in (3, 13, 23):
            blocked[y:y + 2, x:x + 8] = True
    return blocked


DOCK = (1, 16)
PICKS = [(6, 5), (21, 9), (31, 5), (12, 13)]


def pick_route(blocked, stops):
    """Total length and total expanded nodes for visiting `stops` in order with A* between each pair."""
    total, expanded = 0.0, 0
    for a, b in zip(stops, stops[1:]):
        r = astar_cells(blocked, a, b)
        total += r["cost"]
        expanded += r["expanded"]
    return total, expanded


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle

    OUT.mkdir(exist_ok=True)

    def draw_world(ax, world):
        for o in world["obstacles"]:
            if o[0] == "circle":
                ax.add_patch(Circle((o[1], o[2]), o[3], color="0.35"))
            else:
                ax.add_patch(Rectangle((o[1], o[2]), o[3] - o[1], o[4] - o[2], color="0.35"))
        ax.plot(*world["start"], "gs", ms=9)
        ax.plot(*world["goal"], "r*", ms=13)
        ax.set_xlim(0, SIZE); ax.set_ylim(0, SIZE); ax.set_aspect("equal")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")

    # validation on the wall
    exact = wall_corner_path(WALL)
    vg = visibility_graph_path(WALL)
    print(f"exact wall path length {path_length(exact):.4f}; visibility graph {path_length(vg):.4f}")

    # figure 1: RRT tree, raw and smoothed path on the clutter map
    res = rrt(CLUTTER, seed=1)
    sm = shortcut(res["path"], CLUTTER["obstacles"], seed=1)
    fig, ax = plt.subplots(figsize=(6, 6))
    draw_world(ax, CLUTTER)
    for k in range(1, len(res["nodes"])):
        a, b = res["nodes"][res["parent"][k]], res["nodes"][k]
        ax.plot([a[0], b[0]], [a[1], b[1]], "-", color="tab:blue", lw=0.5, alpha=0.6)
    p = np.array(res["path"]); q = np.array(sm)
    ax.plot(p[:, 0], p[:, 1], "-", color="tab:orange", lw=2, label=f"RRT path {path_length(res['path']):.2f} m")
    ax.plot(q[:, 0], q[:, 1], "-", color="tab:green", lw=2.5, label=f"smoothed {path_length(sm):.2f} m")
    ax.set_title(f"RRT tree ({len(res['nodes'])} nodes, {res['iterations']} iterations)")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(OUT / "rrt_tree.png", dpi=120)
    print(f"clutter RRT seed 1: {res['iterations']} iterations, raw {path_length(res['path']):.3f}, smoothed {path_length(sm):.3f}")

    # figure 2: RRT* cost versus iterations on the wall, against the exact length
    star = rrt_star(WALL, iterations=3000, seed=2)
    its = [t[0] for t in star["trace"]]; costs = [t[1] for t in star["trace"]]
    fig2, ax2 = plt.subplots(figsize=(6.5, 4))
    ax2.plot(its, costs, "o-", ms=3, label="RRT* best path")
    ax2.axhline(path_length(exact), color="red", ls="--", label=f"exact optimum {path_length(exact):.3f} m")
    ax2.set_ylim(path_length(exact) - 0.5, min(max(c for c in costs if math.isfinite(c)) + 0.5, 20))
    ax2.set_xlabel("iterations"); ax2.set_ylabel("best path length (m)")
    ax2.set_title("RRT* improves toward the optimum")
    ax2.grid(alpha=0.3); ax2.legend(fontsize=8)
    fig2.tight_layout(); fig2.savefig(OUT / "rrt_star_cost.png", dpi=120)
    print("RRT* trace (iteration, best):", [(i, round(c, 3)) for i, c in star["trace"] if i % 500 == 0])

    # figure 3: three planners on the clutter map
    blocked = rasterize(CLUTTER["obstacles"])
    t0 = time.perf_counter(); ga = grid_astar(blocked, CLUTTER["start"], CLUTTER["goal"]); t_a = time.perf_counter() - t0
    t0 = time.perf_counter(); r1 = rrt(CLUTTER, seed=1); t_r = time.perf_counter() - t0
    t0 = time.perf_counter(); rs = rrt_star(CLUTTER, iterations=2000, seed=1); t_s = time.perf_counter() - t0
    print(f"grid A*  length {ga['cost']:.3f}  expanded {ga['expanded']}  time {t_a:.2f} s")
    print(f"RRT      length {path_length(r1['path']):.3f}  iterations {r1['iterations']}  time {t_r:.2f} s")
    print(f"RRT*     length {path_length(rs['path']):.3f}  nodes {rs['nodes']}  time {t_s:.2f} s")
    fig3, axs = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax_, (name, path_) in zip(axs, [("grid A*", ga["path"]), ("RRT (smoothed)", sm), ("RRT* 2000 it.", rs["path"])]):
        draw_world(ax_, CLUTTER)
        pp = np.array(path_)
        ax_.plot(pp[:, 0], pp[:, 1], "-", color="tab:blue", lw=2)
        ax_.set_title(f"{name}: {path_length(path_):.2f} m", fontsize=10)
    fig3.tight_layout(); fig3.savefig(OUT / "planner_compare.png", dpi=110)

    # failure case
    for gap in (0.05, 0.1, 0.3, 1.0, 3.0):
        print(f"gap {gap}: success rate {success_rate(narrow_map(gap), 0.5, 1000, 100):.2f}")

    for st_ in (0.25, 0.5, 1.0, 2.0):
        r_ = step_study(CLUTTER, st_)
        print(f"step {st_}: success {r_['success']:.2f}, mean iterations {r_['mean_iterations']:.0f}, mean raw length {r_['mean_length']:.2f}")
    gw = grid_astar(blocked, CLUTTER["start"], CLUTTER["goal"], weight=3.0)
    print(f"weighted A* (3 x octile): length {gw['cost']:.3f}, expanded {gw['expanded']}")
    gwall = grid_astar(rasterize(WALL["obstacles"]), WALL["start"], WALL["goal"])
    print(f"wall: grid A* {gwall['cost']:.3f} vs exact {path_length(exact):.3f}")

    # mini-project preview
    wh = warehouse_grid()
    total, exp_ = pick_route(wh, [DOCK] + PICKS + [DOCK])
    print(f"warehouse pick route: length {total:.2f} cells, expanded {exp_}")

# %% [markdown]
# ## Where this stops
# Neither planner is both optimal and cheap: A* is optimal only on the grid you gave it, RRT is
# fast and free of the grid but only probabilistically complete and not optimal, RRT* is
# asymptotically optimal but slower. Real robots also need smooth, drivable paths (Target and roadmap).
