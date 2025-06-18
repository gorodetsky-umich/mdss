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
    "outputDirectory": ".",
    "monitorvariables": ["resrho", "resturb", "cl", "cd", "yplus"],
    "writeTecplotSurfaceSolution": True,
    "solutionPrecision": "double", #  Best for restart
    "volumeVariables": ['resrho', 'mach'],
    # Physics Parameters
    "equationType": "RANS",
    "liftindex": 3,  # z is the lift direction
    # ANK Solver Parameters
    "useANKSolver": True,
    # Termination Criteria
    "L2Convergence": 1e-12,
    "L2ConvergenceCoarse": 1e-2,
    "nCycles": 75000,
}

