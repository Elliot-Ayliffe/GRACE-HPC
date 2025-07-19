# Inputs & Outputs

Before using the tool, it would be helpful to define all the **input arguments** available to the user to enrich their estimations and the **final outputs** (columns of the returned datasets).

## Input Arguments 

| Argument            | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `StartDate`         | The first date of the range to process jobs for, in `YYYY-MM-DD`.  <br>   Default: January 1st of the current year e.g. `2025-01-01`      |
| `EndDate`           | The final date of the range to process jobs for, in `YYYY-MM-DD`.  <br> Default: The current date. |
| `JobIDs`            | Comma-separated list of all the HPC **job IDs** to filter on (e.g `"id1245,id6789"`) <br> Default is "all_jobs", which processes all the jobs ran in the specified date range. |
| `Region`            | UK region of the HPC cluster you are using, needed for carbon intensity data. <br> This is used to retrieve realtime carbon intensity data from the [NESO Carbon Intensity API](https://carbonintensity.org.uk) <br> corresponding to job start times. <br><br> **Options:** `'North Scotland'`, `'South Scotland'`, `'North West England'`, <br> `'North East England'`, `'Yorkshire'`, `'North Wales'`, `'South Wales'`, <br> `'West Midlands'`, `'East Midlands'`, `'East England'`, <br> `'South West England'`, `'South England'`, `'London'`, `'South East England'`. <br><br> Default: `'UK_average'` which was [124 gCO2e/kWh in 2024.](https://www.carbonbrief.org/analysis-uks-electricity-was-cleanest-ever-in-2024/)  |
| `Scope3`            | Option to include scope 3 (embodied) emissions estimates as well as scope 2 in the output. <br>  This feature is only available to a few HPC systems which have undergone lifecycle <br> assessments to obtain a **per node-hour scope 3 emissions factor**. <br><br> **Options:** `Isambard3`, `IsambardAI`, and `Archer2` [(see here)](https://docs.archer2.ac.uk/user-guide/energy/). <br> You may also specify a custom numeric value in gCO2e/node-hour for other HPC systems <br> if these values are available (e.g. `51`). <br><br> Default: `no_scope3` which means only scope 2 (operational emissions) will be calculated <br> and included in the output.|
| `CSV`               | Save the final datasets to CSV file for further analysis elsewhere. <br><br> **Options:** <br> `full`: Entire dataset (all jobs) with all columns [(see below.)](#output-data) <br> `full_summary`: entire dataset with summary columns only. <br> `daily`: dataset aggregated by day with all columns. <br> `daily_summary`: dataset aggregated by day with summary columns only. <br> `total`: dataset aggregated over all total jobs with all columns. <br> `total_summary` : dataset aggregated over all total jobs with summary columns only.  <br> `all`: all of the above datasets saved to CSV files.|




## Output Data 

Below are the columns returned in the outputted datasets once the tool has been run. These are not stored if you are using the command-line interface, unless the user has specified the data to be saved to CSV. The following pages describe how to use the tool and store outputs for each user mode: 

- [Command-line Interface](cli.md)
- [Function Call](function.md)
- [Interactive Jupyter Interface](jupyter.md)

| Column Name           | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `Job_ID`         |  
