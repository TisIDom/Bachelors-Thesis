# Bachelors-Thesis

Code used for my bachelor's thesis experiments on energy-aware real-time task scheduling. The repository contains the simulator, RMS/EDF/PH schedulers, GA/SA/PSO offset optimizers, and scripts for running experiments.

## Running experiments

Experiment settings are in `/src/experiment_config.py`.

Change this file if you want to change things like task counts, utilization levels, number of tasksets, metaheuristic repeats, energy profiles, or optimizer configurations.

To run the tuning stage:
```bash
python /src/run_experiment.py --run tuning --clear
```

This tests the GA, SA and PSO parameter configurations and writes the output to the experiment results folder - /src/experiment_results/

Main files created by the tuning stage:
results.csv - energy, wakeups, deadline misses, optimization time and offsets for each tested configuration
tasksets.csv - generated task sets used in the experiments
convergence.csv - metaheuristic progress by iteration/evaluation
best_configs.json - selected GA, SA and PSO configurations for the final comparison

To recreate the final comparison results:
```bash
python /src/run_experiment.py --run comparison --clear
```

This uses best_configs.json and compares RMS, EDF, PH, GA, SA and PSO.

The final results are written to:
/src/experiment_results/results.csv

Each row contains the method, taskset information, energy profile, total energy, active/idle/sleep time, wakeups, deadline misses, optimization time and the used offsets.
