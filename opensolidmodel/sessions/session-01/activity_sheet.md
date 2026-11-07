# Activity sheet: opensolidmodel, Session 1: A part is a recipe, not a shape: parameters, equations and a rebuild

Name: ____________________   Date: ____________

**Objectives**

- Say what a CAD program stores instead of a picture: parameters, equations and a list of features.
- Evaluate an equation between parameters safely, without running arbitrary code.
- Rebuild a part after one parameter changes and read off its volume, mass and number of faces.
- Explain why tying one dimension to another by an equation keeps a part consistent when it is edited.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
The customer wants 6 holes instead of 4 and a width of 140 mm, with the same hole ratio of 0.4, depth 40 mm and thickness 8 mm. Find the spacing, the hole diameter, the volume and the mass of the new plate.

1. ______________________________  (hint: Spacing: s = w / (n + 1) = 140 / 7 = 20.0 mm.)
2. ______________________________  (hint: Diameter: dia = 0.4 x 20.0 = 8.0 mm. The holes fit: 8.0 is smaller...)
3. ______________________________  (hint: Block: 140 x 40 x 8 = 44800 mm3.)
4. ______________________________  (hint: Holes: 6 x (pi / 4) x 8.0^2 x 8 = 2413 mm3.)
5. ______________________________  (hint: Volume: 44800 - 2413 = 42387 mm3, which is 42.39 cm3.)
6. ______________________________  (hint: Mass: 7850 x 42387 x 1e-9 = 0.333 kg.)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does the recipe store the hole spacing and the diameter as equations instead of as two numbers?

Answer: ______________________________________________

**B. Numerical.** A smaller plate has w = 100 mm, d = 30 mm, h = 6 mm, 3 holes and a ratio of 0.5. Find the spacing, the hole diameter, the volume and the mass.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the graph of mass against the number of holes (ratio 0.4), the curve is lowest at one hole and rises afterwards. Does a plate with more holes weigh less? Explain with the equation.

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: the customer wants the 120 x 40 x 8 mm plate with 4 holes to weigh at most 0.28 kg. Find the smallest hole ratio, to two decimals, and the hole diameter it gives.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
