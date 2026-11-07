# Activity sheet: opentrafficsignal, Session 2: Delay from cycle time, green split and flow

Name: ____________________   Date: ____________

**Objectives**

- Compute the flow ratio, green ratio and degree of saturation of an approach.
- Derive and use the uniform delay d = C (1 - g/C)^2 / (2 (1 - q/s)) for the deterministic queue.
- Read a cumulative arrival and departure diagram: the area between the curves is waiting time.
- Split a cycle between two roads to minimise total delay under a degree-of-saturation limit, and compute Webster's cycle.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With C = 60 s, effective green 27 s for each road (54 s in total, L = 6 s), s = 0.5 cars per second, find x and d for the main road (q = 0.20) and the side road (q = 0.10), and the average delay per car of the junction.

1. ______________________________  (hint: Green ratio lam = 27 / 60 = 0.45 for both roads, so (1 - lam)^2 = 0.55...)
2. ______________________________  (hint: Main road: x = 0.20 x 60 / (27 x 0.5) = 12 / 13.5 = 0.889 (below 1, th...)
3. ______________________________  (hint: Main road delay: d = 60 x 0.3025 / (2 (1 - 0.20/0.5)) = 18.15 / (2 x 0...)
4. ______________________________  (hint: Side road: x = 0.10 x 60 / 13.5 = 0.444 and d = 18.15 / (2 (1 - 0.2)) ...)
5. ______________________________  (hint: Average delay per car = (0.20 x 15.125 + 0.10 x 11.344) / 0.30 = (3.02...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the uniform delay contain the square of the red fraction, (1 - g/C)^2, and not just the red fraction? What does a longer red do to the queue and to each car's wait?

Answer: ______________________________________________


**B. Numerical.** A road has C = 90 s, effective green 40 s and q = 0.15 cars per second (s = 0.5). Find the degree of saturation and the uniform delay. Check the units and decide whether the formula applies.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the delay-against-split graph (C = 60 s, q1 = 0.20, q2 = 0.10), the curve is not defined for splits below about 44 percent or above about 78 percent. Why, and where is the minimum?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with C = 60 s, q1 = 0.20 and q2 = 0.10 cars per second, choose the effective greens (total 54 s) that minimise the average delay with both degrees of saturation at most 0.9. Compare with the equal split and the proportional split. What would you check before using it?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
