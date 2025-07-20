# API Reference

The `gracehpc` package provides the following top-level functions for direct use in Python scripts or interactive jupyter notebook environments:

> *For using GRACE-HPC from the command-line, see [Command-line Interface](cli.md).*

---

## `gracehpc_run(args)`

!!! info "Function: gracehpc_run(StartDate, EndDate, JobIDs, Region, Scope3, CSV)"
    **Location:** `gracehpc.script.gracehpc_run`
    **Usage:** In Python scripts (.py) or Jupyter Notebooks (.ipynb)
    **Returns:** `full_df`, `daily_df`, `total_df`. Outputs are also displayed terminal via rich console.

---

## `jupyter_UI()`

!!! info "Function: jupyter_UI()"
    **Location:** `gracehpc.script.gracehpc_run`
    **Usage:** In Jupyter Notebooks (.ipynb) only
    **Returns:** `results`. Displays a full interactive interface, enabling users to input parameters through widgets and visualise plots immediately.
     


