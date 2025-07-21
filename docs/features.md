# About GRACE-HPC

## What is GRACE-HPC?

`gracehpc` is a lightweight Python package designed to enable users and operators of SLURM-based HPC systems to estimate and analyse the carbon footprint of their computational workloads. It calculates and displays **energy consumption, Scope 2 (operational)** and **Scope 3 (embodied)** carbon emissions for your jobs ran on the system, using SLURM accounting logs and user-specified parameters.

The package is designed to work on any HPC system that uses SLURM as workload manager, however, it has only been tested on Isambard-AI and Isambard 3 at these early stages. See the [FAQs](faqs.md) for more information.

## How to use it?

The package prioritises user experience, accessibility, and flexibility by offering three usage modes designed to accommodate a wide range of users.

1. [**Command-line Interface**](cli.md)

The tool can be used directly from the command line of your HPC system with simple commands and a wide range of arguments. Ideal for quick analyses for users more comfortable with a lower-level interface and output.

2. [**Python Function Call**](function.md)

The same core engine can be called via a function in a Python Script (.py) or a Jupyter Notebook (.ipynb). This mode is ideal for workflow integration and automation, allowing the tool to be embedded into larger Python applications. It also returns the raw datasets produced by the tool for further exploration and user-lead analysis afterwards. If you want flexibility, this is the mode for you.

3. [**Interactive Jupyter Interface**](jupyter.md)

A simple, widget-based interface can be launched from a Jupyter Notebook (.ipynb) displaying a rich output containing HTML text boxes and interactive plots. This mode allows users to experiment with different parameters without any coding, visualising interesting plots instantly within a single .ipynb notebook. Ideal for users wanting a higher-level, interactive experience.


## Features 

- **Flexible Job Selection:** Specify a date range to process jobs for, individual Job IDs, or both.

