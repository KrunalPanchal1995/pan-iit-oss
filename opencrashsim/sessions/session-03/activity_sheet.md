# Activity sheet: opencrashsim, Session 3: A crumple zone you can simulate and validate

Name: ____________________   Date: ____________

**Objectives**

- Build a lumped crumple model with a force-displacement curve and step it through time with RK4.
- Validate peak deceleration, stopping distance and stop time against the exact constant-force solution, and audit the energy balance.
- Analyse a two-car collision: momentum conservation, inelastic collision, relative speed and mass ratio.
- Explain and reproduce a failure case: the crumple zone bottoms out and a second, much larger spike appears.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 1000 kg car hits a rigid barrier at 56 km/h with Fp = 200 kN and Lc = 0.8 m. Find the stopping distance and the peak deceleration, and check them against the simulation and the energy balance.

1. ______________________________  (hint: v = 56 / 3.6 = 15.556 m/s, so KE0 = 0.5 * 1000 * 15.556^2 = 120988 J (...)
2. ______________________________  (hint: The ramp (0 to 0.05 m) absorbs half of Fp * XR = 0.5 * 200000 * 0.05 =...)
3. ______________________________  (hint: The remaining 120988 - 5000 = 115988 J is absorbed on the plateau: 115...)
4. ______________________________  (hint: Total stopping distance d = 0.05 + 0.5799 = 0.6299 m. It is less than ...)
5. ______________________________  (hint: Peak deceleration = Fp / m = 200000 / 1000 = 200 m/s^2 = 20.39 g....)
6. ______________________________  (hint: The RK4 simulation gives 0.6299 m, 20.39 g and a stop time of 79.4 ms,...)

Final answer: ____________________

## Questions
**A. Conceptual.** For a fixed crumple length and impact energy, why is a flat force plateau the best force-displacement curve for keeping the peak deceleration low?

Answer: ______________________________________________


**B. Numerical.** A 1200 kg car hits a barrier at 40 km/h; its crumple zone has Fp = 150 kN, XR = 0.05 m and a long length. Find the stopping distance and the peak deceleration.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the deceleration-trace figure the failing design is flat at 25.5 g for about 28 ms and then climbs to 159 g. What happened, which part of the force curve produced the spike, and why does it come at the end of the crash?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: for a 1000 kg car at 56 km/h choose Fp (steps of 10 kN) and Lc (steps of 0.05 m) so that peak deceleration is at most 22 g, Lc is at most 0.65 m and the car stops within 95 percent of Lc. Justify your choice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
