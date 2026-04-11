class EDFScheduler:
    def get_next_request(self, released_requests):
        next_request = min(released_requests, key=lambda r: r.absolute_deadline)
        return next_request
    
class RMSScheduler:
    def get_next_request(self, released_requests):
        next_request = min(released_requests, key=lambda r: (r.absolute_deadline - r.release_time))
        return next_request

class PHScheduler:
        def compute_promotion_times(taskset):
            #idk
            a=0
            
        def get_next_request(self, released_requests):
            next_request = min(released_requests, key=lambda r: (r.absolute_deadline - r.release_time))
            return next_request

# GAOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)

# SAOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)

# PSOOptimizer object:
# optimize(taskset, base_scheduler, energy_model, horizon)