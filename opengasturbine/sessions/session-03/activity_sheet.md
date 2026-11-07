# Activity sheet: opengasturbine, Session 3: A turbojet with real losses: thrust, fuel use and validation

Name: ____________________   Date: ____________

**Objectives**

- Build the turbojet state by state with a compressor, a turbine and a nozzle that each have an efficiency.
- Compute the exit speed, the specific thrust, the fuel per kg of air and the thrust specific fuel consumption (TSFC).
- Validate the model against the ideal cycle of Session 2 and against the energy balance of the whole engine.
- Explain how each loss and the turbine inlet temperature change the thrust and the fuel use.

## Before you start: predict
In your own words, what do you think will happen when you change the main slider in the live app?

______________________________________________________________

## Worked example (fill in as you go)
A static turbojet takes in air at T1 = 288 K. The pressure ratio is 10, the turbine inlet temperature is T3 = 1400 K and the efficiencies are eta_c = 0.85, eta_t = 0.90 and eta_n = 0.95. Find the specific thrust, the TSFC and, for 20 kg/s of air, the thrust and the fuel flow.

1. ______________________________  (hint: T2 = 288 x [1 + (1.9307 - 1) / 0.85] = 603.3 K.)
2. ______________________________  (hint: T4 = 1400 - (603.3 - 288) = 1084.7 K.)
3. ______________________________  (hint: (p4 / p3)^K = 1 - 315.3 / (0.90 x 1400) = 0.7497, so p4 / p3 = 0.36...)
4. ______________________________  (hint: T5s = 1084.7 x (1 / 3.65)^0.2857 = 749.3 K, so the nozzle drop is 0...)
5. ______________________________  (hint: v_e = sqrt(2 x 1005 x 318.6) = 800 m/s, which is the specific thrus...)
6. ______________________________  (hint: q_in = 1005 x (1400 - 603.3) = 800.6 kJ/kg, so fuel/air = 800.6e3 /...)
7. ______________________________  (hint: For 20 kg/s: thrust = 20 x 800 = 16.0 kN and fuel = 20 x 0.0190 = 0...)

Final answer: ____________________

## Questions
**A. Conceptual.** Why does a jet engine need a nozzle, while the gas turbine of a power station does not?

Answer: ______________________________________________

**B. Numerical.** A static turbojet has T1 = 300 K, r = 12, T3 = 1300 K and the efficiencies eta_c = 0.85, eta_t = 0.90 and eta_n = 0.95. Find the exit speed and the TSFC.

Answer: ______________________________________________

**C. Graph and simulation interpretation.** On the thrust graph at T3 = 1400 K the curve is almost flat between r = 8 and r = 14. Why does the thrust not keep rising with pressure ratio, while the TSFC keeps falling?

Answer: ______________________________________________

**D. Design and optimisation challenge.** Design: reach a specific thrust of at least 900 N s/kg and a TSFC of at most 24 g/(kN s), with the efficiencies 0.85, 0.90 and 0.95. Find a pressure ratio and a turbine inlet temperature that work, and say what limits the design in practice.

Answer: ______________________________________________

## Self-check
- [ ] I can explain the key idea to a friend
- [ ] My checkpoint printed PASS
- [ ] I tried one change of my own and wrote what happened: ____________________
