## Python file to modify data and store it in an yaml file format
 
import yaml
import numpy as np

data = {
    'level_1':{
        'hierarchy': '2d_clean',
        'cases': {
            '1': {
                'name': 'NACA0012',
                'nRefinement': 1,
                'mesh_file': '../grids/naca0012', # Add the refinement level and exptention later.
                'geometry_info': {
                    'chordRef': 1.0,
                    'areaRef': 1.0,
                },
                'solver_parameters':{
                    # ANK Solver Parameters
                    "useANKSolver": True,
                    "nSubiterTurb": 20,
                    # NK Solver Parameters
                    "useNKSolver": False,
                    "NKSwitchTol": 1e-6,
                    # Coupled Solver Parameters
                    "ANKCoupledSwitchTol": 1e-3,
                    # Second order Solver Parameters
                    "ANKSecondOrdSwitchTol": 1e-12,
                    # Convergence Criterion
                    "L2Convergence": 1e-8,
                    "nCycles": 150000,
                },
                'aoa_info': [0,10,5], # Info to construct array of aoa [start, end, interval]
                'exp_set': { 
                    '1': {
                        'Re': 1e6, # Reynold's number
                        'mach': 0.7, # Mach number
                        'Temp': 298.0, # Temperature at which experiment was conducted in kelvin
                        'exp_data': 'exp_data/naca0012.txt', # Modify as required.
                    }
                    
                },
            }
        },
    },
    'level_2':{
        'hierarchy': '2d_high_lift',
        'cases': {
            '1': {
                'name': '30p-30n',
                'nRefinement': 3,
                'mesh_file': '../grids/30p-30n_IHC', # Add the refinement level and exptention later.
                'geometry_info': {
                    'chordRef': 1.0,
                    'areaRef': 1.0,
                },
                'solver_parameters':{
                    # ANK Solver Parameters
                    "useANKSolver": True,
                    "nSubiterTurb": 20,
                    # NK Solver Parameters
                    "useNKSolver": False,
                    "NKSwitchTol": 1e-4,
                    # Coupled Solver Parameters
                    "ANKCoupledSwitchTol": 1e-12,
                    # Second order Solver Parameters
                    "ANKSecondOrdSwitchTol": 1e-7,
                    # Convergence Criterion
                    "L2Convergence": 1e-8,
                    "nCycles": 150000,
                },
                'aoa_info': [0, 10, 5], # Info to construct array of aoa [start, end, interval]
                'exp_set': {
                    '1': {
                        'Re': 1e6, # Reynold's number
                        'mach': 0.7, # Mach number
                        'Temp': 298.0, # Temperature at which experiment was conducted in kelvin
                        'exp_data': 'exp_data/30p-30n.txt', # Modify as required.
                    } 
                    
                 }
            }
        }
    }
}
# Write to a YAML file
with open('info.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)