# simulateTestCases

`simulateTestCases` is a Python package designed for running a series of ADflow simulations using mphys and OpenMDAO. This package provides streamlined functions to automate simulation test cases.

## Features

- Simplifies running multiple simulation cases with ADflow.
- Integrates with mphys and OpenMDAO and provides a framework for data management.
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
