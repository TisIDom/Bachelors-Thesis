import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched

if __name__== "__main__":
    hyperperiods = []
    for i in range(1):
        taskset = t_gen.TaskSet(3, 50)

    scheduler = sched.PHScheduler(taskset.taskset)
    simulation = sim.Simulator()
    sim_res = simulation.run(taskset, scheduler, taskset.get_hyperperiod())
    
    print(sim_res.timeline)
    for request in sim_res.requests:
        print(vars(request))
    for request in sim_res.deadline_misses:
        print(vars(request))
    
        
    
# EnergyModel object:
# p_active
# p_idle
# p_sleep
# e_wakeup
# break_even_time
# evaluate(simulation_result)