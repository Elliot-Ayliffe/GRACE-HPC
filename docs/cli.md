# Command-line Interface (CLI)

Now that the configuration file has been edited and saved, you can run `GRACE-HPC` from the command-line to calculate the energy use and carbon footprint of your HPC jobs:

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

  -h, --help               show this help message and exit

  --StartDate STARTDATE    The first date of the range to process jobs for, in YYYY-MM-DD. 
                           Default: 2025-01-01 (January 1st of the current year)

  --EndDate ENDDATE        The final date of the range to process jobs for, in YYYY-MM-DD. 
                           Default: Current date

  --JobIDs JOBIDS          Comma-separated list (no spaces) of all the HPC job IDs to filter on. 
                           E.g. 'id1234,id5678'
                           Default: 'all_jobs'

  --Region REGION          UK region of the HPC cluster needed for realtime carbon intensity data. 
                           Choices: 'North Scotland', 'South Scotland', 'North West England', 'North East England', 
                           'Yorkshire', 'North Wales', 'South Wales', 'West Midlands', 'East Midlands', 'East England',
                           'South West England', 'South England', 'London', 'South East England'. 
                           Default: 'UK_average' 
                           E.g. 'South West England' for Isambard systems and 'South Scotland' for Archer2.

  --Scope3 SCOPE3          Include scope 3 emissions for either: 'Isambard3', 'IsambardAI', 'Archer2', 
                           or a custom numeric value in gCO2e/node-hour for other HPC systems (e.g. '51'). 
                           Default: 'no_scope3'. If 'no_scope3' is selected, only scope 2 emissions will be calculated.

  --CSV CSV                Save the final datasets to CSV files for further analysis. 
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

2. Estimating energy use and carbon emissions for job `121109` ran on `Isambard-AI` without `scope 3` emissions included, saving the `full` dataset to CSV for further analysis.

```bash 
gracehpc run --JobIDs '121109' --Region 'South West England' --CSV 'full'
```

3. Estimating energy use and carbon emissions for jobs `119363 and 119364` ran on `Archer2` with `scope 3` included and saving the `total` aggregated dataset to CSV, combining both jobs.

```bash
gracehpc run --JobIDs '119363,119364' --Region 'South Scotland' --Scope3 'Archer2' --CSV 'total'
```


## Example Terminal Output

Here is an example terminal output for `GRACE-HPC` run on Isambard-AI command line.

```bash
(ghpc_env) username.project@nid01:~/dir> gracehpc run --StartDate 2025-05-01 --EndDate 2025-07-01 --Region 'South West England' --Scope3 'IsambardAI'


╭─ 🌱 GRACE-HPC ─────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                            │
│     Carbon Footprint Estimation for HPC Jobs ran on Isambard-AI                                            │
│                                                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs. If 
energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage 
data and cluster-specific TDP values.

Carbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API 
(https://carbonintensity.org.uk) at the time of job submission. Scope 3 emissions (embodied) are estimated 
from the node-hours used by the job, and the scope 3 emissions factor. For Isambard systems and Archer2, these
scope 3 factors are calculated from the total lifecycle scope 3 emissions for each system divided by the total
node-hours available over the systems projected lifetime.

The results below are calculated using SLURM accounting data for jobs submitted to the Isambard-AI cluster, 
including information such as runtime, resource allocation, resource usage, hardware-level energy counters 
(if available), etc. For a detailed explanation of all methodologies used, please refer to the GRACE-HPC 
documentation.

Note: The results presented here are estimates based on the available data and methodologies with assumptions 
and limitations. Hence this tool should be used for informational purposes only, not as a definitive energy 
and carbon cluster monitoring tool.


────────────────────────────────────────────────── OVERVIEW ──────────────────────────────────────────────────

    HPC System: Isambard-AI
    User Name: eayliffe.d5c
    Date Range: 2025-05-01 to 2025-07-01
    Jobs: Processing all jobs in the selected date range
    System PUE: 1.1
    System Energy Counters: ❌ Not available for all jobs — hardware energy counters were not used in calculations. 
                            Usage-based estimates were used instead.


    
─────────────────────────────────────────── ⚡️ ENERGY CONSUMPTION ────────────────────────────────────────────

    Total Energy Used (estimated): 50.2017 kWh

         - CPUs: 1.0510 kWh
         - GPUs: 40.4767 kWh
         - Memory: 4.1101 kWh
         - Data Centre Overheads (PUE): 4.5638 kWh

    Compute Energy Use (estimated): 45.6379 kWh  
    Compute Energy Use (measured by system counters): N/A (not all jobs had energy counters available)


    
──────────────────────────────────────────── 🌿 CARBON FOOTPRINT ─────────────────────────────────────────────

    Scope 2 Emissions (usage-based): 6.1486 kgCO2e
    Scope 2 Emissions (system counter-based): N/A (not all jobs had energy counters available)
    Scope 3 Emissions: 2.7534 kgCO2e (114 gCO2e/node-hour)

    Total Emissions: 8.9020 kgCO2e (usage-based)

    Average Carbon Intensity: 122.0 gCO2e/kWh (South West England)
    CI distribution (gCO2e/kWh): Q1: 83.0, Median: 121.0 , Q3: 152.0 
    


Note: For Isambard systems and Archer2, market-based Scope 2 emissions = 0 gCO₂e due to 100% certified 
zero-carbon electricity contracts.
The estimates above are based on the UK national grid carbon intensity and are provided for informational 
purposes, representing what the emissions would be if Isambard systems were not powered by renewable energy 
(the grid only).


─────────────────────────────────────────── THIS IS EQUIVALENT TO: ───────────────────────────────────────────

    🚗 Driving 42.15 miles                          (0.21 kgCO2e/mile average UK car, 2023)
    🌲 Tree absorption: 10.7 tree-months            (0.83 kgCO2e/month average UK tree carbon sequestration rate)
    ✈️ Flying 0.063 times from Bristol to Paris     (140 kgCO2e/passenger)
    🏠 UK Households: Daily emissions from 9.7 households electricity use        (UK average)

    Approximate electricity cost: £12.92            (at 0.2573 GBP/kWh)

    See documentation for sources and assumptions of these estimates.

    
───────────────────────────────────────────── ⚙️ USAGE STATISTICS ─────────────────────────────────────────────

    Number of Jobs: 178 (129 successful)
    First → Last Job Submitted: 2025-06-10 → 2025-06-21
    Total Runtime: 0 days 21:38:40
    Total CPU Usage Time: 12 days 14:43:02.495000  (303 hours)
    Total GPU Usage Time: 2 days 09:49:26  (58 hours)
    Memory Requested: 93,388.0 GB
    Node Hours: 24.2
    CPU Hours: 0.0
    GPU Hours: 57.8

    
─────────────────────────────────── ❌ FAILED JOBS & WASTED MEMORY IMPACT ────────────────────────────────────

    Failed Jobs: 49 (27.5%)
    Wasted Scope 2 Emissions: 1.7687 kgCO2e (Usage-based estimate)
    

Note: Failed HPC jobs are a significant source of wasted computational resources and unnecessary carbon 
emissions.
Every failed job still consumes electricity for scheduling, startup, and partial execution—without producing 
useful results.
Reducing failed jobs is a simple yet impactful way to lower your carbon footprint on HPC systems.


Memory overallocation is a common source of energy waste and excess carbon emissions.
On most HPC systems, power draw depends on the amount of memory requested, not the memory actually used.

    If all jobs had been submitted with only the memory they truly required, approximately:

    598.4678 gCO2e could have been saved (Usage-based estimate)


────────────────────────────────────────── DOCUMENTATION & FEEDBACK ──────────────────────────────────────────

Find the methodology including assumptions and limitations of this tool outlined in the documentation:
https://github.com/Elliot-Ayliffe/GRACE-HPC/tree/main

See also what other features are available with the package/API including an interactive Jupyter Notebook 
interface.

If you find any bugs, have questions, or suggestions for improvements, please post these on the GitHub 
repository.
```