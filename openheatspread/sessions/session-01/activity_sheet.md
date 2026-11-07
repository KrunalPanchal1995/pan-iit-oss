# Activity sheet: openheatspread, Session 1: Heat flows through a slab: Fourier's law

Name: ____________________   Date: ____________

**Objectives**

- Explain that heat flows from hot to cold and that its rate is measured in watts.
- Use Q = k A (T_hot - T_cold) / L to compute the heat flow through a slab, by hand and in Python.
- Sketch the temperature profile inside a slab and explain why it is a straight line.
- Compare materials by their thermal conductivity.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A thermal pad (k = 5 W/(m K)) is 1 mm thick and covers 1 cm^2. Its hot face is at 80 C and its cold face at 50 C. Find the heat flow, the heat flux and the temperature half way through.

1. ______________________________  (hint: Convert to metres: L = 1 mm = 0.001 m, A = 1 cm^2 = 0.0001 m^2....)
2. ______________________________  (hint: Q = k A (T_hot - T_cold) / L = 5 * 0.0001 * 30 / 0.001 = 15 W....)
3. ______________________________  (hint: Flux q = Q / A = 15 / 0.0001 = 150000 W/m^2....)
4. ______________________________  (hint: The profile is a straight line, so half way (x = 0.5 mm) the temperatu...)
5. ______________________________  (hint: Sanity check: 15 W is a reasonable laptop-chip power, and a 30 C drop ...)

Final answer: ____________________

## Questions
**A. Conceptual.** A slab of copper and a slab of glass have the same size and the same face temperatures. Which has the larger temperature drop per millimetre, and which carries more heat? Explain.

Answer: ______________________________________________


**B. Numerical.** A thermal pad with k = 5 W/(m K) is 0.5 mm thick and covers 1 cm^2, with faces at 70 C and 50 C. Find the heat flow in W and check that the answer is sensible.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the profile graph for L = 2, 5 and 10 mm (80 C to 40 C), what is the temperature at a depth of 2 mm in each slab, and what does that tell you about the slope?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a pad (k = 5 W/(m K), 1 cm^2) must carry at least 12 W from a chip face at 80 C to a heatsink face at 50 C. Manufacturing says it cannot be thinner than 0.3 mm. Choose a thickness and justify it.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
