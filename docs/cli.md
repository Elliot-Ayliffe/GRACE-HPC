# Command-line Interface (CLI)

Now that the configuration file has been editted and saved, you can run `GRACE-HPC` from the command-line to calculate the energy use and carbon footprint of your HPC jobs:

```bash
gracehpc run [ARGUMENT-OPTIONS]
```
Running this command without any options will execute the analysis with **default values** for all arguments specified below.

## Argument Options

You can customise the output with many arguments and options to enhance the carbon footprint analysis:

```bash
usage: gracehpc run [-h] [--StartDate STARTDATE] [--EndDate ENDDATE] [--JobIDs JOBIDS]
                    [--Region REGION] [--Scope3 SCOPE3] [--CSV CSV]

options:

  -h, --help                show this help message and exit

  --StartDate STARTDATE     The first date of the range to process jobs for, in YYYY-MM-DD. 
                            Default: 2025-01-01

  --EndDate ENDDATE         The final date of the range to process jobs for, in YYYY-MM-DD. 
                            Default: 2025-07-19

  --JobIDs JOBIDS           Comma-separated list (no spaces) of all the HPC job IDs to filter on. 
                            E.g. 'id1234,id5678'
                            Default: 'all_jobs'

  --Region REGION           UK region of the HPC cluster needed for realtime carbon intensity data. 
                            Choices: 'North Scotland', 'South Scotland', 'North West England', 'North East England', 
                            'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', 'East Midlands', 'East England',
                            'South West England', 'South England', 'London', 'South East England'. 
                            Default: 'UK_average' 
                            E.g. 'South West England' for Isambard systems and 'South Scotland' for Archer2.

  --Scope3 SCOPE3           Include scope 3 emissions for either: 'Isambard3', 'IsambardAI', 'Archer2', 
                            or a custom numeric value in gCO2e/node-hour for other HPC systems (e.g. '51'). 
                            Default: 'no_scope3'. If 'no_scope3' is selected, only scope 2 emissions will be calculated.

  --CSV CSV                 Save the final datasets to CSV files for further analysis. 
                            Choices: 'full': entire dataset (all jobs) with all columns, 
                            'full_summary': entire dataset with summary columns only, 
                            'daily': dataset aggregated by day with all columns, 
                            'daily_summary': dataset aggregated by day with summary columns only, 
                            'total': dataset aggregated over all total jobs with all columns, 
                            'total_summary': dataset aggregated over all total jobs with summary columns only,
                            'all' : all of the above datasets saved to CSV files. 
                            Default: 'no_save'
```

## Example Commands 

1. Estimating the energy use and carbon emissions for `all jobs` ran on `Isambard 3` between May and June with `scope 3` emissions included.

```bash
gracehpc run --StartDate 2025-05-01 --EndDate 2025-06-01 --Region 'South West England' --Scope3 'Isambard3'
```

2. Estimating energy use and carbon emissions for job `121109` ran on `Isambard-AI` without `scope 3` emissions included, saving the full dataset to CSV for further analysis.

```bash 
gracehpc run --JobIDs '121109' --Region 'South West England' --CSV 'full'
```

3. Estimating energy use and carbon emissions for jobs `119363 and 119364` ran on `Archer2` with scope 3 included and saving the total aggregated dataset to CSV, combining both jobs.

```bash
gracehpc run --JobIDs '119363,119364' --Region 'South Scotland' --Scope3 'Archer2' --CSV 'total'
```


## Example Terminal Output

