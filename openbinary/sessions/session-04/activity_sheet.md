# Activity sheet: openbinary, Session 4: A carry-lookahead adder

Name: ____________________   Date: ____________

**Objectives**

- Say what a stage generates, propagates or kills, and write g and p from a and b.
- Write every carry directly in terms of g, p and the carry in, and say which stage a carry came from.
- Build a flat carry-lookahead adder and a parallel-prefix adder in the simulator and check them against Python.
- Read gate delays and gate counts from the simulator and say what the speed costs.
- Choose the cheapest design that meets a delay budget and a gate budget.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Add 11 + 5 on four bits using the lookahead equations, with carry in 0, and say where the last carry comes from.

1. ______________________________  (hint: Write the inputs: a = 1011 and b = 0101.)
2. ______________________________  (hint: Generate g = a AND b = 0001 (only stage 0 has two ones) and propagate...)
3. ______________________________  (hint: All the carries from the equations: c1 = g0 + p0 c_in = 1 + 0 = 1; c2...)
4. ______________________________  (hint: The sum bits are s_i = p_i XOR c_i, with c_0 = c_in = 0: s0 = 0 XOR 0...)
5. ______________________________  (hint: The result is 0000 with carry out 1, which is 16, and 11 + 5 = 16. The...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why can a lookahead adder find the carry out of stage 3 without waiting for the carries out of stages 0, 1 and 2? What do generate and propagate mean?

Answer: ______________________________________________


**B. Numerical.** Use the equations to find the carry out of stage 3 (c4) for a = 1101 (13) and b = 0111 (7) with carry in 0. Which stage did it come from? Sanity check with ordinary addition.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** From the delay graph, how many gate delays does the carry out take at 16 bits and at 32 bits for the ripple, flat and prefix adders? What happens to each when the width doubles?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 32-bit adder must have its carry out ready within 7.5 ns at 0.5 ns per gate delay, using at most 1000 gates. Which of the ripple, flat and prefix designs would you choose? What would change if the budget were 10 gate delays?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
