"""
LASSO Regression Analysis for the Minimal Personalization Study
================================================================

Research Question: What is the minimal set of user profile items that allows
an LLM to produce better-adapted responses?

This script analyzes data exported from the study's /api/admin/export endpoint.
It performs:
  1. Data loading and preparation
  2. Construction of the binary item-presence matrix (X)
  3. LASSO regression with cross-validation (primary analysis)
  4. Per-dimension decomposition analysis
  5. Stability analysis via bootstrap
  6. Random forest permutation importance (robustness check)
  7. Tier-level comparison
  8. Visualization

Usage:
  python analysis.py --data export.json --output results/

Requirements:
  pip install numpy pandas scikit-learn matplotlib seaborn scipy
"""

import json
import argparse
import os
import numpy as np
import pandas as pd
from collections import Counter

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LassoCV, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, RepeatedKFold
from sklearn.inspection import permutation_importance
from scipy import stats


# ══════════════════════════════════════════════════════════════════════
# STEP 1: LOAD AND PREPARE DATA
# ══════════════════════════════════════════════════════════════════════

def load_data(filepath):
    """
    Load the exported JSON from /api/admin/export.
    
    The export contains:
      - sessions: participant records with profiling data
      - responses: LLM responses with item_ids (which items were in the prompt)
      - evaluations: participant ratings per task
      - attention_checks: attention check results
      - questions: the 80 profiling items
      - tasks: the 8 task prompts
    """
    print("STEP 1: Loading data...")
    
    with open(filepath) as f:
        data = json.load(f)
    
    print(f"  Sessions:         {len(data['sessions'])}")
    print(f"  Responses:        {len(data['responses'])}")
    print(f"  Evaluations:      {len(data['evaluations'])}")
    print(f"  Attention checks: {len(data['attention_checks'])}")
    print(f"  Questions:        {len(data['questions'])}")
    print(f"  Tasks:            {len(data['tasks'])}")
    
    return data


def filter_inattentive_participants(data, max_failures=2):
    """
    STEP 2: Remove participants who failed too many attention checks.
    
    We exclude anyone with more than max_failures failed attention checks.
    This threshold is set to 2 because the study auto-terminates at 3,
    so participants with 3+ failures have incomplete data anyway.
    Participants with 0-2 failures are kept but flagged.
    """
    print(f"\nSTEP 2: Filtering inattentive participants (threshold: >{max_failures} failures)...")
    
    # Count failures per session
    attn_df = pd.DataFrame(data['attention_checks'])
    if len(attn_df) == 0:
        print("  No attention check data found. Skipping filter.")
        return set(), set()
    
    failures = attn_df[attn_df['passed'] == 0].groupby('session_id').size()
    passes = attn_df[attn_df['passed'] == 1].groupby('session_id').size()
    
    all_sessions = set(s['session_id'] for s in data['sessions'] if s['status'] == 'complete')
    excluded = set(failures[failures > max_failures].index) if len(failures) > 0 else set()
    included = all_sessions - excluded
    
    print(f"  Complete sessions: {len(all_sessions)}")
    print(f"  Excluded (>{max_failures} failures): {len(excluded)}")
    print(f"  Included: {len(included)}")
    
    if len(failures) > 0:
        print(f"  Failure distribution:")
        fail_dist = failures.value_counts().sort_index()
        for n_fail, count in fail_dist.items():
            print(f"    {n_fail} failures: {count} participants")
    
    return included, excluded


def build_analysis_dataframe(data, included_sessions):
    """
    STEP 3: Construct the analysis dataframe.
    
    Each row is one trial (participant × task). Columns include:
      - session_id, task_id: identifiers
      - 80 binary columns (item_X_present): 1 if item X was in the LLM prompt
      - eval_tone, eval_verbosity, eval_structure, eval_initiative, eval_overall: ratings
      - eval_relevance: topic relevance covariate
    
    This is the core data structure for LASSO. The binary columns are
    the predictors (X), and the evaluation scores are the outcomes (Y).
    """
    print("\nSTEP 3: Building analysis dataframe...")
    
    # Get all 80 item IDs
    all_item_ids = sorted([q['id'] for q in data['questions']])
    print(f"  Total profiling items: {len(all_item_ids)}")
    
    # Index responses and evaluations by (session_id, task_id)
    responses_by_key = {}
    for r in data['responses']:
        key = (r['session_id'], r['task_id'])
        responses_by_key[key] = r
    
    evals_by_key = {}
    for e in data['evaluations']:
        key = (e['session_id'], e['task_id'])
        evals_by_key[key] = e
    
    # Build rows
    rows = []
    for session in data['sessions']:
        sid = session['session_id']
        if sid not in included_sessions:
            continue
        
        for r in data['responses']:
            if r['session_id'] != sid:
                continue
            
            key = (sid, r['task_id'])
            ev = evals_by_key.get(key)
            if ev is None:
                continue  # No evaluation for this trial
            
            # Build the binary item-presence vector
            item_ids_in_prompt = set(json.loads(r['item_ids']) if isinstance(r['item_ids'], str) else r['item_ids'])
            
            row = {
                'session_id': sid,
                'task_id': r['task_id'],
                'task_index': r['task_index'],
            }
            
            # 80 binary indicators
            for item_id in all_item_ids:
                row[f'item_{item_id}'] = 1 if item_id in item_ids_in_prompt else 0
            
            # Evaluation scores
            row['eval_tone'] = ev.get('eval_tone')
            row['eval_verbosity'] = ev.get('eval_verbosity')
            row['eval_structure'] = ev.get('eval_structure')
            row['eval_initiative'] = ev.get('eval_initiative')
            row['eval_overall'] = ev.get('eval_overall')
            row['eval_relevance'] = ev.get('eval_relevance')
            
            rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Drop rows with missing evaluations
    eval_cols = ['eval_tone', 'eval_verbosity', 'eval_structure', 'eval_initiative', 'eval_overall']
    df = df.dropna(subset=eval_cols)
    
    n_participants = df['session_id'].nunique()
    n_trials = len(df)
    item_cols = [c for c in df.columns if c.startswith('item_')]
    
    print(f"  Participants: {n_participants}")
    print(f"  Trials (rows): {n_trials}")
    print(f"  Item columns: {len(item_cols)}")
    print(f"  Observations per predictor (N/p): {n_trials / len(item_cols):.1f}")
    
    # Verify item balance in the actual data
    item_presence = df[item_cols].sum()
    print(f"  Item presence range: {item_presence.min():.0f} - {item_presence.max():.0f} "
          f"(mean {item_presence.mean():.1f})")
    
    return df, item_cols, eval_cols


# ══════════════════════════════════════════════════════════════════════
# STEP 4: PRIMARY LASSO ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def run_lasso_analysis(df, item_cols, dv_col, relevance_as_covariate=True):
    """
    Run LASSO regression with cross-validation.
    
    The LASSO (Least Absolute Shrinkage and Selection Operator) does
    two things simultaneously:
      1. Estimates the effect of each item on the outcome
      2. Performs feature selection by shrinking unimportant effects to exactly zero
    
    Items with non-zero coefficients after LASSO are the ones that
    meaningfully predict satisfaction — they form the "minimal set."
    
    We use LassoCV which automatically selects the regularization strength
    (alpha) via cross-validation, balancing model fit against sparsity.
    
    Parameters:
      - df: the analysis dataframe
      - item_cols: list of 80 binary indicator column names
      - dv_col: the outcome variable (e.g., 'eval_overall')
      - relevance_as_covariate: if True, include eval_relevance as a control
    
    Returns:
      - Dictionary of results including coefficients and selected items
    """
    print(f"\n  Running LASSO for DV: {dv_col}...")
    
    # Prepare X matrix
    feature_cols = list(item_cols)
    if relevance_as_covariate and 'eval_relevance' in df.columns:
        feature_cols = feature_cols + ['eval_relevance']
    
    X = df[feature_cols].values.astype(float)
    y = df[dv_col].values.astype(float)
    
    # Remove any NaN rows
    valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X, y = X[valid], y[valid]
    
    # Mean-center Y within participants to remove individual response tendencies
    # (Some people are generally generous raters, others are harsh)
    session_ids = df.loc[valid.nonzero()[0] if isinstance(valid, np.ndarray) else valid, 'session_id'].values
    y_centered = y.copy()
    for sid in np.unique(session_ids):
        mask = session_ids == sid
        y_centered[mask] = y[mask] - y[mask].mean()
    
    print(f"    Observations: {len(y)}")
    print(f"    Features: {X.shape[1]} ({len(item_cols)} items"
          f"{' + relevance' if relevance_as_covariate else ''})")
    print(f"    Y mean: {y.mean():.2f}, Y std: {y.std():.2f}")
    print(f"    Y centered mean: {y_centered.mean():.4f}, Y centered std: {y_centered.std():.2f}")
    
    # ── LassoCV: automatically selects best alpha via cross-validation ──
    # We use 10-fold CV repeated 3 times for stability
    # alphas=100 tests a range of regularization strengths
    lasso_cv = LassoCV(
        alphas=100,
        cv=RepeatedKFold(n_splits=10, n_repeats=3, random_state=42),
        max_iter=10000,
        random_state=42,
    )
    lasso_cv.fit(X, y_centered)
    
    # Extract results
    coefs = pd.Series(lasso_cv.coef_, index=feature_cols)
    item_coefs = coefs[item_cols]
    nonzero = item_coefs[item_coefs != 0].sort_values(ascending=False)
    zero = item_coefs[item_coefs == 0]
    
    # Cross-validated R² score
    cv_scores = cross_val_score(
        Lasso(alpha=lasso_cv.alpha_, max_iter=10000),
        X, y_centered,
        cv=RepeatedKFold(n_splits=10, n_repeats=3, random_state=42),
        scoring='r2'
    )
    
    print(f"    Best alpha: {lasso_cv.alpha_:.6f}")
    print(f"    CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    print(f"    Non-zero items: {len(nonzero)} / {len(item_cols)}")
    print(f"    Zero items: {len(zero)} / {len(item_cols)}")
    
    if relevance_as_covariate and 'eval_relevance' in feature_cols:
        print(f"    Relevance coefficient: {coefs.get('eval_relevance', 'N/A'):.4f}")
    
    if len(nonzero) > 0:
        print(f"    Top items (non-zero coefficients):")
        for item, coef in nonzero.head(15).items():
            item_name = item.replace('item_', '')
            direction = "+" if coef > 0 else "-"
            print(f"      {direction} {item_name:12s}: {coef:+.4f}")
    
    return {
        'dv': dv_col,
        'alpha': lasso_cv.alpha_,
        'cv_r2_mean': cv_scores.mean(),
        'cv_r2_std': cv_scores.std(),
        'all_coefs': coefs,
        'item_coefs': item_coefs,
        'nonzero_items': nonzero,
        'n_nonzero': len(nonzero),
        'n_obs': len(y),
        'relevance_coef': coefs.get('eval_relevance', None),
    }


def run_all_lasso(df, item_cols, eval_cols):
    """
    STEP 4: Run LASSO for each outcome variable.
    
    Primary analysis: eval_overall (the main research question)
    Decomposition: eval_tone, eval_verbosity, eval_structure, eval_initiative
    
    The decomposition tells us not just WHICH items matter, but HOW they
    matter — through which dimension of communication adaptation.
    """
    print("\n" + "=" * 70)
    print("STEP 4: PRIMARY LASSO ANALYSIS")
    print("=" * 70)
    
    results = {}
    
    # Primary analysis
    print("\n── Primary Analysis: Overall Personalization Fit ──")
    results['overall'] = run_lasso_analysis(df, item_cols, 'eval_overall')
    
    # Decomposition analysis
    dimension_dvs = ['eval_tone', 'eval_verbosity', 'eval_structure', 'eval_initiative']
    print("\n── Decomposition Analysis: Per-Dimension ──")
    for dv in dimension_dvs:
        dim_name = dv.replace('eval_', '')
        results[dim_name] = run_lasso_analysis(df, item_cols, dv)
    
    return results


# ══════════════════════════════════════════════════════════════════════
# STEP 5: BOOTSTRAP STABILITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════

def bootstrap_stability(df, item_cols, dv_col='eval_overall', n_bootstrap=500):
    """
    STEP 5: Test how stable the LASSO selection is.
    
    LASSO can be sensitive to the specific data sample. Bootstrap stability
    analysis runs LASSO on many resampled datasets and counts how often
    each item is selected (has a non-zero coefficient).
    
    An item selected in >80% of bootstraps is "stable" — it's robust to
    sampling variation. An item selected in 30-80% is "moderately stable."
    Below 30% is unreliable.
    
    This is the gold standard for validating LASSO feature selection
    (Meinshausen & Bühlmann, 2010).
    """
    print("\n" + "=" * 70)
    print("STEP 5: BOOTSTRAP STABILITY ANALYSIS")
    print("=" * 70)
    print(f"  Running {n_bootstrap} bootstrap iterations...")
    
    # Prepare data
    feature_cols = list(item_cols) + (['eval_relevance'] if 'eval_relevance' in df.columns else [])
    X = df[feature_cols].values.astype(float)
    y = df[dv_col].values.astype(float)
    
    # Mean-center within participant
    session_ids = df['session_id'].values
    y_centered = y.copy()
    for sid in np.unique(session_ids):
        mask = session_ids == sid
        y_centered[mask] = y[mask] - y[mask].mean()
    
    valid = ~(np.isnan(X).any(axis=1) | np.isnan(y_centered))
    X, y_centered = X[valid], y_centered[valid]
    session_ids_valid = session_ids[valid]
    
    # Get the alpha from the full-data LassoCV
    lasso_cv = LassoCV(alphas=100, cv=5, max_iter=10000, random_state=42)
    lasso_cv.fit(X, y_centered)
    alpha = lasso_cv.alpha_
    
    # Bootstrap: resample PARTICIPANTS (not individual trials)
    # This preserves the within-participant correlation structure
    unique_sessions = np.unique(session_ids_valid)
    selection_counts = np.zeros(len(item_cols))
    rng = np.random.RandomState(42)
    
    for b in range(n_bootstrap):
        # Resample participants with replacement
        boot_sessions = rng.choice(unique_sessions, size=len(unique_sessions), replace=True)
        boot_idx = np.concatenate([np.where(session_ids_valid == s)[0] for s in boot_sessions])
        
        X_boot = X[boot_idx]
        y_boot = y_centered[boot_idx]
        
        # Fit LASSO with the same alpha
        lasso = Lasso(alpha=alpha, max_iter=10000)
        lasso.fit(X_boot, y_boot)
        
        # Record which items have non-zero coefficients
        # (Only check the item columns, not relevance)
        item_coefs = lasso.coef_[:len(item_cols)]
        selection_counts += (item_coefs != 0).astype(int)
        
        if (b + 1) % 100 == 0:
            print(f"    Completed {b + 1}/{n_bootstrap}")
    
    # Selection probability for each item
    selection_prob = selection_counts / n_bootstrap
    stability = pd.Series(selection_prob, index=item_cols).sort_values(ascending=False)
    
    stable = stability[stability >= 0.80]
    moderate = stability[(stability >= 0.30) & (stability < 0.80)]
    unstable = stability[stability < 0.30]
    
    print(f"\n  Results:")
    print(f"    Stable items (≥80%):     {len(stable)}")
    print(f"    Moderate items (30-80%): {len(moderate)}")
    print(f"    Unstable items (<30%):   {len(unstable)}")
    
    if len(stable) > 0:
        print(f"\n    Stable items:")
        for item, prob in stable.items():
            print(f"      {item.replace('item_', ''):12s}: selected in {prob*100:.1f}% of bootstraps")
    
    if len(moderate) > 0:
        print(f"\n    Moderately stable items:")
        for item, prob in moderate.items():
            print(f"      {item.replace('item_', ''):12s}: selected in {prob*100:.1f}% of bootstraps")
    
    return stability


# ══════════════════════════════════════════════════════════════════════
# STEP 6: RANDOM FOREST PERMUTATION IMPORTANCE (ROBUSTNESS CHECK)
# ══════════════════════════════════════════════════════════════════════

def random_forest_importance(df, item_cols, dv_col='eval_overall'):
    """
    STEP 6: Random forest with permutation importance.
    
    This serves as a robustness check against LASSO. Random forests
    capture non-linear relationships and interactions that LASSO misses.
    
    Permutation importance measures how much prediction degrades when
    each feature is randomly shuffled — features whose shuffling hurts
    prediction most are the most important.
    
    If the same items rank highly in both LASSO and random forest,
    we have stronger evidence they truly matter.
    """
    print("\n" + "=" * 70)
    print("STEP 6: RANDOM FOREST PERMUTATION IMPORTANCE")
    print("=" * 70)
    
    feature_cols = list(item_cols)
    if 'eval_relevance' in df.columns:
        feature_cols = feature_cols + ['eval_relevance']
    
    X = df[feature_cols].values.astype(float)
    y = df[dv_col].values.astype(float)
    
    valid = ~(np.isnan(X).any(axis=1) | np.isnan(y))
    X, y = X[valid], y[valid]
    
    # Fit random forest
    rf = RandomForestRegressor(
        n_estimators=500,
        max_depth=10,
        min_samples_leaf=20,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X, y)
    
    # Cross-validated R²
    cv_scores = cross_val_score(rf, X, y, cv=5, scoring='r2')
    print(f"  RF CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    # Permutation importance
    perm_imp = permutation_importance(
        rf, X, y,
        n_repeats=30,
        random_state=42,
        n_jobs=-1,
    )
    
    importance = pd.Series(perm_imp.importances_mean, index=feature_cols)
    item_importance = importance[item_cols].sort_values(ascending=False)
    
    print(f"\n  Top 15 items by permutation importance:")
    for item, imp in item_importance.head(15).items():
        item_name = item.replace('item_', '')
        print(f"    {item_name:12s}: {imp:.4f}")
    
    return item_importance


# ══════════════════════════════════════════════════════════════════════
# STEP 7: TIER-LEVEL COMPARISON
# ══════════════════════════════════════════════════════════════════════

def tier_comparison(lasso_results, stability, rf_importance, item_cols):
    """
    STEP 7: Compare which TYPE of information matters most.
    
    This aggregates importance scores by question tier:
      - Vignettes (t, v, s, i items): direct communication preferences
      - Projective proxies (p items): indirect preference signals
      - Primals (pi items): world beliefs
      - Big Five (bfi items): personality traits
    
    This answers the theoretical question: are validated psychological
    instruments better predictors than simple lifestyle questions?
    """
    print("\n" + "=" * 70)
    print("STEP 7: TIER-LEVEL COMPARISON")
    print("=" * 70)
    
    # Map items to tiers
    tier_map = {}
    for col in item_cols:
        item = col.replace('item_', '')
        if item.startswith(('t', 'v', 's', 'i')) and not item.startswith(('item', 'id', 'pi')):
            # Need more careful check
            if item.startswith('t') and item[1:].isdigit(): tier_map[col] = 'Vignettes'
            elif item.startswith('v') and item[1:].isdigit(): tier_map[col] = 'Vignettes'
            elif item.startswith('s') and item[1:].isdigit(): tier_map[col] = 'Vignettes'
            elif item.startswith('i') and item[1:].isdigit(): tier_map[col] = 'Vignettes'
            elif item.startswith('pi_'): tier_map[col] = 'Primals'
            elif item.startswith('p') and item[1:].isdigit(): tier_map[col] = 'Projective'
            elif item.startswith('bfi_'): tier_map[col] = 'Big Five'
        elif item.startswith('pi_'): tier_map[col] = 'Primals'
        elif item.startswith('p') and not item.startswith('pi'): tier_map[col] = 'Projective'
        elif item.startswith('bfi_'): tier_map[col] = 'Big Five'
    
    # Aggregate by tier
    overall_coefs = lasso_results['overall']['item_coefs'].abs()
    
    tier_stats = []
    for tier in ['Vignettes', 'Projective', 'Primals', 'Big Five']:
        tier_items = [c for c, t in tier_map.items() if t == tier]
        
        # LASSO: mean absolute coefficient
        lasso_mean = overall_coefs[tier_items].mean()
        lasso_nonzero = (overall_coefs[tier_items] != 0).sum()
        
        # Stability: mean selection probability
        stab_mean = stability[tier_items].mean()
        
        # RF: mean importance
        rf_mean = rf_importance[tier_items].mean()
        
        tier_stats.append({
            'Tier': tier,
            'N items': len(tier_items),
            'LASSO |β| mean': lasso_mean,
            'LASSO nonzero': lasso_nonzero,
            'Stability mean': stab_mean,
            'RF importance mean': rf_mean,
        })
        
        print(f"\n  {tier} ({len(tier_items)} items):")
        print(f"    LASSO mean |β|:     {lasso_mean:.4f}")
        print(f"    LASSO non-zero:     {lasso_nonzero} / {len(tier_items)}")
        print(f"    Bootstrap stability: {stab_mean:.2%}")
        print(f"    RF importance:       {rf_mean:.4f}")
    
    return pd.DataFrame(tier_stats)


# ══════════════════════════════════════════════════════════════════════
# STEP 8: SEQUENTIAL FORWARD SELECTION (Diminishing Returns Curve)
# ══════════════════════════════════════════════════════════════════════

def sequential_forward_selection(df, item_cols, dv_col='eval_overall', max_items=30):
    """
    STEP 8: Build the diminishing returns curve.
    
    Starting from the most important item (per LASSO), sequentially add
    the next most important and measure cross-validated R² at each step.
    
    This produces the "elbow curve" — the point where adding more items
    yields negligible improvement is the minimal set size.
    """
    print("\n" + "=" * 70)
    print("STEP 8: SEQUENTIAL FORWARD SELECTION")
    print("=" * 70)
    
    # Get item ranking from LASSO
    feature_cols = list(item_cols) + (['eval_relevance'] if 'eval_relevance' in df.columns else [])
    X_full = df[feature_cols].values.astype(float)
    y = df[dv_col].values.astype(float)
    
    session_ids = df['session_id'].values
    y_centered = y.copy()
    for sid in np.unique(session_ids):
        mask = session_ids == sid
        y_centered[mask] = y[mask] - y[mask].mean()
    
    valid = ~(np.isnan(X_full).any(axis=1) | np.isnan(y_centered))
    X_full, y_centered = X_full[valid], y_centered[valid]
    
    # Rank items by absolute LASSO coefficient
    lasso_cv = LassoCV(alphas=100, cv=5, max_iter=10000, random_state=42)
    lasso_cv.fit(X_full, y_centered)
    item_coefs = np.abs(lasso_cv.coef_[:len(item_cols)])
    item_ranking = np.argsort(-item_coefs)  # Descending
    
    # Sequential forward selection
    r2_curve = []
    selected_items = []
    
    max_items = min(max_items, len(item_cols))
    
    for k in range(1, max_items + 1):
        # Use top-k items (plus relevance if applicable)
        top_k_idx = item_ranking[:k]
        col_idx = list(top_k_idx)
        if 'eval_relevance' in feature_cols:
            col_idx.append(len(item_cols))  # Relevance is last column
        
        X_k = X_full[:, col_idx]
        
        # Cross-validated R²
        lasso_k = Lasso(alpha=lasso_cv.alpha_, max_iter=10000)
        scores = cross_val_score(lasso_k, X_k, y_centered, cv=5, scoring='r2')
        
        item_name = item_cols[item_ranking[k-1]].replace('item_', '')
        r2_curve.append({
            'n_items': k,
            'cv_r2': scores.mean(),
            'cv_r2_std': scores.std(),
            'added_item': item_name,
        })
        selected_items.append(item_name)
        
        if k <= 10 or k % 5 == 0:
            print(f"    k={k:2d}: CV R² = {scores.mean():.4f} (±{scores.std():.4f})  added: {item_name}")
    
    r2_df = pd.DataFrame(r2_curve)
    
    # Find elbow point (where marginal gain drops below threshold)
    if len(r2_df) > 1:
        marginal_gains = r2_df['cv_r2'].diff()
        # Elbow: first point where marginal gain < 10% of first gain
        first_gain = marginal_gains.iloc[1] if len(marginal_gains) > 1 else 0
        if first_gain > 0:
            threshold = first_gain * 0.10
            elbow_candidates = r2_df[marginal_gains < threshold].index
            elbow = elbow_candidates[0] if len(elbow_candidates) > 0 else len(r2_df)
        else:
            elbow = len(r2_df)
        
        print(f"\n  Suggested minimal set size: ~{elbow} items")
        print(f"  Items in minimal set: {selected_items[:elbow]}")
    
    return r2_df


# ══════════════════════════════════════════════════════════════════════
# STEP 9: VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════

def create_visualizations(lasso_results, stability, rf_importance, r2_curve, tier_stats, output_dir):
    """
    STEP 9: Generate publication-quality figures.
    """
    print("\n" + "=" * 70)
    print("STEP 9: GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})
    
    # ── Figure 1: LASSO coefficients for overall fit ──
    fig, ax = plt.subplots(figsize=(12, 8))
    coefs = lasso_results['overall']['item_coefs']
    nonzero = coefs[coefs != 0].sort_values()
    if len(nonzero) > 0:
        colors = ['#c44e52' if v < 0 else '#4c72b0' for v in nonzero.values]
        nonzero.index = [idx.replace('item_', '') for idx in nonzero.index]
        nonzero.plot.barh(ax=ax, color=colors)
        ax.set_xlabel('LASSO Coefficient')
        ax.set_title('Profile Items with Non-Zero LASSO Coefficients\n(Predicting Overall Personalization Fit)')
        ax.axvline(x=0, color='black', linewidth=0.5)
    else:
        ax.text(0.5, 0.5, 'No non-zero coefficients found', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('LASSO Coefficients (none significant)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig1_lasso_coefficients.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig1_lasso_coefficients.png")
    
    # ── Figure 2: Bootstrap stability ──
    fig, ax = plt.subplots(figsize=(14, 6))
    stab_sorted = stability.sort_values(ascending=False)
    stab_sorted.index = [idx.replace('item_', '') for idx in stab_sorted.index]
    colors = ['#4c72b0' if v >= 0.8 else '#dd8452' if v >= 0.3 else '#cccccc' for v in stab_sorted.values]
    stab_sorted.plot.bar(ax=ax, color=colors)
    ax.set_ylabel('Selection Probability')
    ax.set_title('Bootstrap Stability of LASSO Item Selection (500 iterations)')
    ax.axhline(y=0.8, color='red', linestyle='--', alpha=0.5, label='Stable threshold (80%)')
    ax.axhline(y=0.3, color='orange', linestyle='--', alpha=0.5, label='Moderate threshold (30%)')
    ax.legend()
    plt.xticks(rotation=90, fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig2_bootstrap_stability.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig2_bootstrap_stability.png")
    
    # ── Figure 3: Diminishing returns curve ──
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(r2_curve['n_items'], r2_curve['cv_r2'], 'o-', color='#4c72b0', markersize=4)
    ax.fill_between(
        r2_curve['n_items'],
        r2_curve['cv_r2'] - r2_curve['cv_r2_std'],
        r2_curve['cv_r2'] + r2_curve['cv_r2_std'],
        alpha=0.2, color='#4c72b0'
    )
    ax.set_xlabel('Number of Profile Items')
    ax.set_ylabel('Cross-Validated R²')
    ax.set_title('Diminishing Returns: Prediction Accuracy vs. Number of Profile Items')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig3_diminishing_returns.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig3_diminishing_returns.png")
    
    # ── Figure 4: Per-dimension decomposition ──
    fig, axes = plt.subplots(1, 4, figsize=(20, 6), sharey=True)
    dims = ['tone', 'verbosity', 'structure', 'initiative']
    for ax, dim in zip(axes, dims):
        coefs = lasso_results[dim]['item_coefs']
        nonzero = coefs[coefs != 0].sort_values()
        if len(nonzero) > 0:
            colors = ['#c44e52' if v < 0 else '#4c72b0' for v in nonzero.values]
            labels = [idx.replace('item_', '') for idx in nonzero.index]
            ax.barh(range(len(nonzero)), nonzero.values, color=colors)
            ax.set_yticks(range(len(nonzero)))
            ax.set_yticklabels(labels, fontsize=7)
        ax.set_title(dim.capitalize())
        ax.axvline(x=0, color='black', linewidth=0.5)
    axes[0].set_ylabel('Profile Items')
    fig.suptitle('LASSO Coefficients by Evaluation Dimension', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig4_dimension_decomposition.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig4_dimension_decomposition.png")
    
    # ── Figure 5: Tier comparison ──
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    tiers = tier_stats['Tier']
    
    axes[0].bar(tiers, tier_stats['LASSO |β| mean'], color='#4c72b0')
    axes[0].set_title('Mean |LASSO Coefficient|')
    axes[0].set_ylabel('Mean |β|')
    
    axes[1].bar(tiers, tier_stats['Stability mean'], color='#dd8452')
    axes[1].set_title('Mean Bootstrap Stability')
    axes[1].set_ylabel('Selection Probability')
    
    axes[2].bar(tiers, tier_stats['RF importance mean'], color='#55a868')
    axes[2].set_title('Mean RF Importance')
    axes[2].set_ylabel('Permutation Importance')
    
    for ax in axes:
        ax.tick_params(axis='x', rotation=15)
    
    fig.suptitle('Which Type of Profile Information Predicts Personalization Best?', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig5_tier_comparison.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig5_tier_comparison.png")
    
    # ── Figure 6: LASSO vs RF agreement ──
    fig, ax = plt.subplots(figsize=(8, 8))
    overall_coefs = lasso_results['overall']['item_coefs'].abs()
    rf_imp = rf_importance[lasso_results['overall']['item_coefs'].index]
    
    ax.scatter(overall_coefs, rf_imp, alpha=0.6, color='#4c72b0')
    for i, (lasso_val, rf_val) in enumerate(zip(overall_coefs, rf_imp)):
        if lasso_val > overall_coefs.quantile(0.9) or rf_val > rf_imp.quantile(0.9):
            item_name = overall_coefs.index[i].replace('item_', '')
            ax.annotate(item_name, (lasso_val, rf_val), fontsize=7, alpha=0.8)
    
    ax.set_xlabel('LASSO |Coefficient|')
    ax.set_ylabel('RF Permutation Importance')
    ax.set_title('Agreement Between LASSO and Random Forest')
    r_val, p_val = stats.spearmanr(overall_coefs, rf_imp)
    ax.text(0.05, 0.95, f'Spearman r = {r_val:.3f} (p = {p_val:.4f})',
            transform=ax.transAxes, fontsize=10, verticalalignment='top')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig6_lasso_rf_agreement.png'), bbox_inches='tight')
    plt.close()
    print(f"  Saved fig6_lasso_rf_agreement.png")


# ══════════════════════════════════════════════════════════════════════
# STEP 10: SUMMARY REPORT
# ══════════════════════════════════════════════════════════════════════

def generate_summary(lasso_results, stability, rf_importance, r2_curve, tier_stats, output_dir):
    """
    STEP 10: Generate a text summary of all findings.
    """
    print("\n" + "=" * 70)
    print("STEP 10: SUMMARY")
    print("=" * 70)
    
    # The minimal set: items that are both LASSO-selected AND bootstrap-stable
    overall_nonzero = set(lasso_results['overall']['nonzero_items'].index)
    stable_items = set(stability[stability >= 0.5].index)
    minimal_set = overall_nonzero & stable_items
    
    summary_lines = [
        "MINIMAL PERSONALIZATION STUDY — ANALYSIS SUMMARY",
        "=" * 50,
        "",
        f"Observations: {lasso_results['overall']['n_obs']}",
        f"Predictors: 80 binary item-presence indicators",
        "",
        "PRIMARY FINDING:",
        f"  LASSO selected {lasso_results['overall']['n_nonzero']} items with non-zero coefficients",
        f"  Cross-validated R²: {lasso_results['overall']['cv_r2_mean']:.4f} (±{lasso_results['overall']['cv_r2_std']:.4f})",
        "",
        f"ROBUST MINIMAL SET ({len(minimal_set)} items — LASSO-selected AND ≥50% bootstrap stability):",
    ]
    
    for item in sorted(minimal_set):
        item_name = item.replace('item_', '')
        coef = lasso_results['overall']['item_coefs'][item]
        stab = stability[item]
        summary_lines.append(f"  {item_name:12s}: β={coef:+.4f}, stability={stab:.0%}")
    
    summary_lines.extend([
        "",
        "PER-DIMENSION BREAKDOWN:",
    ])
    
    for dim in ['tone', 'verbosity', 'structure', 'initiative']:
        n = lasso_results[dim]['n_nonzero']
        r2 = lasso_results[dim]['cv_r2_mean']
        summary_lines.append(f"  {dim:12s}: {n} items selected, CV R² = {r2:.4f}")
    
    if lasso_results['overall']['relevance_coef'] is not None:
        summary_lines.extend([
            "",
            f"RELEVANCE COVARIATE:",
            f"  Coefficient: {lasso_results['overall']['relevance_coef']:.4f}",
            f"  (Positive = higher relevance → higher satisfaction ratings)",
        ])
    
    summary_lines.extend([
        "",
        "TIER COMPARISON:",
    ])
    for _, row in tier_stats.iterrows():
        summary_lines.append(
            f"  {row['Tier']:12s}: {row['LASSO nonzero']:.0f}/{row['N items']:.0f} items selected, "
            f"stability={row['Stability mean']:.0%}, RF imp={row['RF importance mean']:.4f}"
        )
    
    summary_text = "\n".join(summary_lines)
    print(summary_text)
    
    # Save to file
    summary_path = os.path.join(output_dir, 'analysis_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(summary_text)
    print(f"\n  Saved analysis_summary.txt")
    
    # Save detailed results as CSV
    coef_df = pd.DataFrame({
        'item': [c.replace('item_', '') for c in lasso_results['overall']['item_coefs'].index],
        'lasso_coef_overall': lasso_results['overall']['item_coefs'].values,
        'lasso_coef_tone': lasso_results['tone']['item_coefs'].values,
        'lasso_coef_verbosity': lasso_results['verbosity']['item_coefs'].values,
        'lasso_coef_structure': lasso_results['structure']['item_coefs'].values,
        'lasso_coef_initiative': lasso_results['initiative']['item_coefs'].values,
        'bootstrap_stability': stability.values,
        'rf_importance': rf_importance.values,
    })
    coef_path = os.path.join(output_dir, 'item_coefficients.csv')
    coef_df.to_csv(coef_path, index=False)
    print(f"  Saved item_coefficients.csv")
    
    return summary_text


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Analyze Minimal Personalization Study data')
    parser.add_argument('--data', required=True, help='Path to export.json from /api/admin/export')
    parser.add_argument('--output', default='results', help='Output directory for figures and results')
    parser.add_argument('--bootstrap', type=int, default=500, help='Number of bootstrap iterations')
    args = parser.parse_args()
    
    # Step 1: Load data
    data = load_data(args.data)
    
    # Step 2: Filter inattentive participants
    included, excluded = filter_inattentive_participants(data)
    
    # Step 3: Build analysis dataframe
    df, item_cols, eval_cols = build_analysis_dataframe(data, included)
    
    if len(df) < 100:
        print(f"\nWARNING: Only {len(df)} observations. Results may be unreliable.")
        print("Recommended minimum: 800 observations (100 participants × 8 tasks)")
    
    # Step 4: LASSO analysis (primary + decomposition)
    lasso_results = run_all_lasso(df, item_cols, eval_cols)
    
    # Step 5: Bootstrap stability
    stability = bootstrap_stability(df, item_cols, n_bootstrap=args.bootstrap)
    
    # Step 6: Random forest importance
    rf_importance = random_forest_importance(df, item_cols)
    
    # Step 7: Tier comparison
    tier_stats = tier_comparison(lasso_results, stability, rf_importance, item_cols)
    
    # Step 8: Diminishing returns curve
    r2_curve = sequential_forward_selection(df, item_cols)
    
    # Step 9: Visualizations
    create_visualizations(lasso_results, stability, rf_importance, r2_curve, tier_stats, args.output)
    
    # Step 10: Summary
    generate_summary(lasso_results, stability, rf_importance, r2_curve, tier_stats, args.output)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print(f"Results saved to: {args.output}/")
    print("=" * 70)


if __name__ == '__main__':
    main()
