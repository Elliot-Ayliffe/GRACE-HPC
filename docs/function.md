# Python Usage 

For greater flexibility and integration, you can use GRACE-HPC programmatically, directly in a **Python script** (.py) or **Jupyter Notebook** (.ipynb) by importing and calling a function. This enables you to embed the tool into your own workflows, automate analyses, or even develop your own custom carbon footprinting solutions.

## Import the Function

In your Python code, enter:

```python
from gracehpc import gracehpc_run 
```

## Function Arguments
The arguments are identical to those used in the CLI. For detailed descriptions and available options, refer to the [Inputs Arguments](inputs_outputs.md#input-arguments) section.

| Argument            | Type | Format `Example`                                                        |
|---------------------|------|--------------------------------------------------------------------------|
| StartDate           | *str*| YYYY-MM-DD   `"2025-01-01"`                                              |
| EndDate             | *str*| YYYY-MM-DD   `"2025-06-15"`                                             |
| JobIDs              | *str*| Comma separated list (no spaces)   `"id1234,id5678"`                     |
| Region              | *str*| UK Region Name   `"South West England"`                                  |
| Scope3              | *str*| HPC system name or custom value  `"Isambard3"` or `"51"` or `"no_scope3"`                      |
| CSV                 | *str*| CSV output type   `"full", "total", etc.` or `"no_save"`                               |


## Run the Engine
Call the following function to run the full engine (and return 3 dataframes) in a Python script or notebook, instead of the command-line interface.

```python 
full_df, daily_df, total_df = gracehpc_run(
    StartDate="2025-01-01", 
    EndDate="2026-01-01",
    Region="South West England",
    JobIDs="id1234,id5678",
    Scope3="Isambard3",
    CSV="no_save"
)
```
## Function Returns
Output results can be captured in three pandas DataFrames for the further exploration after using the tool. Refer to the [Output Data](inputs_outputs.md#output-data) section for details on the data included and their corresponding column names.

| DataFrame           | Description                                            |
|---------------------|--------------------------------------------------------|
| full_df             | Full job-level dataset - **one row per job**. <br> Includes all fields for each job processed in the date range.   |
| daily_df            |  Daily aggregated dataset - **one row per day**. <br> Aggregates all fields across all jobs per day. <br> E.g. sums the energy and carbon emissions of jobs submitted in each day, and takes the average carbon intensity value.   |
| total_df            | Total summary dataset - **one row aggregating all jobs**. <br> Includes overall totals or averages for each field in the full_df.   |





















(function) def gracehpc_run(
    StartDate: str = f"{datetime.date.today().year}-01-01",
    EndDate: str = datetime.date.today().strftime("%Y-%m-%d"),
    JobIDs: str = "all_jobs",
    Region: str = "UK_average",
    Scope3: str = "no_scope3",
    CSV: str = "no_save"
) -> tuple[Series, Any, Any]
Run the GRACE-HPC tool programmatically in a script (alternative to CLI).

This function enables users to run the full engine to estimate the carbon footprint (scope 2 and scope 3) of your SLURM HPC jobs via python scripts or Jupyter Notebooks, rather than the command line interface (CLI). Results are printed to the console and saved to CSV files if specified. 3 dataframes are returned containing the full, daily and total datasets.

GRACE-HPC: A Green Resource for Assessing Carbon & Energy in HPC.

This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs. If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage statistics.

Carbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API (carbonintensity.org.uk.) at the time of job submission. Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. For Isambard systems and Archer2, these scope 3 factors are calculated from the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.

Args
StartDate : str
The first date of the range to process jobs for, in YYYY-MM-DD. Default is January 1st of the current year.

EndDate : str
The final date of the range to process jobs for, in YYYY-MM-DD. Default is the current date.

JobIDs : str, optional
Comma-separated list of all the HPC job IDs to filter on (no spaces). Default is "all_jobs", which processes all jobs in the specified date range.

Region : str, optional
UK region of the HPC cluster needed for realtime carbon intensity data.

Options: 'North Scotland', 'South Scotland', 'North West England', 'North East England', 'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', 'East Midlands', 'East England', 'South West England', 'South England', 'London', 'South East England'. Default: 'UK_average'.

E.g. 'South West England' for Isambard systems and 'South Scotland' for Archer2.

Scope3 : str, optional
Option to include scope 3 emissions (embodied) in the calculations.

HPC systems available: 'Isambard3', 'IsambardAI', 'Archer2'

Or include custom numeric value in gCO2e/node-hour for other HPC systems (e.g. "51"). Default is 'no_scope3' which means only scope 2 emissions (operational) will be calculated.

CSV : str, optional
Save the final datasets to CSV files for further analysis.

Options

'full' : entire dataset (all jobs) with all columns
'full_summary' : entire dataset with summary columns only
'daily' : dataset aggregated by day with all columns
'daily_summary' : dataset aggregated by day with summary columns only
'total' : dataset aggregated over all total jobs with all columns
'total_summary' : dataset aggregated over all total jobs with summary columns only
'all' : all of the above datasets saved to CSV files
Returns
tuple : pd.DataFrame, pd.DataFrame, pd.DataFrame

full_df: DataFrame containing the full dataset of jobs processed. (1 row per job)
daily_df: DataFrame containing the daily aggregated dataset. (1 row per day)
total_df: DataFrame containing the total aggregated dataset. (1 row totalling all jobs)
Examples
>>> gracehpc_run(StartDate="2025-06-01", EndDate="2053-07-25", JobIDs="12345,67890", Region="South West England", Scope3="IsambardAI", CSV="all")
>>> gracehpc_run(StartDate="2025-01-01", EndDate="2025-08-01", Region="South West England", Scope3="Isambard3", CSV="full_summary")
>>> gracehpc_run(StartDate="2025-07-16", EndDate="2025-07-07", JobIDs"id1245", Region="London", Scope3="51", CSV="no_save")
For more information on the required arguments use:

>>> help(gracehpc_run)