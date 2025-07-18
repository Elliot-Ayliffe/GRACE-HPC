# Installation

## Virtual Environments

Create a virtual environment on your SLURM-based HPC system using either `conda` or `python -m venv`, with Python 3.11 or 3.12.
For Isambard systems follow the [Isambard documentation](https://docs.isambard.ac.uk/user-documentation/guides/python/) for more detailed guidance on setting up environments.

For example, using Conda on the command line, create and activate your virtual environment:

```bash
conda create -n ghpc_env python=3.11
conda activate ghpc_env
```

## From PyPI

The package can be installed from the `PyPI` repository ([here](https://pypi.org)) with `pip` by running the following command in the terminal:

```bash
pip install gracehpc
```

## From Source

Alternatively, install the package directly from GitHub:

```bash 
pip install git+https://github.com/Elliot-Ayliffe/GRACE-HPC.git
```

## Dependencies 

The following packages are required for `gracehpc` and will be installed automatically:

```bash 
pandas
ipykernel
numpy
pyyaml
requests
pytz
ipython
ipywidgets
plotly
rich,
jupyterlab
notebook
widgetsnbextension
jupyter
```
See [pyproject.toml](https://github.com/Elliot-Ayliffe/GRACE-HPC/blob/main/pyproject.toml) for the specific versions.


## Double Check

Confirm that `gracehpc` has installed correctly by running the following command:

```bash 
gracehpc --help
```

An introduction message should appear:

```bash
usage: gracehpc [-h] {configure,run} ...

 

GRACE-HPC: A Green Resource for Assessing Carbon & Energy in HPC.

This tool estimates the energy consumption, scope 2 and scope 3 carbon emissions of your SLURM HPC jobs.
If energy counters are available, it will use them. Otherwise it will estimate energy and emissions from usage statistics. 

positional arguments:
  {configure,run}  Subcommands
    configure      Generate and save the HPC cluster configuration file. Fill in the YAML file with your HPC configuration details before using the tool.
    run            Run the full engine to estimate the carbon footprint (scope 2 and scope 3) of your SLURM HPC jobs.

options:
  -h, --help       show this help message and exit

 

Carbon intensity for scope 2 emissions (operational) is retrieved from the regional Carbon Intensity API (carbonintensity.org.uk.) at the time of job submission. 
Scope 3 emissions (embodied) are estimated from the node-hours used by the job, and the scope 3 emissions factor. 
For Isambard systems and Archer2, these scope 3 factors are calculated from the total lifecycle scope 3 emissions for each system divided by the total node-hours available over the system's projected lifetime.
```

