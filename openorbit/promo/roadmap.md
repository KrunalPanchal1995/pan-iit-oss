# Roadmap: the path to the openorbit Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Split the plane change between burns

**You will learn:** Why the cheapest way to turn the orbit plane shares the turn between both burns.

**You will build:** A planner that divides the 28.5 degree turn between the two burns of the GEO transfer and finds the best split.

**Checkpoint (not met by the shipped code):** A total of at most 4.200 km/s for the transfer with the 28.5 degree turn (the shipped single-burn plan gives 4.222).

**Difficulty:** intermediate

## Session 5: Full rendezvous

**You will learn:** Combining a transfer with a phasing wait so the chaser arrives at the target's position.

**You will build:** A planner that takes a chaser and a target in circular orbits with a starting angle and returns the burns and the time to meet.

**Checkpoint (not met by the shipped code):** The integrated chaser ends within 1 km of the target, and the plan's relative speed at arrival is below 1 m/s (the shipped phasing code only catches up in the same orbit shape, with no transfer).

**Difficulty:** intermediate

## Session 6: Orbit plane drift (J2)

**You will learn:** How the Earth's bulge slowly rotates the plane of an inclined orbit.

**You will build:** An integrator in 3D with the J2 term added to the acceleration.

**Checkpoint (not met by the shipped code):** A 51.6 degree orbit at radius 6778 km drifts its plane by about -5.0 degrees per day (the shipped model has no drift).

**Difficulty:** advanced

## Session 7: Low-thrust spiral

**You will learn:** How an electric thruster raises an orbit by thousands of slow laps, and why its delta-v is different from Hohmann.

**You will build:** A guidance law that steers continuous thrust along the velocity and stops at the target radius.

**Checkpoint (not met by the shipped code):** Arrive at 42164 km from 6778 km with a circular speed within 5 m/s and a delta-v within 2 percent of 4.594 km/s (the shipped finite-burn model cannot do a circular arrival).

**Difficulty:** advanced

## Session 8: Earth to Mars

**You will learn:** The same transfer around the Sun, plus the launch window and the phase angle between the planets.

**You will build:** A heliocentric planner with the Sun's gravitational parameter and circular planet orbits.

**Checkpoint (not met by the shipped code):** A transfer time of about 259 days and a departure phase angle of about 44 degrees (the shipped code only knows the Earth).

**Difficulty:** advanced

## The final step

Combine the milestones: a planner that takes a satellite from a tilted low orbit to a chosen high orbit with split burns, steers the finite burns, and animates the result with equal-area sweeps and a delta-v budget. If your result looks like the Target animation, open a pull request and tell us how you did it.
