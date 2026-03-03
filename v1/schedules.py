"""
Generate balanced incomplete block design assignment schedules.
Each schedule assigns 8 tasks, each with a random subset of 10 items from 50.
Ensures marginal and pairwise balance across the full study.
"""

import json
import random
import numpy as np
from pathlib import Path
from questions import PROFILING_QUESTIONS

NUM_ITEMS = len(PROFILING_QUESTIONS)  # 50
ITEMS_PER_SUBSET = 10
NUM_TASKS = 8
NUM_SCHEDULES = 200  # enough for 150 participants + buffer

ITEM_IDS = [q["id"] for q in PROFILING_QUESTIONS]


def generate_schedules(
    num_schedules=NUM_SCHEDULES,
    num_tasks=NUM_TASKS,
    items_per_subset=ITEMS_PER_SUBSET,
    seed=42,
):
    """
    Generate assignment schedules with approximate balance.

    Strategy: For each schedule, generate task subsets such that:
    1. Each item appears in approximately the same number of trials globally
    2. Each pair of items co-occurs approximately equally
    3. Within a schedule, items are spread across tasks (not all clustered)

    We use a greedy approach: for each trial, sample items with probability
    inversely proportional to how often they've appeared so far.
    """
    rng = np.random.RandomState(seed)

    # Track global appearance counts for balance
    item_counts = np.zeros(NUM_ITEMS)
    pair_counts = np.zeros((NUM_ITEMS, NUM_ITEMS))

    schedules = []

    for sched_idx in range(num_schedules):
        schedule = {"schedule_id": sched_idx, "tasks": []}

        # Track within-schedule item usage to encourage spread
        within_schedule_counts = np.zeros(NUM_ITEMS)

        for task_idx in range(num_tasks):
            # Compute sampling weights: prefer under-represented items
            # Combine global balance + within-schedule spread
            global_weight = 1.0 / (item_counts + 1)
            local_weight = 1.0 / (within_schedule_counts + 1)
            weights = global_weight * 0.7 + local_weight * 0.3
            weights = weights / weights.sum()

            # Sample subset
            chosen_indices = rng.choice(
                NUM_ITEMS, size=items_per_subset, replace=False, p=weights
            )
            chosen_ids = [ITEM_IDS[i] for i in chosen_indices]

            schedule["tasks"].append(
                {"task_index": task_idx, "item_ids": sorted(chosen_ids)}
            )

            # Update counts
            item_counts[chosen_indices] += 1
            within_schedule_counts[chosen_indices] += 1
            for i in chosen_indices:
                for j in chosen_indices:
                    if i != j:
                        pair_counts[i][j] += 1

        schedules.append(schedule)

    # Print balance diagnostics
    total_trials = num_schedules * num_tasks
    expected_per_item = total_trials * items_per_subset / NUM_ITEMS
    print(f"Total trials: {total_trials}")
    print(f"Expected appearances per item: {expected_per_item:.1f}")
    print(f"Actual range: {item_counts.min():.0f} - {item_counts.max():.0f}")
    print(f"Actual mean: {item_counts.mean():.1f}, std: {item_counts.std():.1f}")

    # Pairwise balance
    mask = np.triu(np.ones((NUM_ITEMS, NUM_ITEMS), dtype=bool), k=1)
    pair_vals = pair_counts[mask]
    print(f"Pairwise co-occurrence range: {pair_vals.min():.0f} - {pair_vals.max():.0f}")
    print(f"Pairwise mean: {pair_vals.mean():.1f}, std: {pair_vals.std():.1f}")

    return schedules


def save_schedules(schedules, path="data/schedules.json"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(schedules, f, indent=2)
    print(f"Saved {len(schedules)} schedules to {path}")


if __name__ == "__main__":
    schedules = generate_schedules()
    save_schedules(schedules)
