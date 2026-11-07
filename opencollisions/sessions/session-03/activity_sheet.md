# Activity sheet: opencollisions, Session 3: Off-centre hits: discs in two dimensions, a contact simulation and a crash estimate

Name: ____________________   Date: ____________

**Objectives**

- Find the velocities of two smooth discs after an off-centre collision, from the impact parameter.
- Show that the discs leave at 90 degrees to each other for equal masses, e = 1 and one disc at rest.
- Validate the formulas against an independent time-stepping simulation of the contact.
- Use the work-energy idea to estimate the average force and deceleration of a car stopping against a wall.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Disc 1 (1 kg, radius 0.5 m) moves at 4 m/s along +x and hits disc 2 (1 kg, radius 0.5 m) at rest. The impact parameter is b = 0.5 m and e = 1. Find both velocities after the collision.

1. ______________________________  (hint: sin(phi) = 0.5 / 1.0, so phi = 30 degrees and n = (0.866, 0.5).)
2. ______________________________  (hint: v_n = (4, 0) . n = 3.464 m/s.)
3. ______________________________  (hint: v1' = (4, 0) - (1/2) x 2 x 3.464 x n = (1.00, -1.73) m/s: speed 2.0...)
4. ______________________________  (hint: v2' = 0 + (1/2) x 2 x 3.464 x n = (3.00, 1.73) m/s: speed 3.46 m/s...)
5. ______________________________  (hint: Check momentum: (1.00 + 3.00, -1.73 + 1.73) = (4, 0), the same as b...)
6. ______________________________  (hint: Check energy: 1/2 x 1 x 4 + 1/2 x 1 x 12 = 8 J = 8 J before.)
7. ______________________________  (hint: Check the angle: (1.00, -1.73) . (3.00, 1.73) = 0, so the discs lea...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why do two equal discs leave at 90 degrees to each other when one is at rest and e = 1?

Answer: ______________________________________________

**B. Numerical.** Disc 1 (2 kg, radius 0.6 m) moves at 5 m/s along +x and hits disc 2 (1 kg, radius 0.4 m) at rest with b = 0.3 m and e = 0.6. Find both velocities and the energy lost.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the speed graph, why is disc 2's speed highest at b = 0 and falls towards 0 as b approaches 1 m, while disc 1 keeps more and more of its speed?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: a 1200 kg car drives at 50 km/h into a rigid wall. The average deceleration must not exceed 20 g (a made-up limit for this exercise, not a safety standard). Find the least crumple distance, and compare with the 0.6 m of the worked example.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
