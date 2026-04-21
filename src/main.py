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

    

    with open("output.txt", "a") as f:
        for name, tasks in test_sc.ph_test_scenarios:
            taskset.taskset = tasks
            energy_model= sim.EnergyModel(10, 3, 1, 1, 2)
            simulator = sim.Simulator()
            release_window = taskset.get_hyperperiod() * 2
            evaluation_hyperperiod = taskset.get_hyperperiod() * 2 + max(task.D for task in taskset.taskset)
            
            scheduler = sched.EDFScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, evaluation_hyperperiod)
            energy_vals = energy_model.evaluate(sim_res, 10000, 20000)
            # print(sim_res.timeline)
            # print(energy_vals)
            # for miss in sim_res.deadline_misses:
            #     print(miss)
            scheduler = sched.RMSScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, evaluation_hyperperiod)
            energy_vals = energy_model.evaluate(sim_res, 10000, 20000)
            # print(sim_res.timeline)
            # print(energy_vals)
            # for miss in sim_res.deadline_misses:
            #     print(miss)
            scheduler = sched.PHScheduler(taskset.taskset)
            sim_res = simulator.run(taskset, scheduler, release_window, evaluation_hyperperiod)
            energy_vals = energy_model.evaluate(sim_res, 10000, 20000)
            # print(sim_res.timeline)
            # print(energy_vals)
            # for miss in sim_res.deadline_misses:
            #     print(miss)
            scheduler = sched.RMSScheduler(taskset.taskset)
                        
            optimizer = sched.GAOptimizer()
            sim_res = optimizer.optimize(taskset, scheduler, energy_model, taskset.get_hyperperiod(), 3, 1, release_window, evaluation_hyperperiod)
            energy_vals = energy_model.evaluate(sim_res, 10000, 20000)
            print(sim_res.timeline)
            print(energy_vals)
            for miss in sim_res.deadline_misses:
                print(miss)
            break
            
            
            # simulation = sim.Simulator()
            # sim_res = simulation.run(taskset, scheduler, taskset.get_hyperperiod())
            
            # print(name, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # print(sim_res.timeline, file=f)
            # print(scheduler.z_by_task_id, file=f)
            # # for request in sim_res.requests:
            # #     print(vars(request), file=f)
            # for request in sim_res.deadline_misses:
            #     print(vars(request), file=f)
        
