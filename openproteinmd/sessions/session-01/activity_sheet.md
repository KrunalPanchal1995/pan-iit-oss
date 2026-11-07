# Activity sheet: openproteinmd, Session 1: Atoms as balls on springs: motion follows force

Name: ____________________   Date: ____________

**Objectives**

- Explain that the force on an atom is minus the slope of its potential energy.
- Compute the energy and force of a spring and of a Lennard-Jones pair, by hand and in Python.
- Find the equilibrium bond length of a Lennard-Jones pair and say why it is 2^(1/6) sigma.
- Read a graph of potential energy and force against distance, and predict how a released pair moves.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Find the Lennard-Jones energy and force at r = 1.5 sigma. Is the pair pulled together or pushed apart?

1. ______________________________  (hint: Compute (1/r)^6 = (1/1.5)^6 = 0.08779 and (1/r)^12 = 0.00771....)
2. ______________________________  (hint: V = 4 (0.00771 - 0.08779) = 4 (-0.08008) = -0.3203 epsilon....)
3. ______________________________  (hint: F = (24 / 1.5) [2 (0.00771) - 0.08779] = 16 (-0.07237) = -1.158 epsilo...)
4. ______________________________  (hint: The force is negative, so the atoms are pulled together: r = 1.5 is ou...)
5. ______________________________  (hint: Check with the energy slope: V at 1.49 and 1.51 differ by about 0.0232...)

Final answer: ____________________

## Questions
**A. Conceptual.** A spring pair and a Lennard-Jones pair both oscillate about the same bottom. Why does the spring have a fixed period but the Lennard-Jones pair's period depends on how far you stretch it?

Answer: ______________________________________________


**B. Numerical.** A bond is modelled by a spring with k = 10 and r0 = 1. Find its energy and force at r = 1.3 (all in reduced units), and the Lennard-Jones energy and force at r = 2.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the energy graph, where is the force zero, and what happens to a pair released at r = 1.6 sigma? Read it from the slope.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: choose a spring constant so that a bond pair oscillates with a period of 0.5 tau, and say how large a time step you would then need to follow the motion with about 20 steps per period.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
