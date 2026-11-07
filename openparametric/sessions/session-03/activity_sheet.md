# Activity sheet: openparametric, Session 3: Rules as data: ordering them, catching loops and drawing the part

Name: ____________________   Date: ____________

**Objectives**

- Store rules as text and find the names each rule depends on.
- Sort the rules into an order in which they can be evaluated, and explain why the order of writing does not matter.
- Detect circular rules, unknown names and unsafe expressions and report them clearly.
- Generate a bolted flange from three inputs and check the drawing against the formula by measuring its area.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A flange must carry 60 kN with M12 bolts around a pipe of 114.3 mm outside diameter. Apply the rules in a valid order and find the number of bolts, the bolt circle, the outside diameter, the thickness and the mass.

1. ______________________________  (hint: Order found by the engine: t -> area_b -> f_bolt -> n_min -> n -> p...)
2. ______________________________  (hint: Bolt: the stress area is pi / 4 (12 - 0.9382 x 1.75)^2 = 84.3 mm2,...)
3. ______________________________  (hint: Number of bolts: 60 / 27.0 = 2.22, rounded up to 3, then to an even...)
4. ______________________________  (hint: Bolt circle: the larger of 114.3 + 4 x 12 = 162.3 mm and 4 x 2.5 x...)
5. ______________________________  (hint: Thickness: 0.8 x 12 + 0.02 x 114.3 + 0.04 x 60 = 14.3, rounded up t...)
6. ______________________________  (hint: Mass: area = pi / 4 (198.3^2 - 114.3^2) - 4 x pi / 4 x 14^2 = 20008...)
7. ______________________________  (hint: Check: counting grid points in the drawing gives 20005 mm2, within...)

Final answer: ____________________

## Questions
**A. Conceptual.** The flange rules are written with 'mass' first and 'hole' last. Why can the engine still evaluate them, and in what order does it do it?

Answer: ______________________________________________

**B. Numerical.** By hand, find the flange for 150 kN with M16 bolts and the 114.3 mm pipe: the number of bolts, the bolt circle, the thickness and the mass.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** What does the engine do with the rules a = b + 1, b = c * 2, c = a - 3? And with a rule 'x = y + 1' when nothing defines y? Why is stopping better than trying anyway?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: the load is 300 kN on the 114.3 mm pipe. Which bolt size from M8 to M24 gives the lightest flange, and which rule decides the bolt circle for M8?

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
