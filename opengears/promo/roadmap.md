# Roadmap: the path to the opengears Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Helical gears and a smoother mesh

**You will learn:** How a helix angle raises the contact ratio and adds axial thrust.

**You will build:** A contact-ratio function for helical gears and a comparison with spur gears.

**Checkpoint (not met by the shipped code):** A contact ratio of at least 2.0 for the 20:40 pair at a moderate helix angle (the shipped spur function gives 1.635).

**Difficulty:** intermediate

## Session 5: Three stages in line

**You will learn:** Searching six gears and three stages without a memory blow-up.

**You will build:** A grouped search for in-line three-stage trains.

**Checkpoint (not met by the shipped code):** An in-line three-stage design within 1 percent of 1:100 with all teeth between 17 and 100 (the shipped search handles two stages only).

**Difficulty:** intermediate

## Session 6: Two planetary stages in series

**You will learn:** Chaining Willis relations and meeting the planet-fit rules in each stage.

**You will build:** A designer that picks Ns, Nr and the planet count for each stage.

**Checkpoint (not met by the shipped code):** Two stages in series with total ratio exactly 16 and every planet set passing the fit rules (the shipped code has one stage and a fit check only).

**Difficulty:** advanced

## Session 7: Worm drives and self-locking

**You will learn:** Lead angle, friction and why a worm can hold a load that a spur train cannot.

**You will build:** A worm-pair model with efficiency and a self-locking test.

**Checkpoint (not met by the shipped code):** A model that reports a self-locking worm for a small lead angle and a back-driving worm for a large one (the shipped trains have no self-locking at all).

**Difficulty:** advanced

## Session 8: Torsional resonance of the train

**You will learn:** Natural frequencies of a lumped train and why starting pulses can excite them.

**You will build:** An eigenvalue calculation for the mesh-spring model.

**Checkpoint (not met by the shipped code):** The lowest natural frequency from the eigenvalue calculation agrees with the ring-down of the simulation within 2 percent (the shipped code only simulates).

**Difficulty:** advanced

## The final step

Combine the milestones: a gearbox designer that searches multi-stage and planetary trains for a target ratio and torque, checks fit, losses and start-up shock, and shows each design as turning gears. If your result looks like the Target animation, open a pull request and tell us how you did it.
