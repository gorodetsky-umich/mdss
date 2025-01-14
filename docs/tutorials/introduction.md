# Introduction
The `simulateTestCases` package is a Python-based tool designed to streamline the execution and data management of ADflow simulations. It integrates with MPhys to provide a structured framework for running aerodynamic flow simulations and organizing the resulting data in a hierarchical manner.

This package is particularly suited for projects involving multiple configurations or test cases, ensuring that simulation results are stored and categorized systematically.

### Key Features
- Automates the execution of multiple ADflow simulation cases.
- Allows the user to choose to run the simulations as subprocesses.
- Utilizes YAML configuration files for defining simulation parameters and organizing cases.
- Stores simulation data in a structured directory hierarchy for ease of access and analysis.
- Supports post-processing with methods for comparing results to experimental data and generating plots.

### Inputs

The `simulateTestCases` package requires the following inputs:

1. **YAML Configuration File:**

    **A YAML file specifying:**

    - Simulation hierarchy.
    - Mesh files and solver parameters.
    - Experimental conditions (e.g., Reynolds number, Mach number, and angle of attack).

2. **Output Directory:**

    A directory path where the simulation results will be saved. The structure of this directory mirrors the hierarchy defined in the YAML file.

### Outputs

The outputs of `simulateTestCases` are stored in directories organized according to the simulation hierarchy. These include:

1. **Simulation Data:**

    Results such as C_L, C_D, and Wall Time are saved in CSV and YAML formats.

2. **Hierarchical Directory Structure:**

    Output directories follow the YAML-defined hierarchy, allowing for easy navigation of results.

3. **Visualization:**

    Comparison plots (e.g., experimental vs. simulated data) are generated in PNG format.

### Example Hierarchy

The package organizes simulation data into a clear and logical hierarchy. An example of this structure, that has been used in the tutorials is shown below:

```
Aero Problem
    |
    |---- 2D Clean
    |       |
    |       |---- NACA 0012
    |
    |---- 2D High-Lift
    |       |
    |       |---- Mc Donnell Dolugas 30P-30N
    |
    |---- 3D Clean
    |       |
    |       |---- NASA CRM clean Configuration
    |
    |---- 3D High-Lift
            |
            |---- DLR High-Lift Configuration
```
Explanation of the Hierarchy:

1. **Aero Problem:** Categorizes the type of aerodynamic analysis, such as clean flow or high-lift studies, in 2D or 3D configurations.

2. **2D Clean:** Simulations for 2D configurations without high-lift devices (e.g., NACA 0012 airfoil).

3. **2D High-Lift:** Simulations for 2D configurations with high-lift devices (e.g., McDonnell Douglas 30P-30N airfoil).

4. **3D Clean:** Simulations for 3D configurations without high-lift devices (e.g., NASA Common Research Model Clean Configuration).

5. **3D High-Lift:** Simulations for 3D configurations with high-lift devices (e.g., DLR High-Lift Configuration).