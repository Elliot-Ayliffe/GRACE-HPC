# Configuration

Before running GRACE-HPC, you must generate and edit a configuration file named `hpc_config.yaml` that contains the hardware specification values 
associated with your HPC system. These include:

- Partition Names and their processor type (e.g. `CPU` or `GPU`)
- Processor Thermal Design Power `TDP` values 
- Power Usage Effectiveness `PUE` of the HPC system

After installation, run the following command in the terminal:

```bash 
gracehpc configure
```

This will generate a template `hpc_config.yaml` file in your current working directory.
Open this file, fill in the values replacing the placeholder entries `<...>`, and save the edited version.
This file **must remain in the working directory** to enable GRACE-HPC to run correctly.


> 💡 *We recommend contacting your HPC administrators to obtain accurate TDP values for your cluster*.
> *Alternatively, many common CPU and GPU TDP values can be found on the [Green Algorithms Online Calculator GitHub](https://github.com/GreenAlgorithms/green-algorithms-tool/tree/master/data/latest) provided by Dr Loïc Lannelongue.*


## Example hpc_config.yaml

Here is an example configuration file edited for **Isambard-AI**

```yaml
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
hpc_system: "Isambard-AI"         # (str)

# List the different partitions available on the cluster below with its hardware details (or at least the one you want to use)
partitions:                         

    # Example GPU partition 
    workq:               # For Isambard-AI, this would be workq.
        processor: GPU             
        processor_name: "NVIDIA H100 GPU"     # (str) Name of the GPU model. E.g. "NVIDIA H100 Tensor Core GPU"
        TDP: 700                          # (integer) The TDP of the whole GPU in watts.

        # For GPU partitions, you must also specify the details for supporting CPUs
        CPU_name: "NVIDIA Grace CPU"          # (str) Name of the CPU model 
        CPU_TDP: 3.472                        # (float) The TDP of the CPU per core in Watts.

    # Add additional partitions as needed, following the same structure as above.

### The tools backend does not use the processor names, so they do not affect the calculations.

# Power Usage Effectiveness (PUE) of the data centre/ facility (i.e. the data centre overhead)
PUE: 1.1                # (float) E.g. Isambard-AI has an estimated PUE of 1.1

# Average cost of electricity in GBP per kWh 
electricity_cost: 0.2573            # (float)  Average Cost of electricity in the UK (0.2573 GBP/kWh) - July 2025 - https://www.ofgem.gov.uk/information-consumers/energy-advice-households/energy-price-cap



# ----------------------------------------------------------------------------------------------------------------
# SOME HELPFUL TDP VALUES:
#
# NVIDIA GRACE CPU (Isambard 3): ~ 3.472 W per Core               - (250 W/ 72 cores) https://resources.nvidia.com/en-us-grace-cpu/data-center-datasheet?ncid=no-ncid
# NVIDIA H100 Tensor Core GPU (Isambard-AI): ~ 700 W per GPU (max) - https://resources.nvidia.com/en-us-hopper-architecture/nvidia-tensor-core-gpu-datasheet?ncid=no-ncid
# ----------------------------------------------------------------------------------------------------------------
```