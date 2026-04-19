import task_generator as t_gen

ph_test_scenarios = [

        # 1. Your baseline PH case:
        # one frequent task, two long tasks -> should create visible procrastination windows
        (
            "ph_baseline_long_long_short",
            [
                t_gen.Task(0, 400, 10000, 10000),
                t_gen.Task(1, 420, 1000, 1000),
                t_gen.Task(2, 400, 10000, 10000),
            ]
        ),

        # 2. Same structure, but more slack in the short task
        # PH should have more room to delay wakeups
        (
            "ph_more_short_task_slack",
            [
                t_gen.Task(0, 400, 10000, 10000),
                t_gen.Task(1, 250, 1000, 1000),
                t_gen.Task(2, 400, 10000, 10000),
            ]
        ),

        # 3. Same structure, but very little slack in the short task
        # PH should have much smaller useful procrastination intervals
        (
            "ph_tight_short_task",
            [
                t_gen.Task(0, 400, 10000, 10000),
                t_gen.Task(1, 800, 1000, 1000),
                t_gen.Task(2, 400, 10000, 10000),
            ]
        ),

        # 4. One short task, one medium task, one long task
        # Good for seeing whether PH clusters work into denser bursts
        (
            "ph_short_medium_long",
            [
                t_gen.Task(0, 300, 1000, 1000),
                t_gen.Task(1, 600, 5000, 5000),
                t_gen.Task(2, 700, 10000, 10000),
            ]
        ),

        # 5. Two identical long tasks and one short task
        # Good for same-period tie behavior and Z-value sanity
        (
            "ph_equal_long_tasks",
            [
                t_gen.Task(0, 500, 10000, 10000),
                t_gen.Task(1, 420, 1000, 1000),
                t_gen.Task(2, 500, 10000, 10000),
            ]
        ),

        # 6. One very frequent tiny task plus two big long tasks
        # Should create repeated PH sleep-then-wake cycles
        (
            "ph_tiny_very_frequent_task",
            [
                t_gen.Task(0, 600, 10000, 10000),
                t_gen.Task(1, 100, 500, 500),
                t_gen.Task(2, 600, 10000, 10000),
            ]
        ),

        # 7. Two short tasks and one long task
        # Useful for checking whether multiple arrivals tighten wake_time correctly
        (
            "ph_multiple_short_tasks",
            [
                t_gen.Task(0, 180, 1000, 1000),
                t_gen.Task(1, 220, 2000, 2000),
                t_gen.Task(2, 900, 10000, 10000),
            ]
        ),

        # 8. Lower utilization version with large natural idle windows
        # PH should show strong wakeup reduction if implemented correctly
        (
            "ph_large_idle_windows",
            [
                t_gen.Task(0, 100, 1000, 1000),
                t_gen.Task(1, 300, 5000, 5000),
                t_gen.Task(2, 300, 10000, 10000),
            ]
        ),

        # 9. Borderline-heavy but still potentially feasible
        # Good stress test for PH not breaking deadlines
        (
            "ph_high_utilization_stress",
            [
                t_gen.Task(0, 500, 1000, 1000),
                t_gen.Task(1, 800, 5000, 5000),
                t_gen.Task(2, 700, 10000, 10000),
            ]
        ),

        # 10. Two equal short-period tasks plus one long task
        # Good for same-priority/same-period behavior under PH
        (
            "ph_equal_short_tasks",
            [
                t_gen.Task(0, 150, 1000, 1000),
                t_gen.Task(1, 180, 1000, 1000),
                t_gen.Task(2, 800, 10000, 10000),
            ]
        ),

        # 11. Very sparse long tasks, one short repeating task
        # Good for checking whether PH keeps sleeping after arrivals
        (
            "ph_sparse_long_tasks",
            [
                t_gen.Task(0, 200, 20000, 20000),
                t_gen.Task(1, 420, 1000, 1000),
                t_gen.Task(2, 200, 20000, 20000),
            ]
        ),

        # 12. Medium-frequency interference chain
        # Good for testing whether released requests update wake_time properly
        (
            "ph_interference_chain",
            [
                t_gen.Task(0, 250, 1000, 1000),
                t_gen.Task(1, 350, 2500, 2500),
                t_gen.Task(2, 500, 5000, 5000),
                t_gen.Task(3, 700, 10000, 10000),
            ]
        ),

        # 13. Almost no room for procrastination
        # Good negative test: PH should behave close to plain RMS
        (
            "ph_almost_no_slack",
            [
                t_gen.Task(0, 850, 1000, 1000),
                t_gen.Task(1, 700, 5000, 5000),
                t_gen.Task(2, 700, 10000, 10000),
            ]
        ),

        # 14. Lots of slack, should exaggerate PH benefit
        (
            "ph_lots_of_slack",
            [
                t_gen.Task(0, 80, 1000, 1000),
                t_gen.Task(1, 250, 5000, 5000),
                t_gen.Task(2, 250, 10000, 10000),
            ]
        ),

        # 15. Two long tasks, one short task, but shifted demand
        # Similar to baseline, just varied numbers for robustness
        (
            "ph_baseline_variant",
            [
                t_gen.Task(0, 550, 10000, 10000),
                t_gen.Task(1, 300, 1000, 1000),
                t_gen.Task(2, 450, 10000, 10000),
            ]
        ),
    ]