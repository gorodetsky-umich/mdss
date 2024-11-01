# simulateTestCases

`simulateTestCases` is a Python package designed for running a series of ADflow simulations using mphys and OpenMDAO. This package provides streamlined functions to automate simulation test cases, making it ideal for users working on computational fluid dynamics (CFD) applications.

## Features

- Simplifies running multiple simulation cases with ADflow.
- Integrates with mphys and OpenMDAO for optimization and workflow management.
- Supports analysis and post-processing of simulation results.

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
from simulateTestCases import SimulationRunner

# Initialize the runner with configuration file
runner = SimulationRunner(config_path="path/to/config.yaml")

# Run the simulation series
results = runner.run_all_cases()

# Analyze results
runner.plot_results(results)
