# Dependencies and Installation

## Required Libraries
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

## Installation Instructions
To install `simulateTestCases`, use the following commands:

1. Clone the repository:

    ```
    git clone https://github.com/gorodetsky-umich/simulateTestCases.git
    ```

2. Navigate into the directory:

    ```
    cd simulateTestCases
    ```

3. To install the package without dependencies:

    ```
    pip install .
    ```

    To install the package along with dependencies listed in `requirements.txt`:

    ```
    pip install . -r requirements.txt
    ```

    For an editable installation:
    
    ```
    pip install -e .
    ```