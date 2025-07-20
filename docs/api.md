# API Reference

The gracehpc package provides the following top-level functions for direct use in Python scripts or interactive Jupyter Notebook environments:

> *For using GRACE-HPC from the command-line, see [Command-line Interface](cli.md).*

---
## `gracehpc_run(args)`
<div style="border-left: 4px solid #2980b9; padding: 1em; background-color: #f0f8ff;">

<strong>Function:</strong> <code>gracehpc_run(StartDate, EndDate, JobIDs, Region, Scope3, CSV)</code><br>
<strong>Location:</strong> <code>gracehpc.script.gracehpc_run</code><br>
<strong>Usage:</strong> In Python scripts (.py) or Jupyter Notebooks (.ipynb)<br>
<strong>Returns:</strong> <code>`full_df`, `daily_df`, `total_df`</code> [pandas DataFames]. Outputs are also displayed in the terminal via rich console.

</div>

Runs the GRACE-HPC core engine calculating energy and emissions data using a set of arguments provided by the user.



---

## `jupyter_UI()`
<div style="border-left: 4px solid #2980b9; padding: 1em; background-color: #f0f8ff;">

<strong>Function:</strong> <code>jupyter_UI()</code><br>
<strong>Location:</strong> <code>gracehpc.jupyter.jupyter_UI</code><br>
<strong>Usage:</strong> In Jupyter Notebooks (.ipynb) only<br>
<strong>Returns:</strong> <code>results</code> [dict of 3 DataFrames]. Displays a full interactive interface, enabling users to input parameters through widgets and visualise plots immediately.

</div>

Launches an interactive dashboard-style interface inside a Jupyter Notebook for running GRACE-HPC with widgets, allowing users to repeatedly input parameters and visualise results without coding.





---





