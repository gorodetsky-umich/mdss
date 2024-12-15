# Usage
## Example usage
Here’s a quick example of how to use `simulateTestCases`:

### Running Simulations
```python
from simulateTestCases.run_sim import run_sim

# Initialize the runner with configuration file
sim = run_sim('inputs/naca0012_simInfo.yaml')

# Run the simulation series
sim.run()

# Analyze results
sim.post_process()
```

The above script runs a simulation of the NACA 0012 Airfoil, and is included in the `examples` folder. 

**To run the above python script:**

- Copy the examples directory to a different location:

``` cp -r examples <Path to directory to save copy of examples> ```

- Navigate into the directory:

``` cd <Path to directory to save copy of examples>/examples ```

- Run the python script with a single processor:

``` python run_example.py --inputFile <Path to the input yaml file>```

or run with multiple processors

 ``` mpirun -np <number of processors> python run_example.py --inputFile <Path to the input yaml file>``` to run using multiple processors

After execution, the results are saved in the specified output directory. Key outputs include:

- Simulation outputs in structured directories for each refinement and angle of attack (AOA) level.
- Plots and analysis results, including comparisons with experimental data.
- Generated YAML files, summarizing simulation and output information.

### To read existing simualtion data or generate data

The function `get_sim_data` can be used to get existing simulation data that was generated after a simulation, or to generate new simulation data by passing a `run_flag`. If `run_flag` is `1`, then the function runs the simulation and outputs the data as a dictionary.

The function provides the flexibility of using the input YAML file or  the `overall_sim_info.yaml` file that is generated and stored in the outptut directory after the completion of simulations, as inputs.

```python
from simulateTestCases.utils import get_sim_data

# Specify the path to the input file.
info_file = 'inputs/naca0012_simInfo.yaml'

# Call the function to get simulation data as a dictionary
sim_data = get_sim_data(info_file, 0)

# Print the dictionary
print(sim_data)
```

## Additional Information
### Grid Files
Grids for NACA 0012 and Mc Donnell Dolugas 30P-30N are provided under `examples/grids` in the examples directory. The other grids (CRM clean, and DLR High-Lift) including Naca 0012 and 30P-30N can be found at [Dropbox folder](https://www.dropbox.com/scl/fo/fezdu5be849c78vze7l19/ACCsSHpLGEwCcyFEPWj2FB0?rlkey=ixbr0606y3vx5eadrs61b9cz3&st=i4evwxed&dl=0).

### Experimental data
Experimental data for NACA 0012 and Mc Donnell Dolugas 30P-30N are provided under `examples/exp_data` in the examples directory. The other dat (CRM clean, and DLR High-Lift) including Naca 0012 and 30P-30N, and their references can be found at [Dropbox folder](https://www.dropbox.com/scl/fo/18rcs9bh0qmf19ymptrt2/AHx-xyYSXk_wGXqhvVV2yMM?rlkey=kp0vovsegpddfn78wfjiv8gbi&st=2czi5hbu&dl=0).
