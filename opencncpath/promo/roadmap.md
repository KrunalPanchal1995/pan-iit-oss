# Roadmap: the path to the opencncpath Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 6: Rest machining of the corners

**You will learn:** A second, smaller cutter removes what the first one could not reach.

**You will build:** A second pass with a 2 mm cutter that follows the corner leftover left by the 6 mm cutter.

**Checkpoint (not met by the shipped code):** The corner leftover of the 40 x 30 mm pocket drops from 7.73 mm^2 to at most 0.86 mm^2 (the leftover of a 2 mm cutter) in the height-map.

**Difficulty:** advanced

## Session 7: 3D ball-end finishing

**You will learn:** Scallop height on a curved surface and constant-ridge stepover.

**You will build:** Parallel finishing passes over a hemisphere of radius 15 mm with a ball cutter of radius 3 mm, simulated on a 3D height-map.

**Checkpoint (not met by the shipped code):** The maximum measured ridge on the hemisphere is at most 0.05 mm (the shipped code only finishes a flat floor).

**Difficulty:** advanced

## Session 8: Post-processor dialects

**You will learn:** Why the same toolpath is written differently for different controllers, and how to test a post-processor.

**You will build:** A writer that outputs arcs with I, J and with the R word, and a parser that reads both.

**Checkpoint (not met by the shipped code):** A quarter-circle arc of radius 10 mm written both ways parses to the same length, 15.708 mm, within 1e-6 mm.

**Difficulty:** advanced

## The final step

Combine the milestones: a planner that takes a polygon with bosses, produces continuous contour-parallel rings, finishes the corners with a smaller cutter, writes G-code in two dialects and checks its own removed volume. If your result looks like the Target animation, open a pull request and tell us how you did it. Remember that the output is for study: real machining needs trained operators, machine-specific post-processing and safety checks.
