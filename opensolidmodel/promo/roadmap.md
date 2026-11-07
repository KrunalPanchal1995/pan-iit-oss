# Roadmap: the path to the opensolidmodel Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Arcs and circles in the sketch

**You will learn:** How a round corner or a hole is stored as a centre and a radius, and how a tangent or a concentric statement becomes an equation.

**You will build:** Add a circle (centre point and radius) and the statements 'radius is r', 'point on circle' and 'line tangent to circle' to the solver of Session 3.

**Checkpoint (not met by the shipped code):** A line from a point outside a circle, tangent to it, has the length sqrt(d^2 - r^2), and the solver finds it from a rough guess.

**Difficulty:** intermediate

## Session 5: A feature tree with extrude, cut and revolve

**You will learn:** How a part is a list of features applied in order, and why changing an early feature rebuilds all the later ones.

**You will build:** Extend the rebuild of Session 1 to a list of extrude, cut and revolve features, each with parameters, and recompute the volume after every change.

**Checkpoint (not met by the shipped code):** Revolving a 20 x 40 mm rectangle that touches the axis gives the volume of a cylinder, and cutting a hole through a block removes pi r^2 times the thickness.

**Difficulty:** intermediate

## Session 6: Volume, centre of mass and inertia of a solid

**You will learn:** Why the centre of mass of an extruded part is the centroid of its section, and how mass moves the balance point when a hole is cut.

**You will build:** Add the centre of mass and the moment of inertia about an axis for extruded and revolved parts.

**Checkpoint (not met by the shipped code):** A solid cylinder has I = m r^2 / 2 about its axis, and a plate with a hole has its centre of mass shifted away from the hole.

**Difficulty:** advanced

## Session 7: Fillets and chamfers on the outline

**You will learn:** Why sharp inside corners concentrate stress and how a fillet replaces a corner by an arc that touches both edges.

**You will build:** A function that replaces a convex corner of a polygon by a tangent arc and returns the new area and second moment of area.

**Checkpoint (not met by the shipped code):** A fillet of radius r on a 90 degree corner removes r^2 (1 - pi / 4) of area, and a radius of 0 gives back the original outline.

**Difficulty:** intermediate

## Session 8: Assemblies and mates

**You will learn:** How two parts are placed relative to each other by statements such as 'this face touches that face' and 'these two holes are aligned'.

**You will build:** Give every part a position and an angle and solve the mates with the same Newton method as the sketch.

**Checkpoint (not met by the shipped code):** A bolt hole in a bracket and a hole in a plate end up with the same centre after the solve, and over-constraining the assembly is reported as in Session 3.

**Difficulty:** advanced
