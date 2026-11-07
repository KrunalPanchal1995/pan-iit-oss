# Activity sheet: openheatspread, Session 3: A 2D heat solver, validated, and a laptop with two hot spots

Name: ____________________   Date: ____________

**Objectives**

- Explain how the explicit finite-difference update works and why dt <= dx^2 / (4 alpha) in 2D.
- Validate a solver against two exact cases: a steady 1D wall and a spreading Gaussian hot spot.
- Measure grid convergence and sensitivity to conductivity, and show what happens past the stability limit.
- Apply the validated solver to a board with two hot spots and check the energy balance.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For a material with alpha = 20 mm^2/s on a grid with dx = 1 mm, find the largest stable time step, then find the peak temperature rise of the 60 K, 3 mm Gaussian hot spot after 1 s, from the exact formula, and compare with the solver at r = 0.2.

1. ______________________________  (hint: dt_max = dx^2 / (4 alpha) = 1 / (4 * 20) = 0.0125 s. With r = 0.2 we u...)
2. ______________________________  (hint: Exact width: s0^2 + 2 alpha t = 9 + 2 * 20 * 1 = 49 mm^2....)
3. ______________________________  (hint: Exact peak = 60 * 9 / 49 = 11.02 K (the hot spot has dropped from 60 K...)
4. ______________________________  (hint: The solver gives 10.99 K, a difference of 0.03 K (0.2 percent)....)
5. ______________________________  (hint: Sanity check: heat is conserved by the insulated edges, so as the peak...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the explicit scheme blow up when dt is too large, even though each step only moves a cell toward the average of its neighbours?

Answer: ______________________________________________


**B. Numerical.** Aluminium has alpha = 82.3 mm^2/s. Find the largest stable time step for dx = 0.5 mm. What happens to dt_max if you halve dx again?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the convergence plot the largest errors are 0.449, 0.110, 0.0275 and 0.0069 K for dx = 4, 2, 1 and 0.5 mm. By what factor does the error shrink each time dx is halved? Predict the error at dx = 0.25 mm, then check with `max_error(0.25)`.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the CPU (12 W) and GPU (8 W) must stay at most 85 C in 25 C air (a rise of at most 60 K) with h = 40 W/(m^2 K). The 100 mm x 60 mm aluminium spreader sheet (2.7 g per cm^3) may not weigh more than 20 g. Using the printed table, choose a thickness and justify it.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
