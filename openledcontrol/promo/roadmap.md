# Roadmap: the path to the openledcontrol Target

This is the path, not the code. Each milestone says what you learn, what you build, and how you know it works. Pick one and open a pull request. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Session 4: Debounce instead of hysteresis

**You will learn:** How a time delay (ignore changes shorter than N minutes) fights chatter, and how it differs from two thresholds.

**You will build:** A controller with a single threshold plus a debounce timer, compared with the Schmitt trigger.

**Checkpoint (not met by the shipped code):** At most 2 switches on the seed 7 day with zero hysteresis (the shipped single-threshold comparator gives 20).

**Difficulty:** intermediate

## Session 5: Fade the LED in and out

**You will learn:** Slew limiting or PWM duty cycle as a way to avoid abrupt on-off steps.

**You will build:** A brightness output between 0 and 1 that follows the decision gradually.

**Checkpoint (not met by the shipped code):** The largest one-minute brightness step is at most 0.1 (the shipped switch jumps by 1.0 in one step).

**Difficulty:** intermediate

## Session 6: Make the trip point immune to the supply

**You will learn:** Ratiometric references and why the supply cancels, then how real reference parts are used.

**You will build:** A comparator reference that follows the supply or a stable fixed reference with a regulated supply, checked by Monte Carlo.

**Checkpoint (not met by the shipped code):** With the supply varying between 4.5 and 5.5 V and all other parts exact, the trip level stays within 5 percent of its median (the shipped fixed 2.5 V reference spreads from 13.7 to 23.1 lux, 5th to 95th percentile).

**Difficulty:** advanced

## Session 7: Calibrate the LDR from measurements

**You will learn:** Fitting R10 and gamma to measured points on a log-log graph, with noise.

**You will build:** A fit from six noisy readings of resistance against light, then a controller built from the fitted curve.

**Checkpoint (not met by the shipped code):** Recover gamma within 0.03 and R10 within 5 percent from six readings with 5 percent noise (the shipped code only assumes gamma = 0.7).

**Difficulty:** advanced

## Session 8: A latching alarm with reset

**You will learn:** Memory in logic: how a latch holds an alarm until a person resets it.

**You will build:** A gate-level alarm with inputs A, B and RESET whose output stays on after the cause is gone.

**Checkpoint (not met by the shipped code):** After a one-sample pulse on A the alarm stays 1 until RESET, and the whole behaviour is verified on every combination of inputs for a 3-step sequence (the shipped OR alarm drops to 0 as soon as the cause is gone).

**Difficulty:** advanced

## The final step

Combine the milestones: a controller whose LED fades in at dusk, ignores clouds, keeps its trip point despite the supply, is calibrated to a real LDR, and has a latching alarm for a second sensor. If your result looks like the Target animation, open a pull request and tell us how you did it.
