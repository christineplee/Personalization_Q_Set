"""
Schedule generator v4: Stratified sampling with flexible quotas + aggressive refinement.
"""

import json
import numpy as np
from pathlib import Path

VIGNETTE_IDS = [f"t{i}" for i in range(1,6)] + [f"v{i}" for i in range(1,6)] + \
               [f"s{i}" for i in range(1,6)] + [f"i{i}" for i in range(1,6)]
PROJECTIVE_IDS = [f"p{i}" for i in range(1,13)]
PRIMAL_IDS = [f"pi_{i}" for i in range(1,19)]
BIGFIVE_IDS = [f"bfi_{i}" for i in range(1,31)]

ALL_IDS = VIGNETTE_IDS + PROJECTIVE_IDS + PRIMAL_IDS + BIGFIVE_IDS
NUM_ITEMS = len(ALL_IDS)

ITEM_TO_SECTION = {}
for item in VIGNETTE_IDS: ITEM_TO_SECTION[item] = 'vignettes'
for item in PROJECTIVE_IDS: ITEM_TO_SECTION[item] = 'projective'
for item in PRIMAL_IDS: ITEM_TO_SECTION[item] = 'primals'
for item in BIGFIVE_IDS: ITEM_TO_SECTION[item] = 'bigfive'

SECTION_ITEMS = {
    'vignettes': VIGNETTE_IDS,
    'projective': PROJECTIVE_IDS,
    'primals': PRIMAL_IDS,
    'bigfive': BIGFIVE_IDS,
}

NUM_SCHEDULES = 200
NUM_TASKS = 8
ITEMS_PER_SUBSET = 10

# Flexible quotas: minimum per section, remaining filled freely
# This guarantees every section is represented while allowing marginal balance
SECTION_MIN = {'vignettes': 2, 'projective': 1, 'primals': 1, 'bigfive': 2}
# 2+1+1+2 = 6 fixed, 4 flexible


def generate_schedules(seed=42):
    rng = np.random.RandomState(seed)
    item_to_idx = {item: i for i, item in enumerate(ALL_IDS)}
    
    item_counts = np.zeros(NUM_ITEMS)
    pair_counts = np.zeros((NUM_ITEMS, NUM_ITEMS))
    
    schedules = []
    
    for sched_idx in range(NUM_SCHEDULES):
        schedule = {"schedule_id": sched_idx, "tasks": []}
        within_counts = np.zeros(NUM_ITEMS)
        
        for task_idx in range(NUM_TASKS):
            chosen = []
            chosen_set = set()
            
            # Step 1: Fill minimum quotas per section
            for section, min_n in SECTION_MIN.items():
                pool = [item for item in SECTION_ITEMS[section] if item not in chosen_set]
                w = np.array([1.0 / (item_counts[item_to_idx[i]] + within_counts[item_to_idx[i]] * 5 + 1) for i in pool])
                w /= w.sum()
                picks = rng.choice(len(pool), size=min(min_n, len(pool)), replace=False, p=w)
                for p in picks:
                    chosen.append(pool[p])
                    chosen_set.add(pool[p])
            
            # Step 2: Fill remaining 4 slots from ALL items, weighted by marginal balance
            remaining = ITEMS_PER_SUBSET - len(chosen)
            pool = [item for item in ALL_IDS if item not in chosen_set]
            for _ in range(remaining):
                w = np.array([1.0 / (item_counts[item_to_idx[i]] + within_counts[item_to_idx[i]] * 5 + 1) for i in pool])
                w /= w.sum()
                pick = rng.choice(len(pool), p=w)
                chosen.append(pool[pick])
                chosen_set.add(pool[pick])
                pool.pop(pick)
            
            schedule["tasks"].append({"task_index": task_idx, "item_ids": sorted(chosen)})
            
            for item in chosen:
                idx = item_to_idx[item]
                item_counts[idx] += 1
                within_counts[idx] += 1
            for a in chosen:
                for b in chosen:
                    ai, bi = item_to_idx[a], item_to_idx[b]
                    if ai < bi:
                        pair_counts[ai][bi] += 1
        
        schedules.append(schedule)
    
    print("=== Phase 1 (before refinement) ===")
    print_diagnostics(schedules, item_counts, pair_counts, item_to_idx)
    
    # Phase 2: Aggressive refinement
    print("\nRunning 50,000 refinement swaps...")
    for iteration in range(50000):
        s_idx = rng.randint(NUM_SCHEDULES)
        t_idx = rng.randint(NUM_TASKS)
        items = schedules[s_idx]["tasks"][t_idx]["item_ids"]
        
        # Pick item to swap out
        swap_out = items[rng.randint(len(items))]
        section = ITEM_TO_SECTION[swap_out]
        
        # Count how many from this section are in subset
        section_count = sum(1 for i in items if ITEM_TO_SECTION[i] == section)
        
        # If at minimum for this section, only swap within same section
        at_min = section_count <= SECTION_MIN.get(section, 0)
        
        if at_min:
            candidates = [i for i in SECTION_ITEMS[section] if i not in items]
        else:
            # Can swap to any section (but not one that would make another section go below min)
            candidates = [i for i in ALL_IDS if i not in items]
            # Remove candidates that would violate another section's minimum
            # (This can't happen since we're removing from current section, not others)
        
        if not candidates:
            continue
        
        out_idx = item_to_idx[swap_out]
        expected = 200.0
        expected_pair = 22.8
        
        best_score = 0
        best_cand = None
        
        # Sample subset of candidates for speed
        if len(candidates) > 15:
            sample_idx = rng.choice(len(candidates), size=15, replace=False)
            sampled = [candidates[i] for i in sample_idx]
        else:
            sampled = candidates
        
        for cand in sampled:
            cand_idx = item_to_idx[cand]
            
            # Marginal: want to reduce deviation from expected
            old_dev = abs(item_counts[out_idx] - expected) + abs(item_counts[cand_idx] - expected)
            new_dev = abs(item_counts[out_idx] - 1 - expected) + abs(item_counts[cand_idx] + 1 - expected)
            marginal_gain = old_dev - new_dev
            
            # Pairwise: reduce max pair deviation
            pair_gain = 0
            for other in items:
                if other == swap_out:
                    continue
                oi = item_to_idx[other]
                i1, j1 = min(out_idx, oi), max(out_idx, oi)
                i2, j2 = min(cand_idx, oi), max(cand_idx, oi)
                pair_gain += abs(pair_counts[i1][j1] - expected_pair) - abs(pair_counts[i1][j1] - 1 - expected_pair)
                pair_gain += abs(pair_counts[i2][j2] - expected_pair) - abs(pair_counts[i2][j2] + 1 - expected_pair)
            
            score = marginal_gain * 3 + pair_gain * 1
            if score > best_score:
                best_score = score
                best_cand = cand
        
        if best_cand and best_score > 0.1:
            in_idx = item_to_idx[best_cand]
            new_items = sorted([best_cand if i == swap_out else i for i in items])
            schedules[s_idx]["tasks"][t_idx]["item_ids"] = new_items
            
            item_counts[out_idx] -= 1
            item_counts[in_idx] += 1
            
            for other in items:
                if other == swap_out:
                    continue
                oi = item_to_idx[other]
                i, j = min(out_idx, oi), max(out_idx, oi)
                pair_counts[i][j] -= 1
                i, j = min(in_idx, oi), max(in_idx, oi)
                pair_counts[i][j] += 1
    
    print("\n=== Phase 2 (after refinement) ===")
    print_diagnostics(schedules, item_counts, pair_counts, item_to_idx)
    
    return schedules


def print_diagnostics(schedules, item_counts, pair_counts, item_to_idx):
    total_trials = NUM_SCHEDULES * NUM_TASKS
    
    print(f"  Marginal: range {item_counts.min():.0f}-{item_counts.max():.0f}, "
          f"mean {item_counts.mean():.1f}, std {item_counts.std():.1f}, "
          f"CV {item_counts.std()/item_counts.mean()*100:.1f}%")
    
    mask = np.triu(np.ones((NUM_ITEMS, NUM_ITEMS), dtype=bool), k=1)
    pv = pair_counts[mask]
    print(f"  Pairwise: range {pv.min():.0f}-{pv.max():.0f}, "
          f"mean {pv.mean():.1f}, std {pv.std():.1f}, "
          f"CV {pv.std()/pv.mean()*100:.1f}%")
    print(f"  Pairs with 0 co-occurrence: {np.sum(pv == 0)}")
    
    zero_counts = {sec: 0 for sec in SECTION_ITEMS}
    for s in schedules:
        for t in s['tasks']:
            present = set(ITEM_TO_SECTION[i] for i in t['item_ids'])
            for sec in zero_counts:
                if sec not in present:
                    zero_counts[sec] += 1
    print(f"  Section-degenerate subsets: {sum(zero_counts.values())}")
    
    for sec in ['vignettes', 'projective', 'primals', 'bigfive']:
        counts = [sum(1 for i in t['item_ids'] if ITEM_TO_SECTION[i] == sec)
                  for s in schedules for t in s['tasks']]
        arr = np.array(counts)
        print(f"  {sec:12s} per subset: {arr.min()}-{arr.max()}, mean {arr.mean():.1f}")
    
    # Unique items per participant
    uniq = [len(set(i for t in s['tasks'] for i in t['item_ids'])) for s in schedules]
    print(f"  Items per participant: {min(uniq)}-{max(uniq)}, mean {np.mean(uniq):.1f}")


def save_schedules(schedules, path="data/schedules.json"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(schedules, f, indent=2)
    print(f"\nSaved {len(schedules)} schedules to {path}")


if __name__ == "__main__":
    schedules = generate_schedules()
    save_schedules(schedules)
