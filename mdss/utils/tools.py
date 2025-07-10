from enum import Enum
import os, shutil, yaml, tempfile
import random
from pydantic import BaseModel
from typing import Optional

from mpi4py import MPI

from mdss.utils.helpers import *
from mdss.resources.yaml_config import check_input_yaml, ref_scenario_info


comm = MPI.COMM_WORLD
size = comm.Get_size()

class RunFlag(Enum):
    skip = 0  # Exit without running the simulation
    run = 1   # Run the simulation and populate the data

################################################################################
# Functions to aid pre and post processing
################################################################################
class update_yaml_input():
    """
    Modifies the YAML input.

    Parameters
    ----------
    - **info_file** : str
        Path to the YAML file containing simulation configuration and information.
    """

    def __init__(self, yaml_input):
        check_input_yaml(yaml_input)

        self.sim_info, self.yaml_input_type = load_yaml_input(yaml_input, comm)
        self.out_dir = self.sim_info['out_dir']
        if self.yaml_input_type == YAMLInputType.FILE:
            self.info_file = yaml_input
        elif self.yaml_input_type == YAMLInputType.STRING:
            self.info_file = os.path.join(self.out_dir, "input.yaml")
            with open(self.info_file, 'w') as f:
                yaml.dump(self.sim_info, f, sort_keys=False)
        

    def aero_options(self, aero_options_updt, case_names):
        """
        Modifies the aero options in the YAML input.

        Parameters
        ----------
        aero_options_updt: dict
            A  dictionary containing the aero options to modify.
        
        case_names: list[str]
            A list containing the names of the cases to modify.
            
        """

        for hierarchy, hierarchy_info in enumerate(self.sim_info['hierarchies']): # loop for Hierarchy level
            for case, case_info in enumerate(hierarchy_info['cases']): # loop for cases in hierarchy
                if case_info['name'] in case_names:
                    case_info['aero_options'].update(aero_options_updt)
    
    def aero_meshes(self, mesh_files, case_names, option,  meshes_folder_path=None):
        """
        Adds mesh files to specifies cases and optionally modifies the path to the folder containing meshes, when provided.
        
        Parameters
        ----------
        mesh_files: list[str]
            A list containing the mesh file names to append or modify or remove.
        case_names: list[str]
            A list containing the names of the cases to modify.
        option: str
            'a' to append (add the given aoa to the existing list)
            'm' to modify the list (to overwrite)
            'r' to remove the aoa from the file.
        meshes_folder_path: Optional[str]
            Path to the folder containing meshes
        """
        for hierarchy, hierarchy_info in enumerate(self.sim_info['hierarchies']): # loop for Hierarchy level
            for case, case_info in enumerate(hierarchy_info['cases']): # loop for cases in hierarchy
                if case_info['name'] in case_names:
                    if option == 'a':
                        case_info['mesh_files'].extend(mesh_files)
                    elif option == 'm':
                        case_info['mesh_files'] = mesh_files
                    elif option == 'r':
                        case_info['mesh_files']= [mesh_file for mesh_file in case_info['mesh_files'] if mesh_file not in mesh_files]
                    if meshes_folder_path is not None:
                        case_info['meshes_folder_path'] = meshes_folder_path

    
    def aoa(self, aoa_list, case_names, scenario_names, option):
        """
        Appends, removes and modifies the Angles of Attack listed in `scenario`.

        Parameters
        ----------
        aoa_list: list
            A list containing aoa to append or modify or remove.
        
        case_names: list[str]
            A list containing the names of the cases to modify.
        
        scenario_names: list[str]
            A list containing the name of the scenarios to modify.

        option: str
            'a' to append (add the given aoa to the existing list)
            'm' to modify the list (to overwrite)
            'r' to remove the aoa from the file.
        """
        for hierarchy, hierarchy_info in enumerate(self.sim_info['hierarchies']): # loop for Hierarchy level
            for case, case_info in enumerate(hierarchy_info['cases']): # loop for cases in hierarchy
                if case_info['name'] in case_names:
                    for scenario, scenario_info in enumerate(case_info['scenarios']): # loop for scenarios that may present
                        if scenario_info['name'] in scenario_names:
                            if option == 'a':
                                scenario_info['aoa_list'] = list(set(scenario_info['aoa_list']) | set(aoa_list))  # Convert both to sets to remove duplicates, then back to a list
                            elif option == 'm':
                                scenario_info['aoa_list'] = aoa_list
                            elif option == 'r':
                                scenario_info['aoa_list']= [aoa for aoa in scenario_info['aoa_list'] if aoa not in aoa_list]

    def write_mod_info_file(self, new_fname=None):
        """
         Writes the modified input file.

        Parameters
        ----------
        new_fname: Optional[str]
            New file name along with the path. Overwrites the original file, when a new name is not provided.
        """
        if comm.rank == 0:
            if new_fname is None:
                new_fname = self.info_file
            with open(new_fname, 'w') as info_file_fhandle:
                yaml.dump(self.sim_info, info_file_fhandle, sort_keys=False)

    def return_yaml_string(self):
        """
        Returns
        -------
        Returns the YAML string representation of the simulation information.
        """
        return yaml.dump(self.sim_info, sort_keys=False)

class update_sim_info(update_yaml_input):
    def __init__(self, sim_info: dict):
        check_input_yaml(yaml.dump(sim_info))
        self.sim_info = sim_info
        self.out_dir = self.sim_info['out_dir']
        self.info_file = os.path.join(self.out_dir, "input.yaml")
        with open(self.info_file, 'w') as f:
            yaml.dump(self.sim_info, f, sort_keys=False)
        

def get_sim_data(yaml_input):
    """
    Generates a dictionary containing simulation data organized hierarchically.

    This function processes a YAML file with simulation information and creates a
    nested dictionary (`sim_data`) with details about simulation hierarchies, cases,
    scenarios, refinement levels, and angles of attack.

    Parameters
    ----------
    yaml_input: str
        Path to the input YAML file or raw YAML string containing simulation information or configuration.

    Returns
    -------
    sim_data: dict
        A dictionary containing simulation data.
    """
    check_input_yaml(yaml_input)
    msg = f"YAML file validation is successful"
    print_msg(msg, 'notice', comm)
    sim_info,_ = load_yaml_input(yaml_input, comm)
    sim_data = {} # Initiating a dictionary to store simulation data

    if 'overall_sim_info' in sim_info.keys():  # if the file is output info file, loads the overall_sim_info.yaml
        print_msg(f"File provided is an output yaml file. Continuing to read data", 'notice', comm)
        overall_sim_info = sim_info
    else:
        print_msg(f"File provided is an input yaml file. Checking for existing simulation results in {sim_info['out_dir']}", 'notice', comm)
        out_yaml_file_path = f"{sim_info['out_dir']}/overall_sim_info.yaml"
        if os.path.isfile(out_yaml_file_path):
            overall_sim_info,_ = load_yaml_input(f"{sim_info['out_dir']}/overall_sim_info.yaml", comm)
        else:
            raise FileNotFoundError(f"File {out_yaml_file_path} simulation results not found. Please run the simulation.")

    sim_data['overall_sim_info'] = overall_sim_info.get('overall_sim_info', {})
    # Loop through hierarchy levels
    for hierarchy_index, hierarchy_info in enumerate(overall_sim_info['hierarchies']):
        hierarchy_name = hierarchy_info['name']
        if hierarchy_name not in sim_data:
            sim_data[hierarchy_name] = {}

        # Loop through cases in the hierarchy
        for case_index, case_info in enumerate(hierarchy_info['cases']):
            case_name = case_info['name']
            if case_name not in sim_data[hierarchy_name]:
                sim_data[hierarchy_name][case_name] = {}

            # Loop through scenarios in the case
            for scenario_index, scenario_info in enumerate(case_info['scenarios']):
                scenario_name = scenario_info['name']
                if scenario_info['name'] not in sim_data[hierarchy_name][case_name]:
                    sim_data[hierarchy_name][case_name][scenario_name] = {}

                # Loop through mesh files
                for ii, mesh_file in enumerate(case_info['mesh_files']):
                    failed_aoa = scenario_info['sim_info'][mesh_file]['failed_aoa']
                    if mesh_file not in sim_data[hierarchy_name][case_name][scenario_name]:
                        sim_data[hierarchy_name][case_name][scenario_name][mesh_file] = {}

                    # Loop through angles of attack
                    for aoa in scenario_info['aoa_list']:
                        if aoa not in failed_aoa:
                            aoa_key = f"aoa_{float(aoa)}"
                            sim_data[hierarchy_name][case_name][scenario_name][mesh_file][aoa_key]= scenario_info['sim_info'][mesh_file].get(aoa_key,{})

                    sim_data[hierarchy_name][case_name][scenario_name][mesh_file]['failed_aoa'] = failed_aoa

    return sim_data
    

        