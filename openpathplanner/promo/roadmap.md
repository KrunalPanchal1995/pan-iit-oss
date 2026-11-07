# Roadmap: the path to the openpathplanner Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Choose the pick order

**You will learn:** How visiting several shelves is a travelling-salesman problem, and how to search orders.

**You will build:** A planner that reorders the four picks (then ten picks with a heuristic) before running A* between them.

**Checkpoint (not met by the shipped code):** A route of at most 77.31 cells for the four given picks (the shipped given order gives 82.97).

**Difficulty:** intermediate

## Session 5: Keep a safe distance

**You will learn:** Why a real robot needs clearance, and how inflating obstacles by the robot radius handles it.

**You will build:** Inflated obstacles and a path-clearance function, used by both grid A* and RRT*.

**Checkpoint (not met by the shipped code):** A wall-map path whose smallest distance to every obstacle is at least 0.3 m (the shipped exact path touches the corners, clearance 0).

**Difficulty:** intermediate

## Session 6: Find the narrow passage

**You will learn:** Biased sampling (bridge test, Gaussian sampling near obstacles) for narrow gaps.

**You will build:** An RRT variant that samples more near obstacle edges.

**Checkpoint (not met by the shipped code):** A success rate of at least 0.9 over 100 seeds for a 0.05 m gap within 1000 iterations (the shipped RRT reaches 0.12).

**Difficulty:** advanced

## Session 7: Replan when an aisle is blocked

**You will learn:** Incremental search that reuses work after the map changes (D* Lite idea).

**You will build:** A replanner that updates its route when one aisle cell becomes blocked.

**Checkpoint (not met by the shipped code):** After blocking one cell on the route, replanning expands fewer than half the nodes of a fresh A* search (the shipped code searches again from scratch, 100 percent).

**Difficulty:** advanced

## Session 8: Drivable paths for a car-like robot

**You will learn:** Minimum turning radius, curvature, and hybrid A* or Dubins curves.

**You will build:** A planner whose paths have bounded curvature.

**Checkpoint (not met by the shipped code):** A path on the clutter map with maximum curvature at most 1 per metre (the shipped paths have sharp corners).

**Difficulty:** advanced

## The final step

Combine the milestones: a warehouse robot planner that orders its picks, keeps a safe distance, finds narrow passages, replans when an aisle is blocked and drives smooth paths. If your result looks like the Target animation, open a pull request and tell us how you did it.
