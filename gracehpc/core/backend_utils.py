""" 
backend_utils.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 26/06/25

This module provides utility classes and helper functions used during the backend process of the
GRACE-HPC package.

The module contains the following:

- JobLogUtils (class) - a collection of utility methods for parsing and transforming job log fields. This is imported into the 
                         job_log_manager.py module.

- exit_if_no_jobs (function) - a function to check if the log dataframe is empty or not

- save_output_dfs (function) - a function to save the output dataframes to CSV files based on user arguments.

- get_carbon_intensity (function) - a function to query the Carbon Intensity API for real-time carbon intensity data at the time of job submission.
"""

# Import libraries
import pandas as pd
import numpy as np 
import datetime
import sys 
import os
import requests 
from datetime import timedelta
import pytz


class JobLogUtils():
    """ 
    Class providing utility functions for parsing, cleaning and transforming SLURM data.
    """
    def __init__(self, hpc_config):
        """
        Initialise the JobLogUtils class

        Args:
            hpc_config (dict): Dictionary containing metadata about the HPC cluster.
        """
        self.hpc_config = hpc_config


    def str_to_timedelta(self, time_string):
        """ 
        Converts a duration string into a 'datetime.timedelta' object. 

        Args:
            time_string (str): time duration in the format '[DD-HH:MM:]SS[.MS]'

        Return:
            datetime.timedelta: Parsed timedelta object representing the duration
        """
        # Split the days (DD) from time if present 
        day_parts = time_string.split('-')

        if len(day_parts) == 2:     # If days are present
            days = int(day_parts[0])
            time_part = day_parts[1]
        else:                       # If days are not present
            days = 0
            time_part = time_string

        # Seperate the milliseconds (ms) if present
        ms_parts = time_part.split('.')

        if len(ms_parts) == 2:
            milliseconds = int(ms_parts[1])
            hms_part = ms_parts[0]
        else:
            milliseconds = 0
            hms_part = time_part

        # Split the hours, minutes, seconds
        time_components = hms_part.split(':')
        if len(time_components) == 3:
            padding = []            # add no zeros 
        elif len(time_components) == 2: 
            padding = ['00']        # add zeros to fill in
        elif len(time_components) == 1:
            padding = ['00', '00']  # add zeros to fill in
        else:
            raise ValueError(f"Unable to parse time string: {time_string}")
        
        # store final values
        hours, minutes, seconds = list(map(int, padding + time_components))

        # covert the string to datetime.timedelta
        return datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    

    def process_partition_field(self, job_record):
        """ 
        This method ensures a job's partition field is returned in a clean format:

        - If NaNs are present, it returns an empty string.
        - If multiple partitions are listed, it chooses the first one only
        - gives user warning if their job is associated with more than one partition

        Args:
            job_record (pd.Series): a row from the slurm logs dataframe

        Return: 
            str: a single partition name or none (empty string) if missing                   
        """
        # check if the 'Partition' field is missing (NaN) and return empty string
        if pd.isnull(job_record.Partition):
            return ''
        
        # Split the comma-seperated partition string into a list if there is multiple.
        partition_list = job_record.Partition.split(',')

        # If the job ran (i.e. has an elapsed time > 0) and multiple partitions are listed,
        # warn the user as only 1 partition should apply to a running job.
        if (job_record.ElapsedRuntime.total_seconds() > 0) and (len(partition_list) > 1):
            print(f"\nPARTITION WARNING: More than one partitions were logged for a job that run: "
                  f"JobID: {job_record.JobID}. Partitions (first one is used): {job_record.Partition}\n")
            
        # return the first partition from the list 
        return partition_list[0]
    

    def categorise_partition(self, partition_name):
        """ 
        Determines the processor category of a given partition (e.g. CPU or GPU)
        based on the HPC cluster configuration file.

        Args:
            partition_name (str): Name of the jobs's partition 

        Return:
            str: Partition category ('CPU' or 'GPU')
        """
        # check if the given partition exists in the configuration dictionary
        if partition_name not in self.hpc_config['partitions']:
            raise ValueError(f"\n Partition found is not listed in the configuration file: {partition_name}\n")
        
        # Retrieve and return the category (processor type) of this partition from the configuration file.
        return self.hpc_config['partitions'][partition_name]['processor']
    

    def memory_conversion(self, value, unit_label):
        """ 
        Method that converts a memory value from the given units into 
        standard gigabytes (GB).

        Args:
            value (float): The numeric value of memory
            unit_label (str): the unit associated with the memory value. Must be:
                            - M (megabytes)
                            - G (gigabytes)
                            - K (kilobytes)
        
        Return:
            float: Memory value converted to gigabytes
        """
        # Check unit label is one of the expected
        assert unit_label in ['M', 'G', 'K'], f"Invalid unit '{unit_label}. Expected to be either 'M', 'G', 'K']."

        # If unit is megabytes, divide by 1000
        if unit_label == 'M':
            value = value / 1e3        # 1 GB = 1000 MB
        # If unit is kilobytes, divide by 1,000,000
        if unit_label == 'K':
            value = value / 1e6        # 1 GB = 1,000,000 KB

        # If unit is 'G', no conversion needed
        return value
    

    def requested_memory(self, job_record):
        """ 
        Determines the total requested memory for a submitted job (in GB)

        Args:
            job_record (pd.Series): A single row of the sacct output (containing job details)
        
        Return
            float: Total memory requested by the user for a job, converted to GB using the method above.
        """
        # Extract raw requested memory string, number of nodes and number of CPUs from the job record
        raw_memory_requested = job_record['ReqMem']
        total_nodes = job_record['NNodes']
        total_cpus = job_record['NCPUS']

        # Assign 0GB memory if value is missing
        if pd.isnull(raw_memory_requested):
            memory_unit = 'G'
            total_memory_gb = 0

        # If memory string ends with 'n': memory was requested per node.
        # Multiply the base memory by number of nodes
        elif raw_memory_requested[-1] == 'n':
            memory_unit = raw_memory_requested[-2]  # extract unit
            total_memory_gb = float(raw_memory_requested[:-2] * total_nodes)

        # If memory string ends with 'c': memory was requested per CPU core
        # Multiply base memory by number of CPUs
        elif raw_memory_requested[-1] == 'c':
            memory_unit = raw_memory_requested[-2]      # extract unit
            total_memory_gb = float(raw_memory_requested[:-2]) * total_cpus
        
        # If the memory string ends with a standard unit, parse directly
        elif raw_memory_requested[-1] in ['M', 'G', 'K']:
            memory_unit = raw_memory_requested[-1]      # extract unit (last character)
            total_memory_gb = float(raw_memory_requested[:-1])

        else:       # raise error if the memory format is unrecognisable
            raise ValueError(f"Memory format is unrecognised: {raw_memory_requested}. Cannot read.")
        
        # Convert memory to Gigabytes using method above
        return self.memory_conversion(total_memory_gb, memory_unit)
    

    def process_max_rss(self, job_record):
        """ 
        Processes the MaxRSS (max resident set size) memory usage filed from the SLURM logs
        and converts it to GB.
        MaxRSS is a runtime memory usage metric (how much RAM your job actually used). 
        Not what the user requested.

        Args:
            job_record (pd.Series): a single job record containing the MaxRSS field
        
        Return:
            float: Actual memory used in GB (MaxRSS value in GB), or -1 if not reported
        """
        # If MaxRSS is missing, assume full requested memory was utilised (mark with -1)
        if pd.isnull(job_record.MaxRSS):
            memory_used = -1
        
        # If MaxRSS is zero, memory usage=0
        elif job_record.MaxRSS == '0':
            memory_used = 0

        else:   # check if MaxRSS value is a string
            assert type(job_record.MaxRSS) == str

            # Case 1: MaxRSS ends with a unit character (K,M,G)
            if job_record.MaxRSS[-1].isalpha():
                numeric_part = float(job_record.MaxRSS[:-1])    # extract value
                unit_part = job_record.MaxRSS[-1]               # extract unit
                memory_used = self.memory_conversion(numeric_part, unit_part)       # convert to GB

            # Case 2: MaxRSS does not include a unit (provide K as default)
            else:
                numeric_part = float(job_record.MaxRSS)
                default_unit = 'K'
                memory_used = self.memory_conversion(numeric_part, default_unit)

        return memory_used
    

    def used_memory(self, job_record):
        """ 
        Clarifies the actual memory used by a job.
        If MaxRSS was not recorded, it assumes full requested memory was used.
        
        Args:
            job_record (pd.Series): a row of job data containing requested and used memory fields

        Return:
            float: Estimated memory used in GB
        """
        # If MaxRSS was not available, use ReqMem
        if job_record.UsedMemoryGB == -1:
            return job_record.RequestedMemoryGB
        else: 
            return job_record.UsedMemoryGB
        

    def cpu_gpu_core_hours(self, job_record):
        """ 
        Calculates the the total core-hours charged for a job, separating CPU and GPU usage.
        Depending on the partition category (CPU or GPU), the core-hours charged are estimated based 
        on the number of CPU cores used or the number of GPUs allocated and their corresponding runtime.

        Args:
            job_record (pd.Series): a single row from the job logs DataFrame

        Return:
            tuple (float, float): (charged CPU hours, charged GPU hours)
        """
        # If partition category (processor type) is 'CPU'
        if job_record.PartitionCategory == 'CPU':
            return job_record.CPUwalltime / np.timedelta64(1, 'h'), 0.0       # no GPUs
        
        # If partition category (processor type) is 'GPU'
        else:
            gpu_hours = (job_record.ElapsedRuntime * job_record.GPUsAllocated) / np.timedelta64(1, 'h')
            return 0.0, gpu_hours
        

    def node_hours(self, job_record):
        """ 
        Calculates the total node-hours charged for a job.
        Node-hours are calculated by multiplying elapsed runtime (wallclock)
        by the number of nodes used.

        These are used to calculate scope 3 emissions for Isambard systems

        Args:
            job_record (pd.Series): a single row from the job logs DataFrame

        Return:
            float: total node-hours charged for a job
        """
        node_hours = (job_record.ElapsedRuntime * job_record.TotalNodes) / np.timedelta64(1, 'h')
        return node_hours

    
    def extract_jobID(self, jobID):
        """ 
        Extracts the main job ID from array jobs

        Args:
            JobID (str): Full slurm job ID possibly including a task index
        
        Return:
            str: Main Job ID without array task suffix 
        """
        parts = jobID.split('_')
        
        # check the format is correct (should not be more than 2 parts)
        assert len(parts) <=2, f"Unexpected Job ID format: {jobID}"
        
        # Return main/parent Job ID
        return parts[0]
    

    def standardise_states(self, job_state):
        """ 
        Normalise the job's slurm state into a standard integer code

        Args:
            job_state (str): Raw SLURM job state string from sacct (e.g. 'COMPLETED', 'RUNNING', 'FAILED')

        Return:
            int: Status code (1 = success, -2 = job is still running, 0 = other cases are treated as failed)
        """
        # Common SLURM job states
        successful_states = ['CD', 'COMPLETED']
        acitve_states = ['PD', 'PENDING', 'R', 'RUNNING', 'RQ', 'REQUEUED']

        # For successfully completed jobs
        if job_state in successful_states:
            status_code = 1
        
        # For failed jobs
        else: 
            status_code = 0

        # For running jobs
        if job_state in acitve_states:
            status_code = -2
        
        return status_code


    def CPU_usage_time(self, job_record):
        """ 
        Calculates the effective CPU usage time (for total CPUs) for a job

        Args: 
            job_record (pd.Series): a single row of the job logs DataFrame

        Return:
            timedelta: Total CPU usage time
        """
        # If no CPU usage time (TotalCPU in sacct) is recorded, assume full usage (100%) for all cores
        if job_record.ActualCPUtime.total_seconds() == 0:
            return job_record.CPUwalltime 
        
        # return CPU usage time if available
        return job_record.ActualCPUtime
    
    def GPU_usage_time(self, job_record):
        """ 
        Calculates the GPU usage time for a job

        Args:
            job_record (pd.Series): a single row of the job logs DataFrame

        Return:
            timedelta: Total GPU usage time 

        Notes:
        Due to lack of available data from sacct on GPU usage time, we assume 100% GPU utilization.
        If the job is not run on GPU partition, 0 is returned.
        """
        # Return 0 if job is not run on a GPU partition 
        if job_record.PartitionCategory != 'GPU':
            return datetime.timedelta(0)
        
        # If job elapsed runtime is positive, carry on.
        if job_record.ElapsedRuntime.total_seconds() > 0:
            pass

        # Calculate Total GPU usage time (assuming 100% utilisation)
        gpu_usage_time = job_record.ElapsedRuntime * job_record.GPUsAllocated
        return gpu_usage_time
    

    def min_memory_required(self, job_record):
        """ 
        Calculate the minimum amount of memory (GB) required to run the job

        Args:
            job_record (pd.Series): a single row of the job logs dataframe
        
        Return:
            Min memory required for the job (GB)
        """
        # Round memory to the next GB
        rounded_memory = int(job_record.UsedMemoryGB1) + 1

        # If requested memory is smaller than actual used memory
        if job_record.RequestedMemoryGB < job_record.UsedMemoryGB1:
            return rounded_memory
        
        # Otherwise return the smaller of the two
        else:
            return min(job_record.RequestedMemoryGB, rounded_memory)
        

    def wasted_memory(self, job_record):
        """ 
        Etimates how much memory has been overallocated (i.e. wasted memory)
        It is calculated as the ratio between requested memory and memory required.

        Args:
            job_record (pd.Series): a single row of job logs dataframe

        Return:
            float: ratio of requested memory to required memory 
        """
        # If memory requested was not enough, return 1 
        if job_record.RequestedMemoryGB < job_record.RequiredMemoryGB:
            return 1.0
        else:
            # Otherwise return how much extra memory was requested beyond what was used
            return job_record.RequestedMemoryGB / job_record.RequiredMemoryGB
        

def exit_if_no_jobs(logs_df, user_arguments):
    """ 
    Function to check if any jobs are present in the logs dataframe.
    If no jobs are found within the user-specified date range it exits the program.

    Args:
        job_df (pd.DataFrame): Any DataFrame containing job logs.
        user_arguments (Namespace): Command-line arguments that contain filter options (e.g. JobIDs)

    Return:
        Exits the program logs_df is empty
    """
    if logs_df.empty:
        msg_parts = []

        # Adapt the message based on the user arguments
        if user_arguments.JobIDs != 'all_jobs':     # If the user has specified Job IDs
            msg_parts.append("with the specified job IDs")

        # if user_arguments.WD is not None:           # If the user has specified a working directory
        #     msg_parts.append(f"from the specified working directory: {user_arguments.WD}")

        # Create the message to the user
        filter_message = ', '.join(msg_parts)
        if filter_message:
            filter_message = f" ({filter_message})"
        
        print(f"No jobs were ran within the selected date range ({user_arguments.StartDate} to {user_arguments.EndDate}){filter_message}.")
        sys.exit()





# Function to save dataframes to csv files based on user arguments 
def save_output_dfs(arguments, full_df, daily_df, total_df):
    """
    Saves the output DataFrames to CSV files based on the user-specified CSV argument.
    Summary dataframes are versions with reduced columns for easier readability.
    
    Args:
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
        full_df (pd.DataFrame): Full DataFrame with all jobs (1 row per job)
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day)
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs)
    """
    file_to_save = arguments.CSV

    # Check if the user has provided a valid option for saving files. Print error if not.
    options = ['no_save', 'full', 'daily', 'total', 'full_summary', 'daily_summary', 'total_summary', 'all']
    if file_to_save not in options:
        raise ValueError(f"Unable to Save files due to an invalid --CSV option: '{file_to_save}'. Must be one of: {', '.join(options)}")


    # Define the columns to keep in each summary DataFrame
    full_summary_columns = [
        'Job_ID', 'NameofJob', 'SubmissionTime', 'ElapsedRuntime',
        'EnergyIPMI_kwh', 'energy_estimated_noPUE_kwh', 'energy_estimated_kwh', 
        'Scope2Emissions_IPMI_gCO2e', 'Scope2Emissions_gCO2e', 'Scope3Emissions_gCO2e',
        'TotalEmissions_gCO2e','CarbonIntensity_gCO2e_kwh', 'Cost_GBP', 'driving_miles', 'tree_absorption_months',
        'uk_houses_daily_emissions', 'bris_paris_flights'
    ]

    daily_summary_columns = [
        'SubmissionDate', 'JobCount', 'EnergyIPMI_kwh', 'energy_estimated_noPUE_kwh', 'energy_estimated_kwh', 
        'Scope2Emissions_IPMI_gCO2e', 'Scope2Emissions_gCO2e', 'Scope3Emissions_gCO2e',
        'TotalEmissions_gCO2e', 'CarbonIntensity_gCO2e_kwh','Cost_GBP', 'driving_miles', 'tree_absorption_months',
        'uk_houses_daily_emissions', 'bris_paris_flights'
    ]

    total_summary_columns = [
        'JobCount', 'EnergyIPMI_kwh', 'energy_estimated_noPUE_kwh', 'energy_estimated_kwh', 
        'Scope2Emissions_IPMI_gCO2e', 'Scope2Emissions_gCO2e', 'Scope3Emissions_gCO2e',
        'TotalEmissions_gCO2e', 'CarbonIntensity_gCO2e_kwh', 'Cost_GBP', 'driving_miles', 'tree_absorption_months',
        'uk_houses_daily_emissions', 'bris_paris_flights'
    ]
    # Helper function to save dataframes to CSV files 
    def save(df, filename):
        df.to_csv(f"{filename}.csv", index=False)

    if file_to_save == "no_save":     # This is the default argument option, do not save any files
        return 
    
    if file_to_save in ("full", "all"):
        # save the full jobs df (1 row per job with all columns)
        save(full_df, "full_job_data")

    if file_to_save in ("daily", "all"):
        # save the daily aggregated df (1 row per day with all columns)
        save(daily_df, "daily_data")

    if file_to_save in ("total", "all"):
        # save the total aggregated df (1 row for all jobs with all columns)
        save(total_df, "total_data")
    
    if file_to_save in ("full_summary", "all"):
        # save the full summary df (1 row per job with reduced columns - only important ones)
        save(full_df[full_summary_columns], "full_job_data_summary")

    if file_to_save in ("daily_summary", "all"):
        # save the daily summary df (1 row per day with reduced columns - only important ones)
        save(daily_df[daily_summary_columns], "daily_data_summary")
    
    if file_to_save in ("total_summary", "all"):
        # save the total summary df (1 row for all jobs with reduced columns - only important ones)
        save(total_df[total_summary_columns], "total_data_summary")



# Function for querying the Carbon Intensity API for realtime carbon intensity data
def get_carbon_intensity(submission_times, arguments):
    """
    For each job submission time, this function queries the Carbon Intensity API for the specified region
    and returns the carbon intensity value (gCO2e/kWh) for that time. If the API fails, it falls back 
    to the UK average carbon intensity value (2024).

    API documentation: https://carbon-intensity.github.io/api-definitions/#get-regional-intensity-from-to-regionid-regionid

    Args:
        submission_times (pd.Series): Series of datetime job submission timestamps ('SubmissionTime' column)
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function - must contain 'Region' attribute

    Return:
        pd.Series: Series of carbon intensity values (gCO2e/kWh) corresponding to each job.
    """
    # Define constants for the API
    Date_format_api = "%Y-%m-%dT%H:%MZ"
    time_window = timedelta(minutes=30)  # 30 minutes time window for the API query
    default_CI = 124       # Average UK carbon intensity of electricity (gCO2e/kWh) - 2024 - https://www.carbonbrief.org/analysis-uks-electricity-was-cleanest-ever-in-2024/ 

    # Map the Region Name provided by the user to the region ID used by the API 
    region_map = {
        "North Scotland": 1,
        "South Scotland": 2,
        "North West England": 3,
        "North East England": 4,
        "Yorkshire": 5,
        "North Wales": 6,
        "South Wales": 7,
        "West Midlands": 8,
        "East Midlands": 9,
        "East England": 10,
        "South West England": 11,
        "South England": 12,
        "London": 13,
        "South East England": 14
    }

    # Extract region name from user arguments and the corresponding region ID
    region_name = arguments.Region

    # If the user has not specified a region, use the default UK average carbon intensity for all jobs
    if region_name == "UK_average":
        return pd.Series([default_CI] * len(submission_times), index=submission_times.index)
    
    # Confirm the region name given by the user is valid
    region_id = region_map.get(region_name)
    if region_id is None:
        raise ValueError(f"Invalid region name: '{region_name}'. Must be one of:\n{['UK_average'] + list(region_map.keys())}")
    
    # Loop over each job submission time and query the API 
    carbon_intensity_values = []
    for DateTime in submission_times:
        try:
            # Confirm that the datetime is in UTC and timezone-aware for API compatibility 
            if DateTime.tzinfo is None:
                # from_utc = DateTime.tz_localize("Europe/London").tz_convert("UTC")
                from_utc = DateTime.replace(tzinfo=pytz.UTC)
            else:
                # from_utc = DateTime.tz_convert("UTC")
                from_utc = DateTime.astimezone(pytz.UTC)
        except Exception as e:
            print(f"Error converting datetime {DateTime} to UTC: {e}")
            carbon_intensity_values.append(default_CI)
            continue
    
        to_utc = from_utc + time_window         # the end time is the start time + 30 minutes 
        from_string = from_utc.strftime(Date_format_api)
        to_string = to_utc.strftime(Date_format_api)

        # Querying the API (request) for each job
        url = f"https://api.carbonintensity.org.uk/regional/intensity/{from_string}/{to_string}/regionid/{region_id}"
        try: 
            # Make the GET request to the API 
            api_response = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
            
            # raise an error if the request was unsuccessful
            api_response.raise_for_status()

            # Parse the JSON response as JSON format 
            json_CI_response = api_response.json()

            # Extract the carbon intensity value (gCO2e/kWh) from the response
            carbon_intensity = json_CI_response["data"]["data"][0]["intensity"]["forecast"]

            # Append the value to the list
            carbon_intensity_values.append(carbon_intensity)

        except Exception as e:
            # If the API request fails, use the default carbon intensity value (UK annual average)
            print(f"Failed to get carbon intensity for {DateTime} from the API. Using UK average: {default_CI} gCO2e/kWh. Error: {e}")
            carbon_intensity_values.append(default_CI)

    # Return the carbon intensity values as a pandas Series with the same index as submission_times
    return pd.Series(carbon_intensity_values, index=submission_times.index)
            

    



    

