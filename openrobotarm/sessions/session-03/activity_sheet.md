# Activity sheet: openrobotarm, Session 3: Numerical inverse kinematics and a pick-and-place path

Name: ____________________   Date: ____________

**Objectives**

- Derive the Jacobian of the planar chain and verify it against finite differences.
- Solve inverse kinematics by damped least squares and explain why damping is needed near singularities.
- Show that the smallest singular value goes to zero at a stretched arm and compute the manipulability.
- Follow a straight-line path with smooth timing, check it against forward kinematics, and keep joints away from their limits in the null space.
- Explain failure cases: an unreachable target, elbow flips and joint limits.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Reach the target (0.45, 0.20) m from the start q = (0.3, 0.3, 0.3) rad, lambda = 0.01. Trace the error, and compare the first step with the cap.

1. ______________________________  (hint: Forward kinematics of the start: (0.586, 0.347) m, so the error is e =...)
2. ______________________________  (hint: The raw damped step is dq = (-1.28, 1.56, 1.50) rad: far too large for...)
3. ______________________________  (hint: Iterate: the error falls slowly at first while the steps are capped (0...)
4. ______________________________  (hint: After 8 iterations the error is 4.3e-4 m, after 9 it is 9.5e-7 m and a...)
5. ______________________________  (hint: The iteration stops after 11 iterations with error below 1e-9 m, at q ...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a pure pseudoinverse demand enormous joint speeds near a fully stretched arm, and how does damping fix this? What does damping cost?

Answer: ______________________________________________


**B. Numerical.** Write the Jacobian of the stretched arm (all angles 0) with L = (0.30, 0.25, 0.15) m, and find its rank, its singular values and the manipulability.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the log-log figure, what is the slope of the pseudoinverse line and what does it mean for the speed when the bend is ten times smaller? What does the damped line do?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: plain tracking of the path from (0.25, -0.30) m to (0.25, 0.30) m (a start with q2 near -122 degrees) swings a joint to 150.7 degrees, but the motors stop at 120 degrees. Give two ways to fix it, with numbers, and one trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
