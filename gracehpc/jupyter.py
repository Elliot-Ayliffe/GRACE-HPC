""" 
jupyter.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 13/07/25

This script contains the main function that generates an interactive Jupyter Notebook interface for the GRACE-HPC tool.
This is an alternative to using the command-line interface (CLI) and script usage provided by the package.
This allows users to visualise plots a results interactively within a Jupyter Notebook environment.

Functions included:

Main Functions:

- `title_instructions_formatter()`:
    Displays a styled HTML introduction and user guide explaining the interface and usage.

- `create_input_widgets()`:
    Creates and returns the input widgets (date pickers, dropdowns, text fields) used in the interface.

- `jupyter_UI()`:
    Launches the full interactive user interface inside a Jupyter Notebook. Displays the interface, handles user input,
    runs the backend engine, and presents results interactively. Returns a dictionary of DataFrames with results.
    This function must be called inside a Jupyter Notebook to work correctly.

Usage:

>> results = jupyter_UI()
# After clicking the "Calculate Carbon Footprint" button, the results will be stored in the `results` dictionary, and can be accessed as:
# results['full_df'], results['daily_df'], results['total_df']

>> jupyter_UI()
#  will display the interface and results, but will not return the results dictionary.
"""

# Import libraries
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import datetime
import argparse 
import sys

# Import functions for other modules 
from .cli import confirm_date_args
from .core.emissions_calculator import core_engine
from .script import build_args




def title_instructions_formatter():
    """
    Display the formatted title and instructions for the GRACE-HPC Jupyter Interface.
    """
    # Nicely formatted title for the GRACE-HPC interface
    grace_hpc_title = """
    <div style="
        background-color: #e8f5e9;
        border-left: 6px solid #4caf50;
        padding: 30px;
        border-radius: 8px;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 8px;
    ">
      <h2 style="margin-top: 0; color: #2e7d32; font-size: 2.7em;">GRACE-HPC 🌱 </h2>
      <p style="font-size: 1.8em;"><strong>Green Resource for Assessing Carbon & Energy in HPC</strong></p>
     
      <div style="font-size: 1.2em;">
      <p>This tool estimates the <b>energy consumption, scope 2 and scope 3 carbon emissions</b> of your SLURM HPC jobs.
    If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage data and cluster-specific TDP values.</p>

    <p>Carbon intensity for scope 2 emissions (operational) is retrieved from the regional <a href="https://carbonintensity.org.uk" target="_blank">Carbon Intensity API</a> at the time of job submission. 
    Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. For Isambard systems and Archer2, these scope 3 factors are calculated from 
    the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.</p>

    <p><b>Use this interactive tool to quickly assess, visualise and explore the carbon footprint of your HPC jobs.</b></p>
    <p><b>Note:</b> Estimates are provided for the user's interest only. Please acknowledge the assumptions and limitations below.</p>
     </div>
    </div>
    """

    # User instructions explaining the arguments required
    user_guide = """
    <div style="
        background-color: #e3f2fd;
        border-left: 6px solid #1976d2;
        padding: 30px;
        border-radius: 8px;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 25px;
    ">
    <h2 style="margin-top: 0; color: #1565c0; font-size: 2.1em;">USER GUIDE:</h2>
    <ul style="font-size: 1.3em; line-height: 1.8;">
        <li style="margin-bottom: 13px;"><strong>Select the job date range</strong> &mdash; choose the start and end dates for which to process jobs.</li>
        
        <li style="margin-bottom: 13px;"><strong>Enter your HPC Job IDs</strong> &mdash; Choose to include <code>'all_jobs'</code> within the date range or provide a list of job IDs to filter on (<code>'Job IDs'</code>).
        <ul>
            <li>If you select <code>'Job IDs'</code>, provide a comma-separated list of your job IDs you wish to include (NO SPACES).</li>
        </ul>
        </li>
        
        <li style="margin-bottom: 13px;"><strong>Select your HPC region</strong> &mdash; choose the UK region where your HPC system is located to retrieve real-time carbon intensity data from the <a href="https://carbonintensity.org.uk" target="_blank">Carbon Intensity API</a>.
        <ul>
            <li>E.g. For Isambard systems, select <code>South West England</code> for location-based operational emissions using realtime carbon intensity.</li>
        </ul>
        
        
        <li style="margin-bottom: 13px;"><strong>Scope 3 emissions</strong> &mdash; select whether to include Scope 3 (embodied) emissions within the calculations. HPC systems available include:
        <ul>
            <li><code>IsambardAI</code></li>
            <li><code>Isambard3</code></li>
            <li><code>Archer2</code></li>
            <li>Or provide a custom numeric value (e.g., <code>51</code> gCO₂e/node-hour) for other HPC systems.</li>
        </ul>
        The default is <code>no_scope3</code>, which means only Scope 2 (operational) emissions will be calculated.
        </li>
        
        <li style="margin-bottom: 30px;"><strong>Optionally save results to CSV files</strong> &mdash; choose the datasets you wish to export for further analysis or reporting.
        <ul>
            <li><code>full</code>: all jobs with all columns (1 row per job)</li>
            <li><code>full_summary</code>: all jobs with summary columns only</li>
            <li><code>daily</code>: aggregated daily, all columns (1 row per day)</li>
            <li><code>daily_summary</code>: aggregated daily, summary columns only</li>
            <li><code>total</code>: aggregated total, all columns(1 row totalling all jobs)</li>
            <li><code>total_summary</code>: aggregated total, summary columns only</li>
            <li><code>all</code>: export all of the above</li>
        </ul>
        </li>

        <li>Click the <b>"Calculate Carbon Footprint"</b> button to run the engine and generate the results.</li>
    </ul>
    </div>
    """

    display(HTML(grace_hpc_title + user_guide))




def create_input_widgets():
    """
    Creates and displays the input widgets for the GRACE-HPC Jupyter Interface.
    """
    # Date picker for the StartDate and EndDate
    start_date = widgets.DatePicker(
        description='Start Date:',
        value=datetime.date(datetime.date.today().year, 1, 1), # Default is the 1st January of the current year
        layout=widgets.Layout(width='400px')
    )

    end_date = widgets.DatePicker(
        description='End Date:',
        value=datetime.date.today(),        # Default is the current date
        layout=widgets.Layout(width='400px')
    )

    # Job ID mode selector
    job_mode = widgets.Dropdown(
        options=['all_jobs', 'Job IDs'],
        value='all_jobs',
        description='Jobs:',
        layout=widgets.Layout(width='400px')
    )

    # Text input for Job IDs (hidden until 'Job IDs' is selected)
    job_ids = widgets.Text(
        placeholder='e.g. 12345,67890',
        layout=widgets.Layout(width='400px'),
        description='Job IDs:',
        visible=False
    )

    def job_mode_change(change):
        """
        Show or hide the Job IDs text input based on the selected job mode.
        """
        if change['new'] == 'Job IDs':
            job_ids.layout.display = 'inline-block'
            job_ids.visible = True
        else:
            job_ids.layout.display = 'none'
            job_ids.visible = False
    
    job_mode.observe(job_mode_change, names='value')
    job_ids.layout.display = 'none'  # Initially hide the Job IDs input

    # UK region selector
    region = widgets.Dropdown(
        options=[
            'UK_average', 'North Scotland', 'South Scotland', 'North West England', 'North East England',
            'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', 'East Midlands', 'East England',
            'South West England', 'South England', 'London', 'South East England'
        ],
        value='UK_average',
        description='Region:',
        layout=widgets.Layout(width='400px')
    )

    # Scope 3 emissions selector 
    scope3_drop = widgets.Dropdown(
        options=['no_scope3', 'IsambardAI', 'Isambard3', 'Archer2', 'Other HPC system'],
        value='no_scope3',
        description='Scope 3:',
        layout=widgets.Layout(width='400px')
    )

    # Custom numeric input for scope 3 emissions (hidden until 'Other HPC system' is selected)
    numeric_scope3 = widgets.Text(
        placeholder='e.g. 0.34',
        description='gCO₂e/nodeh:',
        layout=widgets.Layout(width='400px'),
        visible=False
    )

    def scope3_change(change):
        """
        Show or hide the numeric input for scope 3 emissions based on the selected option.
        """
        if change['new'] == 'Other HPC system':
            numeric_scope3.layout.display = 'inline-block'
            numeric_scope3.visible = True
        else:
            numeric_scope3.layout.display = 'none'
            numeric_scope3.visible = False
    

    scope3_drop.observe(scope3_change, names='value')
    numeric_scope3.layout.display = 'none'  # Initially hide the numeric input

    # CSV dataset output selector
    csv_files = widgets.Dropdown(
        options=['no_save', 'full', 'full_summary', 'daily', 'daily_summary', 'total', 'total_summary', 'all'],
        value='no_save',
        description='CSV:',
        layout=widgets.Layout(width='400px')
    )

    return start_date, end_date, job_mode, job_ids, region, scope3_drop, numeric_scope3, csv_files




# Main function available to users
def jupyter_UI():
    """
    Launch an interactive Jupyter user interface for the Grace-HPC tool.
    This function must be called inside a Jupyter Notebook.

    This interface allows users to input job parameters (date range, job IDs, region, scope 3 emissions, and CSV output options),
    and then runs the GRACE-HPC tool to calculate the energy consumption and carbon emissions (scope 2 and optionally scope 3).
    Results are displayed interactively within the notebook, and can be saved to CSV files if desired.

    Returns:
        dict: A dictionary containing 3 dataframes with the results:
            - 'full_df': DataFrame containing the full dataset of jobs processed. (1 row per job)
            - 'daily_df': DataFrame containing the daily aggregated dataset. (1 row per day)
            - 'total_df': DataFrame containing the total aggregated dataset. (1 row totalling all jobs)
    """
    # Display the title and user guide
    title_instructions_formatter()

    # Create input widgets
    start_date, end_date, job_mode, job_ids, region, scope3_drop, numeric_scope3, csv_files = create_input_widgets()

    # Create an output area for displaying results
    output_area = widgets.Output()

    # Results to return after execution 
    results ={}

    # Button that triggers the tool to run (calls the backend)
    run_button = widgets.Button(
        description='Calculate Carbon Footprint',
        button_style='success',
        icon='leaf',
        layout=widgets.Layout(width='400px', margin='20px 0px 0px 0px')
    )

    # Function that is called when the button is clicked
    def when_clicked(b):
        """
        Function to run when the button is clicked.
        It collects the input values and calls the backend function to process the data.
        """
        output_area.clear_output()  # Clear previous output to keep the interface clean 

        # Determine the job IDs to use 
        job_ids_final = job_ids.value if job_mode.value == 'Job IDs' else 'all_jobs'

        # Determine the scope 3 emissions value 
        scope3_final = numeric_scope3.value if scope3_drop.value == 'Other HPC system' else scope3_drop.value


        with output_area:

            # Show message showing the backend is running
            print("Running the GRACE-HPC calculator...\n")

            # Display the job IDs that will be used for this calculation.
            print("Job IDs:", job_ids_final)

            # Display the arguments that will be used.
            print(f"📅 Start Date: {start_date.value.strftime('%Y-%m-%d')}")
            print(f"📅 End Date: {end_date.value}")
            print(f"📍 Region of HPC system: {region.value}")
            print("Scope 3 Included:", scope3_final)
            print(f"💾 CSV Output Option: {csv_files.value}")

            # Convert the user inputs into an argparse.Namespace object
            arguments = build_args(
                StartDate=start_date.value.strftime('%Y-%m-%d'),
                EndDate=end_date.value.strftime('%Y-%m-%d'),
                JobIDs=job_ids_final,
                Region=region.value,
                Scope3=scope3_final,
                CSV=csv_files.value
            )

             # Validate the date arguments are correct 
            try:
                confirm_date_args(arguments)  # Check if the date arguments are valid
            except (ValueError, SystemExit) as e:
                    print(f"❌ Date validation error: {e}")
                    return 

            
            # Execute the entire backend (core_engine) by passing the arguments 
            full_df, daily_df, total_df = core_engine(arguments)

            # Save dataframes to the results dictionary
            results['full_df'] = full_df
            results['daily_df'] = daily_df
            results['total_df'] = total_df

            # Pass the dataframes to the jupyter frontend to display results
            jupyter_output(full_df, daily_df, total_df, arguments)

    
    run_button.on_click(when_clicked)

    # Display the input widgets and the button
    full_widgets = widgets.VBox([
        start_date,
        end_date,
        job_mode,
        job_ids,
        region,
        scope3_drop,
        numeric_scope3,
        csv_files,
        run_button,
        output_area
    ])  
    display(full_widgets)

    return results