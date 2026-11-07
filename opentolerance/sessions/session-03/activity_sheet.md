# Activity sheet: opentolerance, Session 3: Statistical stack-up, capability and cost

Name: ____________________   Date: ____________

**Objectives**

- Combine independent part tolerances by root-sum-square and compare with the worst-case sum.
- Compute Cp, Cpk and the fraction of assemblies out of tolerance, and verify them by Monte Carlo simulation and exact corner enumeration.
- Show how a drifting process centre breaks a stack that looks safe, and quantify it.
- Allocate tolerances to five parts at minimum illustrative cost while meeting a capability target.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
Five independent parts each have a tolerance of +-0.10 mm and the gap must stay within 2.00 +-0.30 mm. Find the worst-case and RSS gap tolerances, sigma, Cp and the fraction out of tolerance for a centred process.

1. ______________________________  (hint: Worst case: 5 x 0.10 = 0.500 mm. That is far outside +-0.30 mm, so a w...)
2. ______________________________  (hint: RSS: sqrt(5 x 0.10^2) = 0.10 x sqrt 5 = 0.224 mm (0.2236). This is ins...)
3. ______________________________  (hint: Sigma of the gap = 0.2236 / 3 = 0.0745 mm....)
4. ______________________________  (hint: Cp = (2.30 - 1.70) / (6 x 0.0745) = 0.60 / 0.447 = 1.34, just above th...)
5. ______________________________  (hint: The limits are 0.30 / 0.0745 = 4.02 sigma away, so the fraction out is...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is the root-sum-square tolerance never larger than the worst-case sum, and what assumption lets us use it? What do we pay for the smaller number?

Answer: ______________________________________________


**B. Numerical.** A gap has limits 1.70 and 2.30 mm and a process with mean 2.10 mm and sigma 0.075 mm. Find Cp and Cpk and say what the difference means.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the drift graph, what happens to the fraction out when the drift grows from 0 to 1 sigma for the allocated tolerances? Read it at 0.5 and 1.0 sigma.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: five parts get equal tolerances. Find the equal tolerance t that gives Cp = 1.33 (four sigma) for a gap of 2.00 +-0.30 mm using RSS, and compare its cost, using k = 3.0, 0.4, 1.0, 0.2 and 0.6, with the equal worst-case design. Is the worst-case design makeable if no process can hold better than +-0.05 mm?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
