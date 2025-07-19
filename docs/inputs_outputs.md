# Inputs & Outputs

Before using the tool, it would be helpful to define all the **input arguments** available to the user to enrich their estimations and the **final outputs** (columns of the returned datasets).

## Input Arguments 

| Parameter            | Description                                                                                                                                                             |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `project_name`       | Name of the project, defaults to `codecarbon`.                                                                                                                          |
| `experiment_id`      | ID of the experiment.                                                                                                                                                    |
| `measure_power_secs` | Interval (in seconds) to measure hardware power usage, defaults to `15`.                                                                                                |
| `tracking_mode`      | `machine` – measure the power consumption of the entire machine (default).  <br> `process` – try to isolate the tracked processes.                                      |
| `gpu_ids`            | User-specified known GPU IDs to track, defaults to `None`.                                                                                                               |
| `log_level`          | Global CodeCarbon log level (by verbosity): `debug`, `info` (default), `warning`, `error`, or `critical`.                                                              |
| `co2_signal_api_token` | API token for co2signal.com (requires sign-up for free beta).                                                                                                        |
| `pue`                | PUE (Power Usage Effectiveness) of the data center where the experiment is being run.      