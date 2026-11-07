# Project form (Hello FOSS)

**Project name:** openrobotarm

**Short description:** Learn forward and inverse kinematics for a pick-and-place robot arm: workspace, joint limits, Jacobians and singularities, in 3 sessions.

**Full description:** openrobotarm is a beginner-friendly learning repo about how a robot arm knows where its gripper is, and how to choose joint angles that put it where we want. In three short sessions you go from a 3-link planar arm and its cumulative joint angles, to the workspace (measured by sampling a grid), the effect of joint limits and the spare freedom of a redundant arm, to a numerical inverse kinematics solver built on the Jacobian. The solver is damped so it survives singularities, follows a smooth straight-line path with null-space joint-limit avoidance, and is checked against forward kinematics to better than a micrometre. Every session follows the same six steps (real-world problem, theory, visual explanation, interactive simulation, worked example, assessment), and has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next, such as whole-arm collision checks, speed limits, calibration and a 3D six-joint arm. Educational model only: not a tool for programming or certifying a real robot.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openrobotarm
