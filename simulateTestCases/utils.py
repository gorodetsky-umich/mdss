import yaml
import pandas as pd
import importlib.resources as resources
import re
from simulateTestCases.yaml_config import ref_sim_info, ref_hpc_info, ref_hierarchy_info, ref_case_info, ref_geometry_info, ref_exp_set_info

################################################################################
# Helper Functions
################################################################################
def load_yaml_file(yaml_file):
    '''Helper Function to load yaml files and display the type of error in loading, if the file cannot be loaded.

    Inputs
    ------
    yaml_file: Name of the YAML File

    Outputs
    -------
    dict_info: Dictionary contatining the YAML file Info'''
    try:
        # Attempt to open and read the YAML file
        with open(yaml_file, 'r') as file:
            dict_info = yaml.safe_load(file)
        return dict_info
    except FileNotFoundError:
        # Handle the case where the YAML file is not found
        if comm.rank == 0:  # Only the root process prints this error
            print(f"FileNotFoundError: The info file '{yaml_file}' was not found.")
    except yaml.YAMLError as ye:
        # Errors in YAML parsing
        if comm.rank == 0:  # Only the root process prints this error
            print(f"YAMLError: There was an issue reading '{yaml_file}'. Check the YAML formatting. Error: {ye}")
    except Exception as e:
        # General error catch in case of other unexpected errors
        if comm.rank == 0:  # Only the root process prints this error
            print(f"An unexpected error occurred while loading the info file: {e}")
    return None

def load_csv_data(csv_file):
    '''Helper Function to load csv files and display the type of error in loading, if the file cannot be loaded.

    Inputs
    ------
    csv_file: Name of the csv File

    Outputs
    -------
    df: Panda data frame containing the csv file Info'''
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

def check_input_yaml(yaml_file):
    '''Helper Function to check if the input yaml file follows the template
    
    Inputs
    ------
    yaml_file: Name of the input yaml file
     
    outputs
    -------
    Checks the yaml file and throws error if the template is not followed'''
    with open(yaml_file, 'r') as file:
        sim_info = yaml.safe_load(file)

    ref_sim_info.model_validate(sim_info)
    if sim_info['hpc'] == 'yes':
        ref_hpc_info.model_validate(sim_info['hpc_info'])
    for hierarchy, hierarchy_info in enumerate(sim_info['hierarchies']): # loop for Hierarchy level
        ref_hierarchy_info.model_validate(hierarchy_info)
        for case, case_info in enumerate(hierarchy_info['cases']): # loop for cases in hierarchy
            ref_case_info.model_validate(case_info)
            ref_geometry_info.model_validate(case_info['geometry_info'])
            for exp_set, exp_info in enumerate(case_info['exp_sets']): # loop for experimental datasets that may present
                ref_exp_set_info.model_validate(exp_info)

def write_python_file(fname):
    """
    Helper function to write a python file to run the simulations on a HPC
    """
    python_code = """
import argparse
from simulateTestCases.run_sim import run_sim

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile", type=str)
args = parser.parse_args()
sim = run_sim(args.inputFile) # Input the simulation info and output dir
sim.run_problem() # Run the simulation
sim.post_process() # Genrates plots comparing experimental data and simulated data and stores them
        """
    # Open the file in write mode
    with open(fname, "w") as file:
        file.write(python_code)

def write_job_script(hpc_info, out_dir, out_file, python_file_path, yaml_file_path):
    """
    Helper function to generate job scripts to run on clusters
    """
    if hpc_info['cluster'] == 'GL':
        # Read the template file
        with resources.open_text("simulateTestCases.templates", "slrum_job_script.sh") as file:
            temp_data = file.read()     
        # Define replacement values
        replacements = {
            "--job-name ": hpc_info['job_name'],
            "--nodes=": hpc_info['nodes'],
            "--ntasks=": hpc_info['nproc'],
            "--account=": hpc_info['account_name'],
            "--mail-user=": hpc_info['email_id'],
            "--output=": f"{out_dir}/{out_file}",
        }
        # Update time if use has given
        try:
            replacements['--time='] = hpc_info['time']
        except:
            print("Warning: Time is not given. Using the defalult: 1:00:00")
        
        file_replacements = {
        r"(srun python )(\S+)": rf"\1{python_file_path}",  # Update Python file
        r"(--inputFile )(\S+)": rf"\1{yaml_file_path}",  # Update YAML file
        }

        # Update the slurm fields
        for key, value in replacements.items():
            pattern = rf"(#SBATCH {key}).*"  # Match the directive
            temp_data = re.sub(pattern, rf"\1 {value}", temp_data)
        
        # Update additional Python file and YAML file
        for pattern, replacement in file_replacements.items():
            temp_data = re.sub(pattern, replacement, temp_data)

        job_script_path = f"{out_dir}/{hpc_info['job_name']}.sh"
        
        # Save the updated content to a new file
        with open(job_script_path, "w") as file:
            file.write(temp_data)
        
        return job_script_path


    