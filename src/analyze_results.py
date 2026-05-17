import pandas as pd
from pathlib import Path

RESULTS_DIR = Path("experiment_results")
OUT_DIR = RESULTS_DIR / "analysis"
OUT_DIR.mkdir(exist_ok=True)

results = pd.read_csv(RESULTS_DIR / "results.csv")

final = results[results["phase"] == "final"]
final = final[final["deadline_misses"] == 0]

summary = final.groupby(
    ["profile", "U", "n", "method", "offset_scenario"],
    as_index=False
).agg(
    runs=("total_energy", "count"),
    mean_energy=("total_energy", "mean"),
    mean_wakeups=("wakeups", "mean"),
    mean_optimization_time_s=("optimization_time_s", "mean"),
)

summary.to_csv(OUT_DIR / "final_summary.csv", index=False)
print(summary)