# Activity sheet: openprocesssim, Session 3: A flowsheet engine: graph, tear stream, closure and honest limits

Name: ____________________   Date: ____________

**Objectives**

- Represent a flowsheet as a graph of blocks and streams, find a run order and a tear stream.
- Solve a recycle loop by successive substitution and by Wegstein acceleration and compare iteration counts.
- Refuse an under- or over-specified flowsheet with a clear degrees-of-freedom message, and report mass and energy closure.
- Run a sensitivity study, and recognise two honest limits: a recycle that cannot converge, and a non-ideal mixture where Raoult's law fails.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Solve the loop with the flash at only 345 K and r = 0.9, first by hand and then with the engine. Compare the iteration counts of substitution and Wegstein.

1. ______________________________  (hint: Mixtures of benzene and toluene boil between 353.2 K and 383.8 K at 1 ...)
2. ______________________________  (hint: The mixer and reactor conserve moles, so the flash feed is S = F + R =...)
3. ______________________________  (hint: So R = 0.9 (100 + R), 0.1 R = 90, R = 900 mol/s, and the bottoms are B...)
4. ______________________________  (hint: The engine agrees: R = 900 mol/s, B = 100 mol/s, V = 0. Substitution n...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a recycle loop need a tear stream?

Answer: ______________________________________________


**B. Numerical.** A heat exchanger heats 100 mol/s of toluene (Cp = 157 J/(mol K)) from 320 K with a utility at 400 K and UA = 15 700 W/K. Find T_out and Q.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the sensitivity figure, how do purity and product flow change between 364 and 372 K at r = 0.9, and does the recycle fraction move the purity curve?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design (the mini-project): find the highest flash temperature on a 0.5 K grid giving at least 0.70 benzene in the vapour, and the smallest r (0.05 grid) giving at least 60 mol/s of product. State the trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
