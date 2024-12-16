#!/bin/bash

# @File    : install_softwares.sh
# @Date    : 12/16/2024
# @Desc    : Clean setup MACH-AERO on Great Lakes
# @Author  : Sanjan CM

# ==============================================================================
#                             Common variables
# ==============================================================================

PWD=$(pwd)
CHK_DIR="$PWD/.mach_install"
BASHRC="$HOME/.bashrc"

MDOLAB_PACKAGES_DIR="$PWD/packages"
COMPILERS="GFORTRAN"

PIP="python3 -m pip"

# Python libraries versions
PYTHON_VERSION="3.9.12"
NUMPY_VERSION="1.21.2"
SCIPY_VERSION="1.7.3"
MPI4PY_VERSION="3.1.4"
PETSC4PY_VERSION="3.15.1"

# External installation versions
PETSC_VERSION="3.15.3"
CGNS_VERSION="4.4.0"

# Delete these later

PETSC_OPT_FLAGS="-O3"
CGNS_OPT_FLAGS="-O3"

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

install_python_libraries() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    # Upgrade pip and install required packages
    $PIP install --upgrade pip
    $PIP install wheel parameterized testflo cython numpy==$NUMPY_VERSION scipy==$SCIPY_VERSION mpi4py==$MPI4PY_VERSION

    success "$name"
}

# ************************************************
#    3rd party packages
# ************************************************

petsc() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    PETSC_INSTALL_DIR="$MDOLAB_PACKAGES_DIR/petsc-$PETSC_VERSION"
    PETSC_ARCH="real-opt"
    
    # Check if PETSc library already exists
    if [ -d "$PETSC_INSTALL_DIR" ] && [ -f "$PETSC_INSTALL_DIR/real-debug/lib/libpetsc.so" ]; then
        echo "PETSc is already installed at $PETSC_INSTALL_DIR."
    else
        . $BASHRC
        cd $MDOLAB_PACKAGES_DIR
        wget -nv http://ftp.mcs.anl.gov/pub/petsc/release-snapshots/petsc-lite-$PETSC_VERSION.tar.gz
        tar -xzf petsc-lite-$PETSC_VERSION.tar.gz
        cd petsc-$PETSC_VERSION
        ./configure --with-shared-libraries --download-superlu_dist --download-parmetis=yes --download-metis=yes \
   --with-fortran-bindings=1 --with-debugging=0 --with-scalar-type=real --PETSC_ARCH=$PETSC_ARCH --with-cxx-dialect=C++11

        make PETSC_DIR=$PETSC_INSTALL_DIR PETSC_ARCH=$PETSC_ARCH all || die "configure/compile/test petsc real failed"

        make PETSC_DIR=$PETSC_INSTALL_DIR PETSC_ARCH=$PETSC_ARCH check
    fi

    # Install petsc4py
    $PIP install petsc4py==$PETSC4PY_VERSION --no-cache || die "petsc4py real failed"

    success "$name"
}

cgnslib() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    CGNS_HOME="$MDOLAB_PACKAGES_DIR/CGNS-$CGNS_VERSION/opt-gfortran"

    # Check if CGNS library already exists
    if [ -d "$CGNS_HOME" ] && [ -f "$CGNS_HOME/lib/libcgns.a" ]; then
        echo "CGNS is already installed at $CGNS_HOME."
        return 0
    fi

    CMAKE_C_COMPILER=$(which gcc)
    CMAKE_Fortran_COMPILER=$(which gfortran)

    . $BASHRC
    cd $MDOLAB_PACKAGES_DIR
    wget -nv https://github.com/CGNS/CGNS/archive/v$CGNS_VERSION.tar.gz
    tar -xzf v$CGNS_VERSION.tar.gz
    cd CGNS-$CGNS_VERSION
    cmake -D CGNS_ENABLE_FORTRAN=ON \
          -D CMAKE_INSTALL_PREFIX=$CGNS_HOME \
          -D CGNS_ENABLE_64BIT=OFF \
          -D CGNS_ENABLE_HDF5=OFF \
          -D CMAKE_C_FLAGS="-fPIC" \
          -D CMAKE_Fortran_FLAGS="-fPIC" .\
          -D CMAKE_C_COMPILER=$CMAKE_C_COMPILER \
          -D CMAKE_Fortran_COMPILER=$CMAKE_Fortran_COMPILER
    make install || die "cgns install command failed"

    success "$name"
}

# ************************************************
#     MACH-Aero layer
# ************************************************

git_clone() {
    git clone https://github.com/mdolab/"$1".git || die "cloning $1 failed"
}

baseclasses() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    cd $MDOLAB_PACKAGES_DIR
    git_clone "baseclasses"
    cd baseclasses
    $PIP install $PIP_DEV . || return

    success "$name"
}

pyspline() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

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

    cd $MDOLAB_PACKAGES_DIR
    git_clone "pygeo"
    cd pygeo
    $PIP install $PIP_DEV .[testing] || return

    success "$name"
}

idwarp() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

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

    cd $MDOLAB_PACKAGES_DIR
    git_clone "adflow"
    cd adflow
    cp config/defaults/config.LINUX_$COMPILERS.mk config/config.mk

    make
    $PIP install $PIP_DEV . || return

    success "$name"
}

pyoptsparse() {
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    cd $MDOLAB_PACKAGES_DIR
    git_clone "pyoptsparse"
    cd pyoptsparse
    $PIP install $PIP_DEV . || return

    success "$name"
}

openmdao(){
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    cd $MDOLAB_PACKAGES_DIR
    git clone http://github.com/OpenMDAO/OpenMDAO
    cd OpenMDAO
    $PIP install $PIP_DEV . || return

    success "$name"
}

mphys(){
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    cd $MDOLAB_PACKAGES_DIR
    git clone https://github.com/OpenMDAO/mphys.git
    cd mphys
    $PIP install $PIP_DEV . || return

    success "$name"
}

mach_aero(){
    local name="${FUNCNAME[0]}"
    install "$name" || return 0

    cd $MDOLAB_PACKAGES_DIR
    git_clone "MACH-Aero"

    success "$name"
}

# ==============================================================================
#                             RUN COMMANDS
# ==============================================================================
rm -rf .mach_install

# Create folder and install python dependencies
create_mdolab_dirs || die "create mdolab directories failed"
install_python_libraries || die "install python libraries failed"

# # Other dependencies
petsc || die "petsc real install failed"
cgnslib || die "cgnslib install failed"

# # MACH-Aero layer
baseclasses || die "baseclasses install failed"
pyspline || die "pyspline install failed"
pygeo || die "pygeo install failed"
idwarp || die "idwarp install failed"
adflow || die "adflow install failed"
pyoptsparse || die "pyoptsparse install failed"

# NASA tools
openmdao || die "openmdao install failed"
mphys || die "mphys install failed"

# The MACH-AERO package
mach_aero || die "mach_aero install failed"

exit 0