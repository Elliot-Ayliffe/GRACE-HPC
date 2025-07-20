# FAQs & Development

## FAQs

- **Which HPC systems is GRACE-HPC compatible with?**

*In theory, GRACE-HPC should work on any HPC system that uses the SLURM workload manager and has access to job accounting data. However, this package has only been tested on Isambard 3 and Isambard-AI so far, therefore, you may encounter some bugs on other systems due to varying SLURM configurations.*

- **Where can I find the TDP values specific to my HPC cluster?**

*Thermal Design Power (TDP) values are sometimes tricky to find. We recommend you contact your HPC system administrators for the most accurate estimates. You should also explore the processor vendor documentation (e.g. [NVIDIA datasheet](https://resources.nvidia.com/en-us-grace-cpu/grace-hopper-superchip?ncid=no-ncid)). However be careful to use the maximum reported values, as administrators can limit their power draw. The [Green Algorithms](https://github.com/GreenAlgorithms/green-algorithms-tool/tree/master/data/latest) project provides many TDP values for common CPUs and GPUs.*

- **What should I do if I find a bug?**

*If you encounter a bug, please open an issue on the [GitHub Repository](https://github.com/Elliot-Ayliffe/GRACE-HPC/issues) with a description and relevant error messages. Contributions, feedback, and suggestions for improvement are welcome and enhance the tool for everyone.*

## Future Development 

