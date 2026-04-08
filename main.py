import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf

if __name__== "__main__":
    hyperperiods = []
    for i in range(1):
        taskset = t_gen.TaskSet(5, 100)
        for task in taskset.taskset:
            print(vars(task))
        print(taskset.get_cpu_utilization())
        print(taskset.get_hyperperiod())
    
    simulation = sim.Simulator()
    simulation.run(taskset, "A", taskset.get_hyperperiod())
    for task in taskset.taskset:
        print(vars(task))
        
    
# EnergyModel object:
# p_active
# p_idle
# p_sleep
# e_wakeup
# break_even_time
# evaluate(simulation_result)