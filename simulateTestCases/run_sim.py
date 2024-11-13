import os
import sys
import pandas as pd
import yaml
import time
import matplotlib.pyplot as plt
from datetime import date, datetime
from mphys.multipoint import Multipoint
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from adflow.mphys import ADflowBuilder
from baseclasses import AeroProblem
import openmdao.api as om
from mpi4py import MPI

comm = MPI.COMM_WORLD

################################################################################
# Setting up default ADflow Options
################################################################################
default_aero_options = {
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
    "nsubiterturb": 5,
    "anksecondordswitchtol": 1e-4,
    "ankcoupledswitchtol": 1e-6,
    "ankinnerpreconits": 2,
    "ankouterpreconits": 2,
    "anklinresmax": 0.1,
    # Termination Criteria
    "L2Convergence": 1e-12,
    "L2ConvergenceCoarse": 1e-2,
    "nCycles": 75000,
}

################################################################################
# Multipoint class definition
################################################################################

class Top(Multipoint):

    """
    exp_info is a dictionary with experimental conditions info. This read from the yaml file later.
    aero_option is a dictionary with ADflow parameters, A default is defined above. However, this is updated for
    every case. The update is also read from the yaml file.
    """

    def __init__(self, case_info, exp_info, aero_options):
        super().__init__()
        self.case_info = case_info
        self.exp_info = exp_info
        self.aero_options = aero_options

    def setup(self):
                        
        adflow_builder = ADflowBuilder(self.aero_options, scenario="aerodynamic")
        adflow_builder.initialize(self.comm)

        ################################################################################
        # MPHY setup
        ################################################################################

        # ivc to keep the top level DVs
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # create the mesh and cruise scenario because we only have one analysis point
        self.add_subsystem("mesh", adflow_builder.get_mesh_coordinate_subsystem())
        self.mphys_add_scenario("cruise", ScenarioAerodynamic(aero_builder=adflow_builder))
        self.connect("mesh.x_aero0", "cruise.x_aero")

    def configure(self):
        aoa = 0.0 # Set default Angle of attack

        geometry_info = self.case_info['geometry_info'] # Load geometry info
        chordRef = geometry_info['chordRef']
        areaRef = geometry_info['areaRef']

        ap0 = AeroProblem(
            name="ap0",
            # Experimental Conditions 
            mach = self.exp_info['mach'], reynolds=self.exp_info['Re'], reynoldsLength=chordRef, T=self.exp_info['Temp'], 
            alpha=aoa,
            # Geometry Info
            areaRef=areaRef, 
            chordRef=chordRef, 
            evalFuncs=["cl", "cd"]
        )
        ap0.addDV("alpha", value=aoa, name="aoa", units="deg")


        # set the aero problem in the coupling and post coupling groups
        self.cruise.coupling.mphys_set_ap(ap0)
        self.cruise.aero_post.mphys_set_ap(ap0)

        # add dvs to ivc and connect
        self.dvs.add_output("aoa", val=aoa, units="deg")

        # call the promote inputs to propagate aoa dvs
        # TODO does not work now
        # self.cruise._mphys_promote_inputs()
        # so connect manually
        self.connect("aoa", ["cruise.coupling.aoa", "cruise.aero_post.aoa"])

class run_sim():

    def __init__(self, info_file, out_dir):
        """
        This function gets the info required for runnign ADflow from the input 'yaml file', and exits, if the file is not readable
        Inputs
            info_file: 'yaml' file conatining simulation info
            out_dir: Directory to store output
        """
        self.out_dir = out_dir
        self.info_file = info_file
        try:
            # Attempt to open and read the YAML file
            with open(info_file, 'r') as file:
                self.sim_info = yaml.safe_load(file)
        except FileNotFoundError:
            # Handle the case where the YAML file is not found
            if comm.rank == 0:  # Only the root process prints this error
                print(f"FileNotFoundError: The info file '{info_file}' was not found.")
            sys.exit(1)
        except yaml.YAMLError as ye:
            # Errors in YAML parsing
            if comm.rank == 0:  # Only the root process prints this error
                print(f"YAMLError: There was an issue reading '{info_file}'. Check the YAML formatting. Error: {ye}")
            sys.exit(1)
        except Exception as e:
            # General error catch in case of other unexpected errors
            if comm.rank == 0:  # Only the root process prints this error
                print(f"An unexpected error occurred while loading the info file: {e}")
            sys.exit(1)
    
    ################################################################################
    # Code to check the yaml file
    ################################################################################
    def check_expected_key(self, dict_to_ckeck, expected_keys):
        error_flag = 0
        msg = [f"Passed: Contains all the expected keys in the right format"]
        # Check each expected key for presence and type
        for key, expected_type in expected_keys.items():
            if key not in dict_to_ckeck:
                msg.append(f"Key not found: '{key}'")
                error_flag = 1
            elif not isinstance(dict_to_ckeck[key], expected_type):
                actual_type = type(dict_to_ckeck[key]).__name__
                expected_type_name = expected_type.__name__
                msg.append(f"Type mismatch: '{key}' is expected to be {expected_type_name}, but found {actual_type}")
                error_flag = 1
        return error_flag, msg

    def write_yaml_validation_text(self, output_file, message):
        # Assuming 'message' is the list collecting validation messages
        with open(output_file, 'w') as file:
            # Write a summary header
            error_count = sum(1 for msg in message if "Key not found" in msg or "Type mismatch" in msg)
            file.write("YAML Validation Report\n")
            file.write("=" * 30 + "\n")
            file.write(f"Total Errors/Warnings Found: {error_count}\n\n")

            # Write each line with formatting
            for line in message:
                if "Checking Hierarchy" in line:
                    # Major heading for each hierarchy
                    file.write("\n" + "=" * 50 + "\n")
                    file.write(f"{line}\n")
                    file.write("=" * 50 + "\n")
                elif "Checking case" in line:
                    # Subheading for each case
                    file.write("\n" + "-" * 40 + "\n")
                    file.write(f"{line}\n")
                    file.write("-" * 40 + "\n")
                elif "Checking exp_set" in line:
                    # Subheading for each exp_set
                    file.write("\n" + " " * 4 + line + "\n")
                    file.write(" " * 4 + "-" * 36 + "\n")
                elif "File does not exist" in line or "Type Error" in line:
                    # Indented error message with a bullet point
                    file.write(" " * 8 + "- " + line + "\n")
                else:
                    # General message with indentation
                    file.write(" " * 4 + line + "\n")

    def check_yaml_file(self):
        """
        This function checks the input yaml file and prints possible places where the code might fail.
        """
        expected_keys_in_hieraechy = {
            'name': str,
            'cases': dict,
        }

        expected_keys_in_case = {
                            'name': str,
                            'nRefinement': int,
                            'solver_parameters': dict,
                            'mesh_file': str,
                            'geometry_info': dict,
                            'exp_sets': dict,
                        }
        
        expected_keys_in_geometry_info = {
            'chordRef': float,
            'areaRef': float,
        }

        expected_keys_in_exp_set = {
            'aoa_list': list,
            'Re': float,
            'mach': float,
            'Temp': float,
            'exp_data': str,
        }

        sim_info_copy = self.sim_info.copy() # Copying to run the loop
        message = [f"Checking {self.info_file} for compatibility with simulateTestCases"]
        if 'hierarchies' in sim_info_copy.keys(): 
            for hierarchie, hierarchie_info in sim_info_copy['hierarchies'].items(): # loop for Hierarchy level
                message.append(f"Checking Hierarchy: {hierarchie}")
                hierarchy_error_flag, msg = self.check_expected_key(hierarchie_info, expected_keys_in_hieraechy)
                message.extend(msg)
                if hierarchy_error_flag == 0:
                    for case, case_info in hierarchie_info['cases'].items(): # loop for cases in hierarchy
                        message.append(f"Checking case: {case}")
                        case_error_flag, msg = self.check_expected_key(case_info, expected_keys_in_case)
                        message.extend(msg)
                        if case_error_flag == 0:
                            message.append(f"Checking if the mesh files are present.....")
                            for ii in range(case_info['nRefinement']):
                                refinement_level = f"L{ii}"
                                mesh_file = f"{case_info['mesh_file']}_{refinement_level}.cgns"
                                if not os.path.isfile(mesh_file):
                                    message.append(f"File does not exist: {mesh_file}")
                                else:
                                    message.append(f"Passed: {mesh_file} exists")
                            message.append(f"Checking the geometry_info dict.....")
                            gemoetry_error_flag, msg = self.check_expected_key(case_info['geometry_info'], expected_keys_in_geometry_info)
                            message.extend(msg)
                            for exp_set, exp_set_info in case_info['exp_sets'].items(): # loop for experimental sets in each case
                                message.append(F"Checking exp_set: {exp_set}")
                                exp_set_error_flag , msg = self.check_expected_key(exp_set_info, expected_keys_in_exp_set)
                                message.extend(msg)
                                if exp_set_error_flag == 0:
                                    if not all(isinstance(item, (float, int)) for item in exp_set_info['aoa_list']):
                                        message.append(f"'Type Error: aoa_list contains values other than float and int'")
                                    if not os.path.isfile(exp_set_info['exp_data']):
                                        message.append(f"File does not exist: {exp_set_info['exp_data']}")
        else:
            message.append(f"Key not found: 'heirarchies' is not present in {self.info_file}")
        
        # Writing messages to a text file
        if not os.path.exists(self.out_dir): # Create the directory if it doesn't exist
            if comm.rank == 0:
                os.makedirs(self.out_dir)
        output_file = f"self.out_dir/yaml_validation.txt"
        self.write_yaml_validation_text(output_file, message)

        print(f"Validation complete. Results saved in {output_file}")

    ################################################################################
    # Code for running simulations
    ################################################################################   
    def run_problem(self):
        """
        This function sets up a openMDAO problem and runs it, generates a text tile to store the output and compile output info into two yaml files
        - One file is stored in the user given output direcytory with information regarding the overall simulation
        - The second file is specific to an angle of attack for each experimental scenario, and stored in the aoa directory
        """
        sim_info_copy = self.sim_info.copy() # Copying to run the loop
        sim_out_info = self.sim_info.copy() # Copying to write the output YAML file
        start_time = time.time()
        start_wall_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for hierarchie, hierarchie_info in sim_info_copy['hierarchies'].items(): # loop for Hierarchy level

            for case, case_info in hierarchie_info['cases'].items(): # loop for cases in hierarchy

                aero_options = default_aero_options.copy()
                aero_options.update(case_info['solver_parameters']) # Update ADflow solver parameters

                for exp_set, exp_info in case_info['exp_sets'].items(): # loop for experimental datasets that may present

                    if comm.rank == 0:
                        print(f"{'#' * 30}")
                        print(f"{'SIMULATION INFO':^30}")
                        print(f"{'#' * 30}")
                        print(f"{'Hierarchy':<20}: {hierarchie_info['name']}")
                        print(f"{'Case Name':<20}: {case_info['name']}")
                        print(f"{'Experimental Condition':<20}: {exp_set}")
                        print(f"{'Reynolds Number (Re)':<20}: {exp_info['Re']}")
                        print(f"{'Mach Number':<20}: {exp_info['mach']}")
                        print(f"{'=' * 30}")
                    
                    # Extract the Angle of attacks for which the simulation has to be run
                    aoa_list = exp_info['aoa_list']

                    exp_sim_info = {} # Creating experimental level sim info dictionary for overall sim info file

                    for ii in range(case_info['nRefinement']): # Loop for refinement levels

                        refinement_level = f"L{ii}"
                        CLList = []
                        CDList = []
                        TList = []
                        FList = [] # Fail flag list

                        refinement_level_dict = {} # Creating refinement level sim info dictionary for overall sim info file

                        # Update Grid file
                        aero_options['gridFile'] = f"{case_info['mesh_file']}_{refinement_level}.cgns"

                
                        for aoa in aoa_list: # loop for angles of attack
                            
                            # Date
                            current_date = date.today()
                            date_string = current_date.strftime("%Y-%m-%d")

                            # Define output directory -- Written to store in the parent directory
                            output_dir = f"{self.out_dir}/{date_string}/{hierarchie_info['name']}/{case_info['name']}/exp_set_{exp_set}/{refinement_level}/aoa_{aoa}"
                            aero_options['outputDirectory'] = output_dir


                            aoa_level_dict = {} # Creating aoa level sim info dictionary for overall sim info file

                            ################################################################################
                            # OpenMDAO setup
                            ################################################################################

                            os.environ["OPENMDAO_REPORTS"]="0" # Do this to disable report generation by OpenMDAO

                            prob = om.Problem()
                            prob.model = Top(case_info, exp_info, aero_options)

                            # Checking for existing sucessful simualtion info, 
                            if os.path.exists(output_dir):
                                try:
                                    aoa_info_file = f"{output_dir}/out.yaml"
                                    with open(aoa_info_file, 'r') as aoa_file:
                                        aoa_sim_info = yaml.safe_load(aoa_file)
                                    fail_flag = aoa_sim_info['fail_flag']
                                    if fail_flag == 0:
                                        CLList.append(aoa_sim_info['cl'])
                                        CDList.append(aoa_sim_info['cd'])
                                        TList.append(float(aoa_sim_info['wall_time'].replace(" sec", "")))
                                        FList.append(fail_flag)

                                        # To Store in the overall simulation out file in case of skipping
                                        aoa_level_dict = {
                                            'cl': float(aoa_sim_info['cl']),
                                            'cd': float(aoa_sim_info['cd']),
                                            'wall_time': aoa_sim_info['wall_time'],
                                            'fail_flag': int(fail_flag),
                                            'out_dir': output_dir,
                                        }
                                        refinement_level_dict[f"aoa_{aoa}"] = aoa_level_dict

                                        if comm.rank == 0:
                                            print(f"{'-'*50}")
                                            print(f"{'NOTICE':^50}")
                                            print(f"{'-'*50}")
                                            print(f"Skipping Angle of Attack (AoA): {float(aoa):<5} | Reason: Existing successful simulation found")
                                            print(f"{'-'*50}")
                                        continue # Continue to next loop if there exists a successful simulation
                                except:
                                    fail_flag = 1
                            elif not os.path.exists(output_dir): # Create the directory if it doesn't exist
                                if comm.rank == 0:
                                    os.makedirs(output_dir)

                            
                            if comm.rank == 0:
                                print(f"{'-'*50}")
                                print(f"Starting Angle of Attack (AoA): {float(aoa):<5}")
                                print(f"{'-'*50}")
                            # Setup the problem
                            prob.setup()

                            # Set the angle
                            prob["aoa"] = float(aoa)

                            om.n2(prob, show_browser=False, outfile=f"{output_dir}/mphys_aero.html")

                            # Run the model
                            aoa_start_time = time.time() # Stote the start time
                            try:
                                prob.run_model()
                                fail_flag = 0
                            except:
                                fail_flag = 1
                                
                            aoa_end_time = time.time() # Store the end time
                            aoa_run_time = aoa_end_time - aoa_start_time # Compute the run time

                            prob.model.list_inputs(units=True)
                            prob.model.list_outputs(units=True)
                    
                            # Store a Yaml file at this level
                            aoa_out_dic = {
                                'case': case_info['name'],
                                'exp_info': exp_info,
                                'AOA': float(aoa),
                                'cl': float(prob["cruise.aero_post.cl"][0]),
                                'cd': float(prob["cruise.aero_post.cd"][0]),
                                'refinement_level': refinement_level,
                                'wall_time': f"{aoa_run_time:.2f} sec",
                                'fail_flag': int(fail_flag),
                                'out_dir': output_dir,
                            }
                            with open(f"{output_dir}/out.yaml", 'w') as interim_out_yaml:
                                yaml.dump(aoa_out_dic, interim_out_yaml, sort_keys=False)
                        
                            # To Store in the overall simulation out file
                            aoa_level_dict = {
                                'cl': float(prob["cruise.aero_post.cl"][0]),
                                'cd': float(prob["cruise.aero_post.cd"][0]),
                                'wall_time': f"{aoa_run_time:.2f} sec",
                                'fail_flag': int(fail_flag),
                                'out_dir': output_dir,
                            }
                            refinement_level_dict[f"aoa_{aoa}"] = aoa_level_dict

                            # Adding cl, cd, wall time, Fail flags to their respective lists to create the csv file at refinement level
                            CLList.append(float(prob["cruise.aero_post.cl"][0]))
                            CDList.append(float(prob["cruise.aero_post.cd"][0]))
                            TList.append(aoa_run_time)
                            FList.append(fail_flag)
                        
                        # Write simulation results to a csv file
                        refinement_level_data = {
                            "Alpha": [f"{alpha:6.2f}" for alpha in aoa_list],
                            "CL": [f"{cl:8.4f}" for cl in CLList],
                            "CD": [f"{cd:8.4f}" for cd in CDList],
                            "FFlag": [f"{int(FF):12f}" for FF in FList],
                            "WTime": [f"{wall_time:10.2f}" for wall_time in TList]
                        }
                        df = pd.DataFrame(refinement_level_data) # Create a panda DataFrame

                        # Define the output file path
                        refinement_level_dir = os.path.dirname(output_dir)
                        ADflow_out_file = f"{refinement_level_dir}/ADflow_output.csv"

                        # Write the DataFrame to a CSV file
                        df.to_csv(ADflow_out_file, index=False)

                        # Add csv file location to the overall simulation out file
                        refinement_level_dict['csv_file'] = ADflow_out_file
                        refinement_level_dict['out_dir'] = refinement_level_dir

                        # Add refinement level dict to exp level dict
                        exp_sim_info[f"{refinement_level}"] = refinement_level_dict

                    # Add experimental level simulation to the overall simulation out file
                    exp_out_dir = os.path.dirname(refinement_level_dir)
                    exp_sim_info['out_dir'] = exp_out_dir
                    sim_out_info['hierarchies'][hierarchie]['cases'][case]['exp_sets'][exp_set]['sim_info'] = exp_sim_info

        end_time = time.time()
        end_wall_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        net_run_time = end_time - start_time
        sim_out_info['overall_sim_info'] = {
            'start_time': start_wall_time,
            'end_time': end_wall_time,
            'total_wall_time': f"{net_run_time:.2f} sec"
        }

        final_out_yaml_dir = f"{self.out_dir}/{date_string}"

        # Define the initial file path
        final_out_yaml_file_path = os.path.join(final_out_yaml_dir, "out.yaml")
        counter = 1

        # Increment the filename if the file already exists
        if comm.rank == 0:
            while os.path.exists(final_out_yaml_file_path):
                final_out_yaml_file_path = os.path.join(final_out_yaml_dir, f"out_{counter}.yaml")
                counter += 1
        with open(final_out_yaml_file_path, 'w') as final_out_yaml_handle:
            yaml.dump(sim_out_info, final_out_yaml_handle, sort_keys=False)

    ################################################################################
    # Code for Post Processing
    ################################################################################
    def load_csv_data(self, csv_file):
        try:
            df = pd.read_csv(csv_file)
            return df
        except FileNotFoundError:
            if comm.rank == 0:
                print(f"Error: The file '{csv_file}' was not found. Please check the file path.")
        except pd.errors.EmptyDataError:
            if comm.rank == 0:
                print("Error: The file is empty. Please check if data has been written correctly.")
        except pd.errors.ParserError:
            if comm.rank == 0:
                print("Error: The file could not be parsed. Please check the file format.")
        except Exception as e:
            if comm.rank == 0:
                print(f"An unexpected error occurred: {e}")
        return None # In case of error, return none.
    
    def post_process(self):
            
        for hierarchie, hierarchie_info in self.sim_info['hierarchies'].items(): # loop for Hierarchy level
            for case, case_info in hierarchie_info['cases'].items(): # loop for cases in hierarchy
                for exp_set, exp_info in case_info['exp_sets'].items(): # loop for experimental datasets that may present
                    
                    # Plot setup
                    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
                    fig.suptitle('Comparison between ADflow Simulation and Experimental Data')

                    # Load Experimental Data
                    try:
                        exp_data = self.load_csv_data(exp_info['exp_data'])
                    except:
                        exp_data = None
                        if comm.rank == 0:
                            print(f"Error: Experimental data location is not specified. Continuing to plot without experimental data")

                    if exp_data is not None: # Only plot if data loaded successfully
                        axs[0].plot(exp_data['Alpha'], exp_data['CL'], label='Experimental', color='black', linestyle='--', marker='o')
                        axs[1].plot(exp_data['Alpha'], exp_data['CD'], label='Experimental', color='black', linestyle='--', marker='o')
                
                    # Load Simulated Data
                    exp_out_dir = exp_info['sim_info']['out_dir']
                    sim_data = {}
                    for ii in range(case_info['nRefinement']): # Loop for refinement levels
                        refinement_level_dir = f"{exp_out_dir}/L{ii}"
                        ADflow_out_file = f"{refinement_level_dir}/ADflow_output.csv"
                        sim_data = self.load_csv_data(ADflow_out_file)
                        if sim_data is not None:  # Only plot if data loaded successfully
                            label = f"L{ii}"
                            axs[0].plot(sim_data['Alpha'], sim_data['CL'], label=label) # Plot CL vs Alpha for this refinement level
                            axs[1].plot(sim_data['Alpha'], sim_data['CD'], label=label) # Plot CD vs Alpha for this refinement level
                    
                    # Setting titles, labels, and legends
                    axs[0].set_title('CL vs Alpha')
                    axs[0].set_xlabel('Alpha (deg)')
                    axs[0].set_ylabel('CL')
                    axs[0].legend()
                    axs[0].grid(True)

                    axs[1].set_title('CD vs Alpha')
                    axs[1].set_xlabel('Alpha (deg)')
                    axs[1].set_ylabel('CD')
                    axs[1].legend()
                    axs[1].grid(True)

                    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to fit title
                    plt.savefig(f"{exp_out_dir}/ADflow_Results.png")

                        



