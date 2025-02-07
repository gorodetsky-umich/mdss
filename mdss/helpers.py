import yaml
import pandas as pd
import importlib.resources as resources
import re
import os, subprocess
from mdss.yaml_config import ref_sim_info, ref_hpc_info, ref_hierarchy_info, ref_case_info, ref_geometry_info, ref_exp_set_info
from mdss.templates import gl_job_script

################################################################################
# Helper Functions
################################################################################
def load_yaml_file(yaml_file, comm):
    """
    Loads a YAML file and returns its content as a dictionary.

    This function attempts to read the specified YAML file and parse its content into a Python dictionary. If the file cannot be loaded due to errors, it provides a detailed error message.

    Inputs
    ----------
    - **yaml_file** : str
        Path to the YAML file to be loaded.

    Outputs
    -------
    **dict or None**
        A dictionary containing the content of the YAML file if successful, or None if an error occurs.
    """
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

def load_csv_data(csv_file, comm):
    """
    Loads a CSV file and returns its content as a Pandas DataFrame.

    This function reads the specified CSV file and converts its content into a Pandas DataFrame. It handles common errors such as missing files, empty files, or parsing issues.

    Inputs
    ----------
    - **csv_file** : str
        Path to the CSV file to be loaded.

    Outputs
    -------
    **pandas.DataFrame or None**
        A DataFrame containing the content of the CSV file if successful, or None if an error occurs.
"""
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        if comm.rank == 0:
            print(f"Warning: The file '{csv_file}' was not found. Please check the file path.")
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
    """
    Validates the structure of the input YAML file against predefined templates.

    This function checks whether the input YAML file conforms to the expected template structure. It validates each section, including simulation, HPC, hierarchies, cases, and experimental sets.

    Inputs
    ----------
    - **yaml_file** : str
        Path to the YAML file to be validated.

    Outputs
    ------
    **ValidationError**
        If the YAML file does not conform to the expected structure.

    Notes
    -----
    - Uses `ref_sim_info`, `ref_hpc_info`, and other reference pydantic models listed in `yaml_config.py` for validation.
    - Ensures hierarchical consistency by iterating through all levels of the YAML structure.
    """
    with open(yaml_file, 'r') as file:
        sim_info = yaml.safe_load(file)

    ref_sim_info.model_validate(sim_info)
    if sim_info['run_as_subprocess']=='yes':
        if 'nproc' not in sim_info or not isinstance(sim_info['nproc'], int):
            raise ValueError("'nproc' must be provided as an integer when 'run_as_subprocess' is 'yes'")
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
    Generates a Python script to run simulations on an HPC cluster.

    This function creates a Python script with predefined code to run simulations, including problem setup, execution, and post-processing.

    Inputs
    ----------
    - **fname** : str
        Path where the Python script should be saved.

    Notes
    -----
    - The generated script uses argparse to accept input YAML files.
    - It imports the `run_sim` class and runs the simulation using `run_problem` method.
    """
    python_code = """
import argparse
from mdss.run_sim import run_sim

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile", type=str)
args = parser.parse_args()
sim = run_sim(args.inputFile) # Input the simulation info and output dir
sim.run_problem() # Run the simulation
        """
    # Open the file in write mode
    with open(fname, "w") as file:
        file.write(python_code)

def write_job_script(sim_info, out_dir, out_file, python_file_path, yaml_file_path):
    """
    Generates a job script for running simulations on an HPC cluster.

    This function reads a Slurm job script template, updates it with specific HPC parameters and file paths, and saves the customized script to the output directory.

    Inputs
    ------
    - **sim_info** : dict
        Dictionary containing simulation details details.
    - **out_dir** : str
        Directory where the job script and output files will be saved.
    - **out_file** : str
        Name of the file to store job output.
    - **python_file_path** : str
        Path to the Python script to be executed by the job script.
    - **yaml_file_path** : str
        Path to the YAML file containing simulation information.

    Outputs
    -------
    - **str**
        Path to the generated job script.

    Notes
    -----
    - Supports customization for the GL cluster with Slurm job scheduling.
    - Uses regex to update the job script with provided parameters.
    - Ensures that the correct Python and YAML file paths are embedded in the job script.
    """
    hpc_info = sim_info['hpc_info']
    if hpc_info['cluster'] == 'GL':
        # Set default time if not provided
        job_time = hpc_info.get('time', '1:00:00')
        mem_per_cpu = hpc_info.get('mem_per_cpu', '1000m')

        # Fill in the template with values from hpc_info and other parameters
        job_script = gl_job_script.format(
            job_name=hpc_info['job_name'],
            nodes=hpc_info['nodes'],
            nproc=hpc_info['nproc'],
            mem_per_cpu=mem_per_cpu,
            time=job_time,
            account_name=hpc_info['account_name'],
            email_id=hpc_info['email_id'],
            out_dir=out_dir,
            out_file=out_file,
            python_file_path=python_file_path,
            yaml_file_path=yaml_file_path
        )

        # Change 'srun python' command to just python command
        if sim_info['run_as_subprocess'] == 'yes':
            job_script = job_script.replace("srun python", "python")
        
        # Define the path for the job script
        job_script_path = f"{out_dir}/{hpc_info['job_name']}.sh"

        # Save the script to the specified file
        with open(job_script_path, "w") as file:
            file.write(job_script)

        return job_script_path
    
################################################################################
# Helper Functions for running the simulations as subprocesses
################################################################################
def run_as_subprocess(sim_info, hierarchy_info, case_info, exp_info, aoa, aoa_out_dir, nproc, comm):
    """
    Executes a simulation case as a subprocess using mpirun.

    This function automates the creation of input files, ensures directories exist, and runs a subprocess to execute simulations in parallel.

    Inputs
    ------
    - **sim_info** : dict  
        Dictionary containing simulation details, such as output directory, job name, and other metadata.
    - **hierarchy_info** : dict  
        Information about the simulation hierarchy, including hierarchy name.
    - **case_info** : dict  
        Details about the simulation case, such as mesh files, geometry, and solver parameters.
    - **exp_info** : dict  
        Experimental setup details, including Reynolds number, Mach number, temperature, and experimental data.
    - **aoa** : float  
        The angle of attack (in degrees) for the simulation.
    - **aoa_out_dir** : str  
        Directory where output specific to the given angle of attack will be stored.
    - **nproc** : int  
        Number of processors to use for the subprocess execution.
    - **comm** : MPI communicator  
        An MPI communicator object to handle parallelism.

    Outputs
    -------
    - **None**  
        This function does not return any value but performs the following actions:
        1. Creates necessary directories and input files.
        2. Launches a subprocess to execute the simulation using `mpirun`.
        3. Prints standard output and error logs from the subprocess for debugging.

    Notes
    -----
    - The function ensures the proper setup of the simulation environment for the given angle of attack.
    - The generated Python script and YAML input file are specific to each simulation run.
    - Uses MPI to parallelize the simulation process.
    - Captures and displays `stdout` and `stderr` from the subprocess for troubleshooting.
    """
    aoa_specific_sim_info = {
        'out_dir': sim_info['out_dir'],
        'hpc': 'no',
        'run_as_subprocess': 'no',
        'hierarchies':[
            {
                'name': hierarchy_info['name'],
                'cases':[
                    {
                        'name': case_info['name'],
                        'meshes_folder_path': case_info['meshes_folder_path'],
                        'mesh_files': case_info['mesh_files'],
                        'geometry_info': case_info['geometry_info'],
                        'solver_parameters': case_info['solver_parameters'],
                        'exp_sets':[
                            {
                                'aoa_list': [aoa],
                                'Re': exp_info['Re'],
                                'mach': exp_info['mach'],
                                'Temp': exp_info['Temp'],
                                'exp_data': exp_info['exp_data'],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    if not os.path.exists(aoa_out_dir): # Create the directory if it doesn't exist
        if comm.rank == 0:
            os.makedirs(aoa_out_dir)
    
    aoa_specific_input_file = f"{aoa_out_dir}/temp_input_file.yaml"
    if comm.rank==0:
        with open(aoa_specific_input_file, 'w') as input_file:
            yaml.dump(aoa_specific_sim_info, input_file, sort_keys=False)

    python_fname = f"{sim_info['out_dir']}/script_for_subprocess.py"

    if not os.path.exists(python_fname):
        if comm.rank==0:
            write_python_file(python_fname)

    env = os.environ.copy()
    if comm.rank==0:
        print(f"{'-' * 30}")
        print(f"Starting subprocess for aoa: {aoa}")
        if sim_info['hpc'] != 'yes':
            p = subprocess.Popen(
                ['mpirun', '-np', str(nproc), 'python', python_fname, '--inputFile', aoa_specific_input_file],
                env=env,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                text=True  # Ensure output is in text format, not bytes
                )
        elif sim_info['hpc'] == 'yes':
            p = subprocess.Popen(
                ['srun', '-n', str(nproc), 'python', python_fname, '--inputFile', aoa_specific_input_file],
                env=env,
                stdout=subprocess.PIPE,  # Capture standard output
                stderr=subprocess.PIPE,  # Capture standard error
                text=True  # Ensure output is in text format, not bytes
                )
        # Read and print the output and error messages
        stdout, stderr = p.communicate()

        #print("Subprocess Output:", stdout)
        #print("Subprocess Error:", stderr)

        p.wait() # Wait for subprocess to end
        
        print(f"Completed")
        print(f"{'-' * 30}")

    # Delete the files
    if comm.rank == 0:
        os.remove(aoa_specific_input_file)