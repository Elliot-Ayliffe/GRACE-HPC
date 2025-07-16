""" 
script.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 12/07/25

This script contains the main function that enables users to run the GRACE-HPC tool programmatically in a Python script or Jupyter notebook.
This is an alternative to using the command-line interface (CLI) provided by the package.

It includes:

-  `build_args()`: Helper function to convert user inputs into an `argparse.Namespace` object 
  compatible with the backend core engine.

- `gracehpc_run()`: Main function to run the full GRACE-HPC engine and display results, 
  accepting the same input parameters as the CLI 'run' command. This function is part of the package's public API, allowing users to run call it in their own scripts or notebooks.
"""

# Import libraries
import argparse
import datetime 
import sys 

# Import functions from other modules
from .cli import confirm_date_args
from .core.emissions_calculator import core_engine
from .interface.cli_script_output import main_cli_script_output


# Function to convert user inputs into compatible arguments for the core_engine
def build_args(StartDate, EndDate, JobIDs, Region, Scope3, CSV):
    """
    Convert user inputs into an argparse.Namespace object that mimics the CLI 'run' command arguments.
    This format is necessary for the core_engine to process the data correctly.
    
    Args:
        StartDate (str): Start of the date range in 'YYYY-MM-DD' format.
        EndDate (str): End of the date range in 'YYYY-MM-DD' format.
        JobIDs (str): Comma-separated list of HPC job IDs to filter on. 
        Region (str): UK region for carbon intensity data. 
        Scope3 (str): Scope 3 emissions option.
        CSV (str): Option to save data to CSV files.

    Returns:
        argparse.Namespace: An object containing the arguments in a format compatible with the core_engine (tool backend).
    """
    return argparse.Namespace(
        command="run",
        StartDate=StartDate,
        EndDate=EndDate,
        JobIDs=JobIDs,
        Region=Region,
        Scope3=Scope3,
        CSV=CSV
    )


# Main function to run the full tool from a script
def gracehpc_run(StartDate=f"{datetime.date.today().year}-01-01", EndDate=datetime.date.today().strftime("%Y-%m-%d"), JobIDs="all_jobs", Region="UK_average", Scope3="no_scope3", CSV="no_save"):
    """
    Run the GRACE-HPC tool programmatically in a script (alternative to CLI).
    
    This function enables users to run the full engine to estimate the carbon footprint (scope 2 and scope 3) of your SLURM HPC jobs via python scripts or Jupyter Notebooks, 
    rather than the command line interface (CLI).
    Results are printed to the console and saved to CSV files if specified. 3 dataframes are returned containing the full, daily and total datasets.
    
    
    GRACE-HPC: A Green Resource for Assessing Carbon & Energy in HPC. 

    This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs.
    If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage statistics.

    Carbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API (carbonintensity.org.uk.) at the time of job submission. 
    Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. For Isambard systems and Archer2, these scope 3 factors are calculated from 
    the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.

    
    Args:
        StartDate (str): The first date of the range to process jobs for, in YYYY-MM-DD. Default is January 1st of the current year.
        EndDate (str): The final date of the range to process jobs for, in YYYY-MM-DD. Default is the current date.
        JobIDs (str, optional): Comma-separated list of all the HPC job IDs to filter on (no spaces). Default is "all_jobs", which processes all jobs in the specified date range.
        Region (str, optional): UK region of the HPC cluster needed for realtime carbon intensity data.

            Options: 'North Scotland', 'South Scotland', 'North West England', 'North East England', 'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', 
                                'East Midlands', 'East England', 'South West England', 'South England', 'London', 'South East England'. Default: 'UK_average'. 

                                    E.g. 'South West England' for Isambard systems and 'South Scotland' for Archer2.
        Scope3 (str, optional): Option to include scope 3 emissions (embodied) in the calculations.

            HPC systems available: 'Isambard3', 'IsambardAI', 'Archer2'

            Or include custom numeric value in gCO2e/node-hour for other HPC systems (e.g. "51"). Default is 'no_scope3' which means only scope 2 emissions (operational) will be calculated.
        CSV (str, optional): Save the final datasets to CSV files for further analysis. 

            Options
            - 'full'          : entire dataset (all jobs) with all columns  
            - 'full_summary'  : entire dataset with summary columns only  
            - 'daily'         : dataset aggregated by day with all columns  
            - 'daily_summary' : dataset aggregated by day with summary columns only  
            - 'total'         : dataset aggregated over all total jobs with all columns  
            - 'total_summary' : dataset aggregated over all total jobs with summary columns only  
            - 'all'           : all of the above datasets saved to CSV files

    
    Raises: 
        ValueError: If the StartDate/EndDate format is incorrect or if StartDate is after EndDate.

    Returns:
        tuple (pd.DataFrame, pd.DataFrame, pd.DataFrame):
            - full_df: DataFrame containing the full dataset of jobs processed. (1 row per job)
            - daily_df: DataFrame containing the daily aggregated dataset. (1 row per day)
            - total_df: DataFrame containing the total aggregated dataset. (1 row totalling all jobs)

    Examples:
        >>> gracehpc_run(StartDate="2025-06-01", EndDate="2053-07-25", JobIDs="12345,67890", Region="South West England", Scope3="IsambardAI", CSV="all")
        >>> gracehpc_run(StartDate="2025-01-01", EndDate="2025-08-01", Region="South West England", Scope3="Isambard3", CSV="full_summary")
        >>> gracehpc_run(StartDate="2025-07-16", EndDate="2025-07-07", JobIDs"id1245", Region="London", Scope3="51", CSV="no_save")

    For more information on the required arguments use:
        >>> help(gracehpc_run)
    """

    # Convert the user inputs into an argparse.Namespace object
    arguments = build_args(StartDate, EndDate, JobIDs, Region, Scope3, CSV)

    # Validate the date arguments are correct 
    try:
        confirm_date_args(arguments)  # Check if the date arguments are valid
    except ValueError as e:
            print(f"❌ Date validation error: {e}")
            sys.exit(1) # exit the script with an error code 

    # Execute the entire backend (core_engine) by passing the arguments 
    full_df, daily_df, total_df = core_engine(arguments)

    # Pass the dataframes to the script frontend to display results
    main_cli_script_output(full_df, daily_df, total_df, arguments)

    # return dataframes for use in jupyter notebooks or other scripts 
    return full_df, daily_df, total_df



