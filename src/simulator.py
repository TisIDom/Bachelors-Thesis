import math

class Request:
    def __init__(self, id, task_id, release_time, absolute_deadline, remaining_time):
        self.id = id
        self.task_id = task_id
        self.release_time = release_time
        self.absolute_deadline = absolute_deadline
        self.remaining_time = remaining_time
        self.completion_time = 0
        self.is_completed = False
        self.missed_deadline = False
    
        
class SimulationResult:
    def __init__(self):
        # timeline = [(start_time, end_time, request_id), ...] sorted by start_time
        self.timeline = []
        self.requests = []
        self.deadline_misses = []
        self.total_busy_time = 0
        self.total_idle_time = 0
        self.total_sleep_time = 0
        self.wakeups = 0
        self.idle_intervals = 0


class Simulator:
    def run(self,taskset, scheduler, release_window, evaluation_horizon) -> SimulationResult:
        simulation_result = SimulationResult()
        time = 0
        next_request_time = 0
        next_request_idx = 0
        released_requests = []
        is_sleeping = False
        
        all_requests = self.generate_all_request_set(taskset, release_window)
        all_requests.sort(key=lambda x: x.release_time, reverse=False)
        simulation_result.requests = all_requests
        
        while time < evaluation_horizon:
            if next_request_idx < len(all_requests):
                next_request_time = all_requests[next_request_idx].release_time
            else:
                next_request_time = evaluation_horizon
                
            released_requests,next_request_idx = self.get_released_requests(all_requests, released_requests, time, next_request_idx)
            
            if len(released_requests) == 0:
                simulation_result.timeline.append((time, time + (next_request_time - time), -1, -1))
                simulation_result.total_sleep_time += (next_request_time - time)
                is_sleeping = True
                time = next_request_time
                continue
            
            while time < next_request_time:
                prev_time = time
                if is_sleeping:
                    wake_time = scheduler.get_wake_time(released_requests, time)
                    next_event = min(wake_time, next_request_time, evaluation_horizon)
                    if time != next_event:
                        simulation_result.timeline.append((time, time + (next_event - time), -2, -2))
                        simulation_result.total_sleep_time += (next_event - time)
                    time = next_event
                    if time == wake_time:
                        is_sleeping = False
                else:
                    if len(released_requests) == 0:
                        simulation_result.timeline.append((time, time + (next_request_time - time), -1, -1))
                        simulation_result.total_sleep_time += (next_request_time - time)
                        is_sleeping = True
                        time = next_request_time
                        break
                    current_request = scheduler.get_next_request(released_requests, time, taskset)
                    if time + current_request.remaining_time <= next_request_time:
                        # take into account offset?
                        simulation_result.timeline.append((time, time + current_request.remaining_time, current_request.task_id, current_request.id))
                        simulation_result.total_busy_time += current_request.remaining_time
                        time += current_request.remaining_time
                        current_request.remaining_time = 0
                        if time > current_request.absolute_deadline:
                            current_request.missed_deadline = True
                            simulation_result.deadline_misses.append(current_request)
                        current_request.completion_time = time
                        current_request.is_completed = True
                        idx = next((i for i, item in enumerate(released_requests) if item.id == current_request.id), None)
                        if idx is not None:
                            released_requests.pop(idx)
                    else:
                        current_request.remaining_time -= (next_request_time - time)
                        simulation_result.timeline.append((time, time + (next_request_time - time), current_request.task_id, current_request.id))
                        simulation_result.total_busy_time += (next_request_time - time)
                        time = next_request_time
                if time <= prev_time:
                    break
        
        for request in released_requests:
            if (not request.is_completed) and (not request.missed_deadline) and time > request.absolute_deadline:
                request.missed_deadline = True
                simulation_result.deadline_misses.append(request)

        return simulation_result
    
    
    def generate_all_request_set(self, taskset, horizon):
        current_request_id = 0
        request_set = []
        for task in taskset.taskset:
            for n in range(math.ceil(horizon/task.T)):
                release_time = task.offset + task.T*n
                deadline_time = release_time + task.D
                request_set.append(Request(current_request_id, task.id, release_time, deadline_time, task.C))
                current_request_id += 1
        return request_set

        
    def get_released_requests(self, all_requests: list[Request], released_requests: list[Request], current_time, next_request_idx):
        new_request_count = 0
        for request in all_requests[next_request_idx:]:
            if not request.is_completed and request.release_time <= current_time:
                released_requests.append(request)
                new_request_count += 1
            elif request.release_time > current_time:
                break
        next_request_idx += new_request_count
        return released_requests,next_request_idx
    
    
class EnergyModel:
    def __init__(self, p_active, p_idle, p_sleep, e_wakeup, break_even_time):
        self.p_active = p_active
        self.p_idle = p_idle
        self.p_sleep = p_sleep
        self.e_wakeup = e_wakeup
        self.break_even_time = break_even_time
        
        
    def evaluate(self, simulation_result, evaluation_start, evaluation_stop):
        total_energy = 0.0
        active_time = 0.0
        idle_time = 0.0
        sleep_time = 0.0
        wakeups = 0
           
        usable_timeline = simulation_result.timeline[:]
        
        # fuse timeline entries with -1 and -2 task_id
        i = 0
        while i < len(usable_timeline) - 1:
            if usable_timeline[i][2] < 0 and usable_timeline[i + 1][2] < 0:
                usable_timeline[i] = (usable_timeline[i][0], usable_timeline[i + 1][1], -1, -1)
                usable_timeline.pop(i + 1)
            else:
                i += 1
                
        for start_time, end_time, task_id, request_id in usable_timeline:
            clipped_start = max(start_time, evaluation_start)
            clipped_end = min(end_time, evaluation_stop)

            if clipped_end <= clipped_start:
                continue
                
            interval = clipped_end - clipped_start
            if interval <= 0:
                continue

            if task_id >= 0:
                total_energy += self.p_active * interval
                active_time += interval

            else:
                if interval >= self.break_even_time:
                    total_energy += self.p_sleep * interval + self.e_wakeup
                    sleep_time += interval
                    wakeups += 1
                else:
                    total_energy += self.p_idle * interval
                    idle_time += interval

        return {
            "total_energy": total_energy,
            "active_time": active_time,
            "idle_time": idle_time,
            "sleep_time": sleep_time,
            "wakeups": wakeups,
        }