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

#### **SLURM-Extracted Job Data columns**

| Column Name         | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `Job_ID`            |  Unique identifier for your job ran on the HPC system. |
| `UserID`            |  Unique numerical ID of the job submitter. |
| `UserName`            |  Username of the person who submitted the job. |
| `PartitionName`            |  Name of the partition the job was submitted to.   |
| `PartitionCategory`            |  Processor type of the partition (`CPU` or `GPU`). <br> This is provided by the user in `hpc_config.yaml`.|
| `NameofJob`            |  Job name given by the user when submitted. |
| `SubmissionTime`            |  Date and time the job was submitted in  `%Y-%m-%d %H:%M:%S` format (Datetime).
| `SateCode`            |  Numeric code representing the job status (1 = completed/successful, 0 = failed).|
| `TotalNodes`            |  Total number of nodes allocated to the job(s).|
| `CPUsAllocated`            |  Total number of CPU cores allocated to the job(s). |
| `GPUsAllocated`            |  Total number of GPUs allocated to the job(s). |
| `ElapsedRuntime`            |  Total wallclock runtime of the job(s). |
| `CPUusagetime`            |  The actual CPU time consumed by the job(s), summed across all CPUs <br> (measured time CPUs were actively processing). <br> As a timedelta object `D days HH:MM:SS`. |
| `CPUwalltime`            |  Estimated CPU time (NCPUs * `ElapsedRuntime`). <br> The max CPU time if all cores were 100% utilised. <br> As a timedelta object `D days HH:MM:SS`.|
| `GPUusagetime`            |  Estimated GPU usage time (`GPUsAllocated` * `ElapsedRuntime`). <br> Assumes 100% GPU utilisation due to a lack of measured GPU usage data available from SLURM. <br> As a timedelta object `D days HH:MM:SS`.|
| `RequestedMemoryGB`            |  Amount of memory requested by the user at job submissions (in GB). |
| `UsedMemoryGB`            |  Amount of memory actually used by the job(s) (in GB). |
| `RequiredMemoryGB`            |  The estimated minimum amount of memory required for the job(s) to run (in GB).|
| `NodeHours`            |  Calculated total node-hour usage (in hours). |
| `WorkingDirectory`            |  File system path where the job was run from. <br> e.g. `/lus/lfs1aip1/home/d5c/eayliffe.d5c/job` |


#### **Energy Data**

| Column Name         | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `EnergyIPMI_kwh`    | Total energy consumed (kWh) by the job(s) measured by hardware energy/power counters <br> (e.g. **IPMI or RAPL**). This is only logged if energy counters are available on the HPC system |
| `energy_estimated_kwh`            | Total energy consumed (kWh) by the job(s) including the datacenter overhead (PUE factor). <br> This is estimated from usage data and TDP values supplied by the user in `hpc_config.yaml` |
| `energy_esimtated_noPUE_kwh`            |  Total energy consumed by the job(s) without the datacenter overhead (PUE) applied (usage-based estimate) <br> This is for valid comparison with energy counters. |
| `CPU_energy_estimated_kwh`            |  Energy consumed by CPUs (usage-based estimate). |
| `GPU_energy_estimated_kwh`            |  Energy consumed by GPUs (usage-based estimate). |
| `memory_energy_estimated_kwh`            |  Energy consumed by memory (usage-based estimate). |
| `required_memory_energy_estimated_kwh`            |  Energy consumed by memory if only the required memory was allocated (usage-based estimate). |
| `energy_requiredMem_estimated_kwh`            |  Total energy consumed (kWh) by the job(s) if only the required memory was allocated. |
| `failed_energy_kwh`            |  Energy consumed by failed jobs only. |


#### **Carbon Emissions Data**

| Column Name         | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `CarbonIntensity_gCO2e_kwh`            |  Carbon Intensity at the time of job submission for the selected `Region` (in gCO2e/kWh). <br> Retrieved from the carbon intensity API at the time of job submission. <br> This is averaged over all jobs.|
| `Scope2Emissions_gCO2e`            |  Scope 2 (operational) emissions calculated using estimated energy (in gCO2e). |
| `Scope2Emissions_IPMI_gCO2e`            |  Scope 2 (operational) emissions calculated using measured energy (energy counters). |
| `Scope3Emissions_gCO2e`            |  Scope 3 (embodied emissions) estimated for the job(s). <br> Only shows if the `Scope3` argument is set.  |
| `Scope2Emissions_requiredMem_gCO2e`            |  Scope 2 emissions produced if only the required memory had been allocated. |
| `Scope2Emissions_failed_gCO2e`            |  Scope 2 emissions associated with the failed jobs only. |
| `TotalEmissions_gCO2e`            |  Total carbon emissions in gCO2e (scope 2 + scope 3). <br> This includes counter-based scope 2 emissions if energy coutners are available, <br> and usage-based estimates if they aren't. |



#### **Equivalents for User Interest**

These data are provided as approximate values intended to help contextualise the impact of the user's computational carbon footprint.
See the [Methodology](methodology.md) for sources and assumptions for these calculations.

| Column Name         | Description                                                                     |
|---------------------|---------------------------------------------------------------------------------|
| `Cost_GBP`            |  The approximate electricity cost (in British pounds) of running the job(s) <br> based on the value supplied in `hpc_config.yaml`. 
| `driving_miles`            |  The equivalent number of miles driven by an average UK car (miles). |
| `tree_absorption_months`            |  The months for one tree to absorb the total amount of CO2e produced (months). |
| `uk_houses_daily_emissions`            |  Equivalent number of UK household's daily emissions from electricity use. |
| `bris_paris_flights`            |  Equivalent number of flights from Bristol to Paris. |








