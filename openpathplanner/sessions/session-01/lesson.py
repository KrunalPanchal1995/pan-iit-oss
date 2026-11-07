"""Session 1 (Level 1): a warehouse robot must get around the walls.

Run:  python start.py 1
"""
# %% [markdown]
# # Session 1: the shortest path is not the straight line
# **A. Real-world problem.** A robot in a warehouse must reach a shelf. The straight line from
# the robot to the shelf runs through a wall, so the robot must walk around it. How long is the
# real route, and how do we find it with a program?
#
# **Plan.** (1) draw the warehouse as a grid, (2) count the steps of the best route with
# breadth-first search, (3) compare with the straight-line distance, (4) see how the position
# of the door in the wall changes the route.

# %%
import pathlib
from collections import deque

import numpy as np

OUT = (pathlib.Path(__file__).resolve().parent if "__file__" in globals() else pathlib.Path(".")) / "out"

COLS, ROWS = 12, 8          # the floor is 12 cells wide and 8 cells tall
WALL_COL = 6                # a wall runs down column 6 with one door in it
START = (1, 1)              # (column, row) of the robot
SHELF_COL = 10              # the shelf is in column 10


# %% [markdown]
# ## Step 1: the floor as a grid
# Each cell is free (False) or blocked (True). The robot moves one cell at a time: up, down,
# left or right (4 moves). Every move costs 1 step.

# %%
def make_floor(door_row):
    """Boolean grid indexed [row][col]; True means blocked. The wall has one door."""
    blocked = np.zeros((ROWS, COLS), dtype=bool)
    blocked[:, WALL_COL] = True
    blocked[door_row, WALL_COL] = False
    return blocked


# %% [markdown]
# ## Step 2: breadth-first search (BFS)
# BFS explores the floor in rings: first every cell 1 step away, then every cell 2 steps away,
# and so on. The first time it reaches the shelf, that is the fewest possible steps.

# %%
def bfs_steps(blocked, start, goal):
    """Fewest 4-moves from start to goal, or None if the goal cannot be reached."""
    rows, cols = blocked.shape
    dist = {start: 0}
    queue = deque([start])
    while queue:
        c, r = queue.popleft()
        if (c, r) == goal:
            return dist[goal]
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if 0 <= n[0] < cols and 0 <= n[1] < rows and not blocked[n[1], n[0]] and n not in dist:
                dist[n] = dist[(c, r)] + 1
                queue.append(n)
    return None


def bfs_path(blocked, start, goal):
    """The cells of one shortest route (list of (col, row)), or None."""
    rows, cols = blocked.shape
    parent = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            return path[::-1]
        c, r = cell
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if 0 <= n[0] < cols and 0 <= n[1] < rows and not blocked[n[1], n[0]] and n not in parent:
                parent[n] = cell
                queue.append(n)
    return None


# %% [markdown]
# ## Step 3: compare with the straight line
# The straight-line distance ignores walls. The route can never be shorter than it. For
# cells that are `dx` columns and `dy` rows apart, the straight line is sqrt(dx^2 + dy^2) and
# the shortest 4-move route on an empty floor is dx + dy.

# %%
def straight_line(a, b):
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


def route_formula(door_row, shelf_row):
    """Steps with one door: 9 columns across, plus the up/down walk to the door and from it."""
    return (SHELF_COL - START[0]) + abs(START[1] - door_row) + abs(door_row - shelf_row)


# %%
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    OUT.mkdir(exist_ok=True)
    shelf = (SHELF_COL, 2)
    door = 6
    floor = make_floor(door)
    path = bfs_path(floor, START, shelf)
    print(f"door in row {door}: route {len(path) - 1} steps, straight line {straight_line(START, shelf):.2f}")

    fig, ax = plt.subplots(figsize=(6.5, 4.4))
    ax.imshow(floor, cmap="Greys", origin="upper", extent=(-0.5, COLS - 0.5, ROWS - 0.5, -0.5))
    ax.plot([p[0] for p in path], [p[1] for p in path], "o-", color="tab:blue", ms=4, label="shortest route")
    ax.plot([START[0], shelf[0]], [START[1], shelf[1]], "--", color="tab:red", label="straight line (blocked)")
    ax.plot(*START, "gs", ms=10, label="robot")
    ax.plot(*shelf, "r*", ms=14, label="shelf")
    ax.set_xticks(range(COLS))
    ax.set_yticks(range(ROWS))
    ax.set_xlabel("column (cells)")
    ax.set_ylabel("row (cells)")
    ax.set_title(f"Wall with a door in row {door}: {len(path) - 1} steps")
    ax.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "warehouse_route.png", dpi=120)

    doors = list(range(ROWS))
    steps = [bfs_steps(make_floor(d), START, shelf) for d in doors]
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(doors, steps, "o-", label="route length (BFS)")
    ax2.axhline(abs(shelf[0] - START[0]) + abs(shelf[1] - START[1]), color="gray", ls=":", label="empty-floor route")
    ax2.set_xlabel("door row (cells)")
    ax2.set_ylabel("route length (steps)")
    ax2.set_title("The route depends on where the door is")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(OUT / "route_vs_door.png", dpi=120)
    print("steps for door rows 0..7:", steps)

# %% [markdown]
# ## Where this stops
# BFS counts steps and treats every cell the same. Session 2 gives each move a cost, so a
# diagonal move can cost more than a straight one, and adds A*, which searches smarter.
