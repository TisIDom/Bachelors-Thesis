import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched
import plot as pl

if __name__== "__main__":
    # Scenarios for experiments
    # Synchronous release
    # all offsets = 0
    # Random phase / asynchronous release
    # each task gets a random offset, between 0 and task.D
    # Structured phase patterns
    # aligned or clustered

    with open("output.txt", "a") as f:
        energy_model= sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30)
        simulator = sim.Simulator()
        
        for iii in range(5):
            print(iii)
            
            taskset = t_gen.TaskSet(20, 50, True)
            
            H = taskset.get_hyperperiod()
            Dmax = max(task.D for task in taskset.taskset)
            evaluate_start = H + Dmax
            evaluate_stop = evaluate_start + H
            release_window = evaluate_stop
            simulation_horizon = evaluate_stop
            
            
            # scheduler = sched.EDFScheduler(taskset.taskset)
            # edf_sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            # energy_vals = energy_model.evaluate(edf_sim_res, evaluate_start, evaluate_stop)
            # # print(edf_sim_res.timeline, file=f)
            # print(energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in edf_sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            scheduler = sched.RMSScheduler(taskset.taskset)
            rms_sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            rms_energy_vals = energy_model.evaluate(rms_sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            print(rms_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in rms_sim_res.deadline_misses:
                print(vars(miss), file=f)
                
            scheduler = sched.PHScheduler(taskset.taskset)
            ph_sim_res2 = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            ph_energy_vals = energy_model.evaluate(ph_sim_res2, evaluate_start, evaluate_stop)
            # print(ph_sim_res2.timeline, file=f)
            print(ph_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in ph_sim_res2.deadline_misses:
                print(vars(miss), file=f)
            print(ph_sim_res2.timeline, file=f)
            
            
            # scheduler = sched.RMSScheduler(taskset.taskset)      
            # optimizer = sched.GAOptimizer()
            # ga_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop, 100, 50)
            # energy_vals = energy_model.evaluate(ga_sim_res, evaluate_start, evaluate_stop)
            # # print(sim_res.timeline, file=f)
            # print(energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in ga_sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            scheduler = sched.RMSScheduler(taskset.taskset)      
            optimizer = sched.SAOptimizer()
            sa_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            sa_energy_vals = energy_model.evaluate(sa_sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            print(sa_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in sa_sim_res.deadline_misses:
                print(vars(miss), file=f)
            
            
            
            print("ENERGY DIFF: ")
            print(ph_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            print(sa_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            
            
            # pl.plot_timeline(edf_sim_res.timeline[:100], title="EDF")
            # pl.plot_timeline(rms_sim_res.timeline[:100], title="RMS")
            # pl.plot_timeline(ph_sim_res.timeline[:100], title="PH")
            # pl.plot_timeline(ph_sim_res2.timeline[:100], title="PH")
            # pl.plot_timeline(ga_sim_res.timeline[:100], title="GA")
            # pl.plot_timeline(sa_sim_res.timeline[:100], title="SA")
            
            
            # break
        


        
        
