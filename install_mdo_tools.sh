#!/bin/bash

# @File    : install_mdo_tools.sh
# @Time    : 3/12/2024
# @Desc    : Clean setup MACH-AERO on a local system
# @Author  : Galen Ng, edited by Sanjan CM

# ==============================================================================
#                             Common variables
# ==============================================================================

PWD=$(pwd)
CHK_DIR="$PWD/.mach_install"
BASHRC="$HOME/.bashrc"

MDOLAB_PACKAGES_DIR="$PWD/packages"
COMPILERS="GCC"

PIP="python3 -m pip"

PYTHON_VERSION="3.11.1"
NUMPY_VERSION="1.25.2"
SCIPY_VERSION="1.11.1"
MPI4PY_VERSION="3.1.4"

CGNS_VERSION="4.3.0"
CGNS_OPT_FLAGS="-O3"

OPENMPI_VERSION="4.1"

PETSC_VERSION="3.18.5"
PETSC_OPT_FLAGS="-O3"

ARCH_FLAGS=""
MACRH_OPT_FLAGS=""

# ==============================================================================
#                             Functions
# ==============================================================================
die() {
    echo "Something happened in $1, Stopping. Manual cleanup might be needed."
    exit 1
}

success() {
    local chk_file="$CHK_DIR/$1"
    mkdir -p $CHK_DIR && touch $chk_file
}

install() {
    local chk_file="$CHK_DIR/$1"
    local repo_dir="$MDOLAB_PACKAGES_DIR/$1"
    echo "Preparing to install $1"
    if [[ -f $chk_file ]]; then
        echo "$1 has already been installed... skipping"
        return 1
    fi
    if [[ -d $repo_dir ]]; then
        echo "Directory $repo_dir exists... deleting"
        rm -rf $repo_dir
    fi
    return 0
}

create_mdolab_dirs() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    mkdir -p $MDOLAB_PACKAGES_DIR

    success "$name"
}

setup_dependencies() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    sudo apt-get update -y
    sudo apt-get upgrade -y

    # List of packages to check and install if missing
    packages=(
        build-essential
        gfortran
        cmake
        git
        wget
        libopenblas-dev
        libhdf5-dev
        mpich
        libmpich-dev
        python3
        python3-pip
    )

    for package in "${packages[@]}"; do
        if dpkg -s "$package" &> /dev/null; then
            echo "$package is already installed."
        else
            echo "Installing $package..."
            sudo apt-get install -y "$package"
        fi
    done

    success "$name"
}

setup_python_env() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    ENV_NAME="mdo"

    # Function to check if a command exists
    command_exists() {
        command -v "$1" &>/dev/null
    }

    # Ensure all required dependencies for pyenv are installed
    REQUIRED_PACKAGES=(
        make build-essential libssl-dev zlib1g-dev libbz2-dev
        libreadline-dev libsqlite3-dev wget curl llvm
        libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev
        liblzma-dev libgdbm-dev libnss3-dev libgdbm-compat-dev
    )

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! dpkg -s "$package" &>/dev/null; then
            echo "Installing missing dependency: $package"
            sudo apt-get install -y "$package"
        else
            echo "Dependency $package is already installed."
        fi
    done

    # Check if pyenv is installed and available
    if ! command_exists pyenv; then
        echo "Installing pyenv..."
        curl https://pyenv.run | bash

        # Add pyenv to bashrc if not already added
        if ! grep -Fxq 'export PYENV_ROOT="$HOME/.pyenv"' $BASHRC; then
            echo 'export PYENV_ROOT="$HOME/.pyenv"' >> $BASHRC
            echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> $BASHRC
            echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init --path)"\nfi' >> $BASHRC
            echo 'eval "$(pyenv init -)"' >> $BASHRC
            echo 'eval "$(pyenv virtualenv-init -)"' >> $BASHRC
        fi

        echo "Pyenv installed. Please restart your shell and re-run this script."
        exit 0
    fi

    # Ensure the current shell session is updated with the new pyenv settings
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    # Install pyenv-virtualenv if not already installed
    if [ ! -d "$PYENV_ROOT/plugins/pyenv-virtualenv" ]; then
        git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
        eval "$(pyenv virtualenv-init -)"
    fi

    # Install the specified version of Python if not already installed
    if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
        pyenv install "$PYTHON_VERSION"
    fi

    # Create a virtual environment with the specified name if not already created
    if ! pyenv virtualenvs --bare | grep -qx "$ENV_NAME"; then
        pyenv virtualenv "$PYTHON_VERSION" "$ENV_NAME"
    fi

    # Activate the virtual environment
    pyenv activate "$ENV_NAME"

    # Upgrade pip and install required packages
    pip install --upgrade pip
    pip install wheel parameterized testflo cython numpy==$NUMPY_VERSION scipy==$SCIPY_VERSION mpi4py==$MPI4PY_VERSION

    success "$name"
}

# ************************************************
#    3rd party packages
# ************************************************
cgnslib() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    CGNS_INSTALL_DIR="$MDOLAB_PACKAGES_DIR/CGNS"

    # Check if CGNS library already exists
    if [ -d "$CGNS_INSTALL_DIR" ] && [ -f "$CGNS_INSTALL_DIR/lib/libcgns.a" ]; then
        echo "CGNS is already installed at $CGNS_INSTALL_DIR."

        # Add CGNS environment variables to .bashrc
        if ! grep -Fxq "# -- CGNS" $BASHRC; then
            echo "# -- CGNS" >> $BASHRC
            echo "export CGNS_HOME=$CGNS_INSTALL_DIR" >> $BASHRC
            echo "export PATH=\$PATH:\$CGNS_HOME/bin" >> $BASHRC
            echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$CGNS_HOME/lib" >> $BASHRC
        else
            echo "CGNS environment variables already added to $BASHRC."
        fi

        return 0
    fi

    . $BASHRC
    cd $MDOLAB_PACKAGES_DIR
    wget -nv https://github.com/CGNS/CGNS/archive/v$CGNS_VERSION.tar.gz
    tar -xzf v$CGNS_VERSION.tar.gz
    cd CGNS-$CGNS_VERSION
    cmake -D CGNS_ENABLE_FORTRAN=ON \
          -D CMAKE_INSTALL_PREFIX=$CGNS_INSTALL_DIR \
          -D CGNS_ENABLE_64BIT=OFF \
          -D CGNS_ENABLE_HDF5=OFF \
          -D CMAKE_C_FLAGS="-fPIC" \
          -D CMAKE_Fortran_FLAGS="-fPIC" .
    make install || die "cgns install command failed"

    # Add CGNS environment variables to .bashrc
    if ! grep -Fxq "# -- CGNS" $BASHRC; then
        echo "# -- CGNS" >> $BASHRC
        echo "export CGNS_HOME=$CGNS_INSTALL_DIR" >> $BASHRC
        echo "export PATH=\$PATH:\$CGNS_HOME/bin" >> $BASHRC
        echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$CGNS_HOME/lib" >> $BASHRC
    else
        echo "CGNS environment variables already added to $BASHRC."
    fi

    success "$name"
}

openmpi() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    OPENMPI_INSTALL_DIR="$MDOLAB_PACKAGES_DIR/openmpi-$OPENMPI_VERSION.0"
    MPI_INSTALL_DIR="$OPENMPI_INSTALL_DIR/opt-gfortran"

    # Check if OpenMPI library already exists
    if [ -d "$MPI_INSTALL_DIR" ] && [ -f "$MPI_INSTALL_DIR/bin/mpicc" ]; then
        echo "OpenMPI is already installed at $MPI_INSTALL_DIR."
    else
        . $BASHRC
        cd $MDOLAB_PACKAGES_DIR
        wget -nv https://download.open-mpi.org/release/open-mpi/v$OPENMPI_VERSION/openmpi-$OPENMPI_VERSION.0.tar.gz
        tar -xzf openmpi-$OPENMPI_VERSION.0.tar.gz
        cd openmpi-$OPENMPI_VERSION.0
        ./configure --prefix=$OPENMPI_INSTALL_DIR
        make all install || die "configure/compile/test openmpi failed"
        which mpicc || die "openmpi install failed"

        # Add PETSc environment variables to .bashrc
        if ! grep -Fxq "# -- OpenMPI Installation" $BASHRC; then
            echo "# -- OpenMPI Installation" >> $BASHRC
            echo "export MPI_INSTALL_DIR=$OPENMPI_INSTALL_DIR/opt-gfortran" >> $BASHRC
            echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$MPI_INSTALL_DIR/lib" >> $BASHRC
            echo "export PATH=\$MPI_INSTALL_DIR/bin:\$PATH" >> $BASHRC
        else
            echo "MPI environment variables already added to $BASHRC."
        fi
    fi

    success "$name"
}

petsc_real() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    PETSC_INSTALL_DIR="$MDOLAB_PACKAGES_DIR/petsc-$PETSC_VERSION"
    PETSC_ARCH="real-debug"
    
    # Check if PETSc library already exists
    if [ -d "$PETSC_INSTALL_DIR" ] && [ -f "$PETSC_INSTALL_DIR/real-debug/lib/libpetsc.so" ]; then
        echo "PETSc is already installed at $PETSC_INSTALL_DIR."
    else
        . $BASHRC
        cd $MDOLAB_PACKAGES_DIR
        wget -nv http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-$PETSC_VERSION.tar.gz
        tar -xzf petsc-lite-$PETSC_VERSION.tar.gz
        cd petsc-$PETSC_VERSION
        ./configure --PETSC_ARCH=$PETSC_ARCH \
                    --with-scalar-type=real \
                    --with-debugging=1 \
                    --download-metis=yes \
                    --download-parmetis=yes \
                    --download-superlu_dist=yes \
                    --with-shared-libraries=yes \
                    --with-fortran-bindings=1 \
                    --with-cxx-dialect=C++11 \
                    # --with-mpi-dir=$MPI_INSTALL_DIR \
        make all || die "configure/compile/test petsc real failed"
    fi

    # Install petsc4py
    cd $PETSC_INSTALL_DIR/src/binding/petsc4py
    $PIP install . || die "petsc4py real failed"

    # Add PETSc environment variables to .bashrc
    if ! grep -Fxq "# -- PETSc Installation" $BASHRC; then
        echo "# -- PETSc Installation" >> $BASHRC
        echo "export PETSC_ARCH=arch-real-debug" >> $BASHRC
        echo "export PETSC_DIR=$PETSC_INSTALL_DIR" >> $BASHRC
    else
        echo "PETSc environment variables already added to $BASHRC."
    fi

    success "$name"
}

git_clone() {
    git clone https://github.com/mdolab/"$1".git || die "cloning $1 failed"
}

# ************************************************
#     MACH-Aero layer
# ************************************************

# Function to activate the python environment
activate_python_env() {
    local ENV_NAME="mdo"
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    pyenv activate $ENV_NAME
}

baseclasses() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "baseclasses"
    cd baseclasses
    $PIP install $PIP_DEV . || return

    success "$name"
}

pyspline() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "pyspline"
    cd pyspline
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

pygeo() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "pygeo"
    cd pygeo
    $PIP install $PIP_DEV .[testing] || return

    success "$name"
}

idwarp() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "idwarp"
    cd idwarp
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

adflow() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "adflow"
    cd adflow
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

cgnsutilities() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "cgnsutilities"
    cd cgnsutilities
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

pyhyp() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "pyhyp"
    cd pyhyp
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

pyoptsparse() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git_clone "pyoptsparse"
    cd pyoptsparse
    $PIP install $PIP_DEV . || return

    success "$name"
}

openmdao(){
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git clone http://github.com/OpenMDAO/OpenMDAO
    cd OpenMDAO
    $PIP install $PIP_DEV . || return

    success "$name"
}

mphys(){
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    activate_python_env
    cd $MDOLAB_PACKAGES_DIR
    git clone https://github.com/OpenMDAO/mphys.git
    cd mphys
    $PIP install $PIP_DEV . || return

    success "$name"
}

# ==============================================================================
#                             RUN COMMANDS
# ==============================================================================
rm -rf .mach_install

# Compiler Dependencies
setup_dependencies || die "setup dependencies failed"
create_mdolab_dirs || die "create mdolab directories failed"

# Python environment
setup_python_env || die "python environment setup failed"

# Other dependencies
cgnslib || die "cgnslib install failed"
openmpi || die "openmpi install failed"
petsc_real || die "petsc real install failed"

# MACH-Aero layer
baseclasses || die "baseclasses install failed"
pyspline || die "pyspline install failed"
pygeo || die "pygeo install failed"
idwarp || die "idwarp install failed"
adflow || die "adflow install failed"
cgnsutilities || die "cgnsutilities install failed"
pyhyp || die "pyhyp install failed"
pyoptsparse || die "pyoptsparse install failed"
openmdao || die "openmdao install failed"
mphys || die "mphys install failed"

exit 0