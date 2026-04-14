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
        # do nothing for now
        temp_taskset = taskset.copy()
        temp_taskset.sort(key=lambda x: x.D, reverse=False)
        for task in temp_taskset:
            print(vars(task))
            
        a = []
        for task in taskset:
            a.append(1)
        return a
    
    
            

# GAOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)

# SAOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)

# PSOOptimizer object:1
# optimize(taskset, scheduler, energy_model, horizon)