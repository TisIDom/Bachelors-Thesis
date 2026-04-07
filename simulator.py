import math

class Request:
    id = 0 
    task_id = 0
    release_time = 0
    absolute_deadline = 0
    remaining_time = 0
    completion_time = 0
    
    def __init__(self, id, task_id, release_time, absolute_deadline, remaining_time):
        self.id = id
        self.task_id = task_id
        self.release_time = release_time
        self.absolute_deadline = absolute_deadline
        self.remaining_time = remaining_time
    
        
class SimulationResult:
    # timeline = [(start_time, end_time, request_id), ...] sorted by start_time
    timeline = [()]
    requests = []
    deadline_misses = 0
    total_busy_time = 0
    total_idle_time = 0
    total_sleep_time = 0
    wakeups = 0
    idle_intervals = 0
    
    def __init__():
        a = 0


class Simulator:
    def run(self,taskset, scheduler, horizon) -> SimulationResult:
        simulation_result = SimulationResult()
        time = 0
        all_requests = self.generate_all_request_set(taskset, horizon)
        print(all_requests)
        return SimulationResult()
        
        while time < horizon:
            # scheduler.schedule_request_set()
            a = 0
            
        return simulation_result
    
    def generate_all_request_set(taskset, horizon):
        current_request_id = 0
        request_set = []
        for task in taskset:
            for n in range(math.ceil(horizon/task.C)):
                request_set.append(Request(current_request_id, task.id, task.D*n, task.D*(n+1), task.C))
                current_request_id += 1
        return request_set
        
    def get_released_requests(all_requests, current_time):
        requests = 0
        
        
        
        
# Simulator object:

# run(taskset, scheduler, horizon) -> SimulationResult

# SimulationResult object:
# timeline
# requests
# deadline_misses
# total_busy_time
# total_idle_time
# total_sleep_time
# wakeups
# idle_intervals


# Request object:
# task_id
# running_intervals
# release_time
# absolute_deadline
# remaining_time
# completion_time
