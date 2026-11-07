# Roadmap: the path to the opensculpt Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Marching cubes: a 3D mesh and an STL file

**You will learn:** Extending marching squares to 3D, triangles, and what makes a mesh watertight.

**You will build:** A function that turns the mug field into triangles and writes an STL file.

**Checkpoint (not met by the shipped code):** The mesh area of a unit sphere is within 1 percent of 4 pi and every edge is shared by exactly two triangles (the shipped code only extracts 2D contours).

**Difficulty:** advanced

## Session 5: Repair the field: redistancing

**You will learn:** Why max and min fields are not exact distances and how to fix them (fast sweeping or iteration).

**You will build:** A routine that turns the field of two crossing half-spaces into a true distance field.

**Checkpoint (not met by the shipped code):** At the point (1, 1) beside the corner of the intersection of two half-spaces the repaired value is the true distance sqrt(2) to within 1 percent (the shipped field says 1).

**Difficulty:** advanced

## Session 6: Fewer samples: adaptive octree volume

**You will learn:** Using the distance value to skip big empty or full cells.

**You will build:** A volume estimator that refines only the cells near the surface.

**Checkpoint (not met by the shipped code):** The volume of the mug within 0.5 percent of the reference using fewer than one fifth of the evaluations of a uniform grid (the shipped uniform grid has rms error of about 0.9 percent at N = 128).

**Difficulty:** advanced

## Session 7: Assembly: a lid that fits

**You will learn:** Transforms (translate, rotate) of fields and clearance between parts.

**You will build:** A lid part positioned on the mug with a fixed clearance.

**Checkpoint (not met by the shipped code):** The two parts have no overlap and the smallest gap between them, found from the fields, is between 0.04 and 0.06 cm; the capacity is still 300 mL to 1 percent.

**Difficulty:** intermediate

## Session 8: Sensitivity-driven design

**You will learn:** Using d(volume)/d(thickness) to solve the mass limit without trying every wall.

**You will build:** A Newton iteration on the wall thickness that holds 300 mL.

**Checkpoint (not met by the shipped code):** The wall for a 320 g mug is found within 0.01 cm in at most 5 steps (the shipped code only evaluates the two walls 0.50 and 0.55 cm).

**Difficulty:** intermediate

## The final step

Combine the milestones: a sliders-driven mug with its lid, a mesh you can export and a design loop that meets the 300 mL and mass limits. If your result looks like the Target animation, open a pull request and tell us how you did it.
