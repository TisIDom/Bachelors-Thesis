import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched
import test_scenarios as test_sc

if __name__== "__main__":
    hyperperiods = []
    for i in range(1):
        taskset = t_gen.TaskSet(3, 50)

    # Scenarios for experiments
    # Synchronous release
    # all offsets = 0
    # Random phase / asynchronous release
    # each task gets a random offset, between 0 and task.D
    # Structured phase patterns
    # aligned or clustered

    with open("output.txt", "a") as f:
        for name, tasks in test_sc.ph_test_scenarios:
            taskset = t_gen.TaskSet(10, 75)
            energy_model= sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30)
            simulator = sim.Simulator()
            
            H = taskset.get_hyperperiod()
            Dmax = max(task.D for task in taskset.taskset)
            evaluate_start = H + Dmax
            evaluate_stop = evaluate_start + H
            release_window = evaluate_stop
            simulation_horizon = evaluate_stop
            
            scheduler = sched.EDFScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for miss in sim_res.deadline_misses:
                print(miss, file=f)
            scheduler = sched.RMSScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for miss in sim_res.deadline_misses:
                print(miss, file=f)
            scheduler = sched.PHScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for miss in sim_res.deadline_misses:
                print(miss, file=f)
            scheduler = sched.RMSScheduler(taskset.taskset)
                        
            optimizer = sched.GAOptimizer()
            sim_res = optimizer.optimize(taskset, scheduler, energy_model, release_window, 40, 12, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for miss in sim_res.deadline_misses:
                print(miss, file=f)
            break
        
