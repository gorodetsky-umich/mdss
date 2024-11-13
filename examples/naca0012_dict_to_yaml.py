import yaml
import numpy as np

data = {
    'hierarchies':{
        '1':{
            'name': '2d_clean',
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
                    'exp_sets': { 
                        '1': {
                            'aoa_list': [0,5], # Info to construct array of aoa [start, end, interval]
                            'Re': 1e6, # Reynold's number
                            'mach': 0.7, # Mach number
                            'Temp': 298.0, # Temperature at which experiment was conducted in kelvin
                            'exp_data': 'exp_data/naca0012.txt', # Modify as required.
                        }
                    
                    },
                },
            },
        },
    },
}
# Write to a YAML file
with open('naca0012_simInfo.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)