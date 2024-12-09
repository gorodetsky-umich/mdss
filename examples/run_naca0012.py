from simulateTestCases.run_sim import run_sim

output_dir = 'output'
sim = run_sim('naca0012_simInfo.yaml', output_dir) # Input the simulation info and output dir

sim.run_problem() # Run the simulation
sim.post_process() # Genrates plots comparing experimental data and simulated data and stores them