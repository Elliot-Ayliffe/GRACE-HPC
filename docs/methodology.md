# Methodology 

This page outlines the methodology and assumptions used by the `gracehpc` backend to pull job data, estimate energy consumption and calculate scope 2 and scope 3 emissions.


## Pull Job Data

- **Extracting Accounting Logs Using *sacct***

Job accounting data is retrieved using the SLURM `sacct` command. The following command is used to extract over the specified date range:

```bash
sacct --start <StartDate> --end <EndDate> \
   --format UID,USER,Partition,JobID,JobName,Submit,State,Elapsed,AllocTRES, \ 
            NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,ConsumedEnergyRaw
```

Visit the [**SLURM Documentation**](https://slurm.schedmd.com/sacct.html) for details on each field.

This raw accounting data is then parsed and processed into usable formats to enable downstream calculations and returnable numeric data. 


## Energy Consumption

#### System Energy Counters

`gracehpc` has been programmed to use system energy counters if they are available on your specific HPC cluster. These energy use values are returned in the `ConsumedEnergyRaw` sacct field.

`ConsumedEnergyRaw`: Total energy consumed by all tasks in a job, in joules. 

See the [**acct_gather.conf**](https://slurm.schedmd.com/acct_gather.conf.html) documentation for more details on the type of plugins available and how they are configured.

#### Usage-based Energy Estimates

As energy counters are not always available on HPC systems, `gracehpc` also implements an approximate energy consumption calculation that incorporates resource usage data and known hardware power draw (TDP values).

Formula:

$$
E_{\text{compute}} = (T_{\text{CPU}} \cdot P_{\text{CPU}}) + (T_{\text{GPU}} \cdot P_{\text{GPU}}) + (T_{\text{elapsed}} \cdot P_{\text{mem}})
$$

$$
E_{\text{total}} = E_{\text{compute}} \cdot \text{PUE}
$$

Where:

- $E_{\text{compute}}$ = Total compute energy use 
- $T_{\text{CPU}}$ = CPU usage time 
- $P_{\text{CPU}}$ = CPU power draw (TDP)
- $T_{\text{GPU}}$ = GPU usage time
- $P_{\text{GPU}}$ = GPU power draw (TDP)
- $T_{\text{elapsed}}$ = Total elapsed runtime 
- $P_{\text{mem}}$ = Memory power draw (based on power per GB)
- $E_{\text{total}}$ = Total energy consumed including the data center overhead
- $\text{PUE}$ = Power Usage Effectiveness of the data centre - quantifies the extra energy needed to operate the data center (e.g. lighting, cooling)




## Scope 2 Emissions 

Scope 2 emissions are calculated using the energy consumed and the carbon intensity of producing this energy at a specified region.

$$
\text{S2} = E_{\text{total}} \cdot \text{CI}
$$

Where:

- $\text{S2}$ = Operational carbon emissions in *gCO2e*
- $E_{\text{total}}$ = Total energy consumed in *kWh*
- $\text{CI}$ = Carbon intensity of electricity consumed in *gCO2e/kWh*

#### Carbon Intensity Source

If the user specifies a region corresponding to their HPC system's location,  real-time national grid carbon intensity values are retrieved via the [NESO Carbon Intensity API](https://carbonintensity.org.uk). These values, matched to each job's submission time, enable more accurate and region-specific Scope 2 estimates - assuming the HPC system draws power from the national grid.

If a region is not specified, the [2024 UK average carbon intensity](https://www.carbonbrief.org/analysis-uks-electricity-was-cleanest-ever-in-2024/)is used: `124 gCO₂/kWh`




## Scope 3 Emissions

Scope 3 emissions can be calculated for 3 HPC systems: **Isambard 3**, **Isambard-AI**, and [**Archer 2**](https://docs.archer2.ac.uk/user-guide/energy/). These have undergone lifecycle assessments estimating a per node-hour scope 3 emissions factor. These factors are calculated from the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime. GRACE-HPC estimates the embodied emissions for each job based on node usage and job duration.

Per node-hour scope 3 emissions:

- **Isambard 3:** `43 gCO₂e / node-hour`
- **Isambard-AI:** `114 gCO₂e / node-hour`
- [**Archer 2:**](https://docs.archer2.ac.uk/user-guide/energy/) `23 gCO₂e / node-hour`

Formula:

$$
\text{S3} = \text{NH} \cdot \text{EF}
$$

Where:

- $\text{S3}$ = Embodied carbon emissions for the job(s) in *gCO2e*
- $\text{NH}$ = Node-Hours consumed by the job(s)
- $\text{EF}$ = Scope 3 emissions factor in *gCO₂e/node-hour*

You can input a custom per node-hour scope 3 factor for other HPC systems if the appropriate analyses have been done and the data is available.


## Contextual Equivalents

To help users better understand and contextualise the impact of their HPC carbon footprint, GRACE-HPC provides several real-world equivalents. These translate raw carbon emissions values into more relatable terms and are intended solely for **informational purposes**.

Formula:

$$
\text{Equivalent unit} = \frac{\text{Total Emissions (gCO₂)}}{\text{Emissions Factor (CO₂/unit)}}
$$

#### Driving
Equivalent number of miles driven in an average UK petrol/diesel car.

- **Value used:** 211.2 gCO₂e/mile 
- **Source:** [UK average car CO₂ emissions (2023) - NimbleFins](https://www.nimblefins.co.uk/average-co2-emissions-car-uk#nogo)


#### Tree-Months
Number of months it would take a single mature tree to absorb the CO₂ emitted.

- **Value used:** 833 gCO₂e/month - based on 10 kgCO₂e per year
- **Source:** [One Tree Planted](https://onetreeplanted.org/blogs/stories/how-much-co2-does-tree-absorb?srsltid=AfmBOopRTUnD98_burqqG8JqB93xk9VGxHDDes7QyZj0p-OMyvQSgJsG)


#### Household Daily Electricity Use
Equivalent to the daily electricity emissions of this number of average UK households.

- **Values used:** 7.397 kWh/day & UK average carbon intensity in 2024 (124 gCO₂e/kWh)
- **Source:** [Ofgem - 2700kWh/year average](https://www.ofgem.gov.uk/average-gas-and-electricity-usage)

#### Bristol-Paris Flights
Equivalent number of one-way passenger flights from Bristol to Paris.

- **Value used:** 141700 gCO₂e/flight (per passenger)
- **Source:** [Curb6](https://curb6.com/footprint/flights/bristol-brs/paris-cdg)







