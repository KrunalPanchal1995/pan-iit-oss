# Roadmap: the path to the opendronecontrol Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: The rate loop and gyroscope noise

**You will learn:** Why real flight controllers add a third, innermost loop on the body rate, why the D term amplifies sensor noise, and how a first-order low-pass filter tames it.

**You will build:** A rate loop (PI on the roll rate) inside the Session 3 attitude loop, gyro readings with 0.05 rad/s of random noise, and a low-pass filter on the derivative.

**Checkpoint (not met by the shipped code):** With 0.05 rad/s gyro noise the standard deviation of the commanded torque in hover falls by at least half when the filter (cut-off 20 Hz) is switched on, while the 1 m move still settles within 4 s (the shipped code has perfect sensors).

**Difficulty:** intermediate

## Session 5: Integrator wind-up and wind gusts

**You will learn:** Why the integral term keeps growing while the thrust is saturated, how that causes a large overshoot, and how anti-wind-up (clamping or back-calculation) fixes it; how a steady side wind needs integral action in the position loop.

**You will build:** Anti-wind-up for the height PID and a side-wind force on the planar drone, with an I term in the position loop.

**Checkpoint (not met by the shipped code):** A climb of 10 m with the thrust limit active overshoots by less than half as much with anti-wind-up as without; and in a steady 1 N side wind the drone holds y within 2 cm of the target (the shipped position loop is PD and drifts).

**Difficulty:** intermediate

## Session 6: The full 3-D quadrotor

**You will learn:** Roll, pitch and yaw, the rotation matrix, the 4x4 mixer for an X-frame, and how yaw is controlled by the drag torque of rotors spinning in opposite directions.

**You will build:** A 12-state rigid-body model with four motors and the cascaded PID on all three axes.

**Checkpoint (not met by the shipped code):** A 1 m move along x, then along y, each settles within 4 s with yaw held within 2 degrees; the energy check (thrust work minus potential-energy gain) closes within 1 percent in a vertical climb (the shipped model is planar).

**Difficulty:** advanced

## Session 7: Estimating the state

**You will learn:** A gyroscope drifts and an accelerometer is noisy; a complementary filter fuses them into a good tilt estimate.

**You will build:** Simulated gyro (with bias) and accelerometer readings and a complementary filter; the controller flies on the estimate, not on the true state.

**Checkpoint (not met by the shipped code):** With a gyro bias of 0.02 rad/s the estimated tilt stays within 1 degree of the truth for 60 s of hover, while integrating the gyro alone drifts by more than 60 degrees (the shipped code reads the true state).

**Difficulty:** advanced

## Session 8: Fly a square mission

**You will learn:** Waypoints, a smooth reference path, and how to keep the cascade tracking a moving target.

**You will build:** Take-off to 1.5 m, a 2 m square, landing, and a gust halfway, flown by the 3-D model of Session 6 with the estimator of Session 7.

**Checkpoint (not met by the shipped code):** The largest distance from the planned path stays below 10 cm and the drone lands within 5 cm of its start (the shipped code has no mission).

**Difficulty:** advanced

## The final step

Combine the milestones: a 3-D quadrotor with a rate, attitude and position cascade, filtered noisy sensors and anti-wind-up, flying the square through a gust, animated with its motor speeds and tilt angles. If your result looks like the Target, open a pull request and tell us how you did it.
