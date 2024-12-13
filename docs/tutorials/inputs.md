# Inputs

The `simulateTestCases` package requires the following inputs to configure and execute simulations:

---

## YAML Configuration File

A YAML file is required to define the simulation parameters and organize test cases. The YAML file structure and respective descriptions are given below.

### Input YAML file Structure

The YAML file organizes simulation data into a structured hierarchy, enabling clear configuration of cases and experimental conditions. Below is the structure used in the YAML file:

```yaml
out_dir: # str, path to the output directory
hpc: # str, 'yes' or 'no'
hpc_info: # dict, only needed if hpc is yes
  cluster: # str, name of the cluste. GL for Great Lakes
  job_name: # str, name of the job
  nodes: # int, number of nodes
  nproc: # int, total number of processors
  time: #str, time in D-H:M:S format
  account_name: # str, account name
  email_id: # str
hierarchies: # list, List of hierarchies
# First hierarchy
- name: # str, name of the hierarchy
  cases: # list, list of cases in this hierarchy
  # First case in the hierarchy
  - name: # str, name of the case
    meshes_folder_path: # str, path to the floder containing the mesh files for this case
    mesh_files: # list, list of mesh file names
    - # str, name of the finest mesh
    - # str, .
    - # str, .
    - # str, name of the corasest mesh
    geometry_info: # dict, dictionary of geometry info
      chordRef: # float, reference chord length
      areaRef: # flaot, reference area
    solver_parameters: # dict, dictionary of solver parameters. For more information see solver parameters section
      # ......
    exp_sets: # list, list of dictionaries contating experimental info
    # First experimental set in current case
    - aoa_list: # list, list of angle of attacks(AoA) to run in with the experimental info
      Re: # float, Reynold's number 
      mach: # float, Mach number
      Temp: # float, Temperature in Kelvin scale
      exp_data: # str, path to experimental data
    
    # Second experimental set in current case

  # Second case in current hierachy

# Second hierarchy
```

Please note that adherence to this structure is essential; any deviation may lead to errors when running simulations. Examples of correctly formatted YAML files are provided in the `examples/inputs` folder.

The yaml script can also be used as a starting point for generating custom YAML files.

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
---


