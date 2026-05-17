import math
import simulator as sim
import copy
import random
import time
import json

class Scheduler:
    def __init__(self, taskset):
        # do nothing
        a=0
        
    def get_wake_time(self, released_requests, time):
        return time

class EDFScheduler(Scheduler):
    def get_next_request(self, released_requests, time, taskset):
        next_request = min(released_requests, key=lambda r: r.absolute_deadline)
        return next_request
        
    
class RMSScheduler(Scheduler):        
    def get_next_request(self, released_requests, time, taskset):
        next_request = min(released_requests, key=lambda r: (taskset.taskset[r.task_id].T, r.task_id))
        return next_request
    
     
class PHScheduler(RMSScheduler):
    z_by_task_id = []
    
    def __init__(self, taskset):
        self.z_by_task_id = self.compute_z_times(taskset)
    
    def get_wake_time(self, released_requests, time):
        if len(released_requests) == 0:
            return time
        wake = min(
            request.release_time + min(self.z_by_task_id)
            for request in released_requests
            if not request.is_completed
        )
        return max(time, wake)
    
    def compute_z_times(self, taskset):
        temp_taskset = copy.deepcopy(taskset)
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
                # if new_wcrt > temp_taskset[i].D:
                #     return None
                wcrt_iterations.append(new_wcrt)
                j+=1
            temp_z_by_id.append(temp_taskset[i].T - wcrt)
        
        z_by_id = [0] * len(temp_taskset)
        for i, task in enumerate(temp_taskset):
            z_by_id[task.id] = temp_z_by_id[i]
        
        return z_by_id

            
class GAOptimizer:
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop, population_size, generation_count, mutation_rate=0.03, elite_count=2, ts_candidates=2, mutation_max_amount=250, trace_writer=None, trace_context=None):
        temp_taskset = copy.deepcopy(taskset)
        simulator = sim.Simulator()
        start_time = time.perf_counter()
        evaluations = 0
        chromosomes = [[random.randint(0, taskset.taskset[j].T - 1) for j in range(len(taskset.taskset))]
                       for _ in range(population_size)
                       ]
        
        # generate starting values
        for chromosome in chromosomes:
            chromosome[0] = 0
            # for j in range(1, len(chromosome)):
            #     new_offset = random.randint(0, taskset.taskset[j].T - 1)
            #     chromosome[j] = new_offset
        
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
                evaluations += 1

            if min(fitness_by_id) < curr_best_total:
                curr_best_total = min(fitness_by_id)
                curr_best_offsets = chromosomes[fitness_by_id.index(min(fitness_by_id))].copy()
            
            if trace_writer is not None:
                row = dict(trace_context or {})
                row.update({"optimizer": "GA", "iteration": i, "algorithm_step": "generation", "temperature": "", "evaluations": evaluations, "elapsed_s": time.perf_counter() - start_time, "iteration_best_objective": min(fitness_by_id), "best_objective": curr_best_total, "best_offsets": json.dumps([int(x) for x in curr_best_offsets])})
                trace_writer.writerow(row)
            
            ranked = sorted(zip(fitness_by_id, chromosomes), key=lambda x: x[0])
            elites = []
            for j in range(elite_count):
                elites.append(ranked[j][1].copy())
            
            for _ in range(len(chromosomes)-elite_count):
                idx, surviving_chromosome = self.tournament_select(chromosomes, fitness_by_id, ts_candidates)
                chromosome_mate_pool.append((idx, surviving_chromosome))

            new_chromosomes = self.mate_chromosomes(chromosome_mate_pool)
            
            for j in range(len(new_chromosomes)):
                new_chromosomes[j] = self.mutate(new_chromosomes[j][1], taskset, mutation_rate, mutation_max_amount)
                
            chromosomes = elites + new_chromosomes

        final_chromosome = curr_best_offsets.copy()
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
                mate_indices = random.sample(range(len(chromosomes)), 2)
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
        
    def mutate(self, child, taskset, mutation_chance, mutation_max_amount):
        new_child = child[:]
        for i in range(1, len(new_child)):
            if random.random() < mutation_chance:
                sign = random.randint(0,1)
                if sign == 1:
                    new_child[i] = max(0, new_child[i] - random.randint(1, mutation_max_amount))
                    
                else:
                    new_child[i] = min(new_child[i] + random.randint(1, mutation_max_amount), taskset.taskset[i].D-1)
                    
        return new_child
        

class SAOptimizer:
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop, T=1000000, T_delta=0.95, T_min=1, rep_per_sched=5, max_move_amount=50, trace_writer=None, trace_context=None):
        simulator = sim.Simulator()
        start_time = time.perf_counter()
        evaluations = 0
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
        evaluations += 1
        
        curr_best_total = current_energy
        curr_best_offsets = offset_array.copy()
        
        iteration = 0
        while T > T_min:
            iteration_best_total = float("inf")
            for j in range(rep_per_sched):
                new_offset_array = self.neighborhood_move(taskset, offset_array, max_move_amount)
                for k, new_offset in enumerate(new_offset_array):
                    temp_taskset.taskset[k].offset = new_offset
                sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
                energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
                new_energy = energy_vals['total_energy']
                evaluations += 1
                if new_energy < iteration_best_total:
                    iteration_best_total = new_energy
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
            if trace_writer is not None:
                row = dict(trace_context or {})
                row.update({"optimizer": "SA", "iteration": iteration, "algorithm_step": "temperature_step", "temperature": T, "evaluations": evaluations, "elapsed_s": time.perf_counter() - start_time, "iteration_best_objective": iteration_best_total, "best_objective": curr_best_total, "best_offsets": json.dumps([int(x) for x in curr_best_offsets])})
                trace_writer.writerow(row)
            T = T * T_delta
            iteration += 1
        
        # use best solution
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
                new_offset_array[idx] = min(new_offset_array[idx] + random.randint(1, step), min(taskset.taskset[idx].D, taskset.taskset[idx].T)-1)
            else:
                new_offset_array[idx] = max(0, new_offset_array[idx] - random.randint(1, step))
    
        # switch 2 offsets
        elif choice == 2:
            idx1, idx2 = random.sample(range(1, len(new_offset_array)), 2)
            temp = new_offset_array[idx1]
            new_offset_array[idx1] = min(new_offset_array[idx2], min(taskset.taskset[idx1].D, taskset.taskset[idx1].T)-1)
            new_offset_array[idx2] = min(temp, min(taskset.taskset[idx2].D, taskset.taskset[idx2].T)-1)
            
        # regenerate 1 offset
        elif choice == 3:
            idx = random.randint(1, len(new_offset_array)-1)
            new_offset_array[idx] = random.randint(0, min(taskset.taskset[idx].D, taskset.taskset[idx].T)-1)
        return new_offset_array


class PSOOptimizer():
    def optimize(self, taskset, scheduler, energy_model, release_window, evaluation_hyperperiod, evaluate_start, evaluate_stop, particle_count=30, informant_count=3, iteration_count=100, trace_writer=None, trace_context=None):
        # recommended params based on PSO book:
        # particle_count = [20,40]
        # informant_count = [3,5]
        simulator = sim.Simulator()
        start_time = time.perf_counter()
        evaluations = 0
        particles = []
        curr_time = 0
        time_limit = iteration_count
        temp_taskset = copy.deepcopy(taskset)
        best_offsets = []
        best_energy = float("inf")
        
        for i in range(particle_count):
            particles.append(self.Particle(taskset, i, random.sample(range(0,particle_count),informant_count)))
        
        for curr_time in range(time_limit):
            iteration_best_energy = float("inf")
            for particle in particles:
                for k, new_offset in enumerate(particle.offsets):
                    temp_taskset.taskset[k].offset = new_offset
                sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
                energy_vals = energy_model.evaluate(sim_res, evaluate_start, evaluate_stop)
                current_energy = energy_vals["total_energy"]
                evaluations += 1
                if current_energy < iteration_best_energy:
                    iteration_best_energy = current_energy
                particle.current_energy = current_energy
                if current_energy < particle.best_offsets_energy:
                    particle.best_offsets = copy.deepcopy(particle.offsets)
                    particle.best_offsets_energy = current_energy
                    if current_energy < best_energy:
                        best_offsets = copy.deepcopy(particle.offsets)
                        best_energy = current_energy
                informant_particles = [particles[i] for i in particle.informant_ids]
                best_informant = min(
                    informant_particles,
                    key=lambda p: p.best_offsets_energy
                )
                particle.best_informant_offsets = copy.deepcopy(best_informant.best_offsets)
                particle.best_informant_energy = best_informant.best_offsets_energy
                particle.calculate_speed(taskset)
                particle.update_position(taskset)
            if trace_writer is not None:
                row = dict(trace_context or {})
                row.update({"optimizer": "PSO", "iteration": curr_time, "algorithm_step": "iteration", "temperature": "", "evaluations": evaluations, "elapsed_s": time.perf_counter() - start_time, "iteration_best_objective": iteration_best_energy, "best_objective": best_energy, "best_offsets": json.dumps([int(x) for x in best_offsets])})
                trace_writer.writerow(row)
                
        for k, new_offset in enumerate(best_offsets):
            temp_taskset.taskset[k].offset = new_offset
        sim_res = simulator.run(temp_taskset, scheduler, release_window, evaluation_hyperperiod)
        return sim_res, best_offsets, best_energy
                
                
    class Particle:
        def __init__(self, taskset, id, informant_ids, v_confidence=0.7, v_confidence_max=1.43):
            self.id = id
            self.offsets = [random.randint(0, taskset.taskset[j].T - 1) for j in range(len(taskset.taskset))]
            self.offsets[0] = 0
            self.current_energy = float("inf")
            self.v = [0] * len(taskset.taskset)
            self.v_confidence = v_confidence
            self.v_confidence_max = v_confidence_max
            self.best_offsets = copy.deepcopy(self.offsets)
            self.best_offsets_energy = float("inf")
            self.informant_ids = informant_ids
            self.best_informant_offsets = []
            self.best_informant_energy = float("inf")

            
        def calculate_speed(self, taskset):
            for i in range(len(self.v)):
                self.v[i] = math.floor(self.v_confidence * self.v[i] + random.uniform(0, self.v_confidence_max) * (self.best_offsets[i] - self.offsets[i]) + random.uniform(0, self.v_confidence_max) * (self.best_informant_offsets[i] - self.offsets[i]))
            
        def update_position(self, taskset):
            for i in range(len(self.offsets)):
                self.offsets[i] = self.offsets[i] + self.v[i]
                clamped_offset = max(0, min(self.offsets[i], taskset.taskset[i].T - 1))
                if clamped_offset != self.offsets[i]:
                    self.v[i] = 0
                    self.offsets[i] = min(max(self.offsets[i], 0), taskset.taskset[i].T-1)