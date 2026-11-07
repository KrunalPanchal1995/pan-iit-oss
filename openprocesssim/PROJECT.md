# Project form (Hello FOSS)

**Project name:** openprocesssim

**Short description:** Build a learning-scale process simulator with mixer, heat exchanger, reactor and flash blocks and a recycle loop, in 3 sessions.

**Full description:** openprocesssim is a beginner-friendly learning repo about how a flowsheet simulator is built, in the spirit of commercial flowsheet tools but at learning scale. In three short sessions you go from a plant drawn as boxes and pipes whose rules are solved together, to a stream object and unit blocks (mixer, splitter, heater, pump, valve) with Antoine vapour pressures, Raoult's law, bubble and dew points and the Rachford-Rice flash, to a small sequential-modular engine: a flowsheet is a graph of blocks, the engine finds an order, cuts the recycle with a tear stream, iterates by successive substitution and Wegstein acceleration, checks degrees of freedom, reports mass and energy closure, and shows an honest failure (an infeasible recycle, and an ethanol-benzene mixture where Raoult's law fails). Every session has a lesson script, a Colab notebook, a live slider app and a checkpoint that prints PASS or FAIL. Thermodynamics is ideal only, with rounded textbook constants; the result is a teaching model, not a design tool, and it is not compatible with any commercial package. The repo is intentionally incomplete: a Target animation and a roadmap show where the community can take it next.

**Technologies (comma-separated):** Python, NumPy, Matplotlib, JavaScript, LaTeX

**Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss/tree/main/openprocesssim
