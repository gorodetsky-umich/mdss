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
    "outputDirectory": '.', 
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
    "L2ConvergenceRel": 1e-3,
    "nCycles": 10000,
    # force integration
    "forcesAsTractions": False,
}

################################################################################
# Default structural properties for aerostructural problems
################################################################################
default_struct_properties = {
    # Material Properties
    'rho': 2500.0,      # Density in kg/m^3
    'E': 70.0e9,        # Young's modulus in N/m^2
    'nu': 0.30,         # Poisson's ratio
    'kcorr': 5.0/6.0,   # Shear correction factor
    'ys': 350.0e6,      # Yield stress
}

################################################################################
# Default solver options for AeroStructural problem
################################################################################
default_solver_options = {
    'linear_solver_options': {
        'atol': 1e-08, # absolute error tolerance
        'err_on_non_converge': True, # When True, AnalysisError will be raised if not converged
        'maxiter': 25, # maximum number of iterations
        'rtol': 1e-8, # relative error tolerance
        'use_aitken': True, # set to True to use Aitken
    },

    'nonlinear_solver_options': {
        'atol': 1e-08, # absolute error tolerance
        'err_on_non_converge': True, # When True, AnalysisError will be raised if not converged
        'reraise_child_analysiserror': False, # When the option is true, a solver will reraise any AnalysisError that arises during sub-solve; when false, it will continue solving.
        'maxiter': 25, # maximum number of iterations
        'rtol': 1e-08, # relative error tolerance
        'use_aitken': True, # set to True to use Aitken
        'iprint': 2
    }
}

################################################################################
# Default structural options for aerostructural problems
################################################################################
default_struct_options = {
    'iysm': 1, # y-symmetry
}

################################################################################
# Default load info for aerostructural problems
################################################################################
default_load_info = {
    'g': [0.0, -9.81, 0.0], # acceleration due to gravity in m/s^2
    'inertial_load_factor': 1.0 # inertial load factor, times of 'g'
}