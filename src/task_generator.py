import random
import time
import helper_functions as hf


class Task:
    def __init__(self, id, wcet, deadline, period):
        self.id = id
        self.C = wcet
        self.D = deadline
        self.T = period
        self.offset = 0
    
    def change_offset(self, new_offset):
       self.offset = new_offset


class TaskSet:
    
    def __init__(self, count, cpu_target):
        # constraints
        self.min_wcet = 50
        self.max_wcet = 1000
        self.deadlines = [1000, 2000, 2500, 4000, 5000, 7500, 10000, 12500, 15000]
        self.periods = self.deadlines
        self.current_task_id = 0
        
        self.hyperperiod = 0
        self.U = 0
        
        random.seed(time.time())
        self.taskset = []
        self.generate_taskset(count, cpu_target)

    def generate_taskset(self, n, U):
        # uses UUniSort algorithm
        U_vector = [0, U]
        for i in range(n-1):
            new_number = 0
            while new_number in U_vector:
                new_number = round(random.uniform(1, U),0)
            U_vector.append(new_number)
            
        U_vector.sort()
        
        for i in range(U_vector.__len__() - 1):
            U_vector[i] = abs(U_vector[i] - U_vector[i+1])
        U_vector.pop()
        
        for i in range(n):
            allowed_deadlines = []
            for deadline in self.deadlines:
                wcet = round((deadline*U_vector[i])/100,0)
                if not wcet < self.min_wcet and not wcet > self.max_wcet:
                    allowed_deadlines.append(deadline)
            deadline = period = random.choice(allowed_deadlines)
            self.taskset.append(Task(self.current_task_id, int((deadline*U_vector[i])/100), deadline, period))
            self.current_task_id += 1
        
    def is_feasible(taskset):
        print("WIP")
        
    def get_cpu_utilization(self):
        if self.U == 0:
            self.calculate_utilization(self.taskset)
        return self.U
        
    def calculate_utilization(self, taskset):
        for task in taskset:
            self.U += task.C / task.T
        
    def get_hyperperiod(self):
        if self.hyperperiod == 0:
            self.calculate_hyperperiod(self.taskset)
        return self.hyperperiod
    
    def calculate_hyperperiod(self, taskset):
        period_set = []
        for task in taskset:
            period_set.append(task.T)
        
        self.hyperperiod = period_set[0]
        for p in period_set:
            self.hyperperiod = hf.lcm(p, self.hyperperiod)
        