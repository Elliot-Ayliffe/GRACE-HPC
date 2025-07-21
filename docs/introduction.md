# Introduction 

## Motivation 

High-Performance Computing (HPC) plays a crucial role in modern scientific research and technological developments. From modelling the Earth's climate and exploring the universe to accelerating drug development and training large machine learning solutions, HPC makes it possible to tackle problems that require substantial computational power. The recent surge in large-scale Artificial Intelligence has accelerated demand for HPC resources and therefore, supercomputing systems are being utilised more intensively than ever before.

> 🕷️**However, with great computational power comes great energy consumption!**

HPC is inherently energy intensive, as performing parallel workloads across large sets of CPUs and GPUs require significant electricity. Depending on the national grid's energy mix, this can result in major greenhouse gas (GHG) emissions. These emissions are not limited to those produced during operational use (Scope 2) but also include embodied emissions (Scope 3) from the manufacturing and lifecycle of the hardware. Without intervention, data centres and HPC facilities are projected to contribute up to 8% of global GHG emissions by 2030 ([Cao et al. 2022](https://arxiv.org/pdf/2110.09284)). For this reason, it is important to find ways to accurately measure and manage this environmental impact to help inform effective decarbonisation strategies for HPC.

Although awareness of computing's environmental impact is increasing, efforts to comprehensively quantify the carbon footprint of HPC usage at job-level remain limited. Very few studies account for both Scope 2 and Scope 3 emissions in their total carbon estimates. Even fewer user-friendly software tools exist that enable users to easily calculate, understand and mitigate their computational carbon footprint. Developing such tools and methodologies makes the environmental cost of HPC usage both visible and actionable, supporting a more transparent and sustainable future of HPC.



## Terminology