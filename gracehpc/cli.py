""" 
cli.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 11/07/25

This script serves as the command-line interface (CLI) for the GRACE-HPC package,
allowing users to interact with the package's functionalities directly from the terminal.

GRACE-HPC is a toolkit designed to estimate the energy consumption and carbon emissions of HPC jobs.

Command Line Usage:
    'gracehpc configure' - Generates and saves a YAML configuration file ('hpc_config.yaml') in the user's
                           current working directory. The user must fill in this file with their HPC configuration 
                           details before using the tool.
                    
    'gracehpc run [arguments]' - Runs the full backend and frontend engines to process SLURM job logs, calculate energy and emissions data, 
                                 and display the results in the terminal.

User Arguments Available:
    --StartDate: Start date, 'YYYY-MM-DD' format (required)
    --EndDate: End date, 'YYYY-MM-DD' format (required)
    --JobIDs: Comma-separated list of job IDs to filter on (optional), default is 'all_jobs'
    --Region: Region the HPC cluster is located in (for realtime carbon intensity data), default is 'UK_average'. E.g. 'South West England' for Isambard systems.
    --Scope3: Scope 3 per node-hour emissions factor. Options include: 'Isambard3', 'IsambardAI', 'Archer2', or a custom value in gCO2e/nodeh, default = 'no_scope3'
    --CSV: Save the final dataframes to CSV files. Options include 'all', 'full', 'daily', 'total', 'full_summary', 'daily_summary, 'total_summary'. default = 'no_save'
    --help: For more information on available arguments and their usage.
"""

# Import libraries
import argparse
import os 
import sys
import datetime

# Import functions and classes from the package
from .core.emissions_calculator import core_engine
from .config import generate_config_file


def confirm_date_args(arguments):
    """
    Function that checks if the StartDate and EndDate arguments are valid and in the correct format.
    
    Raises:
        ValueError: If the date format is incorrect or if StartDate is after EndDate.
    """
    # Loop over both date arguments 
    for date in [arguments.StartDate, arguments.EndDate]:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            # Print an error message if format is incorrect
            raise ValueError(f"Invalid format for StartDate or EndDate: {date}. Please use 'YYYY-MM-DD' format.")
        
    # Check if StartDate is after EndDate
    start_date = datetime.datetime.strptime(arguments.StartDate, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(arguments.EndDate, "%Y-%m-%d")
    if start_date > end_date:
        raise ValueError(f"StartDate: {arguments.StartDate} is after EndDate: {arguments.EndDate}. Please ensure StartDate is before EndDate.")


def main():
    """
    Main function to handle command-line arguments.
    """
    # Create an main argument parser for the CLI
    arg_parser = argparse.ArgumentParser(prog="gracehpc", description=(
        " \n\nGRACE-HPC: A Green Resource for Assessing Carbon & Energy in HPC.\n\n\n" 
        "This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs.\n" 
        "If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage statistics. "),
    epilog=(
        " \n\nCarbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API (carbonintensity.org.uk.) at the time of job submission. " 
        "Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. For Isambard systems and Archer2, these scope 3 factors are calculated from " 
        "the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.\n\n\n "),
        formatter_class=argparse.RawTextHelpFormatter)  # Use RawTextHelpFormatter to preserve newlines in help text

    # Add subparsers for 'configure' and 'run' commands
    subparsers = arg_parser.add_subparsers(dest="command", help="Subcommands")
    
    # Command: gracehpc configure (no arguments needed for this command)
    configure_subcommand =  subparsers.add_parser("configure", help="Generate and save the HPC cluster configuration file. Fill in the YAML file with your HPC configuration details before using the tool.")

    # Command: gracehpc run
    run_subcommand = subparsers.add_parser("run", help="Run the full engine to estimate the carbon footprint (scope 2 and scope 3) of your SLURM HPC jobs.")

    # ---------------------------------------
    # ADD ARGUMENTS TO THE 'run' SUBCOMMAND
    # ---------------------------------------
    SD_default = f"{datetime.date.today().year}-01-01"      # Set the default start date January 1st of the current year    
    ED_default = datetime.date.today().strftime("%Y-%m-%d")  # Set the default end date to the current date

    # Date range arguments 
    run_subcommand.add_argument("--StartDate", 
                                type=str,
                                help=f"The first date of the range to process jobs for, in YYYY-MM-DD. Default: {SD_default}",
                                default = SD_default)
    run_subcommand.add_argument("--EndDate",
                                type=str,
                                help=f"The final date of the range to process jobs for, in YYYY-MM-DD. Default: {ED_default}",
                                default = ED_default)
    
    # Filtering arguments
    run_subcommand.add_argument("--JobIDs",
                                type=str,
                                help="Comma-separated list (no spaces) of all the HPC job IDs to filter on. Default: 'all_jobs'",
                                default = "all_jobs")
    
    # Region argument for carbon intensity data 
    run_subcommand.add_argument("--Region",
                                type=str,
                                default="UK_average",
                                help=(
                                    "UK region of the HPC cluster needed for realtime carbon intensity data. "
                                    "Options: 'North Scotland', 'South Scotland', 'North West England', 'North East England', 'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', "
                                    "'East Midlands', 'East England', 'South West England', 'South England', 'London', 'South East England'. Default: 'UK_average'. "
                                    "E.g. 'South West England' for Isambard systems and South Scotland for Archer2."))
    
    # Adding Scope 3 emissions or not 
    run_subcommand.add_argument("--Scope3",
                                type=str,
                                default="no_scope3",
                                help=(
                                    "Include scope 3 emissions for either: 'Isambard3', 'IsambardAI', 'Archer2', or a custom numeric value in gCO2e/node-hour for other HPC systems. Default: 'no_scope3'. "
                                    "If 'no_scope3' is selected, only scope 2 emissions will be calculated. "))
    
    # Saving data to CSV files 
    run_subcommand.add_argument("--CSV",
                                type=str,
                                default="no_save",
                                help=(
                                    "Save the final datasets to CSV files for further analysis. "
                                    "Options: 'full': entire dataset (all jobs) with all columns, 'full_summary': entire dataset with summary columns only, "
                                    "'daily': dataset aggregated by day with all columns, 'daily_summary': dataset aggregated by day with summary columns only, "
                                    "'total': dataset aggregated over all total jobs with all columns, 'total_summary': dataset aggregated over all total jobs with summary columns only," \
                                    "'all' : all of the above datasets saved to CSV files. Default: 'no_save'."
                                ))
    

    # Parse CLI arguments
    arguments = arg_parser.parse_args()

    
    # Handle the 'gracehpc configure' command
    if arguments.command == "configure": 
        # call generation function to create the hpc_config.yaml file
        generate_config_file()
        # Stop the script 
        sys.exit(0)

    # Handle the 'gracehpc run' command
    elif arguments.command == "run":

        try:
            confirm_date_args(arguments)  # Check if the date arguments are valid
        except ValueError as e:
            print(f"❌ Date validation error: {e}")
            sys.exit(1) # exit the script with an error code 
        
        # Execute the entire backend (core_engine) by passing the arguments 
        full_df, daily_df, total_df = core_engine(arguments)




        # Pass the dataframes to the terminal frontend to display results
        cli_output(full_df, daily_df, total_df, arguments)





    # Handle the invalid subcommands by printing the help information 
    else:
        arg_parser.print_help()
        sys.exit(1)





# if __name__ == "__main__":
#     main()




        
