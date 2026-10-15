# Openfirststeps (PAN IIT OSS)

**One small open-source project for every real-world goal: learn the path in three sessions, then build the rest yourself.**

Openfirststeps is the umbrella for a family of small teaching repositories made for the [Hello FOSS](https://hellofoss.tech-iitb.org/projects) program (PAN IIT OSS). Each repository has one end goal, for example *reading a flame's soot from video* or *designing a stiff bracket with the least material*. You learn the first three steps (Sessions 1 to 3) with interactive apps that run in your browser, and you see a finished **Target** (animation, figure, playground) so you know what is possible. The code behind the Target stays private on purpose: the repo shows the **path**, you do the building.

## How every repository is laid out

- `README.md`: what the goal is, quick start, the three sessions, the roadmap.
- `sessions/session-01..03/`: lesson, notebook, browser app, exercises, checkpoint (PASS or FAIL).
- `promo/`: the Target media and the roadmap from Session 4 onwards (path only).
- `docs/explainer.pdf`: a short illustrated explainer (built by GitHub Actions).
- `CONTRIBUTING.md`: a git guide for people who have never used git before.
- Open issues labelled `good first issue`, `beginner`, `intermediate`, `advanced`.

## Project form (for Hello FOSS)

- **Project name:** Openfirststeps
- **Short description:** Learn any topic in three sessions. Small open repos, each with a browser app, a finished Target to aim for, and a path to go further.
- **Full description:** Openfirststeps is a collection of 259 small teaching repositories, one per real-world end goal, from mechanics, fluids and combustion to data science, climate, game development, cybersecurity and life skills. Each repo teaches Sessions 1 to 3 (60 to 90 minutes each) with interactive apps and checkpoints, shows a Target to aim for, and leaves a roadmap and beginner-friendly issues so students can extend it.
- **Technologies:** Python, JavaScript, HTML, LaTeX, Shell
- **Repository link:** https://github.com/KrunalPanchal1995/pan-iit-oss
- **Issues link:** https://github.com/KrunalPanchal1995/pan-iit-oss/issues
- **Docs link:** https://github.com/KrunalPanchal1995/pan-iit-oss/blob/main/README.md

## Status

259 repositories planned, 132 built and verified, 90 published so far. Published ones live at `https://github.com/KrunalPanchal1995/<name>` and their apps at `https://krunalpanchal1995.github.io/<name>/`.

## All projects


### Everyday Life and Practical Knowledge

- **[openhousehold](https://github.com/KrunalPanchal1995/openhousehold)** (live; middle school to higher secondary): Predict a household's daily electricity use and bill, and see where the energy goes. Homes use a large share of a country's electricity, and bills are easier to cut once you can see which appliance uses what.
- **[openfridge](https://github.com/KrunalPanchal1995/openfridge)** (live; middle school to higher secondary): Explain and size the refrigerator cycle that keeps food cold. A refrigerator moves heat from a cold space to a warm room, and the same cycle runs air conditioners and heat pumps.
- **[openpressurecooker](https://github.com/KrunalPanchal1995/openpressurecooker)** (live; middle school to higher secondary): Show why a pressure cooker cooks faster using pressure and boiling point. Raising the pressure raises the boiling point of water, so food cooks faster and uses less fuel.
- **[openelevator](https://github.com/KrunalPanchal1995/openelevator)** (live; middle school to higher secondary): Design an elevator ride that is quick and comfortable (counterweight, motor, jerk). An elevator must be quick and still comfortable, which is a trade-off between speed, acceleration and jerk.
- **[opentrafficsignal](https://github.com/KrunalPanchal1995/opentrafficsignal)** (live; middle school to higher secondary): Time a traffic-signal junction to cut waiting and queues. Signal timing decides how long people wait and how long queues grow at a junction.
- **[opengps](https://github.com/KrunalPanchal1995/opengps)** (live; middle school to higher secondary): Fix a position with GPS trilateration and a relativity correction. A position fix comes from timing signals from several satellites, and even tiny clock errors matter.
- **[openqrcode](https://github.com/KrunalPanchal1995/openqrcode)** (live; middle school to higher secondary): Read a damaged QR code using error-correcting codes. Error-correcting codes let a damaged code still be read, which is the same idea that protects data everywhere.
- **[openupi](https://github.com/KrunalPanchal1995/openupi)** (live; middle school to higher secondary): Trace a digital payment from tap to bank balance, and spot where fraud checks sit. A digital payment is a chain of checks between devices, banks and networks, and each step can fail or be attacked.

### Mathematics and Visual Problem-Solving

- **[openunits](https://github.com/KrunalPanchal1995/openunits)** (live; secondary to diploma/undergrad): Catch the Mars Climate Orbiter units bug before it flies. A number without a unit is not an answer, and unit mistakes have destroyed real spacecraft.
- **[opencalculus](https://github.com/KrunalPanchal1995/opencalculus)** (live; secondary to diploma/undergrad): See derivatives and integrals as slopes and areas on a moving car's graph. Slopes and areas on a graph are the language for rates of change and totals in every science.
- **[openvectors](https://github.com/KrunalPanchal1995/openvectors)** (live; secondary to diploma/undergrad): Add forces and velocities as arrows to land a boat across a river. Quantities with direction, like force and velocity, add as arrows, not as plain numbers.
- **[openheights](https://github.com/KrunalPanchal1995/openheights)** (live; secondary to diploma/undergrad): Measure the height of a tower or tree with trigonometry and a phone. Trigonometry lets you measure what you cannot reach, such as the height of a tower.
- **[openfractal](https://github.com/KrunalPanchal1995/openfractal)** (live; secondary to diploma/undergrad): Render a Mandelbrot and Julia zoom video from complex numbers. Simple rules on complex numbers produce endless detail, a good way to see iteration and chaos.
- **[openvfx](https://github.com/KrunalPanchal1995/openvfx)** (live; secondary to diploma/undergrad): Bend a character arm for film VFX using matrix transformations and skinning. Matrices move every point of a shape at once, which is how characters bend in films and games.
- **[openmapproject](https://github.com/KrunalPanchal1995/openmapproject)** (live; secondary to diploma/undergrad): Choose a map projection by measuring its distortion. A flat map must distort the round Earth, and the choice of projection decides what is kept true.
- **[openodds](https://github.com/KrunalPanchal1995/openodds)** (live; secondary to diploma/undergrad): Estimate the odds in dice, cards and lotteries by counting and simulation. Counting and simulation turn vague chance into numbers you can reason with.
- **[openfloat](https://github.com/KrunalPanchal1995/openfloat)** (live; secondary to diploma/undergrad): Learn from floating-point disasters like Patriot and Ariane 5. Computers store numbers with limited precision, and tiny errors can grow into disasters.

### Physics and the Science of Motion

- **[openmotion](https://github.com/KrunalPanchal1995/openmotion)** (live; secondary to diploma/undergrad): Read position, velocity and acceleration graphs of a moving body. Reading position, velocity and acceleration graphs is the base skill of mechanics.
- **[openincline](https://github.com/KrunalPanchal1995/openincline)** (live; secondary to diploma/undergrad): Find the angle where a block starts to slide on a ramp. Whether a block slides depends on a balance between its weight along the slope and friction.
- **[openprojectile](https://github.com/KrunalPanchal1995/openprojectile)** (live; secondary to diploma/undergrad): Plan a cricket shot with air drag. Anything thrown or launched follows a curved path that depends on speed, angle and air drag.
- **[opencrashsim](https://github.com/KrunalPanchal1995/opencrashsim)** (live; secondary to diploma/undergrad): Design crumple zones with momentum and energy balance. Crumple zones absorb energy over a longer time so that the force on people is lower.
- **[openoscillator](https://github.com/KrunalPanchal1995/openoscillator)** (live; secondary to diploma/undergrad): Tune a spring-mass or pendulum to a target period with damping. Springs and pendulums oscillate at natural frequencies that engineers must tune or avoid.
- **[openchaos](https://github.com/KrunalPanchal1995/openchaos)** (live; secondary to diploma/undergrad): See chaos in a double pendulum. A simple double pendulum is unpredictable over time, which shows the limits of forecasting.
- **[opengyro](https://github.com/KrunalPanchal1995/opengyro)** (live; secondary to diploma/undergrad): Explain a spinning top's precession. A spinning body resists changes of direction, which explains tops, bicycles and gyroscopes.
- **[opencentripetal](https://github.com/KrunalPanchal1995/opencentripetal)** (live; secondary to diploma/undergrad): Design a banked curve or roundabout that grips at speed. A turning vehicle needs an inward force, and banking and friction supply it.

### Heat, Thermodynamics and Fluid Mechanics

- **[openheatspread](https://github.com/KrunalPanchal1995/openheatspread)** (live; higher secondary to diploma/undergrad): Predict laptop hot spots with heat diffusion. Electronics fail when heat cannot escape, so predicting hot spots is part of design.
- **[openengine](https://github.com/KrunalPanchal1995/openengine)** (live; higher secondary to diploma/undergrad): Compare Otto and Diesel cycle efficiency on P-V diagrams. Heat engines turn fuel into work, and their efficiency is limited by physics.
- **[openheatpump](https://github.com/KrunalPanchal1995/openheatpump)** (live; higher secondary to diploma/undergrad): Size a heat pump and see why it beats a heater. A heat pump moves heat instead of making it, so it can deliver several units of heat per unit of electricity.
- **[openpipeflow](https://github.com/KrunalPanchal1995/openpipeflow)** (live; higher secondary to diploma/undergrad): Choose a pipe size that meets flow needs within a pump budget. Friction in pipes costs pumping energy, and pipe size decides the cost of moving water.
- **[openhydraulics](https://github.com/KrunalPanchal1995/openhydraulics)** (live; higher secondary to diploma/undergrad): Lift a car with a small force using Pascal's law. Fluids transmit pressure, so a small force on a small piston can lift a car.
- **[openbuoyancy](https://github.com/KrunalPanchal1995/openbuoyancy)** (live; higher secondary to diploma/undergrad): Decide whether a ship floats and stays upright using Archimedes' principle. Whether a ship floats and stays upright follows from displaced water and the position of its centre of gravity.
- **[openboiling](https://github.com/KrunalPanchal1995/openboiling)** (live; higher secondary to diploma/undergrad): Model boiling and bubble growth on a heated surface. Boiling moves large amounts of heat, and bubble behaviour sets how well a surface can cool.

### Electricity, Magnetism and Electronics

- **[openohm](https://github.com/KrunalPanchal1995/openohm)** (live; secondary to diploma/undergrad): Design a resistor circuit to a power and current limit with Ohm's law. Voltage, current and resistance link every electric circuit, and power limits decide what is safe.
- **[opencircuitlab](https://github.com/KrunalPanchal1995/opencircuitlab)** (live; secondary to diploma/undergrad): Build series and parallel circuits and solve them with Kirchhoff's laws. Series and parallel networks, solved with Kirchhoff's laws, are the basis of all circuit analysis.
- **[openrcfilter](https://github.com/KrunalPanchal1995/openrcfilter)** (live; secondary to diploma/undergrad): Design a filter that removes noise from a sensor signal. A filter keeps the signal you want and removes noise, using only a resistor and a capacitor.
- **`openledcontrol`** (built; secondary to diploma/undergrad): Build a light-activated LED controller with a sensor and transistor switch. A transistor lets a tiny sensor signal switch a larger load, the idea behind automatic lights.
- **[openemwave](https://github.com/KrunalPanchal1995/openemwave)** (live; secondary to diploma/undergrad): Watch an antenna radiate and visualise electric and magnetic fields. Accelerating charges radiate waves, which is how radios, mobiles and radar work.
- **[openinduction](https://github.com/KrunalPanchal1995/openinduction)** (live; secondary to diploma/undergrad): Explain how a transformer and a generator work from Faraday's law. A changing magnetic field makes a voltage, the principle behind generators and transformers.
- **[opendcmotor](https://github.com/KrunalPanchal1995/opendcmotor)** (live; secondary to diploma/undergrad): Read and use a DC motor's torque-speed curve for a drive. A motor's torque-speed curve tells you what load it can drive and how fast.

### Chemistry and Materials Science

- **[openmole](https://github.com/KrunalPanchal1995/openmole)** (live; secondary to diploma/undergrad): Balance a reaction and compute how much reagent you need (stoichiometry). Stoichiometry tells you how much of each substance a reaction needs and makes.
- **[openphtitration](https://github.com/KrunalPanchal1995/openphtitration)** (live; secondary to diploma/undergrad): Find an unknown acid concentration from a titration curve. A titration curve reveals the unknown concentration of an acid or base.
- **[openbatterycell](https://github.com/KrunalPanchal1995/openbatterycell)** (live; secondary to diploma/undergrad): Build and size an electrochemical cell for a target voltage. An electrochemical cell turns a chemical reaction into voltage, and its design sets capacity and cost.
- **[openreactionrate](https://github.com/KrunalPanchal1995/openreactionrate)** (live; secondary to diploma/undergrad): Write reaction networks as ODEs and see how catalysts speed them. Reaction networks written as equations show which steps are fast, slow or sped up by a catalyst.
- **[openarrhenius](https://github.com/KrunalPanchal1995/openarrhenius)** (live; secondary to diploma/undergrad): Fit rate constants with uncertainty using the Arrhenius law. Reaction rates depend steeply on temperature, and fitting them with uncertainty is the base of kinetics modelling.
- **[openignition](https://github.com/KrunalPanchal1995/openignition)** (live; secondary to diploma/undergrad): Predict hydrogen-oxygen ignition delay. Ignition delay decides whether a fuel burns safely and efficiently in an engine or furnace.
- **[openstressstrain](https://github.com/KrunalPanchal1995/openstressstrain)** (live; secondary to diploma/undergrad): Read a stress-strain curve to pick a safe material. A stress-strain curve shows how a material stretches, yields and breaks, and so which one to pick.
- **[openphasediagram](https://github.com/KrunalPanchal1995/openphasediagram)** (live; secondary to diploma/undergrad): Read a phase diagram to choose an alloy and heat treatment. A phase diagram maps which phases a mixture forms, guiding alloys and heat treatment.

### Biology, Human Body and Health Science

- **[openheartflow](https://github.com/KrunalPanchal1995/openheartflow)** (live; secondary to diploma/undergrad): Model blood circulation as a pump and pipes to see how blood pressure arises. The circulatory system behaves like a pump and a network of pipes, which explains blood pressure.
- **[openneuron](https://github.com/KrunalPanchal1995/openneuron)** (live; secondary to diploma/undergrad): Simulate a nerve cell firing and how signals travel. Nerve cells fire when a voltage threshold is crossed, which is how signals travel in the body.
- **[opengenetics](https://github.com/KrunalPanchal1995/opengenetics)** (live; secondary to diploma/undergrad): Predict inheritance of traits with Punnett squares and simulation. Inheritance follows simple probability rules that predict how traits appear in offspring.
- **[openepidemic](https://github.com/KrunalPanchal1995/openepidemic)** (live; secondary to diploma/undergrad): Fit an SIR model to outbreak data and test vaccination (general education only). Simple outbreak models show how contact rates and vaccination change the course of a disease.
- **`opennutrition`** (built; secondary to diploma/undergrad): Balance food energy against activity (general education, not medical advice). Food energy and activity balance explain weight change in general terms.

### Civil Engineering and Construction

- **[openbeam](https://github.com/KrunalPanchal1995/openbeam)** (live; diploma/undergrad to advanced undergrad): Meet a deflection limit with the lightest beam (shear, moment, deflection). Beams carry loads by bending, and depth is the cheapest way to make them stiff.
- **[opentruss](https://github.com/KrunalPanchal1995/opentruss)** (live; diploma/undergrad to advanced undergrad): Compute member forces in a truss bridge. A truss carries load through members in tension and compression, using little material.
- **`openfoundation`** (built; diploma/undergrad to advanced undergrad): Choose a foundation size from soil bearing capacity. A foundation must spread the building load so the soil is not overloaded.
- **[openbuildingsway](https://github.com/KrunalPanchal1995/openbuildingsway)** (live; diploma/undergrad to advanced undergrad): Predict building sway in an earthquake with multi-DOF vibration. Tall buildings sway in earthquakes and wind, and designers tune their natural frequencies.
- **[openretainingwall](https://github.com/KrunalPanchal1995/openretainingwall)** (live; diploma/undergrad to advanced undergrad): Check a retaining wall against sliding and overturning. A retaining wall must resist soil pressure without sliding or overturning.
- **[opensurvey](https://github.com/KrunalPanchal1995/opensurvey)** (live; diploma/undergrad to advanced undergrad): Level a site and measure distances with trigonometry and a total station model. Levelling and distance measurement with trigonometry set out every construction site.

### Mechanical Engineering

- **[opengears](https://github.com/KrunalPanchal1995/opengears)** (live; diploma/undergrad to advanced undergrad): Design a gearbox train to hit a target ratio and torque. Gear trains trade speed for torque and set direction, in every machine with a motor.
- **[openlinkage](https://github.com/KrunalPanchal1995/openlinkage)** (live; diploma/undergrad to advanced undergrad): Design a four-bar walking machine (Strandbeest style). Linkages turn one simple motion into a useful path, such as walking legs or wipers.
- **[opentolerance](https://github.com/KrunalPanchal1995/opentolerance)** (live; diploma/undergrad to advanced undergrad): Choose fits and tolerances so parts assemble and still work. Parts must fit together and still work, which is decided by tolerances and fits.
- **[openfatigue](https://github.com/KrunalPanchal1995/openfatigue)** (live; diploma/undergrad to advanced undergrad): Predict how many load cycles a part survives (S-N curve). Repeated loads can break a part that would survive one large load, so life is counted in cycles.
- **[opencncpath](https://github.com/KrunalPanchal1995/opencncpath)** (live; diploma/undergrad to advanced undergrad): Turn a drawing into a CNC toolpath. A CNC machine follows a toolpath made from a drawing, and the path sets cost and quality.
- **[opensculpt](https://github.com/KrunalPanchal1995/opensculpt)** (live; diploma/undergrad to advanced undergrad): Model a mug and other CAD parts with signed distance functions. Solid shapes can be described by simple distance functions, which makes CAD and graphics flexible.

### Computer Science, Programming and Software

- **[openbinary](https://github.com/KrunalPanchal1995/openbinary)** (live; secondary to diploma/undergrad): Build an adder from logic gates and see how computers count. Computers count in binary and compute with logic gates built from switches.
- **`opensorting`** (built; secondary to diploma/undergrad): Compare sorting algorithms by swaps, comparisons and time. Different algorithms do the same job at very different costs as data grows.
- **[openpacket](https://github.com/KrunalPanchal1995/openpacket)** (live; secondary to diploma/undergrad): Follow a packet across the internet from browser to server. Data travels the internet in small packets, routed hop by hop.
- **[opensql](https://github.com/KrunalPanchal1995/opensql)** (live; secondary to diploma/undergrad): Query a small database and design its tables. Relational databases store facts in tables that you question with simple queries.
- **[opencrypto](https://github.com/KrunalPanchal1995/opencrypto)** (live; secondary to diploma/undergrad): Break and then fix a toy cipher, and learn why keys matter. Keys, not secrecy of the method, protect messages, and weak ciphers are easy to break.

### Artificial Intelligence, Data Science and Robotics

- **[openneuralnet](https://github.com/KrunalPanchal1995/openneuralnet)** (live; higher secondary to advanced undergrad): Train a neural network from scratch and watch backpropagation. A neural network learns by adjusting weights to reduce error, using backpropagation.
- **[openregression](https://github.com/KrunalPanchal1995/openregression)** (live; higher secondary to advanced undergrad): Predict crop yield with regression and spot overfitting. Fitting a line to data predicts new values, but too flexible a model memorises noise.
- **`openclassifier`** (built; higher secondary to advanced undergrad): Draw decision boundaries and read a confusion matrix. A classifier draws a boundary between categories, and a confusion matrix shows its mistakes.
- **`openrecommend`** (built; higher secondary to advanced undergrad): Build a recommender that suggests what you might like. Recommenders find items similar to what you liked using patterns in many users' choices.
- **`openneuralode`** (built; higher secondary to advanced undergrad): Learn dynamics from data with neural ODEs. A neural network can learn the rate of change of a system and then simulate it forward.
- **`openpinn`** (built; higher secondary to advanced undergrad): Solve the heat equation with a physics-informed network. A network trained with a physical law as part of its loss can solve equations with little data.
- **`opensurrogate`** (built; higher secondary to advanced undergrad): Build a neural surrogate for stiff kinetics. A fast learned stand-in for a slow simulation makes design and uncertainty studies affordable.
- **`opensymbolic`** (built; higher secondary to advanced undergrad): Rediscover physical laws with symbolic regression. Symbolic regression searches for a formula that fits data, so the result can be read and trusted.
- **`openrobotarm`** (built; higher secondary to advanced undergrad): Forward and inverse kinematics for a pick-and-place arm. Inverse kinematics finds the joint angles that put a robot's hand where it is needed.
- **`openpathplanner`** (built; higher secondary to advanced undergrad): Plan routes for a warehouse robot with A* and RRT. A robot must find a route that avoids obstacles, with algorithms like A* and RRT.

### Electrical Power and Renewable Energy

- **[opensolarbattery](https://github.com/KrunalPanchal1995/opensolarbattery)** (live; diploma/undergrad to advanced undergrad): Size a rooftop solar and battery system for a home. Matching solar output, battery size and demand decides cost and reliability of a home system.
- **`opengrid`** (built; diploma/undergrad to advanced undergrad): See how the grid balances supply and demand, and what power factor does. The grid must balance supply and demand every second, and power factor changes the load on lines.
- **`openwindturbine`** (built; diploma/undergrad to advanced undergrad): Estimate wind-turbine power from the wind and blade size. A turbine's power rises with the cube of wind speed, so siting and size matter a great deal.
- **`openmppt`** (built; diploma/undergrad to advanced undergrad): Track the maximum power point of a solar panel. A solar panel gives the most power at one operating point, which a controller keeps tracking.
- **`openhydrogen`** (built; diploma/undergrad to advanced undergrad): Fill a hydrogen tank and use a fuel cell, thermodynamics first. Hydrogen stores and carries energy, and filling and using it involves heat and pressure.

### Chemical, Environmental and Process Engineering

- **`openmassbalance`** (built; diploma/undergrad to advanced undergrad): Close the mass and energy balance of a simple process. What goes into a process must come out or accumulate, and checking that finds errors.
- **`openheatexchanger`** (built; diploma/undergrad to advanced undergrad): Size a heat exchanger for a target outlet temperature. A heat exchanger moves heat between fluids without mixing them, and its size sets cost.
- **`opendistillation`** (built; diploma/undergrad to advanced undergrad): Separate ethanol and water with a distillation column. Distillation separates mixtures by boiling point differences, using a column of stages.
- **`openreactor`** (built; diploma/undergrad to advanced undergrad): Design CSTR and PFR chemical reactors. The type and size of a reactor decide how much of a reactant converts to product.
- **`opendesalination`** (built; diploma/undergrad to advanced undergrad): Estimate the energy to turn seawater into drinking water. Making fresh water from seawater takes a minimum amount of energy set by physics.
- **`opengreensteel`** (built; diploma/undergrad to advanced undergrad): Decarbonise a blast furnace with hydrogen injection. Replacing carbon with hydrogen in a blast furnace could cut a large source of emissions.

### Aerospace, Automotive and Transportation

- **`openairfoil`** (built; higher secondary to advanced undergrad): Estimate airfoil lift and drag with a panel method. The shape of a wing decides its lift and drag, and therefore a plane's fuel use.
- **`openascent`** (built; higher secondary to advanced undergrad): Fly a rocket launch trajectory to orbit with staging. A rocket must climb and turn to reach orbit, and staging drops dead weight on the way.
- **`opensuspension`** (built; higher secondary to advanced undergrad): Tune a quarter-car suspension for ride comfort. A suspension trades comfort against road holding by tuning springs and dampers.
- **`opentrafficflow`** (built; higher secondary to advanced undergrad): Explain traffic jams from nothing with a car-following model. Traffic jams can start from nothing when drivers react to the car in front.
- **`opendronecontrol`** (built; higher secondary to advanced undergrad): PID hover and attitude control of a quadrotor. A multicopter hovers by controlling thrust with feedback, often a PID controller.

### Architecture, Design and Smart Buildings

- **`opendaylight`** (built; higher secondary to diploma/undergrad): Plan windows for natural daylight using the sun path. Window size and sun path decide how much natural light a room gets and how much energy it needs.
- **`opencomfort`** (built; higher secondary to diploma/undergrad): Cool a building passively with shading and ventilation. Shading and ventilation can keep a building cool without much energy.
- **`openevacuation`** (built; higher secondary to diploma/undergrad): Plan a safe evacuation from a building with crowd flow. People move like a flow, and exits and corridors set how quickly a building can be emptied.

### Economics, Business, Finance and Entrepreneurship

- **`opensupplydemand`** (built; secondary to diploma/undergrad): Find the market price where supply meets demand. Price settles where what sellers offer equals what buyers want.
- **[openloan](https://github.com/KrunalPanchal1995/openloan)** (live; secondary to diploma/undergrad): Compare loan EMIs and see how interest compounds. Interest compounds, and the length and rate of a loan decide what you really pay.
- **[openbreakeven](https://github.com/KrunalPanchal1995/openbreakeven)** (live; secondary to diploma/undergrad): Find the break-even point of a small business. The break-even point is the sales level where income covers costs.
- **[openportfolio](https://github.com/KrunalPanchal1995/openportfolio)** (live; secondary to diploma/undergrad): See how diversification lowers risk in a portfolio. Spreading money over assets that do not move together lowers risk.

### Geography, Climate, Environment and Earth Science

- **[openseismo](https://github.com/KrunalPanchal1995/openseismo)** (live; secondary to diploma/undergrad): Locate an earthquake from seismograph arrivals. Arrival times of earthquake waves at several stations locate where the quake began.
- **[opennowcast](https://github.com/KrunalPanchal1995/opennowcast)** (live; secondary to diploma/undergrad): Nowcast rain by advecting radar fields. Moving the latest radar picture forward predicts rain over the next hour.
- **`openclimate`** (built; secondary to diploma/undergrad): Explain the greenhouse effect with a simple energy-balance model. A simple energy balance shows how greenhouse gases warm the Earth.
- **[openwatershed](https://github.com/KrunalPanchal1995/openwatershed)** (live; secondary to diploma/undergrad): Predict a river's flood peak from rainfall on a watershed. Rain falling on a catchment collects into a river, and the shape of the flood peak depends on the land.

### Astronomy and Space Science

- **[openorbit](https://github.com/KrunalPanchal1995/openorbit)** (live; secondary to diploma/undergrad): Plan satellite transfer orbits with Kepler's laws. Kepler's laws and transfer orbits let spacecraft reach other planets with little fuel.
- **[openseasons](https://github.com/KrunalPanchal1995/openseasons)** (live; secondary to diploma/undergrad): Explain day, night, seasons and Moon phases with geometry. The tilt of the Earth and its orbit explain day, night, seasons and Moon phases.
- **[openeclipse](https://github.com/KrunalPanchal1995/openeclipse)** (live; secondary to diploma/undergrad): Predict when and where an eclipse will be seen. Eclipses follow from the geometry of Sun, Moon and Earth and can be predicted far ahead.
- **[openexoplanet](https://github.com/KrunalPanchal1995/openexoplanet)** (live; secondary to diploma/undergrad): Find a planet around another star from a dip in starlight. A planet crossing its star dims the starlight slightly, which is how many planets are found.

### Statistics, Research and Experimental Methods

- **[openexperiment](https://github.com/KrunalPanchal1995/openexperiment)** (live; higher secondary to advanced undergrad): Design a fair experiment and calibrate a sensor. A fair experiment and a calibrated sensor are what make data worth trusting.
- **[openuncertainty](https://github.com/KrunalPanchal1995/openuncertainty)** (live; higher secondary to advanced undergrad): Propagate measurement error into a final answer. Every measurement has error, and the error carries through to the final answer.
- **`openhypothesis`** (planned; higher secondary to advanced undergrad): Run a correct A/B test and read a p-value. A test tells you whether a difference is likely real or just chance.
- **`openkalman`** (planned; higher secondary to advanced undergrad): Track a moving phone by fusing noisy sensors with a Kalman filter. A Kalman filter combines noisy sensors and a model to give a better estimate than either.

### Communication, Language and Creative Skills

- **`opencolor`** (planned; middle school to higher secondary): Build a colour palette that reads well using colour theory. Colour choices change how readable and appealing a design is.
- **`opennotetuner`** (planned; middle school to higher secondary): Build a guitar tuner with the FFT and learn how sound waves work. Sound is vibration, and the FFT finds its pitch, which is how a tuner works.
- **`openanimate`** (planned; middle school to higher secondary): Animate with the classic principles: easing, squash and stretch. Easing and squash-and-stretch make motion feel alive.
- **`opensentence`** (planned; middle school to higher secondary): Draw sentence trees to explain English grammar. Sentence trees show how words fit together, which makes grammar visible.

### Statistics, Research and Experimental Methods

- **[openstereodic](https://github.com/KrunalPanchal1995/openstereodic)** (live; higher secondary to advanced undergrad): Measure 3D surface strain from two cameras (stereo digital image correlation). Two cameras can measure how a surface deforms in 3D without touching it, which turns photos into strain maps.

### Biology, Human Body and Health Science

- **[openproteinmd](https://github.com/KrunalPanchal1995/openproteinmd)** (live; secondary to diploma/undergrad): Fold a small peptide with molecular dynamics (general education). Molecular dynamics follows atoms under forces, showing how a protein folds and moves (general education only).

### Statistics, Research and Experimental Methods

- **[openflame](https://github.com/KrunalPanchal1995/openflame)** (live; higher secondary to advanced undergrad): Measure flame height and flicker frequency from a phone video. Video of a flame holds its height and flicker frequency, which relate to fuel, size and stability.
- **[openkymo](https://github.com/KrunalPanchal1995/openkymo)** (live; higher secondary to advanced undergrad): Read flow speed off the stripe slopes of a kymograph. A kymograph turns motion over time into stripes whose slope is the speed.
- **[openabel](https://github.com/KrunalPanchal1995/openabel)** (live; higher secondary to advanced undergrad): Recover a 3D flame slice from a 2D photo with the Abel inversion. The Abel inversion recovers the inside of an axisymmetric object, like a flame, from a flat image.
- **[openalias](https://github.com/KrunalPanchal1995/openalias)** (live; higher secondary to advanced undergrad): Understand the wagon-wheel effect and recover the true frequency. Sampling too slowly makes fast motion look slow or backwards, as in the wagon-wheel effect, and the true frequency can be recovered.

### Chemistry and Materials Science

- **[openmechanism](https://github.com/KrunalPanchal1995/openmechanism)** (live; secondary to diploma/undergrad): Optimise a kinetic mechanism against experiments. A chemical mechanism with many uncertain rates can be tuned against experiments, which makes combustion models trustworthy.

### Statistics, Research and Experimental Methods

- **`openuqprop`** (planned; higher secondary to advanced undergrad): Push rate uncertainty through to ignition time. Uncertain inputs give uncertain predictions, and propagating the uncertainty shows how much to trust a result.

### Artificial Intelligence, Data Science and Robotics

- **`openpareto`** (planned; higher secondary to advanced undergrad): Pick the best compromise design with multi-objective optimisation. When goals conflict, the Pareto front shows the best possible compromises.

### Heat, Thermodynamics and Fluid Mechanics

- **`openturbulence`** (planned; higher secondary to diploma/undergrad): Climb from mixing length to LES to data-driven RANS. Turbulence is hard to simulate, and closure models trade accuracy against cost.
- **`openlabonchip`** (planned; higher secondary to diploma/undergrad): Sort particles in a microchannel. Tiny channels sort and move particles with fluid forces, shrinking a laboratory onto a chip.

### Chemistry and Materials Science

- **`openhartree`** (planned; secondary to diploma/undergrad): Run Hartree-Fock on the H2 molecule. Hartree-Fock is the first step of computing molecular energies from quantum mechanics.

### Physics and the Science of Motion

- **`openschrodinger`** (planned; secondary to diploma/undergrad): Go from a particle in a box to the hydrogen atom. The Schrodinger equation explains why atoms have discrete energy levels, from a particle in a box to hydrogen.

### Heat, Thermodynamics and Fluid Mechanics

- **`opengasbox`** (planned; higher secondary to diploma/undergrad): Derive the ideal gas law from billiard-ball molecular dynamics. Simulating colliding particles shows how pressure and temperature arise and why the ideal gas law works.

### Chemistry and Materials Science

- **`openconformer`** (planned; secondary to diploma/undergrad): Find stable molecule shapes with reinforcement learning. Molecules take many shapes, and finding the most stable ones guides chemistry and drug design.

### Everyday Life and Practical Knowledge

- **`openbicycle`** (planned; middle school to higher secondary): Choose bicycle gears for hills and speed using gear ratios and cadence. Gears let a rider keep a comfortable pedalling rate on hills and flats.
- **`openwaterheater`** (planned; middle school to higher secondary): Size a water heater and predict how long it takes to heat a bucket. Heating water takes a fixed amount of energy, so power sets how long you wait.
- **`openegg`** (planned; middle school to higher secondary): Predict how long an egg takes to cook with heat conduction. Heat travels into an egg by conduction, so size and temperature decide the cooking time.
- **`openrainwater`** (planned; middle school to higher secondary): Size a rainwater harvesting tank for a roof and a rainy season. A tank must be big enough to bridge dry spells without being wasteful.

### Mathematics and Visual Problem-Solving

- **`openvolume`** (planned; secondary to diploma/undergrad): Compute the volume of a 3D-printed part with integrals. Integrals add up thin slices to give the volume of any shape.
- **`openequations`** (planned; secondary to diploma/undergrad): Solve linear and quadratic equations by seeing where graphs cross. Solving an equation means finding where two graphs meet.
- **`openseries`** (planned; secondary to diploma/undergrad): See how sequences and series build patterns, from savings to fractals. Sequences and series describe repeated growth, from savings to fractals.
- **`opencount`** (planned; secondary to diploma/undergrad): Count arrangements and selections with permutations and combinations. Counting arrangements is the base of probability and passwords.

### Physics and the Science of Motion

- **`openrollercoaster`** (planned; secondary to diploma/undergrad): Design a roller coaster drop that is thrilling and safe using energy conservation. Energy conservation tells how fast a ride goes at every point of the track.
- **`opencollisions`** (planned; secondary to diploma/undergrad): Predict what happens in collisions with momentum and energy. Momentum and energy rules predict how objects move after they hit.
- **`openripple`** (planned; secondary to diploma/undergrad): See how waves add and cancel using superposition. Waves add and cancel, which explains interference, noise cancelling and light patterns.

### Heat, Thermodynamics and Fluid Mechanics

- **`openexpansion`** (planned; higher secondary to diploma/undergrad): Leave the right gaps in bridges and rails for thermal expansion. Materials grow when heated, and structures need gaps so that they do not buckle.
- **`openheatingcurve`** (planned; higher secondary to diploma/undergrad): Read a heating curve with melting and boiling plateaus. Temperature stops rising during melting and boiling because energy goes into changing phase.
- **`openbernoulli`** (planned; higher secondary to diploma/undergrad): Explain lift and spray with Bernoulli's principle. Faster flow means lower pressure, which explains lift, sprays and chimneys.
- **`opencavityflow`** (planned; higher secondary to diploma/undergrad): Solve the lid-driven cavity with Navier-Stokes. The lid-driven cavity is the classic test of a fluid solver.

### Electricity, Magnetism and Electronics

- **`openbatterylife`** (planned; secondary to diploma/undergrad): Predict how long a battery lasts under a load. Battery life depends on capacity, load and how much capacity can really be used.
- **`openfuse`** (planned; secondary to diploma/undergrad): Choose a fuse or breaker rating that protects a circuit. A fuse or breaker must open before wires overheat but not trip in normal use.
- **`openphasor`** (planned; secondary to diploma/undergrad): See AC voltage and current as rotating phasors. AC voltage and current are rotating arrows whose angle gap is the phase.
- **`openamplifier`** (planned; secondary to diploma/undergrad): Design an op-amp amplifier with a target gain. An op-amp with feedback gives a precise, predictable gain.

### Chemistry and Materials Science

- **`opencorrosion`** (planned; secondary to diploma/undergrad): Predict corrosion rate and choose a protection method. Corrosion slowly destroys metal, and protection decisions follow its rate.
- **`opencrystal`** (planned; secondary to diploma/undergrad): Build crystal lattices and measure packing density. Atoms pack in repeating lattices, which sets density and strength.
- **`openequilibrium`** (planned; secondary to diploma/undergrad): Predict how a reaction shifts with Le Chatelier's principle. A reaction at equilibrium shifts when conditions change, which guides industrial yield.

### Biology, Human Body and Health Science

- **`openecosystem`** (planned; secondary to diploma/undergrad): Model predators and prey and see why populations oscillate. Predator and prey numbers rise and fall in linked cycles.
- **`openenzyme`** (planned; secondary to diploma/undergrad): Fit enzyme speed against substrate concentration (Michaelis-Menten). Enzymes speed up reactions, and their speed saturates as substrate grows.
- **`openphotosynthesis`** (planned; secondary to diploma/undergrad): Model how a leaf's photosynthesis responds to light. A leaf's sugar production rises with light and then levels off.

### Civil Engineering and Construction

- **`opencolumn`** (planned; diploma/undergrad to advanced undergrad): Find when a slender column buckles (Euler buckling). A slender column fails by buckling long before the material crushes.
- **`opensettlement`** (planned; diploma/undergrad to advanced undergrad): Estimate how much a building settles on clay over time. Buildings on clay sink slowly as water leaves the soil.
- **`openroadcurve`** (planned; diploma/undergrad to advanced undergrad): Design a road curve with safe speed and sight distance. A curve must be gentle enough for the speed and visible far enough to stop.
- **`openelements`** (planned; diploma/undergrad to advanced undergrad): Find stress around a hole in a plate with 2D finite elements. Finite elements break a part into pieces so a computer can find its stress.

### Mechanical Engineering

- **`openshaft`** (planned; diploma/undergrad to advanced undergrad): Size a shaft for torque with torsion and shear stress. Twisting loads create shear in a shaft, so its size is set by torque.
- **`opencam`** (planned; diploma/undergrad to advanced undergrad): Design a cam profile that gives a smooth follower motion. A cam turns rotation into any chosen follower motion.
- **`openspring`** (planned; diploma/undergrad to advanced undergrad): Design a spring for a target stiffness and load. A spring stores energy, and its stiffness follows from wire size and coils.

### Computer Science, Programming and Software

- **`openrecursion`** (planned; secondary to diploma/undergrad): Solve the Towers of Hanoi and see how recursion works. A problem that contains smaller copies of itself can be solved by a function that calls itself.
- **`opengraphs`** (planned; secondary to diploma/undergrad): Find the shortest route in a network with Dijkstra. Networks of nodes and links describe roads, the internet and friendships, and shortest paths are everywhere.
- **`openhash`** (planned; secondary to diploma/undergrad): See how hash tables find data fast, and how collisions happen. A hash function jumps straight to where data lives, which makes lookups fast.
- **`openbigo`** (planned; secondary to diploma/undergrad): Compare how algorithms grow with Big-O timing experiments. How running time grows with data size decides whether software scales.

### Artificial Intelligence, Data Science and Robotics

- **`openkmeans`** (planned; higher secondary to advanced undergrad): Group data into clusters with k-means. Clustering finds natural groups in data without labels.
- **`opendecisiontree`** (planned; higher secondary to advanced undergrad): Build a decision tree and see how it splits data. A decision tree asks simple questions in order to classify data, and can be read by people.
- **`openedges`** (planned; higher secondary to advanced undergrad): Find edges in images with convolution filters. Edges are where image brightness changes fast, found with simple filters.
- **`openreinforce`** (planned; higher secondary to advanced undergrad): Teach an agent to reach a goal by trial and reward. An agent learns what to do by trying actions and seeing rewards.
- **`opentimeseries`** (planned; higher secondary to advanced undergrad): Forecast a time series with moving averages and exponential smoothing. Smoothing and forecasting use the past to estimate the near future.
- **`openpid`** (planned; higher secondary to advanced undergrad): Tune a PID controller for a heated tank without overshoot. A PID controller corrects error now, from the past and from its trend.
- **`openstability`** (planned; higher secondary to advanced undergrad): See why feedback loops become unstable and how to keep them stable. A feedback loop that reacts too strongly oscillates and can blow up.
- **`opendigitaltwin`** (planned; higher secondary to advanced undergrad): Build a digital twin of a heated room and compare it with measured data. A digital twin is a model kept in step with a real system, used to predict and test.

### Electrical Power and Renewable Energy

- **`openpowerfactor`** (planned; diploma/undergrad to advanced undergrad): Correct a low power factor and cut the line current. A poor power factor draws extra current that heats wires without doing work.
- **`openevcharge`** (planned; diploma/undergrad to advanced undergrad): Plan electric vehicle charging within a home's power limit. Charging many vehicles must fit within a limited supply.
- **`opensolarangle`** (planned; diploma/undergrad to advanced undergrad): Tilt a solar panel for the best yearly energy. Panel tilt and direction decide how much energy it collects over a year.
- **`openmicrogrid`** (planned; diploma/undergrad to advanced undergrad): Dispatch a microgrid of solar, battery and generator at least cost. A microgrid chooses how to use solar, storage and a generator at least cost.

### Chemical, Environmental and Process Engineering

- **`openfiltration`** (planned; diploma/undergrad to advanced undergrad): Size a sand filter and predict how fast it clogs. A filter removes particles until it clogs, which sets size and cleaning schedule.
- **`openwastewater`** (planned; diploma/undergrad to advanced undergrad): Predict how well a treatment tank removes pollution. Treatment tanks remove pollution over time, so size and residence time matter.
- **`openabsorption`** (planned; diploma/undergrad to advanced undergrad): Size a gas absorber that removes a pollutant from air. Gas absorbers wash pollutants out of air with a liquid.
- **`openlifecycle`** (planned; diploma/undergrad to advanced undergrad): Compare two products by their whole life-cycle impact. A product's impact includes making, using and disposing of it, not just use.

### Aerospace, Automotive and Transportation

- **`openbraking`** (planned; higher secondary to advanced undergrad): Predict stopping distance with and without ABS. Stopping distance grows with the square of speed, and ABS keeps wheels gripping.
- **`openevrange`** (planned; higher secondary to advanced undergrad): Predict an electric car's range from battery, speed and drag. Range follows from battery energy and how much power drag and rolling take.
- **`opennozzle`** (planned; higher secondary to advanced undergrad): Design a rocket nozzle for thrust at altitude. A nozzle turns hot gas into fast exhaust, and its shape suits an altitude.
- **`opendrag`** (planned; higher secondary to advanced undergrad): See how aerodynamic drag sets top speed and fuel use. Aerodynamic drag grows with the square of speed and sets fuel use.

### Architecture, Design and Smart Buildings

- **`openacoustics`** (planned; higher secondary to diploma/undergrad): Predict a room's echo time and fix it with absorbers. Echo time in a room depends on its size and how much sound surfaces absorb.
- **`opensmarthome`** (planned; higher secondary to diploma/undergrad): Program a thermostat that keeps a room comfortable with less energy. A smart thermostat saves energy by learning when heat is not needed.

### Economics, Business, Finance and Entrepreneurship

- **`openinflation`** (planned; secondary to diploma/undergrad): See how inflation erodes savings and what real returns are. Prices rise over time, so savings must grow faster than inflation to keep their value.
- **`opencashflow`** (planned; secondary to diploma/undergrad): Plan cash flow for a small business month by month. A business fails when cash runs out, even if it is profitable on paper.
- **`openinventory`** (planned; secondary to diploma/undergrad): Choose an order size that balances ordering and holding cost. Ordering too often costs money, and ordering too much ties up cash; there is a best order size.
- **`opencriticalpath`** (planned; secondary to diploma/undergrad): Find the critical path of a project and the shortest finish time. The longest chain of tasks sets the shortest time a project can finish.
- **`openfactory`** (planned; secondary to diploma/undergrad): Find the bottleneck of a factory line and raise throughput. The slowest step limits a whole production line.
- **`openqueue`** (planned; secondary to diploma/undergrad): Predict waiting times in a queue at a bank or hospital. Waiting time explodes as a service gets close to full, which queue models predict.

### Geography, Climate, Environment and Earth Science

- **`opentides`** (planned; secondary to diploma/undergrad): Predict tides from the Moon and Sun with harmonic analysis. Tides follow the Moon and Sun and can be predicted by adding a few waves.
- **`openaquifer`** (planned; secondary to diploma/undergrad): Predict how groundwater flows and where a well draws from. Groundwater flows through rock and soil, and wells draw down the level.
- **`opencarboncycle`** (planned; secondary to diploma/undergrad): Track carbon between air, oceans and land in a box model. Carbon moves between air, oceans and land, and a box model shows how added carbon spreads.
- **`opentectonics`** (planned; secondary to diploma/undergrad): Show how plates move and where earthquakes and volcanoes occur. Moving plates explain earthquakes, volcanoes and mountains.

### Astronomy and Space Science

- **`openstars`** (planned; secondary to diploma/undergrad): Place stars on the HR diagram and follow their life cycle. A star's brightness and colour reveal its mass and age.
- **`opentelescope`** (planned; secondary to diploma/undergrad): Choose a telescope aperture and eyepiece for what you want to see. Aperture decides how much light and detail a telescope gathers.

### Statistics, Research and Experimental Methods

- **`opensampling`** (planned; higher secondary to advanced undergrad): Design a survey sample and see how its size changes the error. A well-chosen sample tells about a whole population, and its size sets the error.
- **`opencorrelation`** (planned; higher secondary to advanced undergrad): Tell correlation from causation with simulated data. Two things moving together does not mean one causes the other.
- **`openreliability`** (planned; higher secondary to advanced undergrad): Predict failure rates with the Weibull distribution. Failure rates over time tell when to replace or service a part.
- **`opencontrolchart`** (planned; higher secondary to advanced undergrad): Spot a drifting process with control charts. A control chart shows when a process has drifted beyond normal variation.

### Communication, Language and Creative Skills

- **`opencomposition`** (planned; middle school to higher secondary): Compose a photograph with the rule of thirds and golden ratio. Where objects sit in a frame changes how a picture feels.
- **`openaudio`** (planned; middle school to higher secondary): Record and edit sound: waves, sampling and filters. Sound is sampled many times a second, and filters change how it sounds.
- **`openinfographic`** (planned; middle school to higher secondary): Turn a table of numbers into a clear infographic. A clear chart or infographic turns numbers into a message people remember.

### Computer Science, Programming and Software

- **`opengameloop`** (built; secondary to diploma/undergrad): Build a game loop with a fixed timestep and smooth input. A game loop updates the world in fixed steps and draws as fast as it can, which keeps motion smooth on any machine.
- **`opengamephysics`** (planned; secondary to diploma/undergrad): Make a 2D platformer feel right with collision and jump physics. Simple collision and jump rules decide whether a game character feels responsive.
- **`opengameai`** (planned; secondary to diploma/undergrad): Make game enemies chase and avoid using pathfinding and steering. Pathfinding and steering let non-player characters move sensibly around obstacles.

### Mechanical Engineering

- **`opentopology`** (built; diploma/undergrad to advanced undergrad): Find the lightest stiff shape with SIMP topology optimisation. Topology optimisation lets the computer decide where material is needed, giving strong, light parts.
- **`opentopoheat`** (planned; diploma/undergrad to advanced undergrad): Design heat-conduction paths with topology optimisation. The same method places conductive material to carry heat away efficiently.
- **`openlattice`** (planned; diploma/undergrad to advanced undergrad): Fill a 3D-printed part with an optimised lattice. Replacing solid material with a lattice saves weight and absorbs energy.

### Chemistry and Materials Science

- **`openmelting`** (built; secondary to diploma/undergrad): Watch a crystal melt in molecular dynamics and find the melting point. Atoms in a crystal vibrate more as heat rises until the order breaks, which defines melting.
- **`opendiffusion`** (planned; secondary to diploma/undergrad): Measure diffusion from molecular dynamics with the mean squared displacement. How far particles wander over time gives the diffusion coefficient.
- **`openthermostat`** (planned; secondary to diploma/undergrad): Hold temperature constant in molecular dynamics with a thermostat. A thermostat keeps a simulated system at the temperature of an experiment.
- **`openpolymer`** (planned; secondary to diploma/undergrad): Simulate a polymer chain and measure how its size scales with length. Long chains coil, and their size grows with length in a predictable way.

### Mechanical Engineering

- **`openfoldbed`** (planned; diploma/undergrad to advanced undergrad): Design a lightweight folding bed for emergency hospitals. A bed that folds flat can be stored, shipped and set up fast when hospitals need space quickly. This is a design study, not a medical device.
- **`openbedload`** (planned; diploma/undergrad to advanced undergrad): Choose materials and joints so a low-cost bed carries a patient safely. Checking loads and joints shows how simple materials can carry a patient safely. This is a design study, not a medical device.

### Architecture, Design and Smart Buildings

- **`openwardlayout`** (planned; higher secondary to diploma/undergrad): Lay out a temporary ward to limit airborne infection spread with ventilation. Spacing and airflow change how far infectious aerosols travel in a temporary ward. This is an education model, not clinical guidance.

### Chemical, Environmental and Process Engineering

- **`openvaccinebox`** (planned; diploma/undergrad to advanced undergrad): Size an insulated box that keeps vaccines cold for days without power. A well-insulated box with ice can hold a safe temperature when there is no power.
- **`openphasechange`** (planned; diploma/undergrad to advanced undergrad): Size a phase-change material pack for a cold box. A phase-change pack absorbs heat at a steady temperature while it melts.
- **`opencoldchain`** (planned; diploma/undergrad to advanced undergrad): Detect temperature excursions in a vaccine cold chain from logger data. Temperature logs reveal when a shipment left its safe range.

### Cybersecurity and Digital Safety

- **`openpassword`** (built; higher secondary to diploma/undergrad): Measure password strength with entropy and see how hashing protects it. Password strength is about how many guesses an attacker needs, and hashing protects stored passwords.
- **`opensecureweb`** (planned; higher secondary to diploma/undergrad): Find and fix common web vulnerabilities in a safe practice app. Most web attacks use a small set of mistakes that can be learned and fixed.
- **`openthreatmodel`** (planned; higher secondary to diploma/undergrad): Build a threat model and rank security risks. A threat model lists what could go wrong and ranks what to fix first.
- **`opentls`** (planned; higher secondary to diploma/undergrad): See how HTTPS agrees on a secret while an eavesdropper listens. HTTPS lets two strangers agree on a secret key in public, so the traffic cannot be read.

### Heat, Thermodynamics and Fluid Mechanics

- **`openlbm`** (built; higher secondary to diploma/undergrad): Simulate fluid flow with the lattice Boltzmann method. The lattice Boltzmann method recovers fluid flow from simple particle collision rules on a grid.
- **`openchannel`** (planned; higher secondary to diploma/undergrad): Reproduce the law of the wall in turbulent channel flow. Near a wall, turbulent flow follows a universal velocity profile called the law of the wall.
- **`opencascade`** (planned; higher secondary to diploma/undergrad): Show the energy cascade and Kolmogorov scaling in turbulence. Turbulent energy moves from large eddies to small ones where it becomes heat.
- **`openvortexstreet`** (planned; higher secondary to diploma/undergrad): Predict vortex shedding behind a cylinder. Flow past a cylinder sheds alternating vortices at a frequency set by the Strouhal number.
- **`opennssolver`** (planned; higher secondary to diploma/undergrad): Write a small incompressible Navier-Stokes solver with the projection method. A projection method solves the incompressible Navier-Stokes equations step by step on a grid.
- **[openregularity](https://github.com/KrunalPanchal1995/openregularity)** (live; higher secondary to diploma/undergrad): Learn what is known and unknown about smooth Navier-Stokes solutions (the Millennium problem). Whether smooth solutions of the Navier-Stokes equations always stay smooth is a famous open problem; this repo teaches what is known and does not claim a proof.

### Life Skills, Mind and Learning

- **`opentime`** (planned; secondary to diploma/undergrad): Plan your time with a priority matrix and a weekly schedule you will keep. Time is limited, and a simple priority system helps you spend it on what matters. This is general education.
- **`opensleepreset`** (planned; secondary to diploma/undergrad): Reset a disturbed sleep cycle using a circadian rhythm model. The body clock can be shifted with light and timing after sleep is disturbed. This is general education, not medical advice.
- **`openadaptation`** (planned; secondary to diploma/undergrad): Adapt to a new situation with a simple learning loop. Adapting means noticing what changed, trying something small and learning from the result.
- **`openchessmind`** (planned; secondary to diploma/undergrad): Use chess to train calm, fearless decisions under pressure. Chess trains staying calm, thinking in steps and accepting risk. This is general education.
- **`opendesignsense`** (planned; secondary to diploma/undergrad): Judge and improve the aesthetics of an app, a poster or a craft. Alignment, contrast, spacing and balance can be learned and measured.
- **`openfrugal`** (planned; secondary to diploma/undergrad): Cool things cheaply with a terracotta pot and other frugal engineering. Evaporation can cool without electricity, and many problems can be solved cheaply with physics.
- **`openresilience`** (planned; secondary to diploma/undergrad): Manage anxious and low thoughts and build resilience (general education, not therapy). Noticing thoughts, naming them and taking small actions can help. This is general education, not therapy; seek a qualified professional when you need help.
- **`openlearning`** (planned; secondary to diploma/undergrad): Learn any topic faster with retrieval, spacing and first principles. Retrieval and spacing help memory more than rereading.

### Statistics, Research and Experimental Methods

- **[openstitchdic](https://github.com/KrunalPanchal1995/openstitchdic)** (live; higher secondary to advanced undergrad): Merge two cameras with different angles, frame rates and aspect ratios into one uniform data set with Makima interpolation. Cameras that differ in angle, frame rate and aspect ratio can still be merged into one data set with warping and interpolation.

### Mathematics and Visual Problem-Solving

- **`openmathprep`** (planned; secondary to diploma/undergrad): Solve first-year IIT-style math problems by method, with every answer checked by code. A method for every kind of first-year problem helps new students start strong.

### Chemistry and Materials Science

- **`openbonds`** (planned; secondary to diploma/undergrad): Understand chemical bonds and molecular shapes without memorising. Bonds and shapes follow from electrons wanting stable arrangements, so you can reason instead of memorising.

### Electricity, Magnetism and Electronics

- **`opensemifab`** (planned; secondary to diploma/undergrad): See how a semiconductor chip is made, from sand to transistor. A chip is built layer by layer with light, chemistry and heat on a silicon wafer.

### Chemical, Environmental and Process Engineering

- **`openplasma`** (planned; diploma/undergrad to advanced undergrad): Explain plasma pyrolysis, gasification and combustion with one energy and mass balance. Pyrolysis, gasification and combustion differ mainly in how much oxygen is present and how hot it is.
- **[openprocesssim](https://github.com/KrunalPanchal1995/openprocesssim)** (live; diploma/undergrad to advanced undergrad): Build a small open process simulator with flash, heat exchanger and reactor blocks. A process simulator links unit blocks and solves their mass and energy balances together.
- **`openturbflame`** (built; diploma/undergrad to advanced undergrad): Model a turbulent flame with a flamelet closure. A flamelet closure links chemistry to turbulence through the mixture fraction.
- **`opensootmoments`** (built; diploma/undergrad to advanced undergrad): Predict soot size and number with the method of moments. The method of moments follows a few averages of the soot size distribution.
- **`opensootsectional`** (built; diploma/undergrad to advanced undergrad): Predict the soot size distribution with the sectional method. The sectional method splits soot sizes into bins and follows each bin.

### Statistics, Research and Experimental Methods

- **`openflamevolume`** (built; higher secondary to advanced undergrad): Rebuild a 3D flame from many 2D photos using stereo image correlation. Several views of a flame can be combined to rebuild its three-dimensional shape.
- **`opensmokevideo`** (built; higher secondary to advanced undergrad): Estimate smoke density and flow rate from a video using light absorption and refraction. How smoke absorbs and bends light tells its density and how fast it flows.

### Mechanical Engineering

- **`opensolidmodel`** (planned; diploma/undergrad to advanced undergrad): Build a small parametric CAD kernel like SolidWorks. A CAD kernel stores shapes with parameters so they can be edited later.
- **`openparametric`** (planned; diploma/undergrad to advanced undergrad): Generate engineered parts from rules and equations like computational engineering tools. Rules and equations can generate whole parts that change when requirements change.

### Aerospace, Automotive and Transportation

- **`opengasturbine`** (planned; higher secondary to advanced undergrad): Predict gas turbine thrust and efficiency with the Brayton cycle. The Brayton cycle compresses, heats and expands air to make thrust or power.

### Physics and the Science of Motion

- **`openqmintro`** (planned; secondary to diploma/undergrad): Learn the basic ideas of quantum mechanics: superposition, measurement and tunnelling. Superposition, measurement and tunnelling are the core ideas behind chemistry and electronics.

## Licence and credits

Code is MIT licensed. Built for the Hello FOSS program, PAN IIT OSS. Safety and honesty notes: health, life-skills and vaccine-box repos are educational and not medical advice or devices; cybersecurity repos are defensive only; the Navier-Stokes repo teaches what is known and claims no proof.
