# Roadmap: the path to the opencollisions Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Friction and spin between discs

**You will learn:** Why a real ball picks up spin from a glancing hit, and how friction limits the sideways push at the contact.

**You will build:** Add a friction impulse along the contact surface (Coulomb friction with a given coefficient) and a spin for each disc.

**Checkpoint (not met by the shipped code):** With a friction coefficient of 0 the Session 3 results come back exactly, and with friction the angle between the two outgoing discs is no longer exactly 90 degrees.

**Difficulty:** intermediate

## Session 5: Many bodies: Newton's cradle

**You will learn:** How a chain of two-body collisions passes momentum along a line of balls.

**You will build:** A time-stepping simulation of five equal balls in a row with a restitution coefficient, using the Session 2 rule for every contact.

**Checkpoint (not met by the shipped code):** With e = 1, one ball in gives one ball out, and the total momentum and kinetic energy stay constant over the whole run.

**Difficulty:** intermediate

## Session 6: Rotating bodies and angular momentum

**You will learn:** Why an off-centre hit on a rod makes it spin, and what is kept when it does.

**You will build:** A collision of a point mass with a free rod, using conservation of linear and angular momentum.

**Checkpoint (not met by the shipped code):** The total angular momentum about the point of contact is the same before and after, and a hit at the centre gives no rotation.

**Difficulty:** advanced

## Session 7: A better crumple zone

**You will learn:** Why the peak force of a crash is higher than the average force, and how the shape of the force-distance curve matters.

**You will build:** Replace the constant average force of Session 3 by a force that grows linearly with the crumple distance, and compute the peak force and the stopping distance.

**Checkpoint (not met by the shipped code):** For a force that grows linearly the peak force is exactly twice the average force, and the energy absorbed still equals the initial kinetic energy.

**Difficulty:** intermediate

## Session 8: A ball bouncing in a box

**You will learn:** How an event-driven simulation jumps from one collision to the next without small time steps.

**You will build:** A ball bouncing on a floor with restitution e, with the time and speed of every bounce computed exactly.

**Checkpoint (not met by the shipped code):** The k-th rebound height equals e^(2k) times the drop height, and the total time to stop is finite.

**Difficulty:** advanced
