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
            return time
        wake = min(
            request.release_time + self.z_by_task_id[request.task_id]
            for request in released_requests
            if not request.is_completed
        )
        return max(time, wake)
    
    def compute_z_times(self, taskset):
        temp_taskset = taskset.copy()
        temp_taskset.sort(key=lambda x: (x.T, x.id))
        temp_z_by_id = []
        
        for i in range(len(temp_taskset)):
            wcrt_iterations = [temp_taskset[i].C]
            j = 1
            wcrt = 0
            while True:
                new_wcrt = wcrt_iterations[0]
                for k in range(i):
                    new_wcrt += (math.ceil(wcrt_iterations[j-1]/temp_taskset[k].T) * temp_taskset[k].C)
                if wcrt_iterations[j-1] == new_wcrt:
                    wcrt = new_wcrt
                    break
                if new_wcrt > temp_taskset[i].D:
                    return None
                wcrt_iterations.append(new_wcrt)
                j+=1
            temp_z_by_id.append(temp_taskset[i].T - wcrt)
        
        z_by_id = [0] * len(temp_taskset)
        for i, task in enumerate(temp_taskset):
            z_by_id[task.id] = temp_z_by_id[i]
        
        return z_by_id

            
class GAOptimizer:
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop, population_size, generation_count, mutation_rate=0.03, elite_count=2, ts_candidates=2):
        temp_taskset = copy.deepcopy(taskset)
        simulator = sim.Simulator()
        chromosomes = [[random.randint(0, taskset.taskset[j].T) for j in range(len(taskset.taskset))]
                       for _ in range(population_size)
                       ]
        
        # generate starting values
        for chromosome in chromosomes:
            chromosome[0] = 0
            for j in range(1, len(chromosome)):
                new_offset = random.randint(0, taskset.taskset[j].T)
                chromosome[j] = new_offset
        
        for k, new_offset in enumerate(chromosomes[0]):
            temp_taskset.taskset[k].offset = new_offset
        sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
        curr_best_total = energy_vals['total_energy']
        curr_best_offsets = chromosomes[0].copy()
        
        
        for i in range(generation_count):
            fitness_by_id = []
            chromosome_mate_pool = []
            for j, chromosome in enumerate(chromosomes):
                for k, new_offset in enumerate(chromosome):
                    temp_taskset.taskset[k].offset = new_offset
                sim_res = sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
                
                energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
                fitness = energy_vals['total_energy']
                fitness_by_id.append(fitness)
                if len(sim_res.deadline_misses) > 0:
                    fitness = 100000000 + 1000000 * len(sim_res.deadline_misses)
                    
                fitness_by_id[j] = fitness

            if min(fitness_by_id) < curr_best_total:
                curr_best_total = energy_vals['total_energy']
                curr_best_offsets = chromosomes[fitness_by_id.index(min(fitness_by_id))].copy()
            
            print(i)
            print(min(fitness_by_id))
            # print(curr_best_total)
            
            ranked = sorted(zip(fitness_by_id, chromosomes), key=lambda x: x[0])
            elites = []
            for i in range(elite_count):
                elites.append(ranked[i][1].copy())
            
            for _ in range(len(chromosomes)-2):
                idx, surviving_chromosome = self.tournament_select(chromosomes, fitness_by_id, ts_candidates)
                chromosome_mate_pool.append((idx, surviving_chromosome))

            new_chromosomes = self.mate_chromosomes(chromosome_mate_pool)
            
            for i in range(len(new_chromosomes)):
                new_chromosomes[i] = self.mutate(new_chromosomes[i][1], taskset, mutation_rate)
                
            chromosomes = elites + new_chromosomes

        final_chromosome = curr_best_offsets.copy()
        print(final_chromosome)
        for i, new_offset in enumerate(final_chromosome):
                        temp_taskset.taskset[i].offset = new_offset
        sim_res = sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        return sim_res, final_chromosome, curr_best_total
    
    
    def tournament_select(self, chromosomes, fitness_by_id, k):
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
        

class SAOptimizer:
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop, T=1000000, T_delta=0.95, T_min=1, rep_per_sched=5):
        simulator = sim.Simulator()
        offset_array = []
        current_energy = 0
        temp_taskset = copy.deepcopy(taskset)

        # initial solution
        for task in taskset.taskset:
            offset_array.append(random.randint(0, task.D-1))
        offset_array[0] = 0
        for k, new_offset in enumerate(offset_array):
            temp_taskset.taskset[k].offset = new_offset
        sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
        current_energy = energy_vals['total_energy']
        
        curr_best_total = current_energy
        curr_best_offsets = offset_array
        
        while T > T_min:
            for j in range(rep_per_sched):
                new_offset_array = self.neighborhood_move(taskset, offset_array)
                for k, new_offset in enumerate(new_offset_array):
                    temp_taskset.taskset[k].offset = new_offset
                sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
                energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
                new_energy = energy_vals['total_energy']
                energy_delta = current_energy - new_energy
                if energy_delta < 0:
                    acceptance_probability = pow(math.e, energy_delta / T)
                    if random.random() < acceptance_probability:
                        current_energy = new_energy
                        offset_array = new_offset_array
                else:
                    current_energy = new_energy
                    offset_array = new_offset_array
                if new_energy < curr_best_total:
                    curr_best_total = new_energy
                    curr_best_offsets = new_offset_array.copy()
                    print(curr_best_total)
            T = T * T_delta
        
        # use best solution
        print(curr_best_offsets)
        for k, new_offset in enumerate(curr_best_offsets):
            temp_taskset.taskset[k].offset = new_offset
        sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        return sim_res, curr_best_offsets, curr_best_total
    
    
    def neighborhood_move(self, taskset, offset_array, max_move_amount=50):
        choice = random.randint(1, 3)
        new_offset_array = offset_array.copy()
        
        # shift 1 offset
        if choice == 1:
            idx = random.randint(1, len(new_offset_array)-1)
            sign = random.randint(0, 1)
            step = max(max_move_amount, taskset.taskset[idx].D // 20)
            if sign:
                new_offset_array[idx] = min(new_offset_array[idx] + random.randint(1, step), new_offset_array[idx] + taskset.taskset[idx].D-1)
            else:
                new_offset_array[idx] = max(0, new_offset_array[idx] - random.randint(1, step))
    
        # switch 2 offsets
        elif choice == 2:
            idx1, idx2 = random.sample(range(1, len(new_offset_array)-1), 2)
            temp = new_offset_array[idx1]
            new_offset_array[idx1] = min(new_offset_array[idx2], taskset.taskset[idx1].D-1)
            new_offset_array[idx2] = min(temp, taskset.taskset[idx2].D-1)
            
        # regenerate 1 offset
        elif choice == 3:
            idx = random.randint(1, len(new_offset_array)-1)
            new_offset_array[idx] = random.randint(0, taskset.taskset[idx].D-1)
        return new_offset_array

class PSOOptimizer():
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop):
        particles = [self.Particle] * 30
        informant_count = 3
        
    class Particle:
        a=0