# Usage

The above script runs a simulation of the NACA 0012 Airfoil, and is included in the `examples` folder. 

**To run the above python script:**

- Copy the examples directory to a different location:

``` 
cp -r <path-to-repository>/examples <path-to-examples-directory> 
```

- Navigate into the directory:

``` 
cd <path-to-examples-directory> 
```

- Run the python script with a single processor:

``` 
python run_example.py --inputFile 
```

or run with multiple processors

 ``` 
 mpirun -np <number of processors> python run_example.py --inputFile <path-to-input-yaml-file>
 ```

**_Note:_**

- *_Example input yaml files to run on personal computers are stored in `examples/inputs` directory, and for Great Lakes HPC cluster, an example file is stored in `examples/inputs/GL`_*
- *_Make sure to modify the file and file paths ti absolute paths in the yaml file when running in a docker container._*

Use `examples/inputs/naca0012_sinInfo.yaml` or `examples/inputs/GL/naca0012_sinInfo.yaml`(for Great Lakes) to test the package with NACA0012 airfoil.

After execution, the following results are expected which are saved in the specified output directory.

- A copy of the input yaml file in the output directory.
- `overall_sim_info.yaml` in the output directory.
- `ADflow_Results.png` in each experimental level directory, that is a plot comparing C<sub>L</sub>, and C<sub>D</sub> values at all refinement levels to the expeimental data(if provided).

<p align="center">
  <img src="../test_run_doc/ADflow_Results.png" alt="Comparision plot" width="800">
</p>

- `ADflow_output.csv` in each refinement level directory, that is a file containg Angle of Attack(AoA), C<sub>L</sub>, and C<sub>D</sub> data.
- `aoa_<aoa>.yaml` in aoa level directory, that contains the simulation information particular to that angle of attack.
- Default ADflow outputs: A tecplot file, a CGNS surface file, and a CGNS volume file.
## Example usage
Here’s a quick example of how to use `simulateTestCases`:

### Running Simulations
```python
from simulateTestCases.run_sim import run_sim

# Initialize the runner with configuration file
sim = run_sim('<path-to-input-yaml-file>')

# Run the simulation series
sim.run()

# Analyze results
sim.post_process()
```

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
