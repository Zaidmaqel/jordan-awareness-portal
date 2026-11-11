"""
JSSAA Advanced Statistical Analysis Engine.

Implements academic psychometric and inferential statistics:
- Comprehensive item and dimension descriptive statistics with 95% CIs
- NumPy implementation of Cronbach's alpha and alpha-if-item-deleted
- Pearson and Spearman rank correlation matrices with exact p-values
- Rigorous demographic group hypothesis tests (Welch's t, Mann-Whitney U,
  ANOVA, Kruskal-Wallis, effect sizes, and Bonferroni-adjusted post-hoc tests)
- Principal Component Analysis (PCA) for dimensional validation
- Dimension and item strength/weakness rankings
- Methodological cautions regarding cross-sectional causality
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

logger = logging.getLogger("JSSAA.statistics")

CAUSATION_WARNING = (
    "METHODOLOGICAL CAVEAT: All reported correlations and group differences represent "
    "statistical associations derived from cross-sectional observational data. "
    "Correlation does not imply causality or directional influence."
)


# ==========================================
# 1. Descriptive Statistics
# ==========================================

def compute_descriptive_stats(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Compute comprehensive descriptive statistics for given numeric columns:
    mean, SD (ddof=1), median, min, max, skewness, kurtosis, 95% CI, and Likert frequency %.
    """
    records = []
    n_total = len(df)

    for col in columns:
        if col not in df.columns:
            continue

        s = pd.to_numeric(df[col], errors="coerce").dropna()
        n = len(s)
        if n == 0:
            continue

        mean = float(s.mean())
        sd = float(s.std(ddof=1)) if n > 1 else 0.0
        median = float(s.median())
        val_min = float(s.min())
        val_max = float(s.max())
        skew = float(stats.skew(s, bias=False)) if n > 2 else 0.0
        kurt = float(stats.kurtosis(s, bias=False)) if n > 3 else 0.0

        # 95% Confidence Interval
        if n > 1 and sd > 0:
            se = sd / np.sqrt(n)
            t_crit = stats.t.ppf(1 - config.ALPHA / 2, df=n - 1)
            ci_lower = mean - t_crit * se
            ci_upper = mean + t_crit * se
        else:
            ci_lower, ci_upper = mean, mean

        # Likert 1-5 response frequencies
        freq_1 = ((s == 1).sum() / n) * 100.0 if n > 0 else 0.0
        freq_2 = ((s == 2).sum() / n) * 100.0 if n > 0 else 0.0
        freq_3 = ((s == 3).sum() / n) * 100.0 if n > 0 else 0.0
        freq_4 = ((s == 4).sum() / n) * 100.0 if n > 0 else 0.0
        freq_5 = ((s == 5).sum() / n) * 100.0 if n > 0 else 0.0

        records.append({
            "variable": col,
            "n": n,
            "mean": round(mean, 3),
            "sd": round(sd, 3),
            "median": round(median, 3),
            "min": round(val_min, 3),
            "max": round(val_max, 3),
            "skewness": round(skew, 3),
            "kurtosis": round(kurt, 3),
            "ci_95_lower": round(ci_lower, 3),
            "ci_95_upper": round(ci_upper, 3),
            "pct_1": round(freq_1, 1),
            "pct_2": round(freq_2, 1),
            "pct_3": round(freq_3, 1),
            "pct_4": round(freq_4, 1),
            "pct_5": round(freq_5, 1),
        })

    return pd.DataFrame(records)


# ==========================================
# 2. Reliability Analysis (Cronbach's Alpha)
# ==========================================

def cronbach_alpha_numpy(item_matrix: np.ndarray) -> float:
    """
    Vectorized NumPy calculation of Cronbach's alpha coefficient of internal consistency:
        alpha = (k / (k - 1)) * (1 - sum(var_i) / var_total)
    Uses sample variance (ddof=1).
    """
    k = item_matrix.shape[1]
    if k <= 1:
        return 1.0
    item_vars = np.var(item_matrix, axis=0, ddof=1)
    total_scores = np.sum(item_matrix, axis=1)
    total_var = np.var(total_scores, ddof=1)
    if total_var == 0 or np.isnan(total_var):
        return 0.0
    alpha = (k / (k - 1.0)) * (1.0 - (np.sum(item_vars) / total_var))
    return float(alpha)


def interpret_alpha(alpha: float) -> str:
    """Standard psychometric interpretation benchmark for Cronbach's alpha."""
    if alpha >= 0.90:
        return "Excellent"
    elif alpha >= 0.80:
        return "Good"
    elif alpha >= 0.70:
        return "Acceptable"
    elif alpha >= 0.60:
        return "Questionable"
    elif alpha >= 0.50:
        return "Poor"
    else:
        return "Unacceptable"


def compute_scale_reliability(df: pd.DataFrame, item_cols: List[str], scale_name: str) -> Dict[str, Any]:
    """
    Computes overall scale reliability, alpha-if-item-deleted, and
    corrected item-total correlations.
    """
    valid_items = [c for c in item_cols if c in df.columns]
    k = len(valid_items)
    if k < 2:
        return {
            "scale": scale_name,
            "k_items": k,
            "alpha": np.nan,
            "interpretation": "Insufficient items",
            "items_table": pd.DataFrame(),
        }

    mat = df[valid_items].to_numpy(dtype=float)
    overall_alpha = cronbach_alpha_numpy(mat)

    # Compute total score across all items in scale
    total_score = np.sum(mat, axis=1)

    item_records = []
    for i, item_name in enumerate(valid_items):
        # Matrix with item i excluded
        sub_mat = np.delete(mat, i, axis=1)
        alpha_if_del = cronbach_alpha_numpy(sub_mat)

        # Corrected item-total correlation: r(item_i, sum of other items)
        rest_score = total_score - mat[:, i]
        if np.std(mat[:, i]) > 0 and np.std(rest_score) > 0:
            citc, _ = stats.pearsonr(mat[:, i], rest_score)
        else:
            citc = 0.0

        item_records.append({
            "item": item_name,
            "alpha_if_deleted": round(alpha_if_del, 3),
            "corrected_item_total_r": round(citc, 3),
            "lowers_alpha": bool(alpha_if_del > (overall_alpha + 0.01)),
        })

    return {
        "scale": scale_name,
        "k_items": k,
        "alpha": round(overall_alpha, 3),
        "interpretation": interpret_alpha(overall_alpha),
        "items_table": pd.DataFrame(item_records),
    }


def compute_all_reliabilities(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes reliability for all dimensions, overall awareness, and full scale."""
    results: Dict[str, Any] = {}

    # 1. Per dimension
    for dim in config.DIMENSIONS:
        dim_items = [
            q["short_name"] for q in config.QUESTION_MAP.values()
            if q["dimension"] == dim and q["short_name"] in df.columns
        ]
        results[dim] = compute_scale_reliability(df, dim_items, dim)

    # 2. Overall Awareness Scale (4 core dimensions)
    awareness_items = [
        q["short_name"] for q in config.QUESTION_MAP.values()
        if q["dimension"] in config.AWARENESS_DIMENSIONS and q["short_name"] in df.columns
    ]
    results["overall_awareness_scale"] = compute_scale_reliability(df, awareness_items, "overall_awareness_scale")

    # 3. Full Scale (all 23 Likert items)
    all_items = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
    results["full_scale"] = compute_scale_reliability(df, all_items, "full_scale_23_items")

    return results


# ==========================================
# 3. Correlation Analysis
# ==========================================

def compute_correlation_matrices(
    df: pd.DataFrame, cols: List[str]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Computes Pearson and Spearman correlation matrices with exact p-values.
    Returns:
        spearman_corr, spearman_pval, pearson_corr, pearson_pval
    """
    valid_cols = [c for c in cols if c in df.columns]
    n = len(valid_cols)
    s_corr = np.zeros((n, n))
    s_pval = np.zeros((n, n))
    p_corr = np.zeros((n, n))
    p_pval = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                s_corr[i, j] = 1.0
                s_pval[i, j] = 0.0
                p_corr[i, j] = 1.0
                p_pval[i, j] = 0.0
            else:
                x = df[valid_cols[i]].dropna()
                y = df[valid_cols[j]].dropna()
                common_idx = x.index.intersection(y.index)
                if len(common_idx) > 2:
                    sc, sp = stats.spearmanr(df.loc[common_idx, valid_cols[i]], df.loc[common_idx, valid_cols[j]])
                    pc, pp = stats.pearsonr(df.loc[common_idx, valid_cols[i]], df.loc[common_idx, valid_cols[j]])
                    s_corr[i, j], s_pval[i, j] = sc, sp
                    p_corr[i, j], p_pval[i, j] = pc, pp
                else:
                    s_corr[i, j], s_pval[i, j] = np.nan, np.nan
                    p_corr[i, j], p_pval[i, j] = np.nan, np.nan

    spearman_df = pd.DataFrame(s_corr, index=valid_cols, columns=valid_cols)
    spearman_p_df = pd.DataFrame(s_pval, index=valid_cols, columns=valid_cols)
    pearson_df = pd.DataFrame(p_corr, index=valid_cols, columns=valid_cols)
    pearson_p_df = pd.DataFrame(p_pval, index=valid_cols, columns=valid_cols)

    return spearman_df, spearman_p_df, pearson_df, pearson_p_df


def extract_top_correlations(
    corr_df: pd.DataFrame, pval_df: pd.DataFrame, top_k: int = 5
) -> List[Dict[str, Any]]:
    """Extract top strongest distinct pairs (excluding diagonal)."""
    pairs = []
    cols = list(corr_df.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr_df.iloc[i, j]
            p = pval_df.iloc[i, j]
            if not np.isnan(r):
                pairs.append({
                    "var1": cols[i],
                    "var2": cols[j],
                    "r": round(float(r), 3),
                    "abs_r": abs(float(r)),
                    "p_val": float(p),
                    "sig": "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns",
                })
    pairs.sort(key=lambda x: x["abs_r"], reverse=True)
    return pairs[:top_k]


def analyze_media_exposure_relations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Dedicated analysis of how media_exposure correlates with:
    - overall_awareness_score
    - rumor_detection
    - digital_threat_awareness
    - verification_behavior
    """
    target_vars = [
        "overall_awareness_score",
        "dim_rumor_detection",
        "dim_digital_threat_awareness",
        "dim_verification_behavior",
    ]
    results = []
    me_col = "dim_media_exposure"
    if me_col not in df.columns:
        return results

    for tvar in target_vars:
        if tvar in df.columns:
            r_sp, p_sp = stats.spearmanr(df[me_col], df[tvar])
            r_pe, p_pe = stats.pearsonr(df[me_col], df[tvar])
            results.append({
                "exposure_variable": me_col,
                "target_variable": tvar,
                "spearman_rho": round(float(r_sp), 3),
                "spearman_p": float(p_sp),
                "pearson_r": round(float(r_pe), 3),
                "pearson_p": float(p_pe),
                "sig": "***" if p_sp < 0.001 else "**" if p_sp < 0.01 else "*" if p_sp < 0.05 else "ns",
            })
    return results


# ==========================================
# 4. Inferential Demographic Group Tests
# ==========================================

def interpret_cohens_d(d: float) -> str:
    ad = abs(d)
    if ad < 0.2:
        return "negligible"
    elif ad < 0.5:
        return "small"
    elif ad < 0.8:
        return "medium"
    else:
        return "large"


def interpret_eta_squared(eta: float) -> str:
    if eta < 0.01:
        return "negligible"
    elif eta < 0.06:
        return "small"
    elif eta < 0.14:
        return "medium"
    else:
        return "large"


def run_demographic_tests(
    df: pd.DataFrame,
    dependent_var: str = "overall_awareness_score",
    min_group_size: int = config.MIN_GROUP_SIZE,
    alpha: float = config.ALPHA,
) -> pd.DataFrame:
    """
    Conducts rigorous group difference hypothesis testing across demographic variables:
    - Normality check (Shapiro-Wilk)
    - Homogeneity of variance (Levene's test)
    - 2 groups: Welch's t-test + Cohen's d, Mann-Whitney U + Rank Biserial r
    - 3+ groups: One-way ANOVA + Eta-squared, Kruskal-Wallis + Epsilon-squared
    - Bonferroni-corrected pairwise post-hoc tests for significant effects
    """
    records = []

    demographic_vars = list(config.DEMOGRAPHIC_COLUMNS.values())
    for demo in demographic_vars:
        if demo not in df.columns:
            continue

        # Filter groups with n >= min_group_size
        val_counts = df[demo].value_counts()
        valid_groups = val_counts[val_counts >= min_group_size].index.tolist()

        if len(valid_groups) < 2:
            logger.info("Skipping demographic '%s' (fewer than 2 groups with n >= %d).", demo, min_group_size)
            continue

        sub_df = df[df[demo].isin(valid_groups)]
        grouped_data = [sub_df[sub_df[demo] == g][dependent_var].dropna().to_numpy() for g in valid_groups]

        # 1. Normality check per group (Shapiro-Wilk)
        normal_flags = []
        for g_data in grouped_data:
            if len(g_data) >= 3:
                _, p_norm = stats.shapiro(g_data)
                normal_flags.append(p_norm > alpha)
            else:
                normal_flags.append(False)
        all_normal = all(normal_flags)

        # 2. Homogeneity of variance (Levene)
        try:
            _, p_levene = stats.levene(*grouped_data)
            equal_var = p_levene > alpha
        except Exception:
            p_levene = 1.0
            equal_var = True

        # CASE A: Exactly 2 Groups
        if len(valid_groups) == 2:
            g1, g2 = grouped_data[0], grouped_data[1]
            n1, n2 = len(g1), len(g2)
            m1, m2 = np.mean(g1), np.mean(g2)
            s1, s2 = np.std(g1, ddof=1), np.std(g2, ddof=1)

            # Parametric: Welch's t-test
            t_stat, t_pval = stats.ttest_ind(g1, g2, equal_var=False)
            pooled_sd = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2)) if (n1 + n2 > 2) else 1.0
            cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 0 else 0.0

            # Non-parametric: Mann-Whitney U
            u_stat, u_pval = stats.mannwhitneyu(g1, g2, alternative="two-sided")
            rank_biserial = 1.0 - (2.0 * u_stat) / (n1 * n2)

            records.append({
                "demographic": demo,
                "dependent_var": dependent_var,
                "n_groups": 2,
                "groups_evaluated": f"{valid_groups[0]} vs {valid_groups[1]}",
                "test_type": "Welch's t-test (Parametric)",
                "statistic": round(float(t_stat), 3),
                "p_value": float(t_pval),
                "p_adjusted": float(t_pval),
                "effect_size": round(float(cohen_d), 3),
                "effect_size_type": "Cohen's d",
                "magnitude": interpret_cohens_d(cohen_d),
                "is_significant": bool(t_pval < alpha),
                "post_hoc": "N/A (2 groups)",
            })

            records.append({
                "demographic": demo,
                "dependent_var": dependent_var,
                "n_groups": 2,
                "groups_evaluated": f"{valid_groups[0]} vs {valid_groups[1]}",
                "test_type": "Mann-Whitney U (Non-Parametric)",
                "statistic": round(float(u_stat), 3),
                "p_value": float(u_pval),
                "p_adjusted": float(u_pval),
                "effect_size": round(float(rank_biserial), 3),
                "effect_size_type": "Rank-Biserial r",
                "magnitude": interpret_cohens_d(rank_biserial),
                "is_significant": bool(u_pval < alpha),
                "post_hoc": "N/A (2 groups)",
            })

        # CASE B: 3+ Groups
        else:
            k = len(valid_groups)
            n_total = sum(len(g) for g in grouped_data)

            # Parametric: One-Way ANOVA
            f_stat, f_pval = stats.f_oneway(*grouped_data)

            # Calculate Eta-Squared
            grand_mean = np.mean(sub_df[dependent_var])
            ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in grouped_data)
            ss_total = sum((sub_df[dependent_var] - grand_mean)**2)
            eta_sq = ss_between / ss_total if ss_total > 0 else 0.0

            # Non-Parametric: Kruskal-Wallis H
            h_stat, h_pval = stats.kruskal(*grouped_data)
            # Epsilon-squared: (H - k + 1) / (n - k)
            epsilon_sq = (h_stat - k + 1) / (n_total - k) if (n_total > k) else 0.0
            epsilon_sq = max(0.0, float(epsilon_sq))

            # Post-Hoc Pairwise Tests with Bonferroni correction if significant
            post_hoc_summary = "None"
            if h_pval < alpha or f_pval < alpha:
                sig_pairs = []
                n_pairs = (k * (k - 1)) // 2
                for i in range(k):
                    for j in range(i + 1, k):
                        u_ij, p_ij = stats.mannwhitneyu(grouped_data[i], grouped_data[j], alternative="two-sided")
                        p_bonf = min(1.0, p_ij * n_pairs)
                        if p_bonf < alpha:
                            sig_pairs.append(f"{valid_groups[i]}!={valid_groups[j]} (p_adj={p_bonf:.3f})")
                if sig_pairs:
                    post_hoc_summary = "; ".join(sig_pairs)
                else:
                    post_hoc_summary = "No pairwise pair reached adjusted significance"

            records.append({
                "demographic": demo,
                "dependent_var": dependent_var,
                "n_groups": k,
                "groups_evaluated": f"{k} groups: {', '.join(str(g) for g in valid_groups[:4])}...",
                "test_type": "One-way ANOVA (Parametric)",
                "statistic": round(float(f_stat), 3),
                "p_value": float(f_pval),
                "p_adjusted": float(f_pval),
                "effect_size": round(float(eta_sq), 3),
                "effect_size_type": "Eta-squared (η²)",
                "magnitude": interpret_eta_squared(eta_sq),
                "is_significant": bool(f_pval < alpha),
                "post_hoc": post_hoc_summary,
            })

            records.append({
                "demographic": demo,
                "dependent_var": dependent_var,
                "n_groups": k,
                "groups_evaluated": f"{k} groups: {', '.join(str(g) for g in valid_groups[:4])}...",
                "test_type": "Kruskal-Wallis H (Non-Parametric)",
                "statistic": round(float(h_stat), 3),
                "p_value": float(h_pval),
                "p_adjusted": float(h_pval),
                "effect_size": round(float(epsilon_sq), 3),
                "effect_size_type": "Epsilon-squared (ε²)",
                "magnitude": interpret_eta_squared(epsilon_sq),
                "is_significant": bool(h_pval < alpha),
                "post_hoc": post_hoc_summary,
            })

    return pd.DataFrame(records)


# ==========================================
# 5. Principal Component Analysis (PCA)
# ==========================================

def run_pca_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes PCA on scored Likert items (standardized).
    Extracts explained variance, scree eigenvalues, and top factor loadings.
    """
    likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
    X = df[likert_cols].dropna().to_numpy(dtype=float)

    if X.shape[0] < 5 or X.shape[1] < 2:
        return {"error": "Insufficient sample size or variables for PCA"}

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA()
    pca.fit(X_scaled)

    explained_var = pca.explained_variance_ratio_
    eigenvalues = pca.explained_variance_
    cum_var = np.cumsum(explained_var)

    # Component loadings for first 2 components
    loadings_df = pd.DataFrame(
        pca.components_[:2].T,
        index=likert_cols,
        columns=["PC1_Loading", "PC2_Loading"],
    )

    top_pc1 = loadings_df.sort_values(by="PC1_Loading", ascending=False).head(5)
    top_pc2 = loadings_df.sort_values(by="PC2_Loading", ascending=False).head(5)

    return {
        "n_components": len(eigenvalues),
        "eigenvalues": eigenvalues.tolist(),
        "explained_variance_ratio": explained_var.tolist(),
        "cumulative_variance_ratio": cum_var.tolist(),
        "loadings_df": loadings_df,
        "top_pc1_items": top_pc1.index.tolist(),
        "top_pc2_items": top_pc2.index.tolist(),
    }


# ==========================================
# 6. Rankings & Extremes
# ==========================================

def rank_dimensions_and_items(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Ranks dimensions from strongest to weakest mean score.
    Identifies bottom-5 weakest items across the scale.
    """
    dim_means = {}
    for dim in config.DIMENSIONS:
        col = f"dim_{dim}"
        if col in df.columns:
            dim_means[dim] = float(df[col].mean())

    ranked_dims = sorted(dim_means.items(), key=lambda x: x[1], reverse=True)

    # Item-level means
    likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
    item_means = {col: float(df[col].mean()) for col in likert_cols}
    ranked_items = sorted(item_means.items(), key=lambda x: x[1])  # Ascending: weakest first
    bottom_5_items = ranked_items[:5]

    return {
        "ranked_dimensions": ranked_dims,
        "bottom_5_items": bottom_5_items,
        "dimension_means": dim_means,
    }

