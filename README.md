
![GRACE-HPC logo](docs/logo.png)



# About GRACE-HPC

`gracehpc` is a lightweight Python package designed to enable users and operators of SLURM-based HPC systems to estimate and analyse the carbon footprint of their computational workloads. It calculates and displays **energy consumption, Scope 2 (operational)** and **Scope 3 (embodied)** carbon emissions for your jobs ran on the system, using SLURM accounting logs and user-specified parameters.

The package is designed to work on any HPC system that uses SLURM as workload manager, however, it has only been tested on Isambard-AI and Isambard 3 at these early stages.

## Documentation 

For a complete guide to the methodology, installation, and usage of GRACE-HPC, please visit the [**Official Documentation here**](https://grace-hpc.readthedocs.io/en/latest/).

# How to use it?

The package prioritises user experience, accessibility, and flexibility by offering three usage modes designed to accommodate a wide range of users.

1. **Command-line Interface**

The tool can be used directly from the command line of your HPC system with simple commands and a wide range of arguments. Ideal for quick analyses for users more comfortable with a lower-level interface and output.

2. **Python Function Call**

The same core engine can be called via a function in a Python Script (.py) or a Jupyter Notebook (.ipynb). This mode is ideal for workflow integration and automation, allowing the tool to be embedded into larger Python applications. It also returns the raw datasets produced by the tool for further exploration and user-led analysis afterwards. If you want flexibility, this is the mode for you.

3. **Interactive Jupyter Interface**

A simple, widget-based interface can be launched from a Jupyter Notebook (.ipynb) displaying a rich output containing HTML text boxes and interactive plots. This mode allows users to experiment with different parameters without any coding, visualising interesting plots instantly within a single .ipynb notebook. Ideal for users wanting a higher-level, interactive experience.


# Features 

- **Flexible Job Selection:** Specify a date range to process jobs for, individual Job IDs, or both.
<br>

- **Job Log Extraction:** Extracts and processes job details (such as runtime, resource allocation, and usage) using SLURM's sacct command.
<br>

- **Energy Consumption:** Calculates energy consumption using both usage data and system energy counters (if available).
<br>

- **Scope 2 Emissions:** Estimates scope 2 (operational) emissions produced by the jobs using **real-time, region-specific carbon intensity data** from the [National Grid ESO Carbon Intensity API](https://carbonintensity.org.uk).
<br>

- **Scope 3 Emissions:** Includes Scope 3 (embodied) emissions estimates for a few HPC systems that have undergone a lifecycle assessment and calculated a per node-hour scope 3 emissions factor (Isambard 3, Isambard-AI, Archer 2).
<br>

- **Contextual Equivalents:** Results include CO₂e equivalents such as the driving, tree-months and flying to help users interpret and understand the scale of the environmental impact.
<br>

- **Rich Output Options:** View results in the terminal, export to CSV, load as DataFrames, or display interactively in notebooks with instant plots.
<br>

The overall goal of this tool is not to serve as a definitive energy and carbon cluster monitoring tool, but rather to provide accessible estimates that inform and raise awareness about the environmental impact of HPC workloads - promoting more sustainable, carbon-aware practices.
