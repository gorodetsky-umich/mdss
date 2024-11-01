# simulateTestCases

`simulateTestCases` is a Python package designed for running a series of ADflow simulations using mphys and OpenMDAO. This package provides streamlined functions to automate simulation test cases.

## Features

- Simplifies running multiple simulation cases with ADflow.
- Integrates with mphys and OpenMDAO and provides a framework for data management.
- Genrates a comparison plot for each experimental condition in each case.

## Installation

To install `simulateTestCases`, use the following commands:

1. Clone the repository:

    ```bash
    git clone https://github.com/sinaendhran/simulateTestCases.git
    ```

2. Navigate into the directory:

    ```bash
    cd simulateTestCases
    ```

3. Install the package with pip:

    ```bash
    pip install .
    ```

### Dependencies

The package requires the following libraries, which are automatically installed with `pip`:

- `numpy`
- `scipy`
- `pyyaml`
- `matplotlib`
- `pandas`
- `mpi4py`
- `petsc4py`

## Usage

Here’s a quick example of how to use `simulateTestCases`:

```python
from simulateTestCases.run_sim import run_sim

# Initialize the runner with configuration file
sim = run_sim('naca0012_simInfo.yaml', 'output_dir')

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
Hierarchy Levels
|
|---- Level 1
        |
        |---- hierarchy
        |---- cases:
        |       |
        |       |---- case 1
        |       |       |
        |       |       |---- name
        |       |       |---- nRefinement
        |       |       |---- mesh file
        |       |       |---- Geometry Info
        |       |       |---- Solver Parameters
        |       |       |---- AOA
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

- **Hierarchy Levels**: Organizes the simulation data into a multi-level structure for easy navigation.
- **Level 1**: The first level in the hierarchy, where main categories are defined.
- **hierarchy**: Represents the name of the hierarchy within this level.
- **cases**: Contains individual simulation cases under the hierarchy.
  - **case 1**: An individual simulation case with detailed specifications.
    - **name**: The name of the airfoil or the model used in the simulation.
    - **nRefinement**: The number of refinement levels.
    - **mesh file**: The path to the mesh file to be in the simulation.
    - **Geometry Info**: Geometrical details like reference area and chord length for the geometry.
    - **Solver Parameters**: Specific ADflow solver parameters for running the case.
    - **AOA**: List of Angles of Attack to be used in the simulations.
    - **Experimental Conditions**: Defines experimental conditions for validation.
      - **Condition 1**: Includes details like Reynold's number, Mach number, temperature, and the location of experimental data.
      - **Other conditions**: Additional conditions that may be present for comprehensive testing.
- **Additional hierarchy levels**: Allows for adding more structured levels if needed.

Please note that adherence to this structure is essential; any deviation may lead to errors when running simulations. Examples of correctly formatted YAML files are provided in the `examples` folder. These include:

- A YAML file with simulation information for the **NACA 0012 airfoil**
- A YAML file for the **McDonnell Douglas 30P-30N airfoil**

Additionally, a Python script named `dict_to_yaml` is available to help convert a Python dictionary (structured according to the hierarchy above) into a `.yaml` file. This script can also be used as a starting point for generating custom YAML files.

The example YAML files and `dict_to_yaml` script serve as templates to facilitate proper configuration.

### Naming Format for Grid Files

Since ADflow supports only 'CGNS' format for multi-block or overset meshes, please ensure that input grid files use this format. Additionally, the naming convention for grid files should follow this structure: `<name>_L<level of refinement>.cgns`. This naming convention is essential for automating the simulation process. Here, refinement levels start from `L0` (the finest grid) to `Ln`, where `L{n-1}` is the coarsest grid, and `n` represents the number of refinement levels. For example, a valid grid file name would be `funfoil_L0.cgns`. Note that while there are no restrictions on the location of the grid file, adherence to this naming convention is required.
