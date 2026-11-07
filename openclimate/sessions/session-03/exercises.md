# Coding tasks: Session 3

1. **Easy.** Run `run_linear_model(lambda _: F2X, lambda_for_ecs(3.0), 50.0, dt=d)` for d = 2, 1, 0.1 and 0.01 years and compare the warming at year 10 with `step_response`. What happens to the error each time dt shrinks ten times? Try dt = 20: what goes wrong, and why (hint: compare dt with 2 tau)?
2. **Stretch.** Add a second, deep ocean box: C_d dTd/dt = gamma (T - Td), and subtract gamma (T - Td) from the surface equation. With C_d = 100 W yr/(m2 K) and gamma = 0.7 W/(m2 K), show that the warming at CO2 doubling (1 %/yr) drops below the one-box value.
3. **Explain in your own words.** Explain why a 1 percent per year rise in CO2 gives a forcing that grows in a straight line with time.

Not sure where to start? Change one number in `lesson.py`, predict what happens, then run it.
