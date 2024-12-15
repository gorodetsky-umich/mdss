# Installation and dependencies

## Installation innstructions
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
## Dependencies
The framework requires tools built by NASA (OpenMDAO and MPhys) and the MDO lab (MACH-Aero framework). The [MACH-Aero](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/index.html) framework houses all the core packages needed to run CFD simulations. A detailed list of all packages follow:

### Softwares
- [`OpenMDAO`](https://github.com/OpenMDAO/OpenMDAO)
- [`MPhys`](https://github.com/OpenMDAO/mphys)
- [`baseClasses`](https://github.com/mdolab/baseclasses)
- [`pySpline`](https://github.com/mdolab/pyspline)
- [`pyGeo`](https://github.com/mdolab/pygeo)
- [`IDWarp`](https://github.com/mdolab/idwarp)
- [`ADflow`](https://github.com/mdolab/adflow)
- [`pyOptSparse`](https://github.com/mdolab/pyoptsparse)
- `TACS` - maybe later

Most of the above software packages have additional third party dependencies such as PETSc, OpenMPI etc.., a detailed guide for installing them from scratch can be found [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/installFromScratch.html). A custom bash script file is provided as well that will aid in installation.

However, we suggest using Docker. Images are available for both GCC and INTEL compilers [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/dockerInstructions.html#). If you are not familiar with docker, we recommend going through the official documentation [here](https://docs.docker.com/).

Once you pull an image compatible with your machine's architecture, you can follow the instructions mentioned [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/dockerInstructions.html#) to initialize and start a container. Once in the container, clone this repository in the mount directory and install it. Note that if you are referencing any paths inside the container, they must be with respect to the container's folder architecture, not your host machine.

### Python libraries
The following python libraries are required for the framework and can be installed with `pip`:

- `numpy>=1.21`
- `scipy>=1.7`
- `mpi4py>=3.1.4`
- `pyyaml`
- `matplotlib`
- `pandas`
- `petsc4py`

## HPC section - yet to be completed
