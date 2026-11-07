# Activity sheet: openneuron, Session 2: The membrane is an RC circuit: the leaky integrate-and-fire neuron

Name: ____________________   Date: ____________

**Objectives**

- Write the membrane equation C dV/dt = -(V - V_rest)/R + I and explain each term.
- Compute the time constant tau = R C and the rheobase current from typical values.
- Derive the closed-form firing rate and check it against a numerical simulation.
- Solve the design problem: which current gives 20 spikes per second?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For R = 100 megaohm, C = 100 pF and I = 0.2 nA, find the time to reach the threshold and the firing rate with t_ref = 2 ms.

1. ______________________________  (hint: tau = R C = 100 x 100 / 1000 = 10 ms. R I = 100 x 0.2 = 20 mV, which i...)
2. ______________________________  (hint: T = tau ln(R I / (R I - 15)) = 10 ln(20 / 5) = 10 ln 4 = 13.863 ms....)
3. ______________________________  (hint: One cycle = 2 + 13.863 = 15.863 ms, so f = 1000 / 15.863 = 63.04 spike...)
4. ______________________________  (hint: Without a refractory period the rate would be 1000 / 13.863 = 72.13 pe...)
5. ______________________________  (hint: Simulation check: the numerical spike train has its first spike at 13....)

Final answer: ____________________

## Questions
**A. Conceptual.** If R stays the same but the capacitance C is halved, does the neuron fire faster or slower for the same current? Explain without equations, then check with a number.

Answer: ______________________________________________


**B. Numerical.** For R = 100 megaohm, C = 100 pF and I = 0.3 nA find the climb time T and the rate f (t_ref = 2 ms).

Answer: ______________________________________________


**C. Graph and simulation interpretation.** Describe the shape of the f-I curve: what happens below 0.15 nA, just above it, and for very large currents? What does the limit mean?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the cell must fire at 20 spikes per second, within 18 to 22. Find the current for exactly 20 per second, the allowed range of current, and say what makes this design delicate.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
