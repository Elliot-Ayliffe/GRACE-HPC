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

#### **System Energy Counters**

`gracehpc` has been programmed to use system energy counters if they are available on your specific HPC cluster. These energy use values are returned in the `ConsumedEnergyRaw` sacct field.

`ConsumedEnergyRaw`: Total energy consumed by all tasks in a job, in joules. 

See the [**acct_gather.conf**](https://slurm.schedmd.com/acct_gather.conf.html) documentation for more details on the type of plugins available and how they are configured.

#### **Usage-based Energy Estimates**

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
- $\text{PUE}$ = Power Usage Effectiveness of the data centre











## Scope 2 Emissions 















## Scope 3 Emissions










