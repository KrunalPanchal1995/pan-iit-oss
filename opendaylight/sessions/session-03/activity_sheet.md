# Activity sheet: opendaylight, Session 3: Simulate a year of daylight and heat, then plan the window

Name: ____________________   Date: ____________

**Objectives**

- Compute the average daylight factor of a room and the effect of an overhang on it.
- Simulate one year of a room hour by hour: daylight, dimmed lights, solar heat and cooling electricity.
- Validate the simulation with an independent ray test, hand checks, limits and a convergence test.
- Choose the window orientation, size (window-to-wall ratio) and overhang that use the least electricity while giving enough daylight.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The Chennai study room (4 m facade, 5 m deep, 3 m high) has a south window with WWR 0.25 (2 m x 1.5 m = 3 m2) and a 0.6 m overhang 0.3 m above it. Find the visible sky angle, the average daylight factor and the yearly electricity, and check the totals by hand.

1. ______________________________  (hint: Visible sky angle: theta = atan((0.3 + 0.75) / 0.6) = atan(1.75) = 60.26 de...)
2. ______________________________  (hint: Room surface area: 2 x (4 x 5 + 4 x 3 + 5 x 3) = 94 m2. DF = 0.7 x 3 x 60.2...)
3. ______________________________  (hint: The year simulation (365 days x 96 quarter hours) gives: solar heat during ...)
4. ______________________________  (hint: Conduction by hand: (5.8 - 2.0) x 3 m2 x 4 K x 8 h x 365 days / 1000 = 133....)
5. ______________________________  (hint: Cooling electricity = (729.1 + 133.2 + 179.5) / 3 = 347.2 kWh. Total = 179....)
6. ______________________________  (hint: Checks: the 3D ray test and the VSA formula agree within 0.0002; halving th...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why is there a best window size, rather than "the bigger the better" or "the smaller the better"?

Answer: ______________________________________________


**B. Numerical.** For the north window of the mini-project (WWR 0.35, 0.3 m overhang 0.3 m above a 1.5 m window), find the glass area, the visible sky angle and the average daylight factor. Does it meet 2 percent?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 1, by how much do lighting and cooling change from WWR 0.30 to 0.35, and from 0.40 to 0.45? Use this to explain where the minimum lies.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: your client insists on a west-facing window (the view is to the west) and needs DF of at least 2 percent. Using the model, what is the best you can do with the overhang options 0 to 0.9 m? Suggest two design changes outside the model that would help, and say how you would test them.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
