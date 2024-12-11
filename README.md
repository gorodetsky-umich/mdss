# simulateTestCases

`simulateTestCases` is a Python package designed for running a series of ADflow simulations using Mphys and OpenMDAO. This package provides streamlined functions to automate simulation test cases.

## Features

- Simplifies running multiple simulation cases with ADflow.
- Integrates with Mphys and OpenMDAO and provides a framework for data management.
- Genrates a comparison plot for each experimental condition in each case.

## Dependencies

The package requires the following libraries, which can automatically be installed with `pip`:

- `numpy>=1.21`
- `scipy>=1.7`
- `mpi4py>=3.1.4`
- `pyyaml`
- `matplotlib`
- `pandas`
- `petsc4py`

Additionally, the following packages are also needed but may require manual installation:

- `openmdao`
- `mdolab-baseclasses`
- `adflow`
- `mphys`

A bash shell script is provided to download all the required dependencies and software programs provided by the MDO lab. It is assumed that the user is working on a local Debian based machine. 

However, we recommend using Docker. Images are available for both GCC and INTEL compilers [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/dockerInstructions.html#) 

## Installation

To install `simulateTestCases`, use the following commands:

1. Clone the repository:

    ```bash
    git clone https://github.com/gorodetsky-umich/simulateTestCases.git
    ```

2. Navigate into the directory:

    ```bash
    cd simulateTestCases
    ```

3. To install the package without dependencies:

    ```bash
    pip install .
    ```
    To install the package along with dependencies listed in `requirements.txt`:
    ```bash
    pip install . -r requirements.txt
    ```
    For an editable installation:
    ```bash
    pip install -e .
    ```

## Usage

Here’s a quick example of how to use `simulateTestCases`:

```python
from simulateTestCases.run_sim import run_sim

# Initialize the runner with configuration file
sim = run_sim('inputs/naca0012_simInfo.yaml')

# Run the simulation series
sim.run_problem()

# Analyze results
sim.post_process()
```
### Inputs
The `run_sim` class requires two inputs to configure and execute a simulation:

1. **YAML Configuration File**:  
   A `.yaml` file that specifies essential parameters for setting up the simulation. This file should adhere to a specific format for compatibility; otherwise, errors may occur during execution. Correctly formatted YAML files are available in the `examples` directory, including:
   - **NACA 0012 Airfoil**: A sample configuration for simulating the NACA 0012 airfoil.
   - **McDonnell Douglas 30P-30N Airfoil**: A sample configuration for simulating the McDonnell Douglas 30P-30N airfoil.

2. **Output Directory Path**:  
   A string that specifies the directory path where output files will be saved. Ensure that the specified directory exists or that permissions allow for its creation.

### YAML File Structure

The YAML file organizes simulation data into a structured hierarchy, enabling clear configuration of cases and experimental conditions. Below is the hierarchical structure used in the YAML file:

```
Hierarchies
|
|---- Hierarchie 1
        |
        |---- name
        |---- cases:
        |       |
        |       |---- case 1
        |       |       |
        |       |       |---- name
        |       |       |---- nRefinement
        |       |       |---- mesh file
        |       |       |---- Geometry Info
        |       |       |---- Solver Parameters
        |       |       |---- Experimental Conditions:
        |       |               |
        |       |               |---- Condition 1
        |       |               |
        |       |               |---- Other conditions as applicable
        |       | 
        |       |---- Other cases as needed
        |
        |---- Additional hierarchy levels as required.
```

#### Descriptions

- **Hierarchies**: Organizes the simulation data into a multi-level structure for easy navigation.
    - **Hierarchie 1**: The first level in the hierarchy, where main categories are defined.
        - **name**: Represents the name of the hierarchy.
        - **cases**: Contains individual simulation cases under the hierarchy.
            - **case 1**: An individual simulation case with detailed specifications.
                - **name**: The name of the airfoil or the model used in the simulation.
                - **nRefinement**: The number of refinement levels.
                - **mesh file**: The path to the mesh file to be in the simulation.
                - **Geometry Info**: Geometrical details like reference area and chord length for the geometry.
                - **Solver Parameters**: Specific ADflow solver parameters for running the case.
                - **Experimental Conditions**: Defines experimental conditions for validation.
                    - **Condition 1**: Includes details like Reynold's number, Mach number, temperature, list of Angle of Attacks and the location of experimental data.
                - **Other conditions**: Additional conditions that may be present for comprehensive testing.
        - **Other Cases**: Additional cases that may be present in current hierarchie.
    - **Additional hierarchy levels**: Allows for adding more structured levels if needed.

Please note that adherence to this structure is essential; any deviation may lead to errors when running simulations. Examples of correctly formatted YAML files are provided in the `examples` folder. These include:

- A YAML file with simulation information for the **NACA 0012 airfoil**
- A YAML file for the **McDonnell Douglas 30P-30N airfoil**
- A YAML file for running both **NACA 0012 airfoil** and **McDonnell Douglas 30P-30N airfoil**

Additionally, a Python script named `dict_to_yaml` is available to help convert a Python dictionary (structured according to the hierarchy above) into a `.yaml` file. This script can also be used as a starting point for generating custom YAML files.

The example YAML files and `dict_to_yaml` script serve as templates to facilitate proper configuration.

`check_yaml_file()` method helps to check if the yaml file is compatible. This method generates a report, saved as `<output>/yaml_validation.txt`, containing the error details.

### Naming Format for Grid Files

Since ADflow supports only 'CGNS' format for multi-block or overset meshes, please ensure that input grid files use this format. Additionally, the naming convention for grid files should follow this structure: `<name>_L<level of refinement>.cgns`. This naming convention is essential for automating the simulation process. Here, refinement levels start from `L0` (the finest grid) to `L{n-1}`, where `L{n-1}` is the coarsest grid, and `n` represents the number of refinement levels. For example, a valid grid file name would be `funfoil_L0.cgns`. Note that while there are no restrictions on the location of the grid file, adherence to this naming convention is required.

### Outputs
The output directory structure is organized similarly to the YAML file structure, as shown below:

```
Output_Directory
    |
    |---- Hierarchy
            |           
            |---- case
            |       |       
            |       |----Experimental Set
            |             |
            |             |--- Refinement Level
            |             |       |
            |             |       |---- AOA Directory
            |             |       |       |
            |             |       |       |---- ADflow Outputs
            |             |       |       |---- out.yaml
            |             |       |
            |             |       |---- '.csv' file with simulation data
            |             |
            |             |---- Plot of Experimental data vs simulated
            |                   data in png format
            |
            |---- out.yaml                                                                                      
```

Within each **AOA Directory** (Angle of Attack), outputs from ADflow are stored. Additionally, the script generates two `out.yaml` files:
- One is stored in each **AOA Directory**, containing simulation information specific to that angle of attack.
- The other is located in the **Hierarchy** directory and contains simulation information for the entire run.

A `.csv` file is also generated within each **Refinement Level** directory. This file includes `C_L`, `C_D`, and Wall Time for each angle of attack. Using the `post_process` method in `run_sim`, a `.png` plot can be generated comparing experimental data (if available) with simulated data across different levels of refinement.

## Additonal information
The script uses a set of default solver options ad shown below. Changes to these parameters can be specified in the 'yaml' configuration file.

```
# Print Options
"printIterations": False,
"printAllOptions": False,
"printIntro": False,
"printTiming": False,
# I/O Parameters
"gridFile": f"grids/naca0012_L1.cgns", # Default grid file
"outputDirectory": ".",
"monitorvariables": ["resrho", "resturb", "cl", "cd", "yplus"],
"writeTecplotSurfaceSolution": True,
# Physics Parameters
"equationType": "RANS",
"liftindex": 3,  # z is the lift direction
# Solver Parameters
"smoother": "DADI",
"CFL": 0.5,
"CFLCoarse": 0.25,
"MGCycle": "sg",
"MGStartLevel": -1,
"nCyclesCoarse": 250,
# ANK Solver Parameters
"useANKSolver": True,
"nsubiterturb": 5,
"anksecondordswitchtol": 1e-4,
"ankcoupledswitchtol": 1e-6,
"ankinnerpreconits": 2,
"ankouterpreconits": 2,
"anklinresmax": 0.1,
# Termination Criteria
"L2Convergence": 1e-12,
"L2ConvergenceCoarse": 1e-2,
"nCycles": 75000,
```
For more details on ADflow, its installation, and available options, please refer to the [ADflow documentation](https://mdolab-adflow.readthedocs-hosted.com/en/latest/).
