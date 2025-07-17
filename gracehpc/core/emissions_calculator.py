""" 
emissions_calculator.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 08/07/25

This module contains code to estimate the energy consumption and carbon emissions of SLURM-based HPC jobs.
It stores the final estimates along with sacct data in final aggregated dataframes, which can be saved to CSV files.

Steps:

1. Retrieves job logs using the job_log_manager.py module
2. Processes the logs to extract the relevant data
3. Estimates energy consumption and carbon emissions (scope 2 using live grid carbon intensity data and scope 3). Scope 2 = operational, scope 3 = embodied emissions.
4. Aggregates the data into final dataframes which can be saved to CSV files later if specified by the user in the arguments.
"""
# Import libraries
import yaml 
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os 
import requests

# Import functions/classes from other modules
from .backend_utils import exit_if_no_jobs, save_output_dfs, get_carbon_intensity
from .job_log_manager import JobLogProcessor

# Class to estimate energy consumption, scope 2 (operational emissions) and scope 3 (embodied emissions)
class EnergyEmissionsCalculator():
    """ 
    Class for estimating energy consumption and carbon emissions (scope 2 and scope 3) of SLURM-based HPC jobs.
    """
    def __init__(self, hpc_config, arguments):
        """ 
        Initialise the EnergyEmissionsCalculator class with HPC cluster configuration file.

        Args:
            hpc_config (dict): Dictionary containing metadata about the HPC cluster.
            arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
        """
        self.hpc_config = hpc_config        # Store HPC cluster configuration
        self.arguments = arguments      # Store user arguments

        # Store constants 
        self.power_gb_mem = 0.3725 # Power consumption per GB of memory (W/GB) - estimated average from the literature


    def estimate_energy(self, job_record):
        """ 
        Estimate the energy consumption for a single job (1 row) based on 
        sacct usage data. (Not using energy plugins such as IPMI))

        Args:
            job_record (pd.Series): a single row (1 job) containing the processed usage data from sacct.

        Returns:
            pd.Series: The input with energy estimates appended as new columns.
        """
        # Extract the partition information from the configuration file 
        data_partition = self.hpc_config['partitions'][job_record.PartitionName]

        # Determine the TDP values depending on the partition category (CPU or GPU)
        if job_record.PartitionCategory == 'CPU':           # CPU-only partitions 
            cpu_tdp = data_partition['TDP'] # CPU TDP from the configuration file 
            gpu_tdp = 0                     # No GPU power for CPU-only partitions

        else:           # GPU partitions
            cpu_tdp = data_partition['CPU_TDP']    # CPU TDP for GPU partitions
            gpu_tdp = data_partition['TDP']         # GPU TDP from the configuration file

        # Calculate CPU energy from usage data, then convert to kWh (time (h) * power draw (W))
        job_record['CPU_energy_estimated_kwh'] = job_record.CPUusagetime.total_seconds() / 3600 * cpu_tdp / 1000 

        # Calculate GPU energy from usage data, then convert to kWh in the same way
        job_record['GPU_energy_estimated_kwh'] = job_record.GPUusagetime.total_seconds() / 3600 * gpu_tdp / 1000

        # Calculate the memory energy for requested memory then convert to kWh
        job_record['memory_energy_estimated_kwh'] = job_record.ElapsedRuntime.total_seconds() / 3600 * job_record.RequestedMemoryGB * self.power_gb_mem / 1000

        # Sum components and multiply by the PUE (DC overhead) to get total energy consumption estimate (kWh)
        job_record['energy_estimated_kwh'] = (
            job_record.CPU_energy_estimated_kwh + 
            job_record.GPU_energy_estimated_kwh + 
            job_record.memory_energy_estimated_kwh
        ) * self.hpc_config['PUE']

        # Do the same without the PUE for energy plugin comparison
        job_record['energy_estimated_noPUE_kwh'] = (
            job_record.CPU_energy_estimated_kwh + 
            job_record.GPU_energy_estimated_kwh + 
            job_record.memory_energy_estimated_kwh)
        
        # Calculate the memory energy for required memory 
        job_record['required_memory_energy_estimated_kwh'] = job_record.ElapsedRuntime.total_seconds() / 3600 * job_record.RequiredMemoryGB * self.power_gb_mem / 1000

        # total energy using the required memory
        job_record['energy_requiredMem_estimated_kwh'] = (
            job_record.CPU_energy_estimated_kwh + 
            job_record.GPU_energy_estimated_kwh + 
            job_record.required_memory_energy_estimated_kwh
        ) * self.hpc_config['PUE']

        return job_record
    

    def scope2_emissions(self, df_jobs, energy_column, carbon_intensity_values):
        """
        Compute the scope 2 (operational) carbon emissions for each job in a dataframe 
        based on the given energy column (kWh) and realtime grid carbon intensity data.

        Args:
            df_jobs (pd.DataFrame): Full dataframe containing job data with energy columns and submission times.
            energy_column (str): The name of the column containing energy consumption data in kWh (estimated by usage data or measured by energy counters).
            carbon_intensity_values (pd.Series): A pandas series containing carbon intensity values (gCO2e/kWh) for each job's submission time from the web API.

        Returns: 
            pd.Series: a pandas series containing scope 2 emissions estimates for each job (gCO2e) calculated from the specified energy column.
        """

        # Check if energy column is from energy counters or estimated from usage data 
        if energy_column == 'EnergyIPMI_kwh':
            # Confirm if HPC system has working energy counters by checking if any value in the IPMI column is greater than 0
            if (df_jobs[energy_column] > 0).any():
                # Apply data centre overheads (PUE) 
                energy_consumption = df_jobs[energy_column] * self.hpc_config['PUE']
            else:
                # If all values are 0, skip PUE adjustment
                energy_consumption = df_jobs[energy_column]
           
        else:   
            # If column is not from energy counters 
            energy_consumption = df_jobs[energy_column]      

        # calculate and return scope 2 emissions for each job = energy (kWh) * carbon intensity (gCO2e/kWh)
        return energy_consumption * carbon_intensity_values




    def scope3_emissions(self, df_jobs):
        """
        Compute the scope 3 (embodied) carbon emissions for each job in a dataframe 
        using node-hours used and a per-node-hour scope 3 emissions factor.
        Scope 3 emissions estimates are only calculated if the user specifies either 
        'Isambard3', 'IsambardAI', 'Archer2' or their own per-node-scope3 emissions factor for the 
        user argument 'Scope3'.

        Isambard system scope 3 per node-hour estimates are taken from my own lifecycle assessment 
        quantifying embodied and operational emissions.
        Archer2 value is from the Archer2 documentation.
        - 'Isambard 3' = 43.0 gCO2e/node-hour
        - 'Isambard AI' = 114.0 gCO2e/node-hour
        - 'Archer2' = 23.0 gCO2e/node-hour

        Users can enter their own per-node-hour scope 3 value (i.e. for a different HPC system) by passing a number
        in gCO2e/node-hour to the 'Scope3' argument in the CLI or script/JN usable function.

        Args:
            df_jobs (pd.DataFrame): Full dataframe containing job data with a 'NodeHours' column.

        Returns:
            pd.Series: a pandas series containing scope 3 emissions estimates for each job (gCO2e) 
        """
        # Store user argument
        scope3_argument = self.arguments.Scope3

        if scope3_argument == "no_scope3":          # This is the default argument 
            # If no scope 3 emissions are requested, return a series of zeros
            return pd.Series([0.0] * len(df_jobs), index=df_jobs.index)
        
        # Determine the scope 3 emissions factor based on the user argument
        if scope3_argument == "Isambard3":
            scope3_per_nodeh = 43.0     # gCO2e/node-hour
        elif scope3_argument == "IsambardAI":
            scope3_per_nodeh = 114.0    # gCO2e/node-hour
        elif scope3_argument == "Archer2":
            scope3_per_nodeh = 23.0    # gCO2e/node-hour
        else:       # If the user has specified a custom scope 3 (number) or incorrect argument
            try:
                scope3_per_nodeh = float(scope3_argument)       # Convert custom emissions factor to float
            
            except (TypeError, ValueError):
                raise ValueError(f"Invalid Scope3 argument: {scope3_argument}. Please enter a valid number or one of the predefined options: 'Isambard3', 'IsambardAI', 'Archer2' or 'no_scope3'.")
            
        # Calculate scope 3 emissions for each job (node-hours * scope 3 emissions per node-hour)
        return df_jobs['NodeHours'] * scope3_per_nodeh




# Function to retrieve and process job logs from SLURM
def get_job_logs(arguments, hpc_config):
    """
    Retrieve and process job accounting logs from SLURM using the 
    JobLogProcessor class. Based on user arguments.
    
    Args:
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
        hpc_config (dict): Dictionary containing metadata about the HPC cluster.
        
    Returns:
        pd.DataFrame: The final processed dataframe from JobLogProcessor containing all relevant data columns.
    """
    # Instantiate the JobLogProcessor class with HPC cluster configuration and user arguments
    JLP = JobLogProcessor(arguments, hpc_config)

    # Retrieve job logs from SLURM using sacct
    JLP.retrieve_job_logs()

    # Convert the raw sacct output to a structured pandas DataFrame
    JLP.df_conversion()

    # Confirm that there are jobs found within the date range given by the user. If not, exit the program
    exit_if_no_jobs(JLP.sacct_df, arguments)

    # Process and aggregate the job logs df, filtering based on user arguments
    JLP.df_processor()

    # Ensure the processed (aggregated) dataframe is also not empty
    exit_if_no_jobs(JLP.filtered_df, arguments)

    # Verify that the final df only contains logs from a single user
    if len(set(JLP.final_df.UserName)) > 1:
        raise ValueError(f"Multiple users found in the job logs: {set(JLP.final_df.UserName)}. Please ensure you are only processing logs for a single user.")
    
    # Return the final processed/filtered dataframe
    return JLP.final_df


# Function to calculate energy consumption and emissions estimates and add them to the dataframe
def add_emissions_data (df_jobs, emissions_calculator, hpc_config):
    """
    Computes energy consumption, scope2 emissions, and scope 3 emissions estimates 
    for each job and then adds them to the final dataframe. It also calculates 
    contextual equivalent metrics, storing them in additional columns.

    Args:
        df_jobs (pd.DataFrame): The final processed dataframe containing job logs.
        emissions_calculator (Class): The EnergyEmissionsCalculator class instance for calculating energy and emissions.

    Returns:
        pd.DataFrame: The same input dataframe with additional columns for energy consumption, scope 2, scope 3 emissions and
        contextual equivalent metrics.
    """
    # Calculate energy consumption estimates from usage data (not energy counters)
    df_jobs = df_jobs.apply(emissions_calculator.estimate_energy, axis=1)

    # Filter on failed jobs (State code = 0) to see the wasted energy and emissions
    df_jobs['failed_energy_kwh'] = np.where(df_jobs['StateCode'] == 0, df_jobs.energy_estimated_kwh, 0)

    # Get the carbon intensity value at the submission time of each job from the web API - depends on the 'Region' argument given by the user
    carbon_intensity_values = get_carbon_intensity(df_jobs['SubmissionTime'], emissions_calculator.arguments)

    # Store carbon intensity values in the dataframe
    df_jobs['CarbonIntensity_gCO2e_kwh'] = carbon_intensity_values

    # Calculate carbon emissions using full memory (requested)
    df_jobs['Scope2Emissions_gCO2e'] = emissions_calculator.scope2_emissions(df_jobs, 'energy_estimated_kwh', carbon_intensity_values)        # Scope 2 carbon emissions estimated using usage data
    df_jobs['Scope2Emissions_IPMI_gCO2e'] = emissions_calculator.scope2_emissions(df_jobs, 'EnergyIPMI_kwh', carbon_intensity_values)      # Scope 2 carbon emissions estimated using energy counters (if available)
    df_jobs['Scope3Emissions_gCO2e'] = emissions_calculator.scope3_emissions(df_jobs)       # Scope 3 carbon emissions

    # Calculate scope 2 carbon emissions using required memory only to assess wasted memory
    df_jobs['Scope2Emissions_requiredMem_gCO2e'] = emissions_calculator.scope2_emissions(df_jobs, 'energy_requiredMem_estimated_kwh', carbon_intensity_values)

    # Scope 2 emissions of failed jobs
    df_jobs['Scope2Emissions_failed_gCO2e'] = emissions_calculator.scope2_emissions(df_jobs, 'failed_energy_kwh', carbon_intensity_values)

    # Add cost
    cost_per_kwh = hpc_config.get('electricity_cost', 0.2573) # Default = Average Cost of electricity in the UK (0.2573 GBP/kWh) - July 2025 - https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap

    # Use energy from counters if available, otherwise use estimated energy from usage data 
    if (df_jobs['EnergyIPMI_kwh'] > 0).all():
        # Use plugin-energy for cost calculation if available
        df_jobs['Cost_GBP'] = df_jobs['EnergyIPMI_kwh'] * cost_per_kwh    # cost of electricity in GBP

        # Total carbon emissions (scope 2 from energy counters + scope 3)
        df_jobs['TotalEmissions_gCO2e'] = df_jobs['Scope2Emissions_IPMI_gCO2e'] + df_jobs['Scope3Emissions_gCO2e']

    else:
        # Otherwise use estimated energy from usage data
        df_jobs['Cost_GBP'] = df_jobs['energy_estimated_kwh'] * cost_per_kwh

        # Total carbon emissions (scope 2 from usage data + scope 3)
        df_jobs['TotalEmissions_gCO2e'] = df_jobs['Scope2Emissions_gCO2e'] + df_jobs['Scope3Emissions_gCO2e']

    ### ----------------------------------------------------------------------------------------------
    ### CONTEXTUAL EQUIVALENTS
    ### ----------------------------------------------------------------------------------------------

    # Constants
    driving_per_miles = 211.2       # gCO2e/mile - average driving emissions per car in the UK (2023) - https://www.nimblefins.co.uk/average-co2-emissions-car-uk#nogo 
    tree_months_factor = 833      # gCO2e/month - average carbon sequestration rate of one mature tree in the UK (~ 10kgCO2e absorbed per year) - 
                                  # https://onetreeplanted.org/blogs/stories/how-much-co2-does-tree-absorb?srsltid=AfmBOopRTUnD98_burqqG8JqB93xk9VGxHDDes7QyZj0p-OMyvQSgJsG
    daily_UK_house_energy = 7.397       # Average daily electricity use of a UK household (kWh/day) - 2700kWh per year - https://www.ofgem.gov.uk/information-consumers/energy-advice-households/average-gas-and-electricity-use-explained
    average_UK_CI = 124      # Average UK carbon intensity of electricity (gCO2e/kWh) - 2024 - https://www.carbonbrief.org/analysis-uks-electricity-was-cleanest-ever-in-2024/ 
    daily_UK_house_emissions = daily_UK_house_energy * average_UK_CI  # gCO2e/day
    bris_paris_flight = 141700    # gCO2e/passenger - estimated emissions for a one-way flight from Bristol to Paris - https://curb6.com/footprint/flights/bristol-brs/paris-cdg

    # Add equivalents to the dataframe
    df_jobs['driving_miles'] = df_jobs.TotalEmissions_gCO2e / driving_per_miles         # Equivalent miles driven by an average petrol/diesel car in the UK
    df_jobs['tree_absorption_months'] = df_jobs.TotalEmissions_gCO2e / tree_months_factor  # Equivalent months of carbon absorption by a mature tree
    df_jobs['uk_houses_daily_emissions'] = df_jobs.TotalEmissions_gCO2e / daily_UK_house_emissions  # Equivalent number of UK households' daily emissions
    df_jobs['bris_paris_flights'] = df_jobs.TotalEmissions_gCO2e / bris_paris_flight  # Equivalent number of flights from Bristol to Paris

    return df_jobs


# Function to aggregate the data and produce final dataframes 
def aggregate_df(df_jobs, arguments):
    """
    Summarise the job dataframe at different aggregation levels:
    - Full dataframe: one row per job with all columns
    - Daily dataframe: aggregated by day 
    - Total dataframe: aggregated over all jobs

    Args:
        df_jobs (pd.DataFrame): The final processed dataframe containing job logs with energy, emissions estimates and contextual equivalents.
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function

    Returns:
        tuple: three dataframes containing the full job data, daily aggregated data and total aggregated data.
            - full_df (pd.DataFrame): original job data with added emissions columns (one row per job)
            - daily_df (pd.DataFrame): daily aggregated data (one row per day)
            - total_df (pd.DataFrame): total aggregated data (one row summarising all jobs)
    """
    # Dictionary defining how to aggregate each column (keys are output column names, values are input column names and aggregation functions)
    aggregation_dict = {
        'JobCount': ('UserName', 'count'),  # count the number of jobs via UserName occurrences
        'FirstJobTime': ('SubmissionTime', 'min'),  # earliest job submission time
        'LastJobTime': ('SubmissionTime', 'max'),  # latest job submission time
        
        ## Energy columns 
        'energy_estimated_kwh': ('energy_estimated_kwh', 'sum'),  # total energy estimated from usage data (with PUE)
        'energy_estimated_noPUE_kwh': ('energy_estimated_noPUE_kwh', 'sum'),  # total energy estimated from usage data (without PUE)
        'CPU_energy_estimated_kwh': ('CPU_energy_estimated_kwh', 'sum'),  # total CPU energy estimated from usage data
        'GPU_energy_estimated_kwh': ('GPU_energy_estimated_kwh', 'sum'),  # total GPU energy estimated from usage data
        'memory_energy_estimated_kwh': ('memory_energy_estimated_kwh', 'sum'),  # total memory energy estimated from usage data
        'EnergyIPMI_kwh': ('EnergyIPMI_kwh', 'sum'),  # total energy from counters (if available)

        ## Emissions columns
        'Scope2Emissions_gCO2e': ('Scope2Emissions_gCO2e', 'sum'),  # total scope 2 emissions from usage data (using energy_estimated)
        'Scope2Emissions_IPMI_gCO2e': ('Scope2Emissions_IPMI_gCO2e', 'sum'),  # total scope 2 emissions from energy counters (if available)
        'Scope2Emissions_requiredMem_gCO2e': ('Scope2Emissions_requiredMem_gCO2e', 'sum'),  # total scope 2 emissions from usage data using required memory only
        'Scope2Emissions_failed_gCO2e': ('Scope2Emissions_failed_gCO2e', 'sum'), # scope 2 emissions of failed jobs (using energy_estimated)
        'Scope3Emissions_gCO2e': ('Scope3Emissions_gCO2e', 'sum'),  # total scope 3 emissions (will be 0 if no scope 3 emissions are requested)
        'TotalEmissions_gCO2e': ('TotalEmissions_gCO2e', 'sum'),  # total carbon emissions (scope 2 + scope 3). Uses Scope2Emissions_IPMI if energy counters are available
        'CarbonIntensity_gCO2e_kwh': ('CarbonIntensity_gCO2e_kwh', 'mean'),  # average carbon intensity at job submission time (from web API)

        ## General Sacct parameter columns 
        'CPUusagetime': ('CPUusagetime', 'sum'),  # total CPU usage time
        'GPUusagetime': ('GPUusagetime', 'sum'),  # total GPU usage time
        'ElapsedRuntime': ('ElapsedRuntime', 'sum'),  # total elapsed runtime
        'NodeHours': ('NodeHours', 'sum'),  # total node-hours charged
        'CPUhours': ('CPUhours', 'sum'),  # total CPU-hours charged
        'GPUhours': ('GPUhours', 'sum'),  # total GPU-hours used charged 
        'RequestedMemoryGB': ('RequestedMemoryGB', 'sum'),  # total requested memory (GB)
        'RequiredMemoryGB': ('RequiredMemoryGB', 'sum'),  # total required memory (GB)
        'UsedMemoryGB': ('UsedMemoryGB', 'sum'),  # total used memory (GB)
        'WastedMemoryRatio': ('WastedMemoryRatio', 'mean'),  # average wasted memory ratio
        'successful_jobs': ('StateCode', 'sum'),   # Total number of successful jobs 

        # Contextual equivalents and cost columns
        'Cost_GBP': ('Cost_GBP', 'sum'),  # total cost of electricity use in GBP (uses energy from counters if available)
        'driving_miles': ('driving_miles', 'sum'),  # total equivalent miles driven by an average petrol/diesel car in the UK
        'tree_absorption_months': ('tree_absorption_months', 'sum'),  # total equivalent months of carbon absorption by a mature tree
        'uk_houses_daily_emissions': ('uk_houses_daily_emissions', 'sum'), # total equivalent number of UK households' daily emissions
        'bris_paris_flights': ('bris_paris_flights', 'sum'),  # total equivalent number of flights from Bristol to Paris
    }

    def aggregation(df, group_by_column=None):
        """
        Function to aggregate the job dataframe by the specified column.

        Args:
            df (pd.DataFrame)): the full job dataframe to aggregate.
            group_by_column (list): list of columns to group by. Default is None (the entire dataframe is aggregated)

        Returns:
            pd.DataFrame: the aggregated dataframe.
        """
        group_by_column1 = group_by_column if group_by_column else (lambda _: True)  # If no group by column is specified, aggregate the entire dataframe

        # Aggregate using the aggregation dictionary
        aggregated_df = df.groupby(group_by_column1).agg(**aggregation_dict) 

        # Reset the index to make the grouped columns regular columns
        aggregated_df.reset_index(inplace=True, drop=(group_by_column is None))

        # Add extra summary columns
        aggregated_df['SuccessFraction'] = aggregated_df.successful_jobs / aggregated_df.JobCount # Ratio of successful jobs 
        aggregated_df['FailedFraction'] = 1 - aggregated_df.SuccessFraction  # Ratio of failed jobs
        aggregated_df['EmissionsFraction'] = aggregated_df.TotalEmissions_gCO2e / aggregated_df.TotalEmissions_gCO2e.sum()  # The share of total emissions contribution per group 

        return aggregated_df
    
    # Add a seperate column for the date of each submissions (not the time)
    df_jobs['SubmissionDate'] = df_jobs.SubmissionTime.dt.date

    # Full dataframe: one row per job with all columns (no aggregation)
    full_df = df_jobs.copy()

    # Daily aggregated dataframe: one row per day
    daily_df = aggregation(df_jobs, group_by_column=['SubmissionDate'])

    # Total aggregated dataframe: one row summarising all jobs
    total_df = aggregation(df_jobs)

    # return all three dataframes
    return full_df, daily_df, total_df


# Function to run the whole backend process 
def core_engine(arguments):
    """
    Main function to run the entire backend process:
    - Retrieving job logs from SLURM 
    - Processing the logs to extract relevant data
    - Calculating energy consumption and emissions estimates
    - Aggregating the data into final dataframes

    Args: 
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
    
    Returns:
        tuple: three dataframes containing the full job data, daily aggregated data and total aggregated data
    """
    # Load the hpc_config.yaml file (user must edit this file to match their HPC system)
    with open('hpc_config.yaml', 'r') as file:
        try: 
            hpc_config = yaml.safe_load(file)  # Load the YAML file into a dictionary
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading hpc_config.yaml: {e}")
        
    # Initialise the EnergyEmissionsCalculator class with the loaded configuration and user arguments
    EEC = EnergyEmissionsCalculator(hpc_config, arguments)

    # Extract raw job log data 
    df_raw = get_job_logs(arguments, hpc_config=hpc_config)

    # Add energy consumption and emissions estimates to the job logs dataframe
    df_emissions = add_emissions_data(df_raw, emissions_calculator=EEC, hpc_config=hpc_config)

    # Aggregate the data into final dataframes
    full_df, daily_df, total_df = aggregate_df(df_emissions, arguments=arguments)

    # Save the dfs to CSV files if the user has specified in the arguments 
    save_output_dfs(arguments, full_df, daily_df, total_df)

    return full_df, daily_df, total_df
