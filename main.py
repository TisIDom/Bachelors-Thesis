import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf

if __name__== "__main__":
    hyperperiods = []
    for i in range(1):
        taskset = t_gen.TaskSet(20, 50)
        for j in range(20):
            print(taskset.taskset[j].id, taskset.taskset[j].C, taskset.taskset[j].D, taskset.taskset[j].T)
        print(taskset.get_cpu_utilization())
        
    
# EnergyModel object:
# p_active
# p_idle
# p_sleep
# e_wakeup
# break_even_time
# evaluate(simulation_result)