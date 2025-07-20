# API Reference

The gracehpc package provides the following top-level functions for direct use in Python scripts or interactive Jupyter Notebook environments:

> *For using GRACE-HPC from the command-line, see [Command-line Interface](cli.md).*

---

<div style="border-left: 4px solid #2980b9; padding: 1em; background-color: #f0f8ff;">
## `gracehpc_run(args)`

!!! info "Function: gracehpc_run(StartDate, EndDate, JobIDs, Region, Scope3, CSV)"
    **Location:** `gracehpc.script.gracehpc_run`
    **Usage:** In Python scripts (.py) or Jupyter Notebooks (.ipynb)
    **Returns:** `full_df`, `daily_df`, `total_df`. Outputs are also displayed terminal via rich console.
</div>
---

## `jupyter_UI()`

!!! info "Function: jupyter_UI()"
    **Location:** `gracehpc.script.gracehpc_run`
    **Usage:** In Jupyter Notebooks (.ipynb) only
    **Returns:** `results`. Displays a full interactive interface, enabling users to input parameters through widgets and visualise plots immediately.



