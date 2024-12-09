import yaml
import numpy as np

data = {
    'hierarchies': [
            {
            'name': '2d_high_lift',
            'cases': [
                {
                    'name': '30p-30n',
                    'meshes_folder_path': '../grids', # path to the folder containing mesh files
                    'mesh_files': ['30p-30n_overset_L0.cgns',
                                   '30p-30n_overset_L1.cgns',
                                   '30p-30n_overset_L2.cgns',], # List of mesh files intended for different levels of refinement
                    'geometry_info': {
                        'chordRef': 1.0,
                        'areaRef': 1.0,
                    },
                    'solver_parameters':{
                        # ANK Solver Parameters
                        'useANKSolver': True,
                        'nSubiterTurb': 20,
                        # NK Solver Parameters
                        "useNKSolver": False,
                        "NKSwitchTol": 1e-4,
                        # Coupled Solver Parameters
                        "ANKCoupledSwitchTol": 1e-7,
                        # Second order Solver Parameters
                        "ANKSecondOrdSwitchTol": 1e-5,
                        # Convergence Criterion
                        "L2Convergence": 1e-10,
                        "nCycles": 150000,
                        'liftIndex': 2,
                        # IHC Options
                        'nearWallDist': 0.01,
                    },                   
                    'exp_sets': [
                        {
                            'aoa_list': [0, 5], # Info to construct array of aoa [start, end, interval]
                            'Re': 1e6, # Reynold's number
                            'mach': 0.7, # Mach number
                            'Temp': 298.0, # Temperature at which experiment was conducted in kelvin
                            'exp_data': 'exp_data/30p-30n.txt', # Modify as required.
                        },  
                    ],
                },
            ],
        },
    ],
}

# Write to a YAML file
with open('30p-30n_simInfo.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)