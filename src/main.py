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
            scheduler = sched.RMSScheduler(taskset.taskset)
            optimizer = sched.GAOptimizer()
            optimizer.optimize(taskset, scheduler, 0, taskset.get_hyperperiod(), 20, 1)
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
        
