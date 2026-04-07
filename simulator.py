import math

class Request:
    id = 0 
    task_id = 0
    release_time = 0
    absolute_deadline = 0
    remaining_time = 0
    completion_time = 0
    is_completed = False
    
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

    
    def __init__(self):
        a = 0


class Simulator:
    def __init__(self):
        a = 0
    
    def run(self,taskset, scheduler, horizon) -> SimulationResult:
        simulation_result = SimulationResult()
        time = 0
        next_request_idx = 0
        released_requests = []
        all_requests = self.generate_all_request_set(taskset, horizon)
        all_requests.sort(key=lambda x: x.release_time, reverse=False)
        released_requests,next_request_idx = self.get_released_requests(all_requests, released_requests, time, next_request_idx)
            
        while time < horizon:
            time = horizon
            # scheduler.schedule_request_set(request_set)
            
        return simulation_result
    
    def generate_all_request_set(self, taskset, horizon):
        current_request_id = 0
        request_set = []
        for task in taskset.taskset:
            for n in range(math.ceil(horizon/task.D)):
                request_set.append(Request(current_request_id, task.id, task.D*n, task.D*(n+1), task.C))
                current_request_id += 1
        return request_set
        
    def get_released_requests(self, all_requests: list[Request], released_requests: list[Request], current_time, next_request_idx):
        new_request_count = 0
        for request in all_requests[next_request_idx:]:
            if not request.is_completed and request.release_time <= current_time:
                released_requests.append(request)
                new_request_count += 1
            elif request.release_time > current_time:
                next_request_idx += new_request_count
                break
        return released_requests,next_request_idx