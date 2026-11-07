# Activity sheet: opentrafficsignal, Session 1: Two phases, one queue

Name: ____________________   Date: ____________

**Objectives**

- Describe a two-phase signal plan (green, amber, red) and its cycle time.
- Explain why a queue grows on red and shrinks on green.
- Predict the peak queue with q x r and the time to clear it with q r / (s - q).
- Read a graph of queue length against time and tell when a junction cannot cope.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A road has green g = 27 s, amber 3 s and cars arrive at q = 0.15 cars per second (s = 0.5). Find the cycle time, the red time, the peak queue, the time to clear it and the capacity. Does the queue clear every cycle?

1. ______________________________  (hint: C = 2 (27 + 3) = 60 s and r = C - g = 60 - 27 = 33 s....)
2. ______________________________  (hint: Peak queue = q r = 0.15 x 33 = 4.95 cars....)
3. ______________________________  (hint: Cars leave at 0.5 and arrive at 0.15, so the queue shrinks at 0.35 car...)
4. ______________________________  (hint: 14.14 s is less than the 27 s of green, so the queue clears with 12.9 ...)
5. ______________________________  (hint: Capacity = s g / C = 0.5 x 27 / 60 = 0.225 cars per second, above 0.15...)

Final answer: ____________________

## Questions
**A. Conceptual.** On green, cars leave at 0.5 cars per second, yet the queue shrinks more slowly than that. Why? What happens to the shrinking speed as the arrival rate gets closer to 0.5?

Answer: ______________________________________________


**B. Numerical.** Road A has green 20 s, amber 3 s and q = 0.10 cars per second (s = 0.5). Find C, r, the peak queue, the time to clear it and the capacity. Sanity check: is the answer in the right units?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the second figure (largest queue against arrival rate for g = 27 s), the points rise in a straight line and then take off. At what arrival rate does it happen, and what is happening to the queue after that?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: two equal roads each receive q = 0.18 cars per second. Choose the green time g (a whole number of seconds, amber 3 s) so that the queue clears every cycle and the peak queue is at most 6 cars. Which g would you pick and why?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
