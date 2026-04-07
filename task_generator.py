import random
import time
import helper_functions as hf
# Task object:
# worst case execution time WCET C; based on Jejurikar [0.5ms,10ms]
# deadline D; based on Jejurikar [10ms,125ms]
# periodicity T; based on Jejurikar [10ms,125ms]
# offset


class Task:
    id = 0
    C = 0
    D = 0
    T = 0
    offset = 0
    def __init__(self, id, wcet, deadline, period):
        self.id = id
        self.C = wcet
        self.D = deadline
        self.T = period
    
    def change_offset(self, new_offset):
       self.offset = new_offset


# TaskSet object:
# Tasks[] taskset; based on Jejurikar n <= 20
# generate_taskset(n, U)
# is_feasible(taskset)
# calculate_utilization(taskset)
# calculate_hyperperiod(taskset)

class TaskSet:
    # constraints
    min_wcet = 0.5
    max_wcet = 10
    deadlines = [10, 20, 25, 40, 50, 75, 100, 125]
    periods = deadlines
    current_task_id = 0
    
    hyperperiod = 0
    U = 0
    
    taskset = []
    
    def __init__(self, count, cpu_target):
        random.seed(time.time())
        self.generate_taskset(count, cpu_target)

    def generate_taskset(self, n, U):
        # uses UUniSort algorithm
        U_vector = [0, U]
        for i in range(n-1):
            U_vector.append(random.uniform(1, U))
            
        U_vector.sort()
        
        for i in range(U_vector.__len__() - 1):
            U_vector[i] = abs(U_vector[i] - U_vector[i+1])
        U_vector.pop()
        
        for i in range(n):
            deadline = period = random.choice(self.deadlines)
            self.taskset.append(Task(self.current_task_id, round((deadline*U_vector[i])/100,2), deadline, period))
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
        # print(depth)
        # if taskset.__len__() != 0:
        #     print(taskset[0].T)
        # print(self.hyperperiod)
        
        # depth = depth + 1
        # if depth >= self.taskset.__len__():
        #     return 2
        # if self.hyperperiod == 0:
        #     self.hyperperiod = taskset[0].T
        # self.hyperperiod = hf.lcm(self.hyperperiod, self.calculate_hyperperiod(taskset[1:], depth))
        period_set = []
        for task in taskset:
            period_set.append(task.T)
        
        self.hyperperiod = period_set[0]
        for p in period_set:
            self.hyperperiod = hf.lcm(p, self.hyperperiod)
            
