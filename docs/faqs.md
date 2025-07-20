# FAQs & Development

## FAQs

- **Which HPC systems is GRACE-HPC compatible with?**

*In theory, GRACE-HPC should work on any HPC system that uses the SLURM workload manager and has access to job accounting data. However, this package has only been tested on Isambard 3 and Isambard-AI so far, therefore, you may encounter some bugs on other systems due to varying SLURM configurations. The tool could be adapted to work for other workload managers by modifying the [job_log_manger.py](https://github.com/Elliot-Ayliffe/GRACE-HPC/blob/main/gracehpc/core/job_log_manager.py) and [backend_utils.py](https://github.com/Elliot-Ayliffe/GRACE-HPC/blob/main/gracehpc/core/backend_utils.py) scripts.*

- **Where can I find the TDP values specific to my HPC cluster?**

*Thermal Design Power (TDP) values are sometimes tricky to find. We recommend you contact your HPC system administrators for the most accurate estimates. You should also explore the processor vendor documentation (e.g. [NVIDIA datasheet](https://resources.nvidia.com/en-us-grace-cpu/grace-hopper-superchip?ncid=no-ncid)). However be careful to use the maximum reported values, as administrators can limit their power draw. The [Green Algorithms](https://github.com/GreenAlgorithms/green-algorithms-tool/tree/master/data/latest) project provides many TDP values for common CPUs and GPUs.*

- **What should I do if I find a bug?**

*If you encounter a bug, please open an issue on the [GitHub Repository](https://github.com/Elliot-Ayliffe/GRACE-HPC/issues) with a description and relevant error messages. Contributions, feedback, and suggestions for improvement are welcome and enhance the tool for everyone.*

## Future Development 

Additional features to consider if we had more time:

- **Advanced Job Filtering:** Allow filtering by the `Account` *sacct* field and working directory in addition to Job IDs. The `Account` field in SLURM corresponds to the project or billing code the job is charged to. It is used as an identifier to track usage across different projects or research groups. 

- **Carbon-aware Scheduling tool:** Implementation of a job scheduling recommendation tool that provides advice on when to run jobs during low carbon intensity windows. It could be linked up to the 48 hour forecasts provided by the [NESO carbon intensity API](https://carbon-intensity.github.io/api-definitions/#carbon-intensity-api-v2-0-0) informing users of the best submission times to minimise their operational carbon emissions.

- **Decarbonisation Strategies:** Provide tailored decarbonisation strategies and advice so users can make an effort to reduce their computational carbon footprint.