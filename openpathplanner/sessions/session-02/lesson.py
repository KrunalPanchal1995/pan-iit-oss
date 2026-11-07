"""Session 2 (Level 2): the grid as a graph; BFS, Dijkstra and A*.

Run:  python start.py 2
"""
# %% [markdown]
# # Session 2: BFS, Dijkstra and A* on a grid graph
# **A. Real-world problem.** Real warehouse robots can move diagonally, and a diagonal move is
# longer (sqrt 2 times) than a straight one. Counting steps (Session 1) is no longer enough:
# we need the cheapest route. We also care how much work the search does, because a robot
# that thinks for a long time wastes battery and time.
#
# **Plan.** (1) turn the grid into a graph with edge costs 1 and sqrt 2, (2) write BFS and
# Dijkstra, (3) add A* with an admissible heuristic, (4) check that A* finds the same cost as
# Dijkstra while expanding fewer nodes, (5) study how aisle width and obstacle density change
# the route and the work.

# %%
import heapq
import math
import pathlib
from collections import deque

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"
SQRT2 = math.sqrt(2.0)


# %% [markdown]
# ## Step 1: the grid is a graph
# A *node* is a free cell (column, row). An *edge* joins two neighbouring free cells and has a
# cost. With 4-connection the neighbours are up, down, left, right (cost 1). With 8-connection
# the four diagonal neighbours are added (cost sqrt 2 = 1.414...). A diagonal move is not
# allowed to cut a corner: both cells beside it must be free.

# %%
def neighbors(blocked, node, diag=False):
    """List of (neighbour, edge cost) for a node (col, row). blocked[row, col] is True for walls."""
    rows, cols = blocked.shape
    c, r = node
    out = []
    for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nc, nr = c + dc, r + dr
        if 0 <= nc < cols and 0 <= nr < rows and not blocked[nr, nc]:
            out.append(((nc, nr), 1.0))
    if diag:
        for dc, dr in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nc, nr = c + dc, r + dr
            if (0 <= nc < cols and 0 <= nr < rows and not blocked[nr, nc]
                    and not blocked[r, nc] and not blocked[nr, c]):
                out.append(((nc, nr), SQRT2))
    return out


def from_text(lines):
    """Build (blocked, start, goal) from text rows: '#' wall, 'S' start, 'G' goal, '.' free."""
    rows = len(lines)
    cols = len(lines[0])
    blocked = np.zeros((rows, cols), dtype=bool)
    start = goal = None
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == "#":
                blocked[r, c] = True
            elif ch == "S":
                start = (c, r)
            elif ch == "G":
                goal = (c, r)
    return blocked, start, goal


def path_cost(path):
    """Total cost of a path of neighbouring nodes: 1 per straight move, sqrt 2 per diagonal."""
    return sum(1.0 if (a[0] == b[0] or a[1] == b[1]) else SQRT2 for a, b in zip(path, path[1:]))


def _walk_back(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


# %% [markdown]
# ## Step 2: breadth-first search and Dijkstra
# *Expanded nodes* = nodes taken from the waiting list and finished. It is our measure of work.
#
# * **BFS** uses a first-in-first-out queue. It minimises the NUMBER of moves, so it is exactly
#   right when every edge costs 1 (4-connection) but not when diagonals cost sqrt 2.
# * **Dijkstra** keeps a priority queue (Python's `heapq`) ordered by cost-so-far g. It always
#   finishes the cheapest unfinished node, so the first time it finishes the goal the cost is
#   the minimum.

# %%
def bfs(blocked, start, goal, diag=False):
    parent = {start: None}
    queue = deque([start])
    expanded = 0
    while queue:
        node = queue.popleft()
        expanded += 1
        if node == goal:
            path = _walk_back(parent, node)
            return {"path": path, "cost": path_cost(path), "expanded": expanded}
        for n, _ in neighbors(blocked, node, diag):
            if n not in parent:
                parent[n] = node
                queue.append(n)
    return {"path": None, "cost": math.inf, "expanded": expanded}


def dijkstra(blocked, start, goal, diag=False):
    g = {start: 0.0}
    parent = {start: None}
    heap = [(0.0, start)]
    done = set()
    while heap:
        cost, node = heapq.heappop(heap)
        if node in done:
            continue                      # an old, more expensive entry for this node
        done.add(node)
        if node == goal:
            return {"path": _walk_back(parent, node), "cost": cost, "expanded": len(done)}
        for n, w in neighbors(blocked, node, diag):
            new = cost + w
            if new < g.get(n, math.inf):
                g[n] = new
                parent[n] = node
                heapq.heappush(heap, (new, n))
    return {"path": None, "cost": math.inf, "expanded": len(done)}


def cost_map(blocked, source, diag=False):
    """Cheapest cost from `source` to every cell (inf where unreachable): Dijkstra without a goal."""
    dist = np.full(blocked.shape, math.inf)
    dist[source[1], source[0]] = 0.0
    heap = [(0.0, source)]
    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist[node[1], node[0]]:
            continue
        for n, w in neighbors(blocked, node, diag):
            if cost + w < dist[n[1], n[0]]:
                dist[n[1], n[0]] = cost + w
                heapq.heappush(heap, (cost + w, n))
    return dist


# %% [markdown]
# ## Step 3: A* and an admissible heuristic
# A* orders the priority queue by f = g + h, where g is the cost so far and h(n) is a guess of
# the cost still to go. If h NEVER OVERESTIMATES the true remaining cost (h is *admissible*),
# A* still returns the cheapest path. Why: when A* finishes the goal with cost C, every
# unfinished node n on the true best path has f(n) = g(n) + h(n) <= g(n) + (true remaining
# cost) = best cost, so a path cheaper than C would have been finished first.
#
# * 4-connected grid: Manhattan distance dx + dy never overestimates (each move changes dx + dy by 1).
# * 8-connected grid: octile distance (dx + dy) + (sqrt 2 - 2) * min(dx, dy) is the exact cost on an
#   empty floor, so it never overestimates either.
# Using h = 0 turns A* back into Dijkstra.

# %%
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def octile(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dx + dy) + (SQRT2 - 2.0) * min(dx, dy)


def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def astar(blocked, start, goal, diag=False, h=None, weight=1.0):
    """A* search. h(node, goal) is the heuristic (default: octile if diag else Manhattan).
    weight > 1 inflates h; that breaks admissibility and the path may no longer be cheapest."""
    if h is None:
        h = octile if diag else manhattan
    g = {start: 0.0}
    parent = {start: None}
    heap = [(weight * h(start, goal), 0.0, start)]
    done = set()
    while heap:
        _, cost, node = heapq.heappop(heap)
        if node in done:
            continue
        done.add(node)
        if node == goal:
            return {"path": _walk_back(parent, node), "cost": cost, "expanded": len(done)}
        for n, w in neighbors(blocked, node, diag):
            new = cost + w
            if new < g.get(n, math.inf):
                g[n] = new
                parent[n] = node
                heapq.heappush(heap, (new + weight * h(n, goal), new, n))
    return {"path": None, "cost": math.inf, "expanded": len(done)}


# %% [markdown]
# ## Step 4: warehouses to test on
# * `random_grid`: obstacles with a given density, seeded so results repeat.
# * `serpentine`: long shelf rows with an opening at alternating ends, so the robot must
#   snake through the aisles. `aisle` is the aisle width in cells; shelves are 2 cells deep.

# %%
# A small grid where BFS (fewest moves) is NOT the cheapest route when diagonals cost sqrt 2.
BFS_TRAP = ["S....#",
            "...#.G",
            "......",
            "#...#."]

# A 5 x 3 grid you can solve by hand (see the checkpoint): a wall in column 2 with its gap in row 2.
HAND_GRID = ["S.#..",
             "..#.G",
             "....."]


def random_grid(width, height, density, seed):
    """Random obstacles; the corners (0, 0) and (width-1, height-1) are kept free."""
    rng = np.random.default_rng(seed)
    blocked = rng.random((height, width)) < density
    blocked[0, 0] = False
    blocked[height - 1, width - 1] = False
    return blocked


def serpentine(width, height, aisle):
    """Shelf rows (2 cells deep) separated by aisles of `aisle` cells. Returns (blocked, start, goal, shelf_cells)."""
    blocked = np.zeros((height, width), dtype=bool)
    y, k = aisle, 0
    while y + 2 + aisle <= height:
        blocked[y:y + 2, :] = True
        if k % 2 == 0:
            blocked[y:y + 2, width - 1] = False      # opening at the right end
        else:
            blocked[y:y + 2, 0] = False              # opening at the left end
        y += 2 + aisle
        k += 1
    goal_col = width - 1 if k % 2 == 0 else 0
    return blocked, (0, 0), (goal_col, height - 1), int(blocked.sum())


def density_stats(density, n_seeds=40, width=30, height=20):
    """Average over seeded random grids (8-connected, corner to corner), solvable grids only."""
    costs, dij, ast = [], [], []
    for seed in range(n_seeds):
        b = random_grid(width, height, density, seed)
        rd = dijkstra(b, (0, 0), (width - 1, height - 1), True)
        if rd["path"] is None:
            continue
        costs.append(rd["cost"])
        dij.append(rd["expanded"])
        ast.append(astar(b, (0, 0), (width - 1, height - 1), True)["expanded"])
    return {"solvable": len(costs), "mean_cost": float(np.mean(costs)),
            "mean_dijkstra": float(np.mean(dij)), "mean_astar": float(np.mean(ast))}


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)

    # figure 1: the four searches on one warehouse
    rng_grid = random_grid(30, 20, 0.25, seed=0)
    start, goal = (0, 0), (29, 19)
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    for ax, (name, fn) in zip(axes, [("Dijkstra", lambda b: dijkstra(b, start, goal, True)),
                                     ("A* (octile)", lambda b: astar(b, start, goal, True)),
                                     ("A* with h = 0", lambda b: astar(b, start, goal, True, h=lambda a, b2: 0.0))]):
        res = fn(rng_grid)
        ax.imshow(rng_grid, cmap="Greys", origin="upper")
        p = np.array(res["path"])
        ax.plot(p[:, 0], p[:, 1], "-", color="tab:blue", lw=2)
        ax.plot(*start, "gs")
        ax.plot(*goal, "r*", ms=11)
        ax.set_title(f"{name}\ncost {res['cost']:.2f}, expanded {res['expanded']}", fontsize=9)
        ax.set_xlabel("column (cells)")
    axes[0].set_ylabel("row (cells)")
    fig.tight_layout()
    fig.savefig(OUT / "search_compare.png", dpi=120)
    d, a = dijkstra(rng_grid, start, goal, True), astar(rng_grid, start, goal, True)
    print(f"random grid 25%: Dijkstra cost {d['cost']:.3f} expanded {d['expanded']}; A* cost {a['cost']:.3f} expanded {a['expanded']}")

    # figure 2: aisle width and obstacle density
    print("serpentine warehouse 30 x 25, 8-connected")
    widths = [1, 2, 3, 4, 5]
    lens, dij_exp, ast_exp, shelves = [], [], [], []
    for a_w in widths:
        b, s, g_, n_shelf = serpentine(30, 25, a_w)
        rd, ra = dijkstra(b, s, g_, True), astar(b, s, g_, True)
        lens.append(rd["cost"]); dij_exp.append(rd["expanded"]); ast_exp.append(ra["expanded"]); shelves.append(n_shelf)
        print(f"  aisle {a_w}: shelf cells {n_shelf:3d}, path cost {rd['cost']:.2f}, Dijkstra expanded {rd['expanded']}, A* expanded {ra['expanded']}")
    densities = [0.0, 0.1, 0.2, 0.3, 0.4]
    mean_cost, mean_dij, mean_ast = [], [], []
    for dens in densities:
        st = density_stats(dens)
        mean_cost.append(st["mean_cost"]); mean_dij.append(st["mean_dijkstra"]); mean_ast.append(st["mean_astar"])
        print(f"  density {dens:.1f}: solvable {st['solvable']:2d}/40, mean cost {st['mean_cost']:.2f}, mean expanded Dijkstra {st['mean_dijkstra']:.0f}, A* {st['mean_astar']:.0f}")
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
    ax1.plot(widths, lens, "o-", label="path cost")
    ax1.set_xlabel("aisle width (cells)")
    ax1.set_ylabel("path cost (cell widths)")
    ax1.set_title("Narrow aisles: more shelves, longer route")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=8)
    ax2.plot(densities, mean_dij, "o-", label="Dijkstra")
    ax2.plot(densities, mean_ast, "s-", label="A* (octile)")
    ax2.set_xlabel("obstacle density (fraction of cells)")
    ax2.set_ylabel("mean nodes expanded")
    ax2.set_title("Work versus obstacle density (30 x 20 grid)")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "aisle_density.png", dpi=120)

# %% [markdown]
# ## Where this stops
# Grid paths have jagged directions and only 8 headings. Session 3 leaves the grid: it plans
# in continuous space with RRT and compares with A*.
