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

Example function calls:

```python 
>>> gracehpc_run(StartDate="2025-06-01", EndDate="2053-07-25", JobIDs="12345,67890", Region="South West England", Scope3="IsambardAI", CSV="all")
>>> gracehpc_run(StartDate="2025-01-01", EndDate="2025-08-01", Region="South West England", Scope3="Isambard3", CSV="full_summary")
>>> gracehpc_run(StartDate="2025-07-16", EndDate="2025-07-07", JobIDs="id1245", Region="London", Scope3="51", CSV="no_save")
```

For more information on the required arguments run:

```python 
help(gracehpc_run)
```
### Output
The output generated is the same as that produced in the terminal for the CLI, [see here for an example](cli.md#example-terminal-output).


## Function Returns
Output results can be captured in three pandas DataFrames for the further exploration after using the tool. Refer to the [Output Data](inputs_outputs.md#output-data) section for details on the data included and their corresponding column names.

| DataFrame           | Description                                            |
|---------------------|--------------------------------------------------------|
| full_df             | Full job-level dataset - **one row per job**. <br> Includes all fields for each job processed in the date range.   |
| daily_df            |  Daily aggregated dataset - **one row per day**. <br> Aggregates all fields across all jobs per day. <br> E.g. sums the energy and carbon emissions of jobs submitted in each day, <br> and takes the average carbon intensity value.   |
| total_df            | Total summary dataset - **one row aggregating all jobs**. <br> Includes overall totals or averages for each field in the full_df.   |


You can now filter, explore, or process these DataFrames further. See some examples below:

```python 
# Access the energy consumed by CPUs for each job 
cpu_energy = full_df["CPU_energy_estimated_kwh"]

# Filter the daily_df to extract data for a specific submission date
# Convert the SubmissionDate column to datetime format
daily_df["SubmissionDate"] = pd.to_datetime(daily_df["SubmissionDate"])
filtered_daily = daily_df[daily_df["SubmissionDate"] == pd.to_datetime("2025-06-16")]

# Find jobs in full_df with a specific job name
ai_job = full_df[full_df["NameofJob"] == "AI_benchmark"]

# Select only successful jobs (StateCode == 1)
successful_jobs = full_df[full_df["StateCode"] == 1]
```