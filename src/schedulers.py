class EDFScheduler:
    def get_next_request(self, released_requests):
        next_request = min(released_requests, key=lambda r: r.absolute_deadline)
        return next_request
    
class RMSScheduler:
    def get_next_request(self, released_requests):
        print("Released requests:")
        for request in released_requests:
            print(vars(request))
        next_request = min(released_requests, key=lambda r: (r.absolute_deadline - r.release_time))
        print("Chosen request: ")
        print(vars(next_request))
        return next_request

# PHScheduler object:
# compute_promotion_times(taskset)
# schedule_taskset(taskset)

# GAOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)

# SAOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)

# PSOOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)