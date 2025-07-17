""" 
config.py

Author: Elliot Ayliffe
Student ID: 2046374
Date: 11/07/25

Contains a function to generate a configuration file containing required HPC system details 
for the user to fill in before using the GRACE-HPC tool.
"""

# Import libraries 
import os 
import yaml 

def generate_config_file():
    """
    Generates and saves a template hpc_config.yaml file in the user's current working directory.
    The user must fill in this file with their specific HPC system's configuration details before using the tool.
    Edit the placeholder values (e.g. the values inside < > ) with their actual HPC system details.
    If the file already exists a new one is not created. To use the tool, the user must have correctly
    filled in this file and kept it in the same directory.
    """
    config_file = "hpc_config.yaml"

    # Check that the file does not already exist
    if os.path.exists(config_file):
        print(f"⚠️   {config_file} already exists in the current directory (no new file created). Ensure you have filled it in with your HPC system details before using the tool.")
        return
    
    # Create the configuration file template
    template = """\
# ----------------------------------------------------------------------------------------------------------------
# GRACE-HPC CONFIGURATION FILE
# ----------------------------------------------------------------------------------------------------------------
#
# This file must be edited by the user to include their specific HPC system details before using the GRACE-HPC tool.
# Please replace all placeholders enclosed in < > with the best estimates for your HPC cluster specifications (e.g. Isambard 3, Isambard-AI etc...)
# Remove all < > brackets after filling in the values.
# See the documentation for an example configuration file (hpc_config.yaml) with the correct format.



---
# The name of your HPC system (e.g. "Isambard 3", "Isambard-AI")
hpc_system: "<HPC System Name>"         # (str)

# List the different partitions available on the cluster below with its hardware details (or at least the one you want to use)
partitions:                         

    # Example CPU partition 
    <Partition1_Name>:               # E.g. For Isambard 3, this would be grace. For Isambard-AI, comment out this partition and use the GPU partition template below.
        processor: <CPU>             # Is the partition CPU or GPU based? E.g. Isambard 3 = CPU, Isambard-AI = GPU, Archer2 = CPU 
        processor_name: "<NVIDIA Grace CPU>"    # (str) The model name of the processor. E.g. "NVIDIA Grace CPU" 
        TDP: <5>                     # (float) The thermal design power (TDP) of the processor per core in Watts. (CPU)

    # Example GPU partition 
    <Partition2_Name>:               # For Isambard-AI, this would be workq.
        processor: <GPU>             
        processor_name: "<NVIDIA H100 GPU>"     # (str) Name of the GPU model. E.g. "NVIDIA H100 Tensor Core GPU"
        TDP: <500>                          # (integer) The TDP of the whole GPU in watts.

        # For GPU partitions, you must also specify the details for supporting CPUs
        CPU_name: "<NVIDIA Grace CPU>"          # (str) Name of the CPU model 
        CPU_TDP: <5>                        # (float) The TDP of the CPU per core in Watts.

    # Add additional partitions as needed, following the same structure as above.

### The tools backend does not use the processor names, so they do not affect the calculations.

# Power Usage Effectiveness (PUE) of the data centre/ facility (i.e. the data centre overhead)
PUE: <1.1>                # (float) E.g. Isambard-AI has an estimated PUE of 1.1

# Average cost of electricity in GBP per kWh 
electricity_cost: 0.2573            # (float)  Average Cost of electricity in the UK (0.2573 GBP/kWh) - July 2025 - https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap





# ----------------------------------------------------------------------------------------------------------------
# SOME HELPFUL TDP VALUES:
#
# NVIDIA GRACE CPU (Isambard 3): ~ 3.472 W per Core               - (250 W/ 72 cores) https://resources.nvidia.com/en-us-grace-cpu/data-center-datasheet?ncid=no-ncid
# NVIDIA H100 Tensor Core GPU (Isambard-AI): ~ 700 W per GPU (max) - https://resources.nvidia.com/en-us-hopper-architecture/nvidia-tensor-core-gpu-datasheet?ncid=no-ncid
# ----------------------------------------------------------------------------------------------------------------


"""
    # Write the config file 
    with open(config_file, "w") as f:
        f.write(template)

    print(f"✅ {config_file} saved in your current directory. Please edit the placeholders < > accordingly following the guidance given in the file. Input your specific HPC system details before using the tool.")


if __name__ == "__main__":
    generate_config_file()