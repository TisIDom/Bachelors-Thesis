to do:

    taskset testing:
    - test all algorithms with these taskset generation parameters:
        - task count [3-20]
        - cpu util [5-95 or 0-90] depends on feasibility though likely 90 if not less


    GA:
    - play with mutation aggression, maybe not necessarrily full regeneration but maybe also slight adjustment at higher rate?
    - testing with different parameters, keep track of performance (optimizing time as well as fitness improvements) on same taskset:
        - population count [20-100]
        - generation count [20-50]
        - mutation rates [0-0.2]
        - elite count [1-5] 
        - tournament select candidates [2-4] 

    SA:
    - play with neighborhood move aggression, different likelihood of each happening
    - testing with different parameters, keep track of performance (optimizing time as well as fitness improvements) on same taskset:
        - temp [?-?]
        - minimum temp [1?]
        - temperature change multiplier [0.9-0.99]
        - repetitions per temp [1-10]

    PSO:
    - implement


    Thesis direction:
    - define task set model, energy model, simulator
    - explain and compare EDF, RMS, PH
    - explain GA SA PSO; tune each algo parameter set and then compare based on optimization time and results 
    - final comparison between all on new tasksets of varying parameters
    - explain which mh algo is most useful with what parameters and when, when it is not useful, try to argue why, compare offline vs real-time scheduling, 

