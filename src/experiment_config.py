from pathlib import Path

import simulator as sim


OUTPUT_DIR = Path("experiment_results")

BASE_SEED = 12345

U_LEVELS = [0.25, 0.50, 0.75]
TASK_COUNTS = [5, 10, 15, 20]

TASKSETS_PER_COMBINATION = 7
META_REPEATS = 2

TUNING_U_LEVELS = U_LEVELS
TUNING_TASK_COUNTS = TASK_COUNTS
TUNING_TASKSETS_PER_COMBINATION = 7
TUNING_META_REPEATS = 2

MAX_TASKSET_GENERATION_ATTEMPTS = 500

PROGRESS_EVERY = 25
TUNING_PROGRESS_EVERY = 25

LOG_DISCARDS = False


ENERGY_PROFILES = {
    "baseline": sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30),
    "expensive_wakeup": sim.EnergyModel(10.0, 3.0, 0.2, 160.0, 60),
    "shallow_sleep": sim.EnergyModel(10.0, 3.0, 0.8, 80.0, 40),
    "cheap_deep_sleep": sim.EnergyModel(10.0, 3.0, 0.05, 60.0, 20),
}


GA_CONFIGS = {
    "GA-1":  dict(population_size=20, generation_count=30, mutation_rate=0.02, elite_count=2, mutation_max_amount=100),
    "GA-2":  dict(population_size=20, generation_count=30, mutation_rate=0.03, elite_count=2, mutation_max_amount=250),
    "GA-3":  dict(population_size=20, generation_count=30, mutation_rate=0.05, elite_count=2, mutation_max_amount=500),
    "GA-4":  dict(population_size=30, generation_count=30, mutation_rate=0.03, elite_count=2, mutation_max_amount=250),
    "GA-5":  dict(population_size=30, generation_count=30, mutation_rate=0.05, elite_count=2, mutation_max_amount=500),
    "GA-6":  dict(population_size=30, generation_count=30, mutation_rate=0.08, elite_count=2, mutation_max_amount=500),
    "GA-7":  dict(population_size=50, generation_count=30, mutation_rate=0.03, elite_count=2, mutation_max_amount=250),
    "GA-8":  dict(population_size=50, generation_count=30, mutation_rate=0.05, elite_count=2, mutation_max_amount=500),
    "GA-9":  dict(population_size=50, generation_count=30, mutation_rate=0.08, elite_count=4, mutation_max_amount=500),
    "GA-10": dict(population_size=60, generation_count=30, mutation_rate=0.05, elite_count=4, mutation_max_amount=500),
}


SA_CONFIGS = {
    "SA-1":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=3, max_move_amount=50),
    "SA-2":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=5, max_move_amount=50),
    "SA-3":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=8, max_move_amount=50),
    "SA-4":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=3, max_move_amount=100),
    "SA-5":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=5, max_move_amount=100),
    "SA-6":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=8, max_move_amount=100),
    "SA-7":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=3, max_move_amount=250),
    "SA-8":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=5, max_move_amount=250),
    "SA-9":  dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=8, max_move_amount=250),
    "SA-10": dict(T=1000000, T_delta=0.95, T_min=50, rep_per_sched=5, max_move_amount=500),
}


PSO_CONFIGS = {
    "PSO-1":  dict(particle_count=20, informant_count=3, iteration_count=35),
    "PSO-2":  dict(particle_count=20, informant_count=5, iteration_count=35),
    "PSO-3":  dict(particle_count=20, informant_count=8, iteration_count=35),
    "PSO-4":  dict(particle_count=30, informant_count=3, iteration_count=35),
    "PSO-5":  dict(particle_count=30, informant_count=5, iteration_count=35),
    "PSO-6":  dict(particle_count=30, informant_count=8, iteration_count=35),
    "PSO-7":  dict(particle_count=40, informant_count=3, iteration_count=35),
    "PSO-8":  dict(particle_count=40, informant_count=5, iteration_count=35),
    "PSO-9":  dict(particle_count=50, informant_count=8, iteration_count=35),
    "PSO-10": dict(particle_count=60, informant_count=5, iteration_count=35),
}


OPTIMIZER_CONFIGS = {
    "GA": GA_CONFIGS,
    "SA": SA_CONFIGS,
    "PSO": PSO_CONFIGS,
}