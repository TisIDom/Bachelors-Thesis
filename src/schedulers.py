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
    def optimize(self, taskset, scheduler, energy_model, horizon, population_size, generation_count, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop):
        
        chromosomes = [[random.randint(0, taskset.taskset[j].T) for j in range(len(taskset.taskset))]
                       for _ in range(population_size)
                       ]
        
        # generate starting values
        for chromosome in chromosomes:
            chromosome[0] = 0
            for j in range(1, len(chromosome)):
                new_offset = random.randint(0, taskset.taskset[j].T)
                chromosome[j] = new_offset
        
        with open("output.txt", "w") as f:
            for i in range(generation_count):
                fitness_by_id = []
                chromosome_mate_pool = []
                for j, chromosome in enumerate(chromosomes):
                    temp_taskset = copy.deepcopy(taskset)
                    for k, new_offset in enumerate(chromosome):
                        temp_taskset.taskset[k].offset = new_offset
                    simulator = sim.Simulator()
                    sim_res = sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
                    
                    energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
                    fitness = energy_vals['total_energy']
                    fitness_by_id.append(fitness)
                    if len(sim_res.deadline_misses) > 0:
                        fitness = 100000000 + 1000000 * len(sim_res.deadline_misses)
                        
                    fitness_by_id[j] = fitness

                ranked = sorted(zip(fitness_by_id, chromosomes), key=lambda x: x[0])
                elite1 = ranked[0][1].copy()
                elite2 = ranked[1][1].copy()
                
                for _ in range(len(chromosomes)-2):
                    idx, surviving_chromosome = self.tournament_select(chromosomes, fitness_by_id)
                    chromosome_mate_pool.append((idx, surviving_chromosome))

                new_chromosomes = self.mate_chromosomes(chromosome_mate_pool)
                
                for i in range(len(new_chromosomes)):
                    new_chromosomes[i] = self.mutate(new_chromosomes[i][1], taskset, 0.03)
                    
                chromosomes = [elite1, elite2] + new_chromosomes
                
        final_chromosome = chromosomes[fitness_by_id.index(min(fitness_by_id))]
        for i, new_offset in enumerate(final_chromosome):
                        temp_taskset.taskset[i].offset = new_offset
        sim_res = sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        return sim_res
    
    
    def tournament_select(self, chromosomes, fitness_by_id, k=2):
        candidate_indices = random.sample(range(len(chromosomes)), k)
        best_idx = min(candidate_indices, key=lambda i: fitness_by_id[i])
        return best_idx, chromosomes[best_idx]
    
    def mate_chromosomes(self, chromosomes):
        new_chromosomes = []
        idx = 0
        for _ in range(int(len(chromosomes)/2)):
            mate1 = (0, [])
            mate2 = (0, [])
            while mate1[0] == mate2[0]:
                mate_indices = random.sample(range(len(chromosomes)-1), 2)
                mate1 = chromosomes[mate_indices[0]]
                mate2 = chromosomes[mate_indices[1]]
            child1, child2 = self.crossover(mate1[1], mate2[1])
            new_chromosomes.append((idx, child1))
            idx += 1
            new_chromosomes.append((idx, child2))
            idx += 1
        return new_chromosomes
    
    def crossover(self, mate1, mate2):
        p1, p2 = sorted(random.sample(range(1, len(mate1)), 2))
        child1 = mate1[:p1] + mate2[p1:p2] + mate1[p2:]
        child2 = mate2[:p1] + mate1[p1:p2] + mate2[p2:]
        child1[0] = 0
        child2[0] = 0
        return child1, child2
        
    def mutate(self, child, taskset, mutation_chance):
        new_child = child[:]
        for i in range(1, len(new_child)):
            if random.random() < mutation_chance:
                new_child[i] = random.randint(0, taskset.taskset[i].T-1)
        return new_child
        

# SAOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)

# PSOOptimizer object:
# optimize(taskset, scheduler, energy_model, horizon)