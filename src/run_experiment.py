import argparse
import copy
import csv
import hashlib
import json
import random
import statistics
import time

import task_generator as t_gen
import simulator as sim
import schedulers as sched
import experiment_config as cfg


cfg.OUTPUT_DIR.mkdir(exist_ok=True)

RESULTS_CSV = cfg.OUTPUT_DIR / "results.csv"
TASKSETS_CSV = cfg.OUTPUT_DIR / "tasksets.csv"
CONVERGENCE_CSV = cfg.OUTPUT_DIR / "convergence.csv"
BEST_CONFIGS_JSON = cfg.OUTPUT_DIR / "best_configs.json"


RESULT_FIELDS = [
    "phase", "U", "n", "taskset_id", "profile", "method", "offset_scenario", "config_name", "repeat", "total_energy", "active_time", "idle_time", 
    "sleep_time", "wakeups", "deadline_misses", "runtime_s", "optimization_time_s", "best_offsets", "H", "Dmax", "evaluate_start", "evaluate_stop",
]

TASKSET_FIELDS = [
    "U", "n", "taskset_id", "generation_attempt", "task_id", "C", "D", "T", "offset", "offsets_by_scenario",
]

CONVERGENCE_FIELDS = [
    "phase", "U", "n", "taskset_id", "profile", "config_name", "repeat", "optimizer", "iteration", "algorithm_step", 
    "temperature", "evaluations", "elapsed_s", "iteration_best_objective", "best_objective", "best_offsets",
]


def stable_seed(*parts):
    text = "|".join(str(x) for x in parts)
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def seconds_text(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}min"
    return f"{seconds / 3600:.2f}h"


def progress(name, done, total, start_time, every):
    if done % every == 0 or done == total:
        print(f"{name}: {done}/{total} | elapsed={seconds_text(time.perf_counter() - start_time)}", flush=True)


def write_row(path, fields, row):
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()

    out = {field: row.get(field, "") for field in fields}

    if isinstance(out.get("best_offsets"), list):
        out["best_offsets"] = json.dumps(out["best_offsets"])

    if isinstance(out.get("offsets_by_scenario"), dict):
        out["offsets_by_scenario"] = json.dumps(out["offsets_by_scenario"])

    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writerow(out)


def set_offsets(taskset, offsets):
    for task, offset in zip(taskset.taskset, offsets):
        task.offset = int(offset)


def evaluate_scheduler(taskset, method, energy_model):
    H = taskset.get_hyperperiod()
    Dmax = max(task.D for task in taskset.taskset)

    evaluate_start = H
    evaluate_stop = 2 * H
    release_window = evaluate_stop
    simulation_horizon = evaluate_stop + Dmax

    if method == "RMS":
        scheduler = sched.RMSScheduler(taskset.taskset)
    elif method == "EDF":
        scheduler = sched.EDFScheduler(taskset.taskset)
    else:
        scheduler = sched.PHScheduler(taskset.taskset)

    simulator = sim.Simulator()

    start = time.perf_counter()
    sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
    runtime_s = time.perf_counter() - start

    energy = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)

    return {
        **energy, "deadline_misses": len(sim_res.deadline_misses), "runtime_s": runtime_s, "optimization_time_s": 0.0, "best_offsets": [int(task.offset) for task in taskset.taskset],
        "H": H, "Dmax": Dmax, "evaluate_start": evaluate_start, "evaluate_stop": evaluate_stop,
    }


def evaluate_optimizer(taskset, optimizer_name, config, energy_model, trace_context=None):
    H = taskset.get_hyperperiod()
    Dmax = max(task.D for task in taskset.taskset)

    evaluate_start = H
    evaluate_stop = 2 * H
    release_window = evaluate_stop
    simulation_horizon = evaluate_stop + Dmax

    base_scheduler = sched.RMSScheduler(taskset.taskset)

    trace_file = None
    trace_writer = None

    if trace_context is not None:
        if not CONVERGENCE_CSV.exists() or CONVERGENCE_CSV.stat().st_size == 0:
            with CONVERGENCE_CSV.open("w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=CONVERGENCE_FIELDS).writeheader()

        trace_file = CONVERGENCE_CSV.open("a", newline="", encoding="utf-8")
        trace_writer = csv.DictWriter(trace_file, fieldnames=CONVERGENCE_FIELDS)

    start = time.perf_counter()

    try:
        if optimizer_name == "GA":
            optimizer = sched.GAOptimizer()
            sim_res, best_offsets, _ = optimizer.optimize(
                taskset, base_scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop,
                population_size=config["population_size"], generation_count=config["generation_count"],
                mutation_rate=config["mutation_rate"], elite_count=config["elite_count"],
                mutation_max_amount=config["mutation_max_amount"], trace_writer=trace_writer, trace_context=trace_context,
            )

        elif optimizer_name == "SA":
            optimizer = sched.SAOptimizer()
            sim_res, best_offsets, _ = optimizer.optimize(
                taskset, base_scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop,
                T=config["T"], T_delta=config["T_delta"], T_min=config["T_min"], rep_per_sched=config["rep_per_sched"],
                max_move_amount=config["max_move_amount"], trace_writer=trace_writer, trace_context=trace_context,
            )

        else:
            optimizer = sched.PSOOptimizer()
            sim_res, best_offsets, _ = optimizer.optimize(
                taskset, base_scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop,
                particle_count=config["particle_count"], informant_count=config["informant_count"],
                iteration_count=config["iteration_count"], trace_writer=trace_writer, trace_context=trace_context,
            )

    finally:
        if trace_file is not None:
            trace_file.close()

    optimization_time_s = time.perf_counter() - start
    best_offsets = [int(x) for x in best_offsets]
    set_offsets(taskset, best_offsets)

    energy = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)

    return {
        **energy, "deadline_misses": len(sim_res.deadline_misses), "runtime_s": 0.0, "optimization_time_s": optimization_time_s, "best_offsets": best_offsets, "H": H, 
        "Dmax": Dmax, "evaluate_start": evaluate_start, "evaluate_stop": evaluate_stop,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=["tuning", "comparison"], required=True)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.clear:
        RESULTS_CSV.unlink(missing_ok=True)
        TASKSETS_CSV.unlink(missing_ok=True)
        CONVERGENCE_CSV.unlink(missing_ok=True)

        if args.run == "tuning":
            BEST_CONFIGS_JSON.unlink(missing_ok=True)

    start_total = time.perf_counter()

    print(f"Run mode: {args.run}")
    print("Generating tasksets...")

    all_tasksets = []
    taskset_total = len(cfg.U_LEVELS) * len(cfg.TASK_COUNTS) * cfg.TASKSETS_PER_COMBINATION
    taskset_done = 0
    taskset_start = time.perf_counter()

    for U in cfg.U_LEVELS:
        for n in cfg.TASK_COUNTS:
            for taskset_id in range(cfg.TASKSETS_PER_COMBINATION):
                taskset = None
                offsets_by_scenario = None
                generation_attempt = 0

                for attempt in range(cfg.MAX_TASKSET_GENERATION_ATTEMPTS):
                    seed = stable_seed(cfg.BASE_SEED, "taskset", U, n, taskset_id, attempt)
                    candidate = t_gen.TaskSet(n, int(round(U * 100)), True, seed=seed)

                    offsets_by_scenario = {}
                    offsets_by_scenario["sync"] = [0 for _ in candidate.taskset]

                    rng = random.Random(stable_seed(seed, "discrete_async"))
                    choices = [500, 1000, 1500, 2000]
                    discrete_offsets = []

                    for i, task in enumerate(candidate.taskset):
                        max_offset = int(min(task.D, task.T)) - 1
                        valid = [x for x in choices if x <= max_offset]
                        discrete_offsets.append(0 if i == 0 else rng.choice(valid) if valid else 0)

                    offsets_by_scenario["discrete_async"] = discrete_offsets

                    rng = random.Random(stable_seed(seed, "random"))
                    random_offsets = []

                    for i, task in enumerate(candidate.taskset):
                        max_offset = int(min(task.D, task.T)) - 1
                        random_offsets.append(0 if i == 0 else rng.randint(0, max_offset))

                    offsets_by_scenario["random"] = random_offsets

                    ph_feasible = True

                    for offsets in offsets_by_scenario.values():
                        temp_taskset = copy.deepcopy(candidate)
                        set_offsets(temp_taskset, offsets)

                        res = evaluate_scheduler(temp_taskset, "PH", cfg.ENERGY_PROFILES["baseline"])

                        if res["deadline_misses"] > 0:
                            ph_feasible = False
                            break

                    if not ph_feasible:
                        if cfg.LOG_DISCARDS:
                            print(f"discarded taskset U={U}, n={n}, id={taskset_id}, attempt={attempt}")
                        continue

                    taskset = candidate
                    generation_attempt = attempt
                    break

                if taskset is None:
                    raise RuntimeError(f"Could not generate taskset U={U}, n={n}, id={taskset_id}")

                set_offsets(taskset, offsets_by_scenario["sync"])
                all_tasksets.append((U, n, taskset_id, taskset, offsets_by_scenario))

                for task in taskset.taskset:
                    write_row(TASKSETS_CSV, TASKSET_FIELDS, {
                        "U": U, "n": n, "taskset_id": taskset_id, "generation_attempt": generation_attempt,
                        "task_id": task.id, "C": task.C, "D": task.D, "T": task.T,
                        "offset": task.offset, "offsets_by_scenario": offsets_by_scenario,
                    })

                taskset_done += 1
                progress("Tasksets", taskset_done, taskset_total, taskset_start, cfg.PROGRESS_EVERY)

    if args.run == "tuning":
        tuning_tasksets = [
            row for row in all_tasksets
            if row[0] in cfg.TUNING_U_LEVELS and row[1] in cfg.TUNING_TASK_COUNTS and row[2] < cfg.TUNING_TASKSETS_PER_COMBINATION
        ]

        tuning_total = len(tuning_tasksets) * sum(len(configs) for configs in cfg.OPTIMIZER_CONFIGS.values()) * cfg.TUNING_META_REPEATS
        tuning_done = 0
        tuning_failed = 0
        tuning_rows = []
        tuning_start = time.perf_counter()

        print(f"Tuning runs: {tuning_total}")

        for U, n, taskset_id, base_taskset, offsets_by_scenario in tuning_tasksets:
            for optimizer_name, configs in cfg.OPTIMIZER_CONFIGS.items():
                for config_name, config in configs.items():
                    for rep in range(cfg.TUNING_META_REPEATS):
                        random.seed(stable_seed(cfg.BASE_SEED, "tuning", U, n, taskset_id, optimizer_name, config_name, rep))

                        taskset = copy.deepcopy(base_taskset)
                        set_offsets(taskset, offsets_by_scenario["sync"])

                        try:
                            result = evaluate_optimizer(
                                taskset, optimizer_name, config, cfg.ENERGY_PROFILES["baseline"],
                                trace_context={
                                    "phase": "meta_tuning", "U": U, "n": n, "taskset_id": taskset_id,
                                    "profile": "baseline", "config_name": config_name, "repeat": rep,
                                },
                            )
                        except Exception as exc:
                            tuning_failed += 1
                            tuning_done += 1
                            print(f"FAILED tuning: {optimizer_name} {config_name}, U={U}, n={n}, id={taskset_id}, rep={rep}: {exc}")
                            progress("Tuning", tuning_done, tuning_total, tuning_start, cfg.TUNING_PROGRESS_EVERY)
                            continue

                        row = {
                            "phase": "meta_tuning", "U": U, "n": n, "taskset_id": taskset_id, "profile": "baseline",
                            "method": optimizer_name, "offset_scenario": "optimized", "config_name": config_name,
                            "repeat": rep, **result,
                        }

                        tuning_rows.append(row)
                        write_row(RESULTS_CSV, RESULT_FIELDS, row)

                        tuning_done += 1
                        progress("Tuning", tuning_done, tuning_total, tuning_start, cfg.TUNING_PROGRESS_EVERY)

        print(f"Tuning finished: {tuning_done}/{tuning_total}, failed={tuning_failed}")

        best_configs = {}

        for optimizer_name, configs in cfg.OPTIMIZER_CONFIGS.items():
            candidates = []

            for config_name in configs:
                rows = [
                    row for row in tuning_rows
                    if row["method"] == optimizer_name and row["config_name"] == config_name and row["deadline_misses"] == 0
                ]

                if rows:
                    mean_energy = statistics.mean(row["total_energy"] for row in rows)
                    mean_time = statistics.mean(row["optimization_time_s"] for row in rows)
                    candidates.append((mean_energy, mean_time, config_name, len(rows)))

            candidates.sort(key=lambda x: (x[0], x[1]))

            print(f"\n{optimizer_name} tuning summary:")
            for mean_energy, mean_time, config_name, row_count in candidates:
                print(f"  {config_name}: energy={mean_energy:.3f}, time={mean_time:.3f}s, rows={row_count}")

            best_configs[optimizer_name] = candidates[0][2]

        with BEST_CONFIGS_JSON.open("w", encoding="utf-8") as f:
            json.dump(best_configs, f, indent=2)

        print("\nSelected configs:")
        for optimizer_name, config_name in best_configs.items():
            print(f"  {optimizer_name}: {config_name}")

    if args.run == "comparison":
        with BEST_CONFIGS_JSON.open("r", encoding="utf-8") as f:
            best_configs = json.load(f)

        baseline_methods = ["RMS", "EDF", "PH"]
        offset_scenarios = ["sync", "discrete_async", "random"]

        runs_per_taskset_profile = len(baseline_methods) * len(offset_scenarios) + len(best_configs) * cfg.META_REPEATS
        comparison_total = len(cfg.ENERGY_PROFILES) * len(all_tasksets) * runs_per_taskset_profile
        comparison_done = 0
        comparison_failed = 0
        comparison_start = time.perf_counter()

        print(f"Comparison runs: {comparison_total}")

        for profile_name, energy_model in cfg.ENERGY_PROFILES.items():
            for U, n, taskset_id, base_taskset, offsets_by_scenario in all_tasksets:

                for scenario_name in offset_scenarios:
                    for method in baseline_methods:
                        taskset = copy.deepcopy(base_taskset)
                        set_offsets(taskset, offsets_by_scenario[scenario_name])

                        result = evaluate_scheduler(taskset, method, energy_model)

                        write_row(RESULTS_CSV, RESULT_FIELDS, {
                            "phase": "final", "U": U, "n": n, "taskset_id": taskset_id, "profile": profile_name,
                            "method": method, "offset_scenario": scenario_name, "config_name": "", "repeat": 0, **result,
                        })

                        comparison_done += 1
                        progress("Comparison", comparison_done, comparison_total, comparison_start, cfg.PROGRESS_EVERY)

                for optimizer_name, config_name in best_configs.items():
                    config = cfg.OPTIMIZER_CONFIGS[optimizer_name][config_name]

                    for rep in range(cfg.META_REPEATS):
                        random.seed(stable_seed(cfg.BASE_SEED, "comparison", profile_name, U, n, taskset_id, optimizer_name, rep))

                        taskset = copy.deepcopy(base_taskset)
                        set_offsets(taskset, offsets_by_scenario["sync"])

                        try:
                            result = evaluate_optimizer(taskset, optimizer_name, config, energy_model)
                        except Exception as exc:
                            comparison_failed += 1
                            comparison_done += 1
                            print(f"FAILED comparison: {optimizer_name} {config_name}, profile={profile_name}, U={U}, n={n}, id={taskset_id}, rep={rep}: {exc}")
                            progress("Comparison", comparison_done, comparison_total, comparison_start, cfg.PROGRESS_EVERY)
                            continue

                        write_row(RESULTS_CSV, RESULT_FIELDS, {
                            "phase": "final", "U": U, "n": n, "taskset_id": taskset_id, "profile": profile_name,
                            "method": f"{optimizer_name}+RMS", "offset_scenario": "optimized",
                            "config_name": config_name, "repeat": rep, **result,
                        })

                        comparison_done += 1
                        progress("Comparison", comparison_done, comparison_total, comparison_start, cfg.PROGRESS_EVERY)

        print(f"Comparison finished: {comparison_done}/{comparison_total}, failed={comparison_failed}")

    print(f"\nDone in {seconds_text(time.perf_counter() - start_total)}")
    print(f"Results: {RESULTS_CSV}")
    print(f"Tasksets: {TASKSETS_CSV}")
    print(f"Convergence: {CONVERGENCE_CSV}")
    print(f"Best configs: {BEST_CONFIGS_JSON}")


if __name__ == "__main__":
    main()