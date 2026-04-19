import math
import simulator as sim
import copy
import random

class Scheduler:
    def __init__(self, taskset):
        # do nothing
        a=0
        
    def get_wake_time(self, released_requests, time):
        return time

class EDFScheduler(Scheduler):
    def get_next_request(self, released_requests, time):
        next_request = min(released_requests, key=lambda r: r.absolute_deadline)
        return next_request
        
    
class RMSScheduler(Scheduler):        
    def get_next_request(self, released_requests, time):
        next_request = min(released_requests, key=lambda r: (r.absolute_deadline - r.release_time))
        return next_request
    
     
class PHScheduler(RMSScheduler):
    z_by_task_id = []
    def __init__(self, taskset):
        self.z_by_task_id = self.compute_z_times(taskset)
    
    def get_wake_time(self, released_requests, time):
        if len(released_requests) == 0:
            return None
        return min(
            request.release_time + self.z_by_task_id[request.task_id]
            for request in released_requests
            if not request.is_completed
        )
    
    def compute_z_times(self, taskset):
        temp_taskset = taskset.copy()
        temp_taskset.sort(key=lambda x: (x.T, x.id))
            
        raw_z = [0] * len(temp_taskset)
        cumulative_util = 0.0
        for i, task in enumerate(temp_taskset):
            cumulative_util += task.C / task.T
            raw_z[i] = round((1 - cumulative_util) * task.T, 0)
            
        adjusted_z = raw_z.copy()
        for i in range(len(adjusted_z) - 2, -1, -1):
            adjusted_z[i] = min(adjusted_z[i], adjusted_z[i + 1])
        
        z_by_id = [0] * len(temp_taskset)
        for i, task in enumerate(temp_taskset):
            z_by_id[task.id] = adjusted_z[i]
            
        return z_by_id
    
            
class GAOptimizer:
    def optimize(self, taskset, scheduler, energy_model, horizon, population_size, generation_count):
        chromosomes = [[random.randint(0, taskset.taskset[j].T) for j in range(len(taskset.taskset))]
                       for _ in range(population_size)
                       ]
        
        # generate starting values
        for chromosome in chromosomes:
            for j in range(len(chromosome)):
                new_offset = random.randint(0, taskset.taskset[j].T)
                chromosome[j] = new_offset
        
        with open("output.txt", "w") as f:
            print(chromosomes, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for i in range(generation_count):
                for chromosome in chromosomes:
                    temp_taskset = copy.deepcopy(taskset)
                    for i, new_offset in enumerate(chromosome):
                        temp_taskset.taskset[i].offset = new_offset
                    simulation = sim.Simulator()
                    sim_res = simulation.run(temp_taskset, scheduler, horizon)
                    
                    # for request in sim_res.requests:
                    #     print(vars(request))    
            
                    print(sim_res.timeline, file=f)
                    # print(scheduler.z_by_task_id, file=f)
                    # for request in sim_res.requests:
                    #     print(vars(request), file=f)
                    for request in sim_res.deadline_misses:
                        print(vars(request), file=f)
    
        

# SAOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)

# PSOOptimizer object:1
# optimize(taskset, scheduler, energy_model, horizon)