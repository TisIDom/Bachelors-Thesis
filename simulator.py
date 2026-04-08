import math

class Request:
    id = 0 
    task_id = 0
    release_time = 0
    absolute_deadline = 0
    remaining_time = 0
    completion_time = 0
    is_completed = False
    missed_deadline = False
    
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
        
        while time < horizon:
            if next_request_idx == all_requests.__len__():
                break
            next_request_time = all_requests[next_request_idx].release_time
            
            delta_time = next_request_time - time
            time += delta_time
            released_requests,next_request_idx = self.get_released_requests(all_requests, released_requests, time, next_request_idx)
            # scheduler.schedule_request_set(request_set)

            if next_request_time != all_requests[next_request_idx].release_time:
                next_request_time = all_requests[next_request_idx].release_time
            else:
                next_request_time = horizon
            while time < next_request_time:
                # get next scheduled request
                if released_requests.__len__() == 0:
                    # check if enough time for sleep, otherwise idle
                    time = next_request_time
                    break
                current_request = released_requests[0]
                if time + current_request.remaining_time <= next_request_time:
                    # take into account offset?
                    # add to busy time
                    time += current_request.remaining_time
                    current_request.remaining_time = 0
                    if time > current_request.absolute_deadline:
                        current_request.missed_deadline = True
                    current_request.completion_time = time
                    current_request.is_completed = True
                    released_requests.pop(0)
                else:
                    current_request.remaining_time -= (next_request_time - time)
                    time = next_request_time
            
        for request in all_requests:
            print(vars(request))
        return simulation_result
    
    def generate_all_request_set(self, taskset, horizon):
        current_request_id = 0
        request_set = []
        for task in taskset.taskset:
            for n in range(math.ceil(horizon/task.T)):
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