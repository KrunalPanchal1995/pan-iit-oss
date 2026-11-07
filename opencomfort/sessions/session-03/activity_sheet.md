# Activity sheet: opencomfort, Session 3: Simulate a hot day and choose a passive design

Name: ____________________   Date: ____________

**Objectives**

- Model a room with air and thermal mass and step it through a day with Runge-Kutta 4.
- Validate the simulation against Session 1 and the energy balance (heat in = heat stored).
- Compare shading, a white roof, all-day ventilation and night flushing, and measure what each one buys.
- Use an adaptive comfort limit and discomfort degree-hours to choose the cheapest design that works.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
For the as-built room at 15:00 on 15 April, find the outdoor temperature and the sol-air temperature of the dark roof. Then validate the simulation: with constant inputs (34 C outside and on the roof, 160 W of sun, 10 air changes per hour) it must give the Session 1 answer.

1. ______________________________  (hint: Outdoor: T_out = 31 + 4.5 cos(0) = 35.5 C....)
2. ______________________________  (hint: Sun on the roof at 15:00: altitude 45.8 degrees, beam 1100 exp(-0.18 / 0.71...)
3. ______________________________  (hint: Sol-air: T_sa = 35.5 + 0.8 x 716 / 20 - 3.9 = 60.2 C for the dark roof, and...)
4. ______________________________  (hint: Validation: with constant inputs the mass stops changing, so T_a = 34 + (16...)
5. ______________________________  (hint: Energy check on the real day: heat flowing in over 24 h minus heat stored i...)

Final answer: ____________________

## Questions
**A. Conceptual.** In the design-day results, opening the windows all day beats night flushing (36.0 C against 36.9 C). When would night flushing win, and why?

Answer: ______________________________________________


**B. Numerical.** Find the sol-air temperature of a flat roof at noon when the outdoor air is 34.2 C and the sun on the roof is 1027 W/m2, for a dark roof (a = 0.8) and a white roof (a = 0.3). How much hotter than the air is each?

Answer: ______________________________________________


**C. Graph and simulation interpretation.** In Figure 1, why does the as-built room reach its peak around 15:30 and stay above 38 C all night, while the outdoor air falls to 26.5 C?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: using `choose_design`, find the cheapest package that keeps discomfort under 25 K h, and the cheapest under 20 K h. Explain why the roof coating comes before the overhang for this room.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
