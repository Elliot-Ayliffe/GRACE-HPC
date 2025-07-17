""" 
job_log_manager.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 27/06/25

This module provides functionality to extract, clean and process SLURM job accounting logs (from 'sacct')
into a clear, reformatted pandas DataFrame.

It is designed to be generalisable across HPC clusters that use SLURM as a workload manager.
The module contains:

- JobLogProcessor (class) - a class that inherits 'JobLogUtils' to pull logs using 'sacct', convert to a DataFrame,
                     and clean that DataFrame (to prepare it for later processing).

This class is used in the main backend program to retrieve the job logs needed to estimate energy usage and carbon footprint.
"""

# Import libraries
import pandas as pd
import numpy as np 
import os
import datetime
from io import BytesIO
import subprocess
import warnings
import argparse

# Import functions/classes from modules 
from .backend_utils import JobLogUtils

# Suppress pandas SettingWithCopyWarning to avoid cluttering the output
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# This class inherits the utility class to be able to use its methods
class JobLogProcessor(JobLogUtils):
    """ 
    Class for collecting, aggregating and cleaning SLURM job logs retrieved using 'sacct'.
    Inherits a utility class containing various helper methods for parsing, and processing 
    job data. This class also provides methods to convert the raw output into structured,
    enriched pandas DataFrame.
    """
    def __init__(self, arguments, hpc_config):
        """
        Initialise the JobLogProcessor class

        Args:
            arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
            hpc_config (dict): Dictionary containing metadata about the HPC cluster.
        """
        super().__init__(hpc_config=hpc_config)
        
        # Store user input arguments for use throughout the class
        self.arguments = arguments

        # Set placeholders for the logs at different processing stages
        self.sacct_df = None      # raw sacct output logs converted into a DataFrame 
        self.cleaned_df = None  # Intermediate cleaned logs df 
        self.filtered_df = None     # Filtered logs (job-level) df
        self.final_df = None     # Final processed df (reordered columns)      


    def retrieve_job_logs(self):
        """ 
        Fetches job accounting logs from SLURM by running 'sacct' on the command line. 
        This method retrieves the accounting logs based on the arguments (e.g. start and end dates). 
        The output includes raw job metadata which is parsed and processed later.
        """
        # Construct the SLURM command with the user arguments and correct formatting
        slurm_command = [
            "sacct",
            "--start", self.arguments.StartDate,
            "--end", self.arguments.EndDate,
            "--format",
            "UID,USER,Partition,JobID,JobName,Submit,State,Elapsed,AllocTRES,NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,ConsumedEnergyRaw",
            "-P"    # Pipe delimiter for easier parsing (separated by '|')
        ]

        # Run the sacct command and capture its output as raw bytes 
        process = subprocess.run(slurm_command, stdout=subprocess.PIPE) 
        
        # Save the output as a class attribute for later processing
        self.sacct_data = process.stdout


    def df_conversion(self):
        """
        Transforms the raw 'sacct' output logs into a structured pandas Dataframe 
        by parsing the output (stored as bytes) into a more friendly tabular format.
        """
        # Seperate fields on '|'
        sacct_df = pd.read_csv(BytesIO(self.sacct_data), sep="|", dtype='str')

        # Convert ConsumedEnergyRaw (energy IPMI plugin) from sting to float
        if 'ConsumedEnergyRaw' in sacct_df.columns: 
            sacct_df['ConsumedEnergyRaw'] = pd.to_numeric(sacct_df['ConsumedEnergyRaw'], errors='coerce').fillna(0)  # Convert to float, fill NaN with 0
            sacct_df['EnergyIPMI_kwh'] = sacct_df['ConsumedEnergyRaw'] / 3600000    # Joules to kWh conversion 
        else:
            sacct_df['EnergyIPMI_kwh'] = 0.0

        # set some numeric columns (number of nodes and CPUs) to integers so they can be used in calculations
        for column in ['NNodes', 'NCPUS']:
            sacct_df[column] = sacct_df[column].astype('int64')

        # Store the df in the placeholder class attribute
        self.sacct_df = sacct_df

    
    def df_processor(self):
        """ 
        Process the columns of the logs DataFrame using the methods from 'JobLogUtils',
        clean and filter based on the arguments provided by the user.
        The final dataframe contains columns for all relevant data from the sacct output.
        """
        ### ------------------------------- ###
        ### ADDING COLUMNS TO THE DATAFRAME ###
        ### ------------------------------- ###

        # Add columns that don't require processing (rename them to prevent accidental overwriting of data)
        self.sacct_df['UserID'] = self.sacct_df.UID     # User ID
        self.sacct_df['UserName'] = self.sacct_df.User      # Username
        self.sacct_df['NameofJob'] = self.sacct_df.JobName      # Job name
        self.sacct_df['CPUsAllocated'] = self.sacct_df.NCPUS        # Number of CPUs allocated for the job
        self.sacct_df['TotalNodes'] = self.sacct_df.NNodes      # Total number of Nodes used
        self.sacct_df['WorkingDirectory'] = self.sacct_df.WorkDir       # The working directory the job was ran from

        # Process elapsed runtime of jobs (wallclock time) by converting strings to timedelta objects
        self.sacct_df['ElapsedRuntime'] = self.sacct_df['Elapsed'].apply(self.str_to_timedelta)

        # Process the partition names using method from utility class
        self.sacct_df['PartitionName'] = self.sacct_df.apply(self.process_partition_field, axis=1)

        # Extract job ID removing the '.' part for each row in the df
        self.sacct_df['Job_ID'] = self.sacct_df.JobID.apply(lambda id_string: id_string.split('.')[0])

        # Process the job submission time (convert from string timestamp to datetime object)
        self.sacct_df['SubmissionTime'] = self.sacct_df.Submit.apply(lambda submit_str: datetime.datetime.strptime(submit_str, "%Y-%m-%dT%H:%M:%S"))

        # Normalise the jobs state into a standard integer using utility method
        self.sacct_df['StateCode'] = self.sacct_df['State'].apply(self.standardise_states)

        # Extract the number of allocated GPUs for each job
        # Sometimes AllocTRES may not be available for older versions of SLURM
        if 'AllocTRES' in self.sacct_df.columns:        # If AllocTRES is available extract GPUs from output by searching for gres/gpu
            self.sacct_df['GPUsAllocated'] = (pd.to_numeric(self.sacct_df.AllocTRES.str.extract(r'((?<=gres\/gpu=)\d+)', expand=False)).fillna(0).astype('int64'))
            # Fills 0 if it cannot find gres/gpu 
        else:   # if AllocTRES not available due to old slurm version 
            print("WARNING - 'AllocTRES' sacct command not found due to incompatible SLURM version.")
            self.sacct_df['GPUsAllocated'] = 0      # default to 0

        # Extract the total CPU time (i.e. Actual CPU time consumed by a job, summed across all CPUs - measured)
        self.sacct_df['ActualCPUtime'] = self.sacct_df['TotalCPU'].apply(self.str_to_timedelta)

        # Extract the estimated CPU time (NCPUS * Elapsed). (i.e. the max CPU time if all cores were 100% utilised)
        if 'CPUTime' in self.sacct_df.columns:      # If CPUTime is available
            self.sacct_df['CPUwalltime'] = self.sacct_df['CPUTime'].apply(self.str_to_timedelta)
        else:       # If CPUTime is not available, calculate it manually 
            self.sacct_df['CPUwalltime'] = self.sacct_df.ElapsedRuntime * self.sacct_df.NCPUS

        # Log the memory requested by the user for each job (converted to GB)
        self.sacct_df['RequestedMemoryGB'] = self.sacct_df.apply(self.requested_memory, axis=1)

        # Log the memory actually used by each job (converted to GB)
        self.sacct_df['UsedMemoryGB'] = self.sacct_df.apply(self.process_max_rss, axis=1)

        ### ----------------------- ###
        ### FILTERING THE DATAFRAME ###
        ### ----------------------- ###

        # Groups rows by Job ID, merging each column across job steps (so the df has 1 row per job)
        self.cleaned_df = self.sacct_df.groupby('Job_ID').agg({
            'UserID': 'first',      # Take the first entry
            'UserName': 'first', 
            'NameofJob': 'first',
            'CPUsAllocated': 'max',     # Take the maximum value
            'TotalNodes': 'max',
            'WorkingDirectory': 'first',
            'PartitionName': 'first',
            'SubmissionTime': 'min',        # Take the min value (earliest start time)
            'StateCode': 'min',
            'ElapsedRuntime': 'max',
            'GPUsAllocated': 'max',
            'ActualCPUtime': 'max',
            'CPUwalltime': 'max',
            'RequestedMemoryGB': 'max',
            'UsedMemoryGB': 'max',
            'EnergyIPMI_kwh': 'max'   
        })

        # Filter out jobs that are still running or pending (StateCode -2)
        self.filtered_df = self.cleaned_df.loc[self.cleaned_df.StateCode != -2]

        # If MaxRSS was not recorded, make used memory equal to requested memory using utility method
        self.filtered_df['UsedMemoryGB1'] = self.filtered_df.apply(self.used_memory, axis=1)

        # Set the partition category column (i.e. processor type)
        self.filtered_df['PartitionCategory'] = self.filtered_df.PartitionName.apply(self.categorise_partition)

        # Set GPUs to 1 as a fallback if AllocTRES is missing.
        if 'AllocTRES' not in self.sacct_df.columns:
            self.filtered_df.loc[self.filtered_df.PartitionCategory == 'GPU', 'GPUsAllocated'] = 1

        # Determine which CPU usage time is available for calculations 
        self.filtered_df['CPUusagetime'] = self.filtered_df.apply(self.CPU_usage_time, axis=1)

        # Determine which GPU usage time is available for calculations
        self.filtered_df['GPUusagetime'] = self.filtered_df.apply(self.GPU_usage_time, axis=1)

        # Compute the total CPU-Hours and GPU-Hours used for each job
        self.filtered_df[['CPUhours', 'GPUhours']] = self.filtered_df.apply(self.cpu_gpu_core_hours, axis=1, result_type='expand')

        # Compute the total Node-Hours used for each job
        self.filtered_df['NodeHours'] = self.filtered_df.apply(self.node_hours, axis=1)

        # Compute the minimum amount of memory required for each job to run
        self.filtered_df['RequiredMemoryGB'] = self.filtered_df.apply(self.min_memory_required, axis=1)

        # Compute the amount of memory that was overallocated (i.e. wasted memory)
        self.filtered_df['WastedMemoryRatio'] = self.filtered_df.apply(self.wasted_memory, axis=1)

        ### ------------------------------------------ ###
        ### OPTIONAL FILTERING BASED ON USER ARGUMENTS ###
        ### ------------------------------------------ ###

        # Reset index to standard integers (making JobID a normal column again)
        self.filtered_df.reset_index(inplace=True)

        # Clean the Job ID column (get main job ID)
        self.filtered_df['MainJobID'] = self.filtered_df.Job_ID.apply(self.extract_jobID)

        # If user specifies in arguments, filter by Job ID (only keep specified IDs in the df)
        if self.arguments.JobIDs != 'all_jobs':     # this is the default
            preserved_ids = self.arguments.JobIDs.split(',')        # split the jobs IDs on the comma if user provides multiple 
            self.filtered_df = self.filtered_df.loc[self.filtered_df.MainJobID.isin(preserved_ids)]

        # If user specifies in arguments, filter by working directory that the jobs were ran
        # if self.arguments.WD is not None:
        #     self.filtered_df = self.filtered_df.loc[self.filtered_df.WorkingDirectory == self.arguments.WD]

        
        ### Reordering the final Dataframe
        column_order = [
            'Job_ID', 'MainJobID', 'UserID', 'UserName', 'PartitionName', 'PartitionCategory', 'NameofJob', 'SubmissionTime',
            'StateCode', 'ElapsedRuntime', 'TotalNodes', 'CPUsAllocated', 'GPUsAllocated', 'CPUusagetime', 'ActualCPUtime', 
            'CPUwalltime', 'GPUusagetime', 'RequestedMemoryGB', 'UsedMemoryGB', 'NodeHours', 'CPUhours', 'GPUhours', 
            'UsedMemoryGB1', 'RequiredMemoryGB', 'WastedMemoryRatio', 'WorkingDirectory','EnergyIPMI_kwh'
        ]

        self.final_df = self.filtered_df[column_order]
