"""
jupyter_output.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 15/07/25

This module contains functions to display plots and statistics as rich HTML 
and interactive plots within a Jupyter Notebook environment for the GRACE-HPC package.

It provides the main frontend output function for the jupyter.py script

Key Functions:

- 'JN_stats_plots (full_df, daily_df, total_df, arguments, hpc_config)':
    Generates and displays interesting visualisations of energy use and carbon emissions using HTML and plotly for accessing the 3 dataframes (full_df, daily_df, total_df)

- 'main_jupyter_output (full_df, daily_df, total_df, arguments)':
    Main frontend function called by the jupyter.py script. Loads the configuration file and calls the 'JN_stats_plots' function to produce the full jupyter output.
"""


# Import libraries 
from IPython.display import display, HTML, Markdown
import ipywidgets as widgets
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pandas as pd 
import numpy as np
import yaml


# ---------------------------------------------------------------------------------------------------------------------------------
# FORMATTING TEXT CONVERTER FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------------------

def emissions_unit_converter(gco2e):
    """
    Format the emissions (gCO2e) value into a human-readable string with appropriate units,
    using g, kg or T (tonnes) depending on the size of the value.
    
    Args:
        gco2e (float): Emissions value in grams of CO2 equivalent (gCO2e).
        
    Returns:
        str: Formatted emissions as text value with appropriate units (e.g. "530 gCO2e")
    """
    co2e_text = "CO2e"
    
    # If emissions is less than 1000 grams, display in grams
    if gco2e < 1e3:
        emissions_text = f"{gco2e:,.4f} g{co2e_text}"             

    # If emissions is between 1000 grams and 1 million grams, display in kilograms
    elif gco2e < 1e6:
        emissions_text = f"{gco2e / 1e3:,.4f} kg{co2e_text}"      # Must convert to kg

    # If emissions is greater than 1 million grams, display in tonnes
    else:
        emissions_text = f"{gco2e / 1e6:,.4f} T{co2e_text}"        # Must convert to tonnes
    
    return emissions_text



def tree_months_formatter(tree_months_value, splitting_years=True):
    """
    Format a given number of 'tree-months' into a more human-readable string.

    A tree-month is a proxy metric representing how many months a tree would need to absorb
    a given amount of carbon. This function provides readable formatting depending on the
    size of the value, converting to tree-years when appropriate

    Args:
        tree_months_value (float): The number of tree-months to format.
        splitting_years (bool): If True, splits larger values into years and months.
    
    Returns:
        str: Formatted string representing the tree-months value.
    """
    tm_int = int(tree_months_value)  # Convert to integer for formatting
    tree_years = int(tm_int / 12)  # Calculate full tree-years

    # For small values,
    if tm_int < 1:
        formatted_tm_text = f"{tree_months_value:.3f} tree-months"

    # values less than 12 months
    elif tm_int < 12:
        formatted_tm_text = f"{tree_months_value:.1f} tree-months"

    # for values up to 2 years 
    elif tm_int < 24:
        formatted_tm_text = f"{tm_int} tree-months"

    # For values up to 10 years 
    elif tm_int < 120:
        if splitting_years:
            remaining_months = tm_int - tree_years * 12
            formatted_tm_text = f"{tree_years} tree-years and {remaining_months} tree-months"
        else:
            formatted_tm_text = f"{tree-years} tree-years"
    
    else:
        formatted_tm_text = f"{tree_months_value / 12:.1f} tree-years"

    return formatted_tm_text




# ---------------------------------------------------------------------------------------------------------------------------------
# PLOTTING FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------------------

def energy_contribution_pie(total_df):
    """
    Function that plots a pie chart showing the proportion of energy used by CPUs, GPUs, memory, and data centre overheads over all jobs (total_df).
    
    Args:
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs)

    Returns: 
        fig (plotly.graph_objs.Figure): Plotly pie chart figure object showing energy contributions.
    """
    # Extract energy components
    cpu_energy = total_df["CPU_energy_estimated_kwh"].values[0]
    gpu_energy = total_df["GPU_energy_estimated_kwh"].values[0]
    mem_energy = total_df["memory_energy_estimated_kwh"].values[0]
    total_energy = total_df["energy_estimated_kwh"].values[0]
    no_pue_energy = total_df["energy_estimated_noPUE_kwh"].values[0]

    # Calculate DC overhead
    dc_overhead = total_energy - no_pue_energy

    # Labels and values for the pie chart
    segment_labels = ['CPU', 'GPU', 'Memory', 'Data Centre Overhead']
    values = [cpu_energy, gpu_energy, mem_energy, dc_overhead]

    colours = px.colors.qualitative.Set1

    # Define Plotly pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=segment_labels,
            values=values,
            hole=0.3,
            marker=dict(
                colors=colours[:len(values)],
                line=dict(color='#ffffff', width=2)),
            hovertemplate='%{label}: %{value} kWh<extra></extra>',
            textinfo='percent',
            textfont=dict(size=14),
            insidetextorientation='radial'
        )
    ])

    # format the pie chart
    fig.update_layout(
        title_text='Energy Contribution Breakdown',
        title_font_size=18,
        showlegend=True,
        height=480,
        width=480,
        margin=dict(l=0, r=0, t=20, b=0)
    )

    return fig




def scope2_scope3_pie(total_df, arguments):
    """
    Function that plots a pie chart showing the proportion of scope 2 vs scope 3 emissions for all jobs (total_df).
    Scope 2 emissions are selected based on whether energy counters are available.
    
    Args:
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs)
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function - must contain 'Scope3' attribute

    Returns:
        fig (plotly.graph_objs.Figure): Plotly pie chart figure object showing scope 2 and scope 3 emissions.
    """
    row = total_df.iloc[0]  # Get the first row of the total_df DataFrame

    # If no scope 3 specified, return None (no pie chart)
    if arguments.Scope3 == "no_scope3":
        return None  

    # Determine the scope 2 emissions to use
    if row["EnergyIPMI_kwh"] > 0:               # If energy counters are available
        scope2 = row["Scope2Emissions_IPMI_gCO2e"]
    else:                                       # If no energy counters, use estimated energy
        scope2 = row["Scope2Emissions_gCO2e"]
    
    # Get scope 3 emissions
    scope_3 = row["Scope3Emissions_gCO2e"]

    # The values and labels for the pie chart
    vals = [scope2, scope_3]
    labels = ['Scope 2 (operational)', 'Scope 3 (embodied)']
    colours = ['#4E79A7', '#F28E2B']

    # Create pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=vals,
            marker=dict(colors=colours, line=dict(color='#ffffff', width=2)),
            hovertemplate='%{label}: %{value} gCO2e<extra></extra>',
            textinfo='percent',
            insidetextorientation='radial',
            hole=0.3  
        )
    ])

    # Format the pie chart
    fig.update_layout(
        title_text="Emissions Breakdown: Scope 2 vs Scope 3",
        title_font_size=16,
        showlegend=True,
        height=480,
        width=480,
        margin=dict(l=30, r=30, t=50, b=30),
    )

    return fig



def scatter_full_jobs(full_df):
    """
    Plots a scatter plot of total emissions (gCO2e) vs submission time.
    One point per job using the full_df DataFrame. Green dots represent successful jobs,
    red crosses represent failed jobs.
    
    Args:
        full_df (pd.DataFrame): Full DataFrame containing all jobs processed (1 row per job).
        
    Returns:
        fig (plotly.graph_objs.Figure): Plotly scatter plot figure object showing emissions vs submission time.
    """
    # copy to avoid modifying the original DataFrame
    df = full_df.copy()

    # Convert SubmissionTime to datetime for the x-axis 
    df['SubmissionTime'] = pd.to_datetime(df['SubmissionTime'])

    # Determine the energy column to use based on energy counters availability
    counters_available = (df['EnergyIPMI_kwh'] > 0).all()
    energy_to_use = 'EnergyIPMI_kwh' if counters_available else 'energy_estimated_kwh'
    energy_label = 'Measured Energy (kWh)' if counters_available else 'Estimated Energy (kWh)'

    # Hover template for points
    hover_template = (
        "<b>Job ID:</b> %{customdata[0]}<br>"
        "<b>Submission Time:</b> %{x}<br>"
        "<b>Total Emissions:</b> %{y:.3f} gCO2e<br>"
        f"<b>{energy_label}:</b> %{{customdata[1]:.4f}} kWh<br>"
        "<b>Carbon Intensity:</b> %{customdata[2]:.1f}<extra></extra>"
    )

    # separate the successful and failed jobs
    successful_jobs = df[df['StateCode'] == 1]
    failed_jobs = df[df['StateCode'] == 0]

    # Scatter plot for successful jobs
    successful_trace = go.Scatter(
        x=successful_jobs['SubmissionTime'],
        y=successful_jobs['TotalEmissions_gCO2e'],
        mode='markers',
        name='Successful Jobs',
        marker=dict(color='green', size=8, symbol='circle'),
        customdata=successful_jobs[['Job_ID', energy_to_use, 'CarbonIntensity_gCO2e_kwh']],
        hovertemplate=hover_template
    )

    # Scatter plot for failed jobs
    failed_trace = go.Scatter(
        x=failed_jobs['SubmissionTime'],
        y=failed_jobs['TotalEmissions_gCO2e'],
        mode='markers',
        name='Failed Jobs',
        marker=dict(color='red', size=8, symbol='x'),
        customdata=failed_jobs[['Job_ID', energy_to_use, 'CarbonIntensity_gCO2e_kwh']],
        hovertemplate=hover_template
    )

    # Format the plot 

    formatted_plot = go.Layout(
        title='Job Emissions over Time',
        xaxis=dict(title="Submission DateTime"),
        yaxis=dict(title="Total Emissions (gCO2e)"),
        legend=dict(title="Job Status"),
        height=400,
        margin=dict(l=60, r=30, t=40, b=50)
    )

    fig = go.Figure(data=[successful_trace, failed_trace], layout=formatted_plot)

    return fig




def bar_daily_emissions(daily_df):
    """
    Plots a bar chart the total emissions (gCO2e) aggregated by day using daily_df

    Args:
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day).

    Returns:
        fig (plotly.graph_objs.Figure): Plotly bar chart figure object showing daily emissions
    """
    # Copy the daily_df to avoid modifying the original DataFrame
    df = daily_df.copy()

    # Convert SubmissionDate to datetime for the x-axis
    df['SubmissionDate'] = pd.to_datetime(df['SubmissionDate'])

    # Determine the energy column to use based on energy counters availability
    counters_available = (df['EnergyIPMI_kwh'] > 0).all()
    energy_to_use = 'EnergyIPMI_kwh' if counters_available else 'energy_estimated_kwh'
    energy_label = 'Measured Energy (kWh)' if counters_available else 'Estimated Energy (kWh)'

    # Hover text for bars 
    custom_data = df[['SubmissionDate', energy_to_use, 'CarbonIntensity_gCO2e_kwh']]
    hover_template = (
        "<b>Date:</b>  %{x}<br>"
       "<b>Total Emissions:</b> %{y:.2f} gCO2e<br>"
        f"<b>{energy_label}:</b> %{{customdata[1]:.3f}} kWh<br>"
        "<b>Avg Carbon Intensity:</b> %{customdata[2]:.1f} gCO2e/kWh<extra></extra>"
    )

    # Plot the bar chart
    main_trace = go.Bar(
        x=df['SubmissionDate'],
        y=df['TotalEmissions_gCO2e'],
        name='Daily Aggregated Emissions',
        marker=dict(color='teal'),
        customdata=custom_data,
        hovertemplate=hover_template
    )

    # Format the plot
    formatted_plot = go.Layout(
        title='Daily Total Emissions',
        xaxis=dict(title='Submission Date', type='date'),
        yaxis=dict(title="Total Emissions (gCO2e)"),
        height=400,
        margin=dict(l=60, r=30, t=40, b=50)
    )

    fig = go.Figure(data=[main_trace], layout=formatted_plot)

    return fig



def bar_daily_usage(daily_df):
    """
    Plots a bar chart showing the Job submissions per day using daily_df.
    Hover includes runtime, CPU and GPU usage time and success rate.
    
    Args:
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day).
        
    Returns:
        fig (plotly.graph_objs.Figure): Plotly bar chart figure object showing daily job submissions.
    """
    # Copy the daily_df to avoid modifying the original DataFrame
    df = daily_df.copy()

    # Convert SubmissionDate to datetime for the x-axis
    df['SubmissionDate'] = pd.to_datetime(df['SubmissionDate'])

    # Convert success fraction to percentage
    df['SuccessPercent'] = df['SuccessFraction'] * 100

    # Convert ElapsedRuntime, CPUusagetime, and GPUusagetime to strings for hover text
    def format_timedelta(timedelta):
        total_seconds = int(timedelta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"
   
    df['runtime_str'] = df['ElapsedRuntime'].apply(format_timedelta)
    df['CPU_time_str'] = df['CPUusagetime'].apply(format_timedelta)
    df['GPU_time_str'] = df['GPUusagetime'].apply(format_timedelta)



    # Hover text for bars
    custom_data = df[['runtime_str', 'CPU_time_str', 'GPU_time_str', 'SuccessPercent']]
    hover_template = (
        "<b>Date:</b> %{x}<br>"
        "<b>Job Count:</b> %{y}<br>"
        "<b>Runtime:</b> %{customdata[0]}<br>"
        "<b>CPU Time:</b> %{customdata[1]}<br>"
        "<b>GPU Time:</b> %{customdata[2]}<br>"
        "<b>Success %:</b> %{customdata[3]:.1f}%<extra></extra>"
    )

    # Plot the bar chart
    main_trace = go.Bar(
        x=df['SubmissionDate'],
        y=df['JobCount'],
        name='Daily Job Count',
        marker=dict(color='steelblue'),
        customdata=custom_data,
        hovertemplate=hover_template
    )

    # Format the plot
    formatted_plot = go.Layout(
        title='Job Count per Day',
        xaxis=dict(title='Submission Date', type='date'),
        yaxis=dict(title='Number of Jobs'),
        height=400,
        margin=dict(l=60, r=30, t=40, b=50)
    )

    fig = go.Figure(data=[main_trace], layout=formatted_plot)

    return fig  



def success_failure_pie(total_df):
    """
    Pie chart showing the proportion of successful vs failed jobs over all jobs (total_df).
    
    Args:
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs).
        
    Returns:
        fig (plotly.graph_objs.Figure): Plotly pie chart figure object showing success vs failure.
    """
    # Get the first row from the total_df DataFrame
    row = total_df.iloc[0]

    # Get fractions and total job count
    total_jobs = row['JobCount']
    success_fraction = row['SuccessFraction']
    failure_fraction = row['FailedFraction']
    successful_jobs = row['successful_jobs']
    failed_jobs = total_jobs - successful_jobs

    # define the values and labels for the pie chart
    values = [successful_jobs, failed_jobs]
    labels = ['Successful Jobs', 'Failed Jobs']
    colours = ['#a8e6a2', '#f8bdbd']

    # Create the pie chart 
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colours, line=dict(color='#ffffff', width=2)),
            hovertemplate='%{label}: %{value} <extra></extra>',
            textinfo='percent',
            insidetextorientation='radial',
            hole=0.3  
        )
    ])

    # Format the pie chart
    fig.update_layout(
        title_text="Job Success vs Failure",
        title_font_size=16,
        showlegend=True,
        height=400,
        width=400,
        margin=dict(l=30, r=30, t=50, b=30),
    )
    return fig


def ci_boxplot(full_df, arguments):
    """
    Boxplot showing the distribution of carbon intensity (gCO2e/kwh) over the entire data range (all jobs)
    Reference line for the UK average in 2024.
    
    Args:
        full_df (pd.DataFrame): Full DataFrame containing all jobs processed (1 row per job).
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function - must contain 'Region' attribute
        
        
    Returns:
        fig (plotly.graph_objs.Figure): Plotly boxplot figure object showing carbon intensity distribution.
    """
    # Extract CI values
    ci_vals = full_df['CarbonIntensity_gCO2e_kwh']

    # plot the boxplot
    fig = go.Figure()

    fig.add_trace(go.Box(
        y=ci_vals,
        name=arguments.Region,
        boxpoints='outliers',  
        pointpos=-1.8,  
        marker=dict(color="#4E79A7"),
        line=dict(width=1.5),
        fillcolor='rgba(93, 173, 226, 0.5)',  
        showlegend=False
    ))

    # Add a line for the UK average CI (2024) for reference
    fig.add_hline(
        y=124,
        line=dict(color='red', width=2, dash='dash'),
        name='UK Average. (124 gCO₂e/kWh)',
        showlegend=True
    )

    # Format the plot 
    fig.update_layout(
        title=f"Carbon Intensity Distribution ({arguments.Region})",
        xaxis=dict(title="Region", type='category'),
        yaxis=dict(title="Carbon Intensity (gCO2e/kWh)"),
        height=400,
        width=600,
        margin=dict(l=50, r=30, t=50, b=50)
    )

    return fig








# ---------------------------------------------------------------------------------------------------------------------------------
# FUNCTION TO DISPLAY ALL PLOTS AND STATS IN HTML FORMAT
# --------------------------------------------------------------------------------------------------------------------------------

def JN_stats_plots(full_df, daily_df, total_df, arguments, hpc_config):
    """
    Function to generate the results (energy and emissions stats and plots)
    for the jupyter notebook interactive interface.
    
    Args: 
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
        full_df (pd.DataFrame): Full DataFrame with all jobs (1 row per job)
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day)
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs)
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function
        hpc_config (dict): HPC configuration dictionary containing system details and TDP values.
        
    Returns:
        None: Displays the results in the Jupyter Notebook.
    """

    intro_text = f"""
# **Carbon Footprint Estimation for HPC Jobs ran on {hpc_config['hpc_system']}**

The accelerated demand for high-performance computing resources is raising concerns about the growing carbon footprint of these systems. 
Without intervention , data centres and hpc facilities are projected to contribute up to **8% of global greenhouse gas emissions** by 2030. In the face of the current climate crisis, 
it is essential that **HPC users and operators** develop strategies to **quantify, report and reduce** the carbon emissions associated with their computational workloads.


The results below are calculated using **SLURM accounting data** for jobs submitted to the {hpc_config['hpc_system']} cluster, including information such as runtime,
resource allocation, resource usage, hardware-level energy counters (if available), etc. For a detailed explanation of all methodologies used, 
please refer to the **GRACE-HPC documentation** found at the GitHub repository linked at the bottom of this page.


---

This tool aims to provide both a **transparent overview** and **actionable insights** into the energy and carbon cost of your research. It is designed to:
- 🌿 Promote individual awareness of your own computational carbon footprint  
- 📊 Inform greener decision-making toward more sustainable HPC practices


**Note**: The results presented here are estimates based on the available data and methodologies with assumptions and limitations.
Hence this tool should be used for **informational purposes only**, not as a definitive energy and carbon cluster monitoring tool.

---

""" + "\n\n"
    display(Markdown(intro_text))

    # ------------------------------------------------------
    # OVERVIEW BOX: USER, DATES AND JOB IDS
    # ------------------------------------------------------
    
    # Check if the total_df is empty 
    if total_df.empty:
        display(HTML("<p style='color:red;'>No job data available to analyse.</p>"))
        return

    # Extract variables from arguments and data 
    user_name = full_df.iloc[0].get("UserName", "N/A")
    start_date = arguments.StartDate if hasattr(arguments, "StartDate") else "N/A"
    end_date = arguments.EndDate if hasattr(arguments, "EndDate") else "N/A"
    hpc_name = hpc_config.get('hpc_system', 'Unknown HPC System')

    # Job ID to filter on 
    if arguments.JobIDs == 'all_jobs':
        job_ids_msg = "<li><strong>Jobs:</strong> Processing all jobs in the selected date range</li>"
    else:
        job_ids_msg = f"<li><strong>Jobs:</strong> Processing only for job IDs: <code>{arguments.JobIDs}</code></li>"

    # Check if energy counters were available
    if "EnergyIPMI_kwh" in total_df.columns:

        if (full_df['EnergyIPMI_kwh'] > 0).all():
            energy_counter_status = "✅ Yes — hardware energy counters were available for all jobs and used in calculations!"
        else: 
            energy_counter_status = "❌ Not available for all jobs — hardware energy counters were not used in calculations. Usage-based estimates were used instead."

    else:
        energy_counter_status = "⚠️ Unknown — energy counter column not found in the data"

    # Create the html box 
    overview_box = f"""
    <div style="border: 1px solid #cccccc; border-radius: 0px; padding: 17px; background-color: #fafafa; font-family: sans-serif; width: fit-content;">
        <h3 style="margin-top: 0;">🌍 OVERVIEW</h3>
        <ul style="list-style-type: none; padding-left: 0; font-size: 13.5px;line-height: 25px;">
            <li><strong>HPC System:</strong> {hpc_name}</li>
            <li><strong>User Name:</strong> {user_name}</li>
            <li><strong>Date Range:</strong> {start_date} to {end_date}\n</li>
            {job_ids_msg}
            <li><strong>System PUE:</strong> {hpc_config.get('PUE', 'Unknown')}</li>
            <li><strong>System Energy Counters:</strong> {energy_counter_status}</li>
        </ul>
    </div>
    """
    display(HTML(overview_box))
    display(HTML("<hr>"))


    # ------------------------------------------------------
    # ENERGY BOX: USAGE-BASED AND ENERGY COUNTER-BASED ESTIMATES
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
    if (full_df['EnergyIPMI_kwh'] > 0).all():
        counter_energy_msg = f"{counter_energy:,.4f} kWh"
        job_avg_energy = counter_energy / job_count
        # job_avg_msg = "Per-job Average Energy Use (measured):"

    else:
        counter_energy_msg =  "N/A (not all jobs had energy counters available)"
        job_avg_energy = energy_total / job_count
        # job_avg_msg = "Per-job Average Energy Use (estimated):"


    # Create the html box 
    energy_box = f"""
    <div style="background-color: #eaf4fb; border: 1px solid #b3d8f1; border-radius: 0px; padding: 17px; margin-bottom: 13px; width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #0a4f75;">⚡ ENERGY CONSUMPTION</h3>
        <ul style="margin: 0 0 0 20px; padding: 0; line-height: 25px; font-size: 13.5px;">
            <li><b>Total Energy Used (estimated):</b> {energy_total:,.4f} kWh
            <ul style="margin: 5px 0 5px 20px;">
                <li><b>CPUs:</b> {cpu_energy:,.4f} kWh</li>
                <li><b>GPUs:</b> {gpu_energy:,.4f} kWh</li>
                <li><b>Memory:</b> {mem_energy:,.4f} kWh</li>
                <li><b>Data Centre Overheads (PUE):</b> {dc_overhead:,.4f} kWh</li>
            </ul>
            </li>
            <li><b>Compute Energy Use (estimated):</b> {energy_no_pue:,.4f} kWh</li>
            <li><b>Compute Energy Use (measured by system counters):</b> {counter_energy_msg}</li>
        </ul>
    </div>
    """

    # Create pie chart showing the energy contributions 
    fig = energy_contribution_pie(total_df)
    # pie_chart_widget = go.FigureWidget(fig)        # Need to convert to FigureWidget to display beside the HTML box


    # Add space between the two widgets
    space = widgets.Box(layout=widgets.Layout(width='50px'))

    # Display side-by-side
    display(HTML(energy_box))
    fig.show()

    # ------------------------------------------------------
    # CARBON FOOTPRINT BOX: SCOPE 2 AND SCOPE 3 EMISSIONS
    # ------------------------------------------------------

    # Extract emissions values from the total_df
    scope2_usage = row["Scope2Emissions_gCO2e"]
    scope2_counter = row["Scope2Emissions_IPMI_gCO2e"]
    total_emissions = row["TotalEmissions_gCO2e"]
    total_avg_ci = row["CarbonIntensity_gCO2e_kwh"]

    # determine whether to display counter-based scope 2 emissions
    if (full_df['EnergyIPMI_kwh'] > 0).all():
        scope2_counter_msg = emissions_unit_converter(scope2_counter)
        total_emissions_msg = (
            f"{emissions_unit_converter(total_emissions)} "
            f"(system counter-based)"
        )
    
    else:
        scope2_counter_msg = "N/A (not all jobs had energy counters available)"
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
    
    # Create the carbon footprint html box
    emissions_box = f"""
    <div style="background-color: #e6f4ea; border: 1px solid #b8dcb8; border-radius: 0px; padding: 17px; margin-bottom: 13px; width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #317a32;">🌿 CARBON FOOTPRINT</h3>
        <ul style="margin: 0 0 0 20px; padding: 0; line-height: 25px; font-size: 13.5px;">
            <li><b>Scope 2 Emissions (usage-based):</b> {emissions_unit_converter(scope2_usage)}</li>
            <li><b>Scope 2 Emissions (system counter-based):</b> {scope2_counter_msg}</li>"""

    if scope3_msg is not None:
        emissions_box += f"""
            <li><b>Scope 3 Emissions:</b> {scope3_msg}</li>"""

    emissions_box += f"""
            <li><b>Total Emissions:</b> {total_emissions_msg}</li>
        </ul>

        <p style="margin-top: 10px; font-weight: 400; font-size: 14px;">
            Average Carbon Intensity: {total_avg_ci:,.1f} gCO2e/kWh ({arguments.Region})
        </p>
    </div>
    """


    # Create pie chart showing the scope 2 vs scope 3 
    scopes_fig = scope2_scope3_pie(total_df, arguments)

    if scopes_fig is not None:
        
        display(HTML(emissions_box))  
        scopes_fig.show()

      
    else:
        # If no scope 3 emissions, just display the emissions box without a pie chart
        display(HTML(emissions_box))

    note_html = """
<p style="font-size: 13px; font-style: italic; color: #444; max-width: 700px; margin-top: 10px;">
    \n<b>Note:</b> For Isambard systems, market-based Scope 2 emissions = 0 gCO₂e due to 100% certified zero-carbon electricity contracts. 
    The estimates above are based on the UK national grid carbon intensity and are provided for informational purposes — 
    representing what the emissions would be if Isambard were not powered by renewable energy (the grid only).
</p>
"""
    display(HTML(note_html))


    # ------------------------------------------------------
    # CONTEXTUAL EQUIVALENTS BOX
    # ------------------------------------------------------

    # Extract values from the total_df
    driving_miles = row["driving_miles"]
    tree_months = row["tree_absorption_months"]
    bris_paris_flights = row["bris_paris_flights"]
    uk_houses = row["uk_houses_daily_emissions"]

    # Format the tree months text 
    tree_months_text = tree_months_formatter(tree_months)

    equivalents_box = f"""
    <div style="background-color: #fff9e6; border: 1px solid #f3d481; border-radius: 0px; 
                padding: 17px; margin-bottom: 13px; width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #a87c00;">📊 THIS IS EQUIVALENT TO:</h3>
        <ul style="margin: 0 0 0 20px; padding: 0; line-height: 25px; font-size: 13.5px; color: #000;">
            <li><span style="font-weight: bold;">🚗 Driving</span> {driving_miles:,.2f} miles 
                <span style="color: #555;">(0.21 kgCO2e/mile average UK car, 2023)</span></li>
            <li><span style="font-weight: bold;">🌲 Tree absorption:</span> {tree_months_text}
                <span style="color: #555;">(0.83 kgCO2e/month average UK tree carbon sequestration rate)</span></li>
            <li><span style="font-weight: bold;">✈️ Flying </span> {bris_paris_flights:,.3f} times from Bristol to Paris
                <span style="color: #555;"> (140 kgCO2e/passenger)</span></li>
            <li><span style="font-weight: bold;">🏠 UK Households:</span> Daily emissions from {uk_houses:,.1f} households' electricity use 
                <span style="color: #555;">(UK average)</span></li>
        </ul>
    </div>
    """

    display(HTML(equivalents_box))

    # Electricity cost using the value given in the hpc_config
    total_cost = row['Cost_GBP']
    GBP_per_kwh = hpc_config.get("electricity_cost", "N/A")

   
    cost_box = f"""
    <div style="background-color: #fdecec; border: 1px solid #e9a1a1; 
                border-radius: 0px; padding: 17px; margin-bottom: 13px; 
                width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #b30000;">💰 APPROXIMATE ELECTRICITY COST</h3>
        <p style="margin: 0; font-size: 13.5px;">
            <b>Cost:</b> £{total_cost:.2f} 
            <span style="color: #444;">(at {GBP_per_kwh:.4f} GBP/kWh)</span>
        </p>
    </div>
    """
    display(HTML(cost_box))

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


    # Usage html box
    usage_stats_box = f"""
    <div style="border: 1px solid #cccccc; border-radius: 0px; padding: 17px; 
                background-color: #fafafa; font-family: sans-serif; width: fit-content;">
        <h3 style="margin-top: 0;">⚙️ USAGE STATISTICS</h3>
        <ul style="list-style-type: none; padding-left: 0; font-size: 13.5px; line-height: 25px;">
            <li><strong>Number of Jobs:</strong> {job_count:,} <span style="color: #555;">({successful_jobs:,} successful)</span></li>
            <li><strong>First → Last Job Submitted:</strong> {str(first_job_date.date())} → {str(last_job_date.date())}</li>
            <li><strong>Total Runtime:</strong> {total_runtime}</li>
            <li><strong>Total CPU Usage Time:</strong> {cpu_usage_time} <span style="color: #555;">({cpu_usage_time.total_seconds() / 3600:,.0f} hours)</span></li>
            <li><strong>Total GPU Usage Time:</strong> {gpu_usage_time} <span style="color: #555;">({gpu_usage_time.total_seconds() / 3600:,.0f} hours)</span></li>
            <li><strong>Memory Requested:</strong> {mem_requested:,} GB</li>
            <li><strong>Node Hours:</strong> {node_h:,.1f}</li>
            <li><strong>CPU Hours:</strong> {cpu_h:,.1f}</li>
            <li><strong>GPU Hours:</strong> {gpu_h:,.1f}</li>
        </ul>
    </div>
    """

    display(HTML(usage_stats_box))
    display(HTML("<hr>"))


    # ------------------------------------------------------
    # JOB EMISSIONS PLOT
    # ------------------------------------------------------
    # only show the scatter plot if more than 1 job was found in the data 
    if len(full_df) > 1:
        job_scatter_fig = scatter_full_jobs(full_df)
        job_scatter_fig.show()

    # ------------------------------------------------------
    # DAILY EMISSIONS AND JOB COUNT PLOT
    # ------------------------------------------------------
    # only show the daily plots if more than 1 day was found in the data
    if len(daily_df) > 1:
        daily_emissions_fig = bar_daily_emissions(daily_df)
        daily_emissions_fig.show()
        daily_job_count_fig = bar_daily_usage(daily_df)
        daily_job_count_fig.show()
    
    # ------------------------------------------------------
    # FAILED JOBS STAT BOX
    # ------------------------------------------------------
    # Extract relevant columns
    failed_jobs = job_count - successful_jobs
    failed_scope2 = row['Scope2Emissions_failed_gCO2e']

    failed_jobs_box = f"""
    <div style="background-color: #fdecec; border: 1px solid #e9a1a1; 
                border-radius: 0px; padding: 17px; margin-bottom: 13px; 
                width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #b30000;">❌ FAILED JOBS SUMMARY</h3>
        <p style="margin: 0; font-size: 13.5px;">
            <b>Total Jobs:</b> {job_count}<br>
            <b>Failed Jobs:</b> {failed_jobs}<br>
            <b>Wasted Scope 2 Emissions:</b> {emissions_unit_converter(failed_scope2)} <span style="color: #555;">(Usage-based estimate)</span>
        </p>
    </div>
    """

    failed_note_html = """
    <p style="font-size: 13px; font-style: italic; color: #444; max-width: 700px; margin-top: 10px;">
        <b>Note:</b> Failed HPC jobs are a significant source of wasted computational resources and unnecessary carbon emissions. 
        Every failed job still consumes electricity for scheduling, startup, and partial execution—without producing useful results. 
        Reducing failed jobs is a simple yet impactful way to lower your carbon footprint on HPC systems. 
        Careful job configuration, testing on small scales, and validating inputs before submission can help make every computation count.
    </p>
    """

     # Failed job pie chart
    failed_jobs_pie = success_failure_pie(total_df)

    display(HTML(failed_jobs_box))  
    failed_jobs_pie.show()

 
    display(HTML(failed_note_html))

    # ------------------------------------------------------
    # MEMORY WASTE STAT BOX
    # ------------------------------------------------------

    scope2_required_memory = row['Scope2Emissions_requiredMem_gCO2e']
    wasted_mem_emissions = scope2_usage - scope2_required_memory

    wasted_memory_box = f"""
    <div style="background-color: #edf7ed; border: 1px solid #a6d8a8; 
                border-radius: 0px; padding: 17px; margin-bottom: 13px; 
                width: fit-content; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #1b5e20;">🧠 WASTED MEMORY IMPACT</h3>
        <p style="margin: 0; font-size: 13.5px;">
            Memory overallocation is a common source of energy waste and excess carbon emissions. 
            On most HPC systems, power draw depends on the amount of memory <b>requested</b>, not the memory actually used. 
            If all jobs had been submitted with only the memory they truly required, approximately:<br><br>
            <b>{emissions_unit_converter(wasted_mem_emissions)}</b> could have been saved 
            <span style="color: #444;">(Usage-based estimate)</span>
        </p>
    </div>
    """

    display(HTML(wasted_memory_box))

    # ------------------------------------------------------
    # CARBON INTENSITY DISTRIBUTION PLOTS
    # ------------------------------------------------------
    # Only show the boxplot if the region is not UK_average
    if arguments.Region != 'UK_average':
        ci_box_fig = ci_boxplot(full_df, arguments)
        ci_box_fig.show()

    # ------------------------------------------------------
    # DOCUMENTATION AND FEEDBACK TEXT
    # ------------------------------------------------------
    end_text = """
    <div style="font-family: sans-serif; font-size: 13.5px; max-width: 700px; margin-top: 20px;">
        <h2 style="margin-bottom: 8px;">Documentation and Feedback</h2>
        <p style="margin: 0; color: #444;">
            Find the methodology including assumptions and limitations of this tool outlined in the 
            <a href="https://github.com/Elliot-Ayliffe/GRACE-HPC/tree/main" target="_blank" style="color: #1a73e8; text-decoration: none;">
                documentation
            </a>. See also what other features are available with the package/API including use on the Command-line and in Python scripts/ notebooks.

            If you find any bugs, have questions, or suggestions for improvements, please post these on the 
            <a href="https://github.com/Elliot-Ayliffe/GRACE-HPC/tree/main" target="_blank" style="color: #1a73e8; text-decoration: none;">
                GitHub repository
            </a>.
        </p>
    </div>
    """
    display(HTML(end_text))




# Main frontend function to be called in jupyter.py 
def main_jupyter_output(full_df, daily_df, total_df, arguments):
    """
    Main function to produce the Jupyter Notebook output for the GRACE-HPC results.

    Args:
        full_df (pd.DataFrame): Full DataFrame with all jobs (1 row per job).
        daily_df (pd.DataFrame): Daily aggregated DataFrame (1 row per day).
        total_df (pd.DataFrame): Total aggregated DataFrame over all jobs (1 row for all jobs).
        arguments (argparse.Namespace): User arguments entered in the CLI or script/JN usable function.

    Returns:
        None: Displays the results in the Jupyter Notebook.
    """
    # Load the hpc_config.yaml file (user must edit this file to match their HPC system)
    with open('hpc_config.yaml', 'r') as file:
        try: 
            hpc_config = yaml.safe_load(file)  # Load the YAML file into a dictionary
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading hpc_config.yaml: {e}")

    # Call function to generate the Jupyter Notebook result plotting function 
    JN_stats_plots(full_df, daily_df, total_df, arguments, hpc_config)