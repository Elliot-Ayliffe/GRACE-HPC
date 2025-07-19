# Command-line Interface (CLI)

Now that the configuration file has been editted and saved, you can run `GRACE-HPC` from the command-line to calculate the energy use and carbon footprint of your HPC jobs:

```bash
gracehpc run [ARGUMENT OPTIONS]
```
Running this command without any options will execute the analysis with **default values** for all arguments specified below.

## Argument Options

You can customise the output with many arguments and options to enhance the carbon footprint analysis:

```bash
usage: gracehpc run [-h] [--StartDate STARTDATE] [--EndDate ENDDATE] [--JobIDs JOBIDS] <br>
                    [--Region REGION] [--Scope3 SCOPE3] [--CSV CSV]
```