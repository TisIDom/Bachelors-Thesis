import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched
import test_scenarios as test_sc

if __name__== "__main__":
    # Scenarios for experiments
    # Synchronous release
    # all offsets = 0
    # Random phase / asynchronous release
    # each task gets a random offset, between 0 and task.D
    # Structured phase patterns
    # aligned or clustered

    with open("output.txt", "w") as f:
        for name, tasks in test_sc.ph_test_scenarios:
            taskset = t_gen.TaskSet(20, 50, True)
            # taskset.taskset = [
            #     t_gen.Task(0, 100, 5000, 5000),
            #     t_gen.Task(1, 420, 2000, 2000),
            #     t_gen.Task(2, 920, 4000, 4000),
            #     t_gen.Task(3, 260, 1000, 1000),
            #     t_gen.Task(4, 180, 1000, 1000),
            # ]
            energy_model= sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30)
            simulator = sim.Simulator()
            
            H = taskset.get_hyperperiod()
            Dmax = max(task.D for task in taskset.taskset)
            evaluate_start = H + Dmax
            evaluate_stop = evaluate_start + H
            release_window = evaluate_stop
            simulation_horizon = evaluate_stop
            
            # scheduler = sched.EDFScheduler(taskset.taskset)
            # sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            # energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            # print(energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            scheduler = sched.RMSScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in sim_res.deadline_misses:
                print(vars(miss), file=f)
            
            # scheduler = sched.PHScheduler(taskset.taskset)
            # print(scheduler.z_by_task_id, file=f)
            # sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            # energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            # print(energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in sim_res.deadline_misses:
            #     print(vars(miss), file=f)
                
            # scheduler = sched.RMSScheduler(taskset.taskset)      
            # optimizer = sched.GAOptimizer()
            # sim_res = optimizer.optimize(taskset, scheduler, energy_model, 40, 50, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            # energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            # print(energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            scheduler = sched.RMSScheduler(taskset.taskset)      
            optimizer = sched.SAOptimizer()
            sim_res = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
            print(sim_res.timeline, file=f)
            print(energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in sim_res.deadline_misses:
                print(vars(miss), file=f)
            
            break
        
