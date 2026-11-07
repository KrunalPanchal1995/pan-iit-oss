# Roadmap: the path to the openascent Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Launch from a rotating Earth

**You will learn:** Why launch sites are near the equator and rockets fly east: the ground already moves at up to 465 m/s.

**You will build:** Give the rocket the surface speed of its launch latitude and compute drag with the air speed (velocity minus the rotating air).

**Checkpoint (not met by the shipped code):** Launching east from the equator, the largest payload to a 200 km orbit is at least 250 kg more than the shipped 2000 kg (the shipped model has no rotation).

**Difficulty:** intermediate

## Session 5: Thrust that changes with altitude

**You will learn:** Nozzle pressure thrust: F = F_vac - p_outside A_exit, and why Isp is lower at sea level.

**You will build:** Stages described by vacuum thrust, vacuum Isp and exit area, with the outside pressure from the exponential atmosphere.

**Checkpoint (not met by the shipped code):** Stage 1 lift-off thrust is at least 8 percent below its vacuum thrust and its burnout speed changes by more than 50 m/s against the constant-thrust model.

**Difficulty:** intermediate

## Session 6: Max Q and throttling

**You will learn:** Dynamic pressure q = 0.5 rho v^2 as a structural limit, and the cost of throttling through it.

**You will build:** A throttle law for stage 1 that keeps q below a chosen limit, with the burn lengthened to use all the propellant.

**Checkpoint (not met by the shipped code):** With a 25 kPa limit the flight still reaches orbit, its max Q is at most 25.5 kPa, and its gravity loss is larger than the shipped 1442 m/s (the shipped flight peaks at 34 kPa).

**Difficulty:** intermediate

## Session 7: An optimised upper-stage steering law

**You will learn:** The linear-tangent steering law and how a simple search tunes it for the most payload.

**You will build:** Replace the altitude hold with tan(pitch) = a - b t and search a and b (and the kick) to maximise payload to a 200 km circular orbit.

**Checkpoint (not met by the shipped code):** The optimised flight puts at least 2250 kg into a 200 km orbit with a perigee above 190 km (the shipped guidance tops out at 2000 kg).

**Difficulty:** advanced

## Session 8: The animated Target flight

**You will learn:** Animation of a time history, and how to show a whole flight's physics in one view.

**You will build:** A Matplotlib or browser animation: the rocket over a curved Earth, the first stage falling away after separation, and live altitude, speed, dynamic pressure and delta-v budget panels.

**Checkpoint (not met by the shipped code):** The animation's final frame shows a closed delta-v budget (within 1 m/s) and an orbit with perigee and apogee printed on screen.

**Difficulty:** advanced

## The final step

Combine the milestones: a rotating Earth, altitude-dependent thrust, a max Q limit and an optimised steering law, animated from the pad to orbit with a falling first stage and live panels. If your result looks like the Target description, open a pull request and tell us how you did it.
