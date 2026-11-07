# Activity sheet: openbuildingsway, Session 3: Many floors, many modes: a ten-storey frame in an earthquake

Name: ____________________   Date: ____________

**Objectives**

- Build the mass matrix M and the tridiagonal stiffness matrix K of an N-storey shear building.
- Solve K phi = w^2 M phi with np.linalg.eigh and check the periods and mode shapes against an exact formula.
- Compute modal participation and effective mass, and explain why the first mode matters most.
- Solve the response to a synthetic ground record by modal superposition and by Newmark-beta integration, and validate them against each other and against energy.
- Read peak inter-storey drift and base shear, and explain what a soft storey does.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the periods, mode shapes and effective masses of a two-storey building by hand with m = 200 000 kg and k = 3.5e8 N/m, and check them with the code.

1. ______________________________  (hint: K = k [[2, -1], [-1, 1]] and M = m I. With lambda = w^2 m / k the eige...)
2. ______________________________  (hint: The determinant condition (2 - lambda)(1 - lambda) - 1 = lambda^2 - 3 ...)
3. ______________________________  (hint: k / m = 1750 per s^2, so w1^2 = 0.382 * 1750 = 668.4 and w1 = 25.854 r...)
4. ______________________________  (hint: From the first row, phi2 / phi1 = 2 - lambda: 1.618 for mode 1 (both f...)
5. ______________________________  (hint: Participation for equal masses: Gamma^2 / total mass = (phi1 + phi2)^2...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the first mode carry most of the mass in the response, and why does the second mode have a node (a floor that hardly moves)?

Answer: ______________________________________________


**B. Numerical.** Two storeys with m = 100 000 kg and k = 1e8 N/m: find both frequencies and periods by hand, then say which mode is more dangerous for a ground period of 1 s.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the soft-storey bar chart, which storey carries the largest drift and how much more than in the uniform frame? What does the damage tell an engineer?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the first storey is weaker than the others by a factor f (between 0.35 and 1). Find the smallest f in steps of 0.1 that keeps the first-storey drift at no more than 1.5 times the largest drift of the other storeys. Justify the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
