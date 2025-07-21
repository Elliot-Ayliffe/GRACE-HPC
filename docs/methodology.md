# Methodology 

This page outlines the methodology and assumptions used by the `gracehpc` backend to pull job data, estimate energy consumption and calculate scope 2 and scope 3 emissions.


## Pull Job Data

1. **Extracting Accounting Logs Using *sacct***

Job accounting data is retrieved using the SLURM `sacct` command. The following command is used to extract over the specified date range:

```bash
sacct --start <StartDate> --end <EndDate> \
   --format UID,USER,Partition,JobID,JobName,Submit,State,Elapsed,AllocTRES, \ 
            NNodes,NCPUS,TotalCPU,CPUTime,ReqMem,MaxRSS,WorkDir,ConsumedEnergyRaw
```








## Energy Consumption

















## Scope 2 Emissions 















## Scope 3 Emissions










