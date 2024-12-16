# Installation and Dependencies

## Dependencies

### Core Framework Dependencies
The framework requires tools developed by NASA (OpenMDAO and MPhys) and the MDO Lab (MACH-Aero framework). The [MACH-Aero](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/index.html) framework houses all the core packages needed to run CFD simulations. Below is the list of software required:

- [`OpenMDAO`](https://github.com/OpenMDAO/OpenMDAO)
- [`MPhys`](https://github.com/OpenMDAO/mphys)
- [`baseClasses`](https://github.com/mdolab/baseclasses)
- [`pySpline`](https://github.com/mdolab/pyspline)
- [`pyGeo`](https://github.com/mdolab/pygeo)
- [`IDWarp`](https://github.com/mdolab/idwarp)
- [`ADflow`](https://github.com/mdolab/adflow)
- [`pyOptSparse`](https://github.com/mdolab/pyoptsparse)
- `TACS` (optional)

These software packages may have additional third-party dependencies like PETSc and OpenMPI. A detailed guide for installing them from scratch is available [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/installFromScratch.html).

### Python Libraries
The following Python libraries are required and can be installed via `pip`:

- `numpy>=1.21`
- `scipy>=1.7`
- `mpi4py>=3.1.4`
- `pyyaml`
- `matplotlib`
- `pandas`
- `petsc4py`

---
## Getting Started

### Installation of Dependencies

#### From Scratch
To manually install all dependencies:

1. Refer to the [Scratch Installation Guide](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/installFromScratch.html).
2. A custom bash script `install_packages.sh` is available in this repository to automate the process. Follow `STEP 2` in the [Scratch Installation](#scratch-installation) section.

#### Using Docker
Docker is highly recommended for ease of installation:

1. Pull a Docker image compatible with your machine's architecture. Official images for GCC and INTEL compilers are available [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/dockerInstructions.html).
2. Follow the [Docker Guide](https://docs.docker.com/) to set up Docker.
3. Initialize and start a container, mount the directory, and install this package. instructions mentioned [here](https://mdolab-mach-aero.readthedocs-hosted.com/en/latest/installInstructions/dockerInstructions.html#initialize-docker-container) to initialize and start a container.
4. Once in the container, follow the instructions in the [Package Installation](#package-installation) section to clone this repository in the mount directory and install it. 

**_Note: If you are referencing any paths inside the container, they must be with respect to the container's folder architecture, not your host machine._**

#### HPC Systems
For installation on HPC clusters like Great Lakes or NASA HECC:

1. Install dependencies as modules or compile them manually. Most packages are available in HPC environments as modules.
2. Follow the [Scratch Installation](#scratch-installation) instructions.

---

### Package Installation

The following steps are common for personal computers and HPC systems:

1. Clone the repository:
    ```
    git clone https://github.com/gorodetsky-umich/simulateTestCases.git
    ```
2. Navigate into the directory:
    ```
    cd simulateTestCases
    ```
3. Install the package:
    - Without dependencies:
        ```
        pip install .
        ```
    - With dependencies:
        ```
        pip install . -r requirements.txt
        ```
    - Editable installation:
        ```
        pip install -e .
        ```

---

### Scratch Installation

#### HPC Cluster Setup (e.g., Great Lakes)

1. Add the following lines to your `~/.bashrc` file:
    ```bash
    # Module loads
    module load gcc
    module load openmpi
    module load python/3.9.12
    module load cmake

    # PETSc Installation
    export PETSC_ARCH=real-opt
    export PETSC_DIR=<directory-path>/packages/petsc-3.15.3

    # CGNS Installation
    export CGNS_HOME=<directory-path>/packages/CGNS-4.4.0/opt-gfortran
    export PATH=$PATH:$CGNS_HOME/bin
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CGNS_HOME/lib
    ```
    Replace `<directory-path>` with your installation directory path. Do not forget to `source ~/.bashrc` after editing.

2. Clone the repository:
    ```
    git clone https://github.com/gorodetsky-umich/simulateTestCases.git
    ```

    Copy and execute the installation script:
    ```
    $ cd simulateTestCases

    $ cp simulateTestCases/install_packages_gl.sh <directory-path>/
    
    $ chmod +x install_packages_gl.sh

    $ ./install_packages_gl.sh
    ```

---

### Singularity
(*To Be Documented*)
