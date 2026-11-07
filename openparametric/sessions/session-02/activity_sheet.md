# Activity sheet: openparametric, Session 2: When two rules disagree the stricter one wins: strength, stiffness and material

Name: ____________________   Date: ____________

**Objectives**

- Write the strength rule and the stiffness rule for a cantilever plate and solve each for the thickness.
- Take the larger thickness, round up to a plate that is sold, and check the stress and the sag.
- Find the critical length at which the governing rule changes.
- Run the same rules for two materials and choose the lightest, and check the deflection formula by numerical integration.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A bracket 40 mm wide carries 500 N at 200 mm from the wall and may sag at most 1.0 mm. Take steel with a safety factor of 1.5. Find the thickness from each rule, the plate that is sold, the mass, and the stress and sag of that plate. Then do the same for aluminium.

1. ______________________________  (hint: Allowable stress: 235 / 1.5 = 156.7 MPa. Strength: t = sqrt(6 x 500...)
2. ______________________________  (hint: Stiffness: t = (4 x 500 x 200^3 / (210 000 x 40 x 1.0))^(1/3) = 12....)
3. ______________________________  (hint: The next plate that is sold is 15 mm. Mass: 40 x 15 x 200 x 7850 x...)
4. ______________________________  (hint: Check the plate: stress 6 x 500 x 200 / (40 x 15^2) = 67 MPa (below...)
5. ______________________________  (hint: Aluminium: strength gives 9.68 mm and stiffness gives 17.96 mm (E i...)
6. ______________________________  (hint: The lightest is aluminium: 0.432 kg against 0.942 kg, even though i...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the governing rule change from strength to stiffness when the bracket gets longer? Show it for the steel bracket at L = 100 mm and L = 200 mm.

Answer: ______________________________________________

**B. Numerical.** For the steel bracket (F = 500 N, L = 200 mm, b = 40 mm, at most 1.0 mm sag), find the stress and the sag if a 12 mm plate is used instead of the 15 mm plate. Does it pass?

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the graph of thickness against length, the two curves cross at about 125 mm. By what factor does the required thickness grow when the length doubles from 125 mm to 250 mm?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: a bracket must carry 1000 N at 150 mm, 40 mm wide, with at most 3.0 mm of sag. Find the plate for steel and for aluminium, say which governs, and which bracket is lighter and by how many times.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
