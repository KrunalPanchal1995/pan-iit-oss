# Activity sheet: opengyro, Session 2: The precession formula and a design problem

Name: ____________________   Date: ____________

**Objectives**

- Use L = I w, torque = dL/dt and the moment of inertia of a disc I = m R^2 / 2.
- Derive and use the fast-spin precession rate Omega_p = m g r / (I w), with its assumptions.
- Solve the design problem: choose the spin so a wheel precesses at a target rate.
- Explain why a faster spin gives slower precession and why the mass drops out for a disc.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Wheel: m = 2.0 kg, R = 0.30 m, r = 0.25 m, solid disc. Find the spin for one circle every 4 s, in rad/s and rpm, and check the result.

1. ______________________________  (hint: I = m R^2 / 2 = 2.0 * 0.09 / 2 = 0.0900 kg m^2....)
2. ______________________________  (hint: Target rate: Omega_p = 2 pi / 4 = 1.5708 rad/s....)
3. ______________________________  (hint: Torque: tau = m g r = 2.0 * 9.81 * 0.25 = 4.905 N m....)
4. ______________________________  (hint: L = tau / Omega_p = 4.905 / 1.5708 = 3.123 kg m^2/s, so w = L / I = 3....)
5. ______________________________  (hint: In rpm: 34.70 * 60 / (2 pi) = 331 rpm, about 5.5 turns per second....)
6. ______________________________  (hint: Check: Omega_p = m g r / (I w) = 4.905 / (0.09 * 34.70) = 1.5708 rad/s...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a faster spin give a slower precession? And why does the mass not matter for a solid disc of fixed radius?

Answer: ______________________________________________


**B. Numerical.** A solid-disc wheel with m = 1.0 kg, R = 0.20 m, r = 0.30 m spins at 50 rad/s about a horizontal axle. Find I, Omega_p and the time for one circle.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the period-versus-spin graph (m = 2 kg, R = 0.30 m, r = 0.25 m) the line passes through (34.7, 4). What is its slope, and what would the period be at 17 rad/s?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a real bicycle wheel has its mass on the rim, so I is about m R^2, twice the disc value. With the same m, R and r, what spin gives a 4 s circle? What stays the same? Which is easier to produce by hand, and what is the trade-off?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
