# This python file stores the defaults

################################################################################
# Default Adflow solver options for Aerodynamic problem
################################################################################
default_aero_options_aerodynamic = {
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
    "nSubiterTurb": 5,
    "ANKSecondOrdSwitchTol": 1e-4,
    "ANKCoupledSwitchTol": 1e-6,
    "ankinnerpreconits": 2,
    "ankouterpreconits": 2,
    "anklinresmax": 0.1,
    # Termination Criteria
    "L2Convergence": 1e-12,
    "L2ConvergenceCoarse": 1e-2,
    "nCycles": 75000,
}

################################################################################
# Default Adflow solver options for AeroStructural problem
################################################################################
default_aero_options_aerostructural = {
    # Print Options
    "printIterations": False,
    "printAllOptions": False,
    "printIntro": False,
    "printTiming": False,
    # I/O Parameters
    "gridFile": f"grids/naca0012_L1.cgns", # Default grid file
    "outputDirectory": '.', 
    "monitorvariables": ["resrho", "resturb", "cl", "cd", "yplus"],
    "writeTecplotSurfaceSolution": True,
    # Physics Parameters
    "equationType": "RANS",
    "liftindex": 3,  # z is the lift direction
    # Solver Parameters
    "smoother": "DADI",
    "CFL": 1.5,
    "CFLCoarse": 1.25,
    "MGCycle": "sg",
    "MGStartLevel": -1,
    "nCyclesCoarse": 250,
    # ANK Solver Parameters
    "useANKSolver": True,
    "nSubiterTurb": 10,
    "ANKSecondOrdSwitchTol": 1e-6,
    "ANKCoupledSwitchTol": 1e-8,
    "ankinnerpreconits": 2,
    "ankouterpreconits": 2,
    "anklinresmax": 0.1,
    # Termination Criteria
    "L2Convergence": 1e-14,
    "L2ConvergenceCoarse": 1e-2,
    "L2ConvergenceRel": 1e-4,
    "nCycles": 10000,
    # force integration
    "forcesAsTractions": False,
}
################################################################################
# Default structural properties for aerostructural problems
################################################################################
default_structural_properties = {
    # Material Properties
    'rho': 2500.0,      # Density in kg/m^3
    'E': 70.0e9,        # Young's modulus in N/m^2
    'nu': 0.30,         # Poisson's ratio
    'kcorr': 5.0/6.0,   # Shear correction factor
    'ys': 350.0e6,      # Yeild stress

    # Shell Thickness
    't': 0.01,          # in m
}

################################################################################
# Python script to run subprocesses - DO NOT MODIFY
################################################################################
python_code_for_subprocess = """
import argparse
from mdss.aerostruct import run_problem

parser = argparse.ArgumentParser()
parser.add_argument("--caseInfoFile", type=str)
parser.add_argument("--expInfoFile", type=str)
parser.add_argument("--refLevelDir", type=str)
parser.add_argument("--aoaList", type=str)
parser.add_argument("--aeroGrid", type=str)
parser.add_argument("--structMesh", type=str)

args = parser.parse_args()

run_problem(args.caseInfoFile, args.expInfoFile, args.refLevelDir, args.aoaList, args.aeroGrid, args.structMesh)
"""

################################################################################
# Python script to run on a HPC - DO NOT MODIFY
################################################################################
python_code_for_hpc = """
import argparse
from mdss.run_sim import run_sim

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile", type=str)
args = parser.parse_args()
sim = run_sim(args.inputFile) # Input the simulation info and output dir
sim.run_problem() # Run the simulation
"""

################################################################################
# Template for Greatlakes Job script
################################################################################
gl_job_script = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={nproc}
#SBATCH --ntasks-per-node=36
#SBATCH --cpus-per-task=1
#SBATCH --exclusive
#SBATCH --mem-per-cpu={mem_per_cpu}
#SBATCH --time={time}
#SBATCH --account={account_name}
#SBATCH --partition=standard
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user={email_id}
#SBATCH --output={out_dir}/{out_file}

python {python_file_path} --inputFile {yaml_file_path}
"""
