import math

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
    def optimize(taskset, scheduler, energy_model, horizon):
        a=0

# SAOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)

# PSOOptimizer object:1
# optimize(taskset, scheduler, energy_model, horizon)