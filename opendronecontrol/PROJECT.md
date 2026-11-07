# Project form (Hello FOSS)

**Project name:** opendronecontrol

**Short description:** Learn how a drone hovers: thrust, feedback and PID altitude and attitude control of a quadrotor, from scratch in 3 sessions.

**Full description:** opendronecontrol is a beginner-friendly learning repo about how multicopters fly. In three short sessions you go from thrust and weight (rotor thrust grows with the square of its speed, the hover speed, the thrust-to-weight ratio, and why a fixed throttle drifts as soon as the mass is wrong), to a PID altitude-hold controller whose overshoot, steady-state error and stability you predict with the mass-spring-damper formulas and check in a step-by-step simulation, to a planar quadrotor flown by a cascaded controller: a position loop that asks for a tilt, an attitude loop that makes it, a mixer, tilt compensation and motor lag with its stability limit. You also tune the attitude loop of a camera drone against settling-time, tilt and safety-margin requirements. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target and a roadmap show where the community can take it next (rate loop, wind, 3-D dynamics, state estimation, a waypoint mission). All models are simplified teaching models, not flight-controller design tools.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/opendronecontrol
