import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched

if __name__== "__main__":
    hyperperiods = []
    for i in range(1):
        taskset = t_gen.TaskSet(15, 105)
        for task in taskset.taskset:
            print(vars(task))

    scheduler = sched.RMSScheduler()
    simulation = sim.Simulator()
    sim_res = simulation.run(taskset, scheduler, taskset.get_hyperperiod())
    for task in taskset.taskset:
        print(vars(task))
    print(vars(sim_res))
        
    
# EnergyModel object:
# p_active
# p_idle
# p_sleep
# e_wakeup
# break_even_time
# evaluate(simulation_result)