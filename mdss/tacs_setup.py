import copy
import numpy as np
from tacs import elements, constitutive, functions

class tacs_setup():
    
    def __init__(self, structural_properties, load_info, outputdir):
        self.structural_properties = structural_properties
        self.load_info = load_info
        self.outputdir = outputdir

    # Callback function used to setup TACS element objects and DVs
    def element_callback(self, dvNum, compID, compDescript, elemDescripts, specialDVs, **kwargs):
        # Get Structural Properties
        # Material properties
        rho = self.structural_properties['rho']     # density kg/m^3
        E = self.structural_properties['E']         # Young's modulus (Pa)
        nu = self.structural_properties['nu']       # Poisson's ratio
        kcorr = self.structural_properties['kcorr'] # shear correction factor
        ys = self.structural_properties['ys']       # yield stress
        # Shell thickness
        t = self.structural_properties['t']            # m
        # Setup (isotropic) property and constitutive objects
        prop = constitutive.MaterialProperties(rho=rho, E=E, nu=nu, ys=ys)
        # Set one thickness dv for every component
        con = constitutive.IsoShellConstitutive(prop, t=t, tNum=dvNum)

        # For each element type in this component,
        # pass back the appropriate tacs element object
        transform = None
        elem = elements.Quad4Shell(transform, con)
        return elem

    def problem_setup(self, scenario_name, fea_assembler, problem):
        """
        Helper function to add fixed forces and eval functions
        to structural problems used in tacs builder
        """
        load_type = self.load_info['load_type']
        
        problem.setOption('outputdir', self.outputdir)

        # Add TACS Functions
        if load_type == 'cruise':
            problem.addFunction('mass', functions.StructuralMass)
        problem.addFunction('ks_vmfailure', functions.KSFailure, safetyFactor=1.0, ksWeight=100.0)

        # Add gravity load
        try:
            turn_off_gravity = self.load_info['turn_off_gravity']
        except:
            turn_off_gravity = 'no' # Setting gravity on as default

        try:
            g = self.load_info['g']
        except:
            g = np.array([0.0, -9.81, 0.0]) # in m/s^2, default gravity

        if turn_off_gravity == 'yes':
            g = np.array([0.0, 0.0, 0.0])

        if load_type == 'maneuver':
            inertial_load_factor = self.load_info['inertial_load_factor']
            problem.addInertialLoad(inertial_load_factor* g)
        else: # cruise
            problem.addInertialLoad(g)
