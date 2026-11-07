# Activity sheet: openevacuation, Session 3: Simulate a building evacuation and plan it safely

Name: ____________________   Date: ____________

**Objectives**

- Describe a building as a network of links (doors, stair flights) with a capacity and a travel time.
- Step a queue-and-flow simulation forward in time and find where queues form.
- Validate the simulation: the Session 1 limit, conservation of people, a bottleneck bound and time-step convergence.
- Compare RSET with ASET using a safety factor and choose the number and width of stairs, including the case of a blocked stair.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The block has 3 upper floors and a ground floor, 120 people each, one stair 1.2 m wide (178/279 mm steps, 9 m per flight), 1.2 m stair doors and a 1.5 m final exit. Pre-movement 60 s, corridor 20 m. Estimate the evacuation time by hand, compare with the simulation, and check the plan against ASET = 900 s.

1. ______________________________  (hint: Stair capacity: We = 1.2 - 0.3 = 0.9 m, Fs_max = 1.08 / (4 x 0.266) = 1.015...)
2. ______________________________  (hint: First arrival at the stair: 60 + 20 / 1.19 = 76.8 s. Time for the 360 upper...)
3. ______________________________  (hint: Hand bound: 76.8 + 394.1 + 9.8 = 480.7 s. The simulation gives 482.5 s, jus...)
4. ______________________________  (hint: RSET = 30 + 482.5 = 512.5 s, and 1.5 x 512.5 = 769 s, below 900 s: safe wit...)
5. ______________________________  (hint: Plan with two stairs: both open, RSET = 316 s; one blocked, everyone uses t...)

Final answer: ____________________

## Questions
**A. Conceptual.** With one stair, why do the people on the top floor not wait the longest, even though they are farthest from the exit?

Answer: ______________________________________________


**B. Numerical.** For the same block, find the hand bound with one 1.5 m stair, and the RSET. Is it safe for ASET = 900 s with the factor 1.5?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In the queue figure, the stair-door queue on floor 2 stays flat at about 110 people from 90 s to 220 s and then falls in a straight line. Explain the flat part and the slope.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: the four-storey block (3 upper floors, 120 each) has ASET = 900 s. Using the safety factor 1.5, choose the number of stairs and the narrowest width (1.0, 1.2, 1.5 or 2.0 m) that is safe even with one stair blocked. Then say why a single 2.0 m stair, which is also "safe", is a poor plan.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
