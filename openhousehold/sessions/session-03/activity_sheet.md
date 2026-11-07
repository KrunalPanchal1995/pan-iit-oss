# Activity sheet: openhousehold, Session 3: A month with random usage and rooftop solar

Name: ____________________   Date: ____________

**Objectives**

- Simulate 30 days with random heater time, random habits and random cloud cover.
- Model rooftop solar as a half sine and apply net metering hour by hour.
- Validate the simulation against a hand calculation and against the exact area under a sine.
- Test sensitivity to array size, tariff and usage, and recognise the limit where the bill floors.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
With a 1 kWp array, average weather (cloud 0.85, no random change) and the Session 2 household, find the net energy and the monthly bill by hand and compare with the simulation.

1. ______________________________  (hint: Sun energy per kWp per day without clouds: derate x sum of 12 midpoint...)
2. ______________________________  (hint: With cloud 0.85: 4.597 x 0.85 = 3.907 kWh per day, so 117.2 kWh in 30 ...)
3. ______________________________  (hint: Net per day = load - generation = 8.26 - 3.907 = 4.353 kWh, so net per...)
4. ______________________________  (hint: Bill: 50 + 100 x 3 + (130.6 - 100) x 5 = 50 + 300 + 153.0 = Rs 503 (Rs...)
5. ______________________________  (hint: Compare: no panels Rs 1208.50; without export credit Rs 711.9....)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the bill with net metering fall by less and less for each extra half kWp of panels?

Answer: ______________________________________________


**B. Numerical.** Find the monthly net energy and the net-metering bill for a 1.5 kWp array in average weather (cloud 0.85). Check the result with the simulation.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the bill-versus-size graph, read the bill at 0, 1, 2 and 3 kWp, and explain why the last two points are so close.

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: with a roof for at most 2 kWp, choose the smallest array (in steps of 0.5 kWp) that gives a bill of Rs 350 or less in average weather, then check it in a bad month (cloud 0.6). If exports earned nothing, would the answer still work?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
