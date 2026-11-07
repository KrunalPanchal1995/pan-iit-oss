# Activity sheet: openheatspread, Session 2: Thermal resistance: layers in series and a cooling design

Name: ____________________   Date: ____________

**Objectives**

- Convert each layer of a heat path into a thermal resistance R = L/(kA) or R = 1/(hA).
- Add resistances in series and find the chip temperature T = T_ambient + P R_total.
- Find which layer dominates and which design change gives the largest drop in chip temperature.
- Solve the design problem: how much airflow keeps a chip below its limit?

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A 20 W chip sits on 0.2 mm of paste (k = 3 W/(m K)) and a 3 mm aluminium base (k = 200 W/(m K)), both over 4 cm^2. Air with h = 50 W/(m^2 K) cools 100 cm^2 of fins at 25 C. Find the chip temperature and the temperature at each interface.

1. ______________________________  (hint: R_paste = 0.0002 / (3 * 0.0004) = 0.1667 K/W....)
2. ______________________________  (hint: R_base = 0.003 / (200 * 0.0004) = 0.0375 K/W....)
3. ______________________________  (hint: R_air = 1 / (50 * 0.01) = 2.0000 K/W. R_total = 0.1667 + 0.0375 + 2.00...)
4. ______________________________  (hint: T_chip = 25 + 20 * 2.2042 = 69.08 C....)
5. ______________________________  (hint: Drops: paste 20 * 0.1667 = 3.33 K (chip 69.08 C to 65.75 C), base 20 *...)
6. ______________________________  (hint: Sanity check: the drops 3.33 + 0.75 + 40 = 44.08 K add up to 69.08 - 2...)

Final answer: ____________________

## Questions
**A. Conceptual.** The thermal paste is only 0.2 mm thick and the base is 3 mm thick, yet the air film has far more resistance than either. Why?

Answer: ______________________________________________


**B. Numerical.** A 15 W chip sits on the same paste and a 4 mm copper base (k = 400), with h = 40 W/(m^2 K) on 100 cm^2 of fins. Find the chip temperature.

Answer: ______________________________________________


**C. Graph and simulation interpretation.** On the airflow graph for 10, 20 and 30 W, which of those chips stay below 85 C at h = 50 W/(m^2 K)? Roughly where does the 30 W curve cross 85 C?

Answer: ______________________________________________


**D. Design and optimisation challenge.** Design: a 30 W chip must stay at or below 85 C with the 3 mm aluminium base and h = 50. (a) Find the smallest h that works. (b) Would switching to a copper base (k = 400) be enough instead? (c) Suggest a design and a trade-off.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
