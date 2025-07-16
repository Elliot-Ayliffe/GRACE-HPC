"""
cli_script_output.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 16/07/25

This module contains functions to display GRACE-HPC results in the terminal using the rich library.
It is used for the command-line interface (CLI) and script usage of the GRACE-HPC package.
However, it can also be used in a Jupyter Notebook to display results in a terminal-like format.

It provides the main frontend output function for the cli.py and script.py scripts

Key Functions:

- 'results_terminal_display(full_df, daily_df, total_df, arguments, hpc_config)':  
    Displays a full breakdown of energy and emissions results in the terminal, including summary panels, statistics, and annotated emissions breakdowns.

- 'main_cli_script_output(full_df, daily_df, total_df, arguments)':  
    Main frontend function for CLI/script use. Loads the HPC config file and calls 'results_terminal_display' to produce the full output.
"""




# Import libraries 
from rich import print
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.rule import Rule
import numpy as np 
import pandas as pd
import datetime
import yaml 

# Import functions from other modules
from .jupyter_output import emissions_unit_converter, tree_months_formatter



def results_terminal_display(full_df, daily_df, total_df, arguments, hpc_config):
    """
    Function to display the results in the terminal. This is the output for the 
    CLI and script usage ('gracehpc_run') of the GRACE-HPC package.
    This can also be used in a Jupyter Notebook, but is primarily designed for terminal output.
    
    Args:
        full_df (pd.DataFrame): Full DataFrame with all jobs (1 row per job).
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day).
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs).
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function.
        hpc_config (dict): HPC configuration dictionary containing system details and TDP values.
        
    Returns:
        None: prints the results using the rich library.
    """
    console = Console()
    console.print("\n")
    # Create title
    title_text = Text(f"Carbon Footprint Estimation for HPC Jobs ran on {hpc_config['hpc_system']}", style="bold cyan")

    # Wrap it in a panel
    panel = Panel(
        title_text,
        expand=True,
        border_style="green",
        padding=(1, 5),
        title="🌱 GRACE-HPC",
        title_align="left"
    )

    console.print(panel)

    # Introduction text
    intro = (
        "This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs. "
        "If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage data and cluster-specific TDP values.\n\n"
        "Carbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API (https://carbonintensity.org.uk) at the time of job submission. "
        "Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. "
        "For Isambard systems and Archer2, these scope 3 factors are calculated from the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.\n"
        "\nThe results below are calculated using SLURM accounting data for jobs submitted to the "
        "Isambard-AI cluster, including information such as runtime, resource allocation, resource usage, "
        "hardware-level energy counters (if available), etc. For a detailed explanation of all methodologies used, "
        "please refer to the GRACE-HPC documentation.\n"
    )
    console.print(intro, style="")

    # Note 
    note = Text()
    note.append("Note:", style="bold yellow")
    note.append(" The results presented here are estimates based on the available data and methodologies with assumptions and limitations. ")
    note.append("Hence this tool should be used for ", style="")
    note.append("informational purposes only", style="bold")
    note.append(", not as a definitive energy and carbon cluster monitoring tool.\n")
    console.print(note)

    # ------------------------------------------------------
    # OVERVIEW INFO: USER, DATES AND JOB IDS
    # ------------------------------------------------------
    # Check if the total_df is empty
    if total_df.empty:
        console.print("[bold red]No job data available to analyse.[/]")
        return

    # Extract variables from arguments and data 
    user_name = full_df.iloc[0].get("UserName", "N/A")
    start_date = arguments.StartDate if hasattr(arguments, "StartDate") else "N/A"
    end_date = arguments.EndDate if hasattr(arguments, "EndDate") else "N/A"
    hpc_name = hpc_config.get('hpc_system', 'Unknown HPC System')

    # Job ID to filter on 
    if arguments.JobIDs == 'all_jobs':
        job_ids_msg = "[bold]Jobs:[/bold] Processing all jobs in the selected date range"
    else:
        job_ids_msg = f"[bold]Jobs:[/bold] Processing only for job IDs: [cyan]{arguments.JobIDs}[/cyan]"

     # Check if energy counters were available
    if "EnergyIPMI_kwh" in total_df.columns:

        if total_df.iloc[0]["EnergyIPMI_kwh"] > 0:
            energy_counter_status = "✅ Yes — hardware energy counters were available and used in calculations!"
        else: 
            energy_counter_status = "❌ Not available — hardware energy counters were not used in calculations. Usage-based estimates were used instead."

    else:
        energy_counter_status = "⚠️ Unknown — energy counter column not found in the data"

    console.print(Rule("OVERVIEW", style="bold cyan"))

    # print the overview
    console.print(f"""
    [bold]HPC System:[/bold] {hpc_name}
    [bold]User Name:[/bold] {user_name}
    [bold]Date Range:[/bold] {start_date} to {end_date}
    {job_ids_msg}
    [bold]System PUE:[/bold] {hpc_config.get('PUE', 'Unknown')}
    [bold]System Energy Counters:[/bold] {energy_counter_status}\n
    """)

    # ------------------------------------------------------
    # ENERGY INFO: USAGE-BASED AND ENERGY COUNTER-BASED ESTIMATES
    # ------------------------------------------------------
    row = total_df.iloc[0]  # Get the first and only row of the total_df

    # Extract total energy values aggregated over all jobs (from the total_df)
    energy_total = row['energy_estimated_kwh']
    energy_no_pue = row["energy_estimated_noPUE_kwh"]
    cpu_energy = row["CPU_energy_estimated_kwh"]
    gpu_energy = row["GPU_energy_estimated_kwh"]
    mem_energy = row["memory_energy_estimated_kwh"]
    counter_energy = row["EnergyIPMI_kwh"]
    dc_overhead = energy_total - energy_no_pue
    job_count = row['JobCount']

    # Message for counter-based energy 
    if counter_energy > 0:
        counter_energy_msg = f"{counter_energy:,.4f} kWh"
        job_avg_energy = counter_energy / job_count

    else:
        counter_energy_msg =  "N/A (no energy counters available)"
        job_avg_energy = energy_total / job_count

    console.print(Rule("ENERGY CONSUMPTION", style="bold cyan"))

    # Print total energy statistics
    console.print(f"""
    [bold]Total Energy Used (estimated):[/bold] {energy_total:,.4f} kWh

         - [bold]CPUs:[/bold] {cpu_energy:,.4f} kWh
         - [bold]GPUs:[/bold] {gpu_energy:,.4f} kWh
         - [bold]Memory:[/bold] {mem_energy:,.4f} kWh
         - [bold]Data Centre Overheads (PUE):[/bold] {dc_overhead:,.4f} kWh

    [bold]Compute Energy Use (estimated):[/bold] {energy_no_pue:,.4f} kWh  
    [bold]Compute Energy Use (measured by system counters):[/bold] {counter_energy_msg}\n
    """)

    # ------------------------------------------------------
    # CARBON FOOTPRINT BOX: SCOPE 2 AND SCOPE 3 EMISSIONS
    # ------------------------------------------------------

    # Extract emissions values from the total_df
    scope2_usage = row["Scope2Emissions_gCO2e"]
    scope2_counter = row["Scope2Emissions_IPMI_gCO2e"]
    total_emissions = row["TotalEmissions_gCO2e"]
    total_avg_ci = row["CarbonIntensity_gCO2e_kwh"]
    ci_values = full_df["CarbonIntensity_gCO2e_kwh"].dropna()
    q1 = ci_values.quantile(0.25)
    median = ci_values.median()
    q3 = ci_values.quantile(0.75)



    # determine whether to display counter-based scope 2 emissions
    if counter_energy > 0:
        scope2_counter_msg = emissions_unit_converter(scope2_counter)
        total_emissions_msg = (
            f"{emissions_unit_converter(total_emissions)} "
            f"(system counter-based)"
        )
    
    else:
        scope2_counter_msg = "N/A (no energy counters available)"
        total_emissions_msg = (
            f"{emissions_unit_converter(total_emissions)} "
            f"(usage-based)"
        )

    # Handle scope 3 emissions 
    scope3_msg = None
    scope3_value = None             

    if arguments.Scope3 != 'no_scope3':
        scope3_value = row.get("Scope3Emissions_gCO2e", None)
        if scope3_value is not None:

            scope3_label = ""
            scope3_nodeh_factor = None

            # Determine the per nodehour scope 3 emissions factor to display next to value
            if arguments.Scope3 == 'Isambard3':
                scope3_nodeh_factor = 43
            elif arguments.Scope3 == 'IsambardAI':
                scope3_nodeh_factor = 114
            elif arguments.Scope3 == 'Archer2':
                scope3_nodeh_factor = 23
            else:                                   # If the user gives a custom numeric value (e.g. "50") instead of a system name
                try:
                    scope3_nodeh_factor = float(arguments.Scope3)
                except Exception:
                    pass        # don't display the per nodehour emissions factor
            

            if scope3_nodeh_factor is not None:
                scope3_label = f" ({scope3_nodeh_factor} gCO2e/node-hour)"
            
            # final scope3 text 
            scope3_msg = f"{emissions_unit_converter(scope3_value)}{scope3_label}"

    # Print carbon footprint section 
    console.print(Rule("🌿 CARBON FOOTPRINT", style="bold cyan"))

    if scope3_msg is not None:
        scope3_line = f"[bold]Scope 3 Emissions:[/bold] {scope3_msg}\n"
    else:
        scope3_line = ""

    console.print(f"""
    [bold]Scope 2 Emissions (usage-based):[/bold] {emissions_unit_converter(scope2_usage)}
    [bold]Scope 2 Emissions (system counter-based):[/bold] {scope2_counter_msg}
    {scope3_line}
    [bold]Total Emissions:[/bold] {total_emissions_msg}

    Average Carbon Intensity: {total_avg_ci:,.1f} gCO2e/kWh ({arguments.Region})
    CI distribution (gCO2e/kWh): [bold]Q1:[/bold] {q1:,.1f}, [bold]Median:[/bold] {median:,.1f} , [bold]Q3:[/bold] {q3:,.1f} 
    """)

    console.print(
    "\n\n[italic dim]Note:[/italic dim] For Isambard systems and Archer2, market-based Scope 2 emissions = 0 gCO₂e due to 100% certified zero-carbon electricity contracts.\n"
    "The estimates above are based on the UK national grid carbon intensity and are provided for informational purposes,\n"
    "representing what the emissions would be if Isambard systems were not powered by renewable energy (the grid only).\n\n"
    )

    # ------------------------------------------------------
    # CONTEXTUAL EQUIVALENTS BOX AND APPROXIMATE ELECTRICITY COST
    # ------------------------------------------------------
    # Extract values from the total_df
    driving_miles = row["driving_miles"]
    tree_months = row["tree_absorption_months"]
    bris_paris_flights = row["bris_paris_flights"]
    uk_houses = row["uk_houses_daily_emissions"]

    # Format the tree months text 
    tree_months_text = tree_months_formatter(tree_months)

    # Electricity cost using the value given in the hpc_config
    total_cost = row['Cost_GBP']
    GBP_per_kwh = hpc_config.get("electricity_cost", "N/A")

    console.print(Rule("THIS IS EQUIVALENT TO:", style="bold cyan"))


    console.print(f"""
    [bold]🚗 Driving[/bold] {driving_miles:,.2f} miles            (0.21 kgCO2e/mile average UK car, 2023)
    [bold]🌲 Tree absorption:[/bold] {tree_months_text}            (0.83 kgCO2e/month average UK tree carbon sequestration rate)
    [bold]✈️ Flying[/bold] {bris_paris_flights:,.3f} times from Bristol to Paris            (140 kgCO2e/passenger)
    [bold]🏠 UK Households:[/bold] Daily emissions from {uk_houses:,.1f} households' electricity use             (UK average)

    [bold]Approximate electricity cost:[/bold] £{total_cost:.2f}        (at {GBP_per_kwh:.4f} GBP/kWh)

    [italic]See documentation for sources and assumptions of these estimates.[/italic]\n
    """)

    # ------------------------------------------------------
    # USAGE STATISTICS BOX
    # ------------------------------------------------------
    # Extract usage statistics from the total_df
    job_count = row['JobCount']
    total_runtime = row['ElapsedRuntime']
    successful_jobs = row['successful_jobs']
    cpu_usage_time = row['CPUusagetime']
    gpu_usage_time = row['GPUusagetime']
    mem_requested = row['RequestedMemoryGB']
    node_h = row['NodeHours']
    cpu_h = row['CPUhours']
    gpu_h = row['GPUhours']
    first_job_date = row['FirstJobTime']
    last_job_date = row['LastJobTime']

 
    console.print(Rule("USAGE STATISTICS", style="bold cyan"))

    # Print usage statistics
    console.print(f"""
    [bold]Number of Jobs:[/bold] {job_count:,} ({successful_jobs:,} successful)
    [bold]First → Last Job Submitted:[/bold] {str(first_job_date.date())} → {str(last_job_date.date())}
    [bold]Total Runtime:[/bold] [cyan]{total_runtime}[/cyan]
    [bold]Total CPU Usage Time:[/bold] [cyan]{cpu_usage_time}[/cyan]  ({cpu_usage_time.total_seconds() / 3600:,.0f} hours)
    [bold]Total GPU Usage Time:[/bold] [cyan]{gpu_usage_time}[/cyan]  ({gpu_usage_time.total_seconds() / 3600:,.0f} hours)
    [bold]Memory Requested:[/bold] {mem_requested:,} GB
    [bold]Node Hours:[/bold] {node_h:,.1f}
    [bold]CPU Hours:[/bold] {cpu_h:,.1f}
    [bold]GPU Hours:[/bold] {gpu_h:,.1f}\n
    """)

    # ------------------------------------------------------
    # FAILED JOBS AND MEMORY OVERALLOCATION 
    # ------------------------------------------------------
    # Extract relevant columns
    failed_jobs = job_count - successful_jobs
    failed_percent = (failed_jobs / job_count) * 100 if job_count > 0 else 0
    failed_scope2 = row['Scope2Emissions_failed_gCO2e']
    scope2_required_memory = row['Scope2Emissions_requiredMem_gCO2e']
    wasted_mem_emissions = scope2_usage - scope2_required_memory

    # Section header
    console.print(Rule("FAILED JOBS & WASTED MEMORY IMPACT", style="bold cyan"))

    # Print failed job stats
    console.print(f"""
    [bold]Failed Jobs:[/bold] {failed_jobs} ({failed_percent:.1f}%)
    [bold]Wasted Scope 2 Emissions:[/bold] {emissions_unit_converter(failed_scope2)} [dim](Usage-based estimate)[/dim]
    """)

    console.print(
    "\n[italic dim]Note:[/italic dim] Failed HPC jobs are a significant source of wasted computational resources and unnecessary carbon emissions.\n"
    "Every failed job still consumes electricity for scheduling, startup, and partial execution—without producing useful results.\n"
    "Reducing failed jobs is a simple yet impactful way to lower your carbon footprint on HPC systems.\n"
    )

    console.print(
    "\n[bold]Memory overallocation[/bold] is a common source of energy waste and excess carbon emissions.\n"
    "On most HPC systems, power draw depends on the amount of memory [bold]requested[/bold], not the memory actually used.\n"
    "If all jobs had been submitted with only the memory they truly required, approximately:\n\n"
    
    f"{emissions_unit_converter(wasted_mem_emissions)} could have been saved [dim](Usage-based estimate)[/dim]\n\n"
    )

    # ------------------------------------------------------
    # DOCUMENTATION AND FEEDBACK TEXT
    # ------------------------------------------------------

    console.print(Rule("DOCUMENTATION & FEEDBACK", style="bold cyan"))
    console.print(
    "\nFind the methodology including assumptions and limitations of this tool outlined in the documentation:\n"
    "https://github.com/Elliot-Ayliffe/GRACE-HPC/tree/main\n\n"
    "See also what other features are available with the package/API including an interactive [bold]Jupyter Notebook interface[/bold].\n\n"
    "If you find any bugs, have questions, or suggestions for improvements, please post these on the GitHub repository.\n"
)





# Main frontend function to be called in the cli.py and script.py 
def main_cli_script_output(full_df, daily_df, total_df, arguments):
    """
    Main function to display the results in the terminal for CLI and script usage.
    
    Args:
        full_df (pd.DataFrame): Full DataFrame with all jobs (1 row per job).
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day).
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs).
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function.
        
    Returns:
        None: Displays the results in the terminal or Jupyter Notebook.
    """
    # Load the hpc_config.yaml file (user must edit this file to match their HPC system)
    with open('hpc_config.yaml', 'r') as file:
        try: 
            hpc_config = yaml.safe_load(file)  # Load the YAML file into a dictionary
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading hpc_config.yaml: {e}")
        
    # Call the function to display the results
    results_terminal_display(full_df, daily_df, total_df, arguments, hpc_config)


