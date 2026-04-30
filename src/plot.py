
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_timeline(timeline, title="Scheduler Timeline", filename="placeholder.pdf", show_request_ids=False):
    fig, ax = plt.subplots(figsize=(14, 2.8))

    y = 10
    height = 8

    for start, end, task_id, request_id in timeline:
        duration = end - start

        if task_id == -2:
            label = "Sleep"
            color = "lightgray"
        elif task_id == -1:
            label = "Idle"
            color = "white"
        else:
            label = f"T{task_id}"
            color = f"C{task_id % 20}"

        ax.broken_barh([(start, duration)], (y, height),
                       facecolors=color, edgecolors="black")

        if duration > 0:
            text = label
            if show_request_ids and task_id >= 0:
                text += f"\nR{request_id}"
            if duration >= 150:
                ax.text(start + duration / 2, y + height / 2,
                        text, ha="center", va="center", fontsize=8)

    ax.set_ylim(5, 20)
    ax.set_xlim(min(t[0] for t in timeline), max(t[1] for t in timeline))
    ax.set_yticks([])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)

    legend_handles = [
        mpatches.Patch(facecolor="lightgray", edgecolor="black", label="Sleep"),
        mpatches.Patch(facecolor="white", edgecolor="black", label="Idle")
    ]
    ax.legend(handles=legend_handles, loc="upper right")

    plt.tight_layout()
    plt.savefig(filename)


