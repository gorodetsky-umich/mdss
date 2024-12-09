# Inputs

The `simulateTestCases` package requires the following inputs to configure and execute simulations:

---

## 1. YAML Configuration File

A YAML file is required to define the simulation parameters and organize test cases. The YAML file structure and respective descriptions are given below.

### Input YAML file Structure

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
        |       |       |---- meshes folder path
        |       |       |---- mesh files
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

- **Hierarchies**: A list to organize the simulation data into a multi-level structure for easy navigation.
    - **Hierarchie 1**: The first level in the hierarchy, where main categories are defined.
        - **name**: Represents the name of the hierarchy.
        - **cases**: A list containing individual simulation cases under the hierarchy.
            - **case 1**: An individual simulation case with detailed specifications.
                - **name**: The name of the airfoil or the model used in the simulation.
                - **meshes folder path**: Path to the folder containg mesh files.
                - **mesh files**: A list of mesh files
                - **Geometry Info**: Geometrical details that are required: Reference area and chord length for the geometry.
                - **Solver Parameters**: Specific ADflow solver parameters for running the case.
                - **Experimental Conditions**: A list defining experimental conditions.
                    - **Condition 1**: Details required to define an AeroProblem: Reynold's number, Mach number, temperature, list of Angle of Attacks and the location of experimental data.
                - **Other conditions**: Additional experimental conditions that may be present.
        - **Other Cases**: Additional cases that may be present in current hierarchie.
    - **Additional hierarchy levels**: Allows for adding more structured levels if needed.

Please note that adherence to this structure is essential; any deviation may lead to errors when running simulations. Examples of correctly formatted YAML files are provided in the `examples` folder.

A Python script named `dict_to_yaml` is available to help convert a Python dictionary (structured according to the hierarchy above) into a `.yaml` file. This script can also be used as a starting point for generating custom YAML files.

The example YAML files and `dict_to_yaml` script serve as templates to facilitate proper configuration.

### Solver Parameters
The Solver parameters is a dictionary containing options specific to the ADflow CFD solver, allowing users to customize the solver's behavior to suit their simulation needs. Detailed descriptions of these parameters and their usage can be found in the [ADflow Documentation](https://mdolab-adflow.readthedocs-hosted.com/en/latest/options.html "ADflow Options"). 

If the dictionary is empty or if the default parameters are not modified, the code will use a predefined set of default solver options. These defaults are designed to provide a reliable baseline configuration for running simulations effectively without requiring manual adjustments.

#### Default Solver Parameters:
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
### Experimental Conditions

To define the problem, referred to as the *__AeroProblem__* (focused on aerodynamics), the following conditions along with the Angle of Attack(AoA) and path to the experimental data:

- Reynolds number
- Mach number
- Temperature
- Reynolds length (Computed from geometrical data)

Other properties, such as pressure or density, will be calculated automatically based on the specified values and the governing gas laws.

The `Angle of Attack (AoA)` is required to define the aerodynamic orientation of the flow. The `path to experimental data` can be left blank, as it will not affect the simulation. However, leaving it blank will generate a warning during the post-processing stage.


### Location of Mesh Files

Specifying the location of the mesh files requires two inputs in every case: 

- `meshes_folder_path` gets the path to the folder that contains the mesh files
- `mesh_files` gets the list of file names, that to be run, in the folder specified above.

## 2. Output Directory Path

A string specifying the directory where simulation results will be stored. The directory structure mirrors the hierarchy defined in the YAML file.

**Ensure that:**

- The specified directory exists or permissions allow for its creation.
- The directory has sufficient space to store simulation results.

---


