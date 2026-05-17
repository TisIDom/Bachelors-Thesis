import task_generator as t_gen
import simulator as sim
import time
import helper_functions as hf
import schedulers as sched
import plot as pl

if __name__== "__main__":
    with open("output.txt", "a") as f:
        profiles = {
            "baseline":         sim.EnergyModel(10.0, 3.0, 0.2,  80.0, 30),
            "expensive_wakeup": sim.EnergyModel(10.0, 3.0, 0.2, 160.0, 60),
            "shallow_sleep":    sim.EnergyModel(10.0, 3.0, 0.8,  80.0, 40),
            "cheap_deep_sleep": sim.EnergyModel(10.0, 3.0, 0.05, 60.0, 20),
        }       
        # energy_model= sim.EnergyModel(10.0, 3.0, 0.2, 80.0, 30)
        energy_model = profiles['baseline']
        simulator = sim.Simulator()
        
        for iii in range(1):
            print(iii)
            
            taskset = t_gen.TaskSet(20, 50, True)
            
            
            taskset.taskset = [
                t_gen.Task(0, 500, 2000, 2000, 0),
                t_gen.Task(1, 500, 3000, 3000, 0),
                t_gen.Task(2, 500, 8000, 8000, 0),
            ]

            
            
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
            
            # scheduler = sched.RMSScheduler(taskset.taskset)      
            # optimizer = sched.GAOptimizer()
            # ga_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop, 100, 50)
            # ga_energy_vals = energy_model.evaluate(ga_sim_res, evaluate_start, evaluate_stop)
            # # print(sim_res.timeline, file=f)
            # print(ga_energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in ga_sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            # scheduler = sched.RMSScheduler(taskset.taskset)      
            # optimizer = sched.SAOptimizer()
            # sa_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            # sa_energy_vals = energy_model.evaluate(sa_sim_res, evaluate_start, evaluate_stop)
            # # print(sim_res.timeline, file=f)
            # print(sa_energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in sa_sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            
            # scheduler = sched.RMSScheduler(taskset.taskset)      
            # optimizer = sched.PSOOptimizer()
            # pso_sim_res, best_offsets, best_total_energy = optimizer.optimize(taskset, scheduler, energy_model, release_window, simulation_horizon, evaluate_start, evaluate_stop)
            # pso_energy_vals = energy_model.evaluate(pso_sim_res, evaluate_start, evaluate_stop)
            # # print(sim_res.timeline, file=f)
            # print(pso_energy_vals, file=f)
            # for task in taskset.taskset:
            #     print(vars(task), file=f)
            # for miss in pso_sim_res.deadline_misses:
            #     print(vars(miss), file=f)
            
            
            # print("ENERGY DIFF: ")
            # print(ph_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            # print(ga_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            # print(sa_energy_vals['total_energy']/rms_energy_vals['total_energy'])
            
            # pl.plot_timeline(edf_sim_res.timeline[:100], title="EDF", filename='plots/edf'+str(iii)+'.pdf')
            # pl.plot_timeline(rms_sim_res.timeline[:100], title="RMS", filename='plots/rms'+str(iii)+'.pdf')
            # pl.plot_timeline(ph_sim_res.timeline[:100], title="PH", filename='plots/ph'+str(iii)+'.pdf')
            # pl.plot_timeline(ga_sim_res.timeline[:100], title="GA", filename='plots/ga'+str(iii)+'.pdf')
            # pl.plot_timeline(sa_sim_res.timeline[:100], title="SA", filename='plots/sa'+str(iii)+'.pdf')
            # pl.plot_timeline(pso_sim_res.timeline[:100], title="PSO", filename='plots/pso'+str(iii)+'.pdf')
            
            # break
        


        
        
