import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched
import plot as pl

if __name__== "__main__":
    with open("output.txt", "a") as f:
        energy_model= sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30)
        simulator = sim.Simulator()
        
        for iii in range(1):
            print(iii)
            
            taskset = t_gen.TaskSet(20, 30, True)
            
            H = taskset.get_hyperperiod()
            Dmax = max(task.D for task in taskset.taskset)
            evaluate_start = H + Dmax
            evaluate_stop = evaluate_start + H
            release_window = evaluate_stop
            simulation_horizon = evaluate_stop
            
            
            scheduler = sched.EDFScheduler(taskset.taskset)
            edf_sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            edf_energy_vals = energy_model.evaluate(edf_sim_res, evaluate_start, evaluate_stop)
            # print(edf_sim_res.timeline, file=f)
            print(edf_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in edf_sim_res.deadline_misses:
                print(vars(miss), file=f)
            
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
            ph_sim_res = simulator.run(taskset, scheduler, release_window, simulation_horizon)
            ph_energy_vals = energy_model.evaluate(ph_sim_res, evaluate_start, evaluate_stop)
            # print(ph_sim_res.timeline, file=f)
            print(ph_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in ph_sim_res.deadline_misses:
                print(vars(miss), file=f)
            
            scheduler = sched.RMSScheduler(taskset.taskset)      
            optimizer = sched.GAOptimizer()
            ga_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop, 100, 50)
            ga_energy_vals = energy_model.evaluate(ga_sim_res, evaluate_start, evaluate_stop)
            # print(sim_res.timeline, file=f)
            print(ga_energy_vals, file=f)
            for task in taskset.taskset:
                print(vars(task), file=f)
            for miss in ga_sim_res.deadline_misses:
                print(vars(miss), file=f)
            
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
            print(ga_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            print(sa_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            
            
            pl.plot_timeline(edf_sim_res.timeline[:100], title="EDF", filename='plots/edf'+str(iii)+'.pdf')
            pl.plot_timeline(rms_sim_res.timeline[:100], title="RMS", filename='plots/rms'+str(iii)+'.pdf')
            pl.plot_timeline(ph_sim_res.timeline[:100], title="PH", filename='plots/ph'+str(iii)+'.pdf')
            pl.plot_timeline(ga_sim_res.timeline[:100], title="GA", filename='plots/ga'+str(iii)+'.pdf')
            pl.plot_timeline(sa_sim_res.timeline[:100], title="SA", filename='plots/sa'+str(iii)+'.pdf')
            
            # break
        


        
        
