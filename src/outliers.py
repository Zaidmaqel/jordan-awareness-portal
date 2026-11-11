"""
JSSAA Anomaly, Outlier, and Response Quality Detection Module.

Implements multi-tiered quality audits:
1. Item-level Z-scores (|Z| > Z_THRESHOLD)
2. Respondent-level Z-scores on Overall Awareness Score (|Z| > Z_THRESHOLD)
3. Interquartile Range (IQR) outliers on Overall Awareness Score
4. Straight-lining detection (zero variance across raw Likert responses)
5. Semantic inconsistency auditing across logical pairs (|normal - reversed| >= 3)
6. Speeding audit (conditional on duration availability)
7. Sensitivity Analysis: Rerun core indicators with flagged respondents removed.
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.statistics import cronbach_alpha_numpy, rank_dimensions_and_items

logger = logging.getLogger("JSSAA.outliers")


class QualityAuditor:
    """
    Performs psychometric data quality checks, anomaly identification,
    and sensitivity re-estimation.
    """

    def __init__(
        self,
        z_threshold: float = config.Z_THRESHOLD,
        iqr_multiplier: float = config.IQR_MULTIPLIER,
        consistency_diff_threshold: float = config.CONSISTENCY_DIFF_THRESHOLD,
        min_completion_seconds: Any = config.MIN_COMPLETION_SECONDS,
    ):
        self.z_threshold = z_threshold
        self.iqr_multiplier = iqr_multiplier
        self.consistency_diff_threshold = consistency_diff_threshold
        self.min_completion_seconds = min_completion_seconds

    def audit(
        self, df: pd.DataFrame, raw_likert_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Runs all anomaly and quality detection algorithms.

        Args:
            df: Preprocessed dataframe (with reverse-coded items and overall scores).
            raw_likert_df: Raw Likert responses BEFORE reverse-coding for straight-lining.

        Returns:
            Tuple of:
            - item_outliers_df: Table of item-level Z outliers
            - suspicious_df: Consolidated table of flagged respondents with detailed reasons
            - summary_stats: Dict of count per defect category
        """
        flagged_reasons: Dict[int, List[str]] = {idx: [] for idx in df.index}

        # 1. Item-level Z-score Outliers
        likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
        item_outlier_records = []

        for col in likert_cols:
            s = df[col].dropna()
            sd = s.std(ddof=1)
            if sd > 0:
                mean = s.mean()
                z_scores = (s - mean) / sd
                extreme_idx = z_scores[abs(z_scores) > self.z_threshold].index
                for idx in extreme_idx:
                    val = float(df.at[idx, col])
                    z_val = float(z_scores.at[idx])
                    item_outlier_records.append({
                        "respondent_id": idx,
                        "item": col,
                        "value": val,
                        "z_score": round(z_val, 3),
                    })

        item_outliers_df = pd.DataFrame(item_outlier_records)

        # 2. Respondent-level Z-score on Overall Score
        overall_scores = df["overall_awareness_score"]
        o_sd = overall_scores.std(ddof=1)
        if o_sd > 0:
            o_mean = overall_scores.mean()
            overall_z = (overall_scores - o_mean) / o_sd
            resp_z_outliers = overall_z[abs(overall_z) > self.z_threshold].index
            for idx in resp_z_outliers:
                flagged_reasons[idx].append(f"Overall Score Z-Score Outlier (Z={overall_z.at[idx]:.2f})")

        # 3. Respondent-level IQR Outlier on Overall Score
        q1 = overall_scores.quantile(0.25)
        q3 = overall_scores.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - self.iqr_multiplier * iqr
        upper_bound = q3 + self.iqr_multiplier * iqr
        iqr_outliers = overall_scores[(overall_scores < lower_bound) | (overall_scores > upper_bound)].index
        for idx in iqr_outliers:
            flagged_reasons[idx].append(
                f"Overall Score IQR Outlier ({overall_scores.at[idx]:.2f} outside [{lower_bound:.2f}, {upper_bound:.2f}])"
            )

        # 4. Straight-Lining Check (Zero variance on raw answers BEFORE reverse-coding)
        common_cols = [c for c in likert_cols if c in raw_likert_df.columns]
        raw_variances = raw_likert_df[common_cols].var(axis=1)
        straightliners = raw_variances[raw_variances == 0.0].index
        for idx in straightliners:
            # Get the repeated value
            repeated_val = raw_likert_df.loc[idx, common_cols].iloc[0]
            flagged_reasons[idx].append(f"Straight-lining (variance=0 across all items; selected {repeated_val})")

        # 5. Semantic Consistency Audit
        # Check pairs after reverse-coding: flag if |normal - reversed| >= 3
        for pair in config.CONSISTENCY_PAIRS:
            v1, v2 = pair[0], pair[1]
            if v1 in df.columns and v2 in df.columns:
                diffs = (df[v1] - df[v2]).abs()
                inconsistent_idx = diffs[diffs >= self.consistency_diff_threshold].index
                for idx in inconsistent_idx:
                    flagged_reasons[idx].append(
                        f"Inconsistent Logical Pair: |{v1}({df.at[idx, v1]:.0f}) - {v2}({df.at[idx, v2]:.0f})| = {diffs.at[idx]:.0f} >= {self.consistency_diff_threshold}"
                    )

        # 6. Speeding Check (if duration column exists)
        if self.min_completion_seconds is not None and "duration_seconds" in df.columns:
            speeders = df[df["duration_seconds"] < self.min_completion_seconds].index
            for idx in speeders:
                flagged_reasons[idx].append(
                    f"Speeding (completed in {df.at[idx, 'duration_seconds']}s < {self.min_completion_seconds}s)"
                )

        # Consolidate suspicious responses table
        suspicious_records = []
        for idx, reasons in flagged_reasons.items():
            if reasons:
                suspicious_records.append({
                    "respondent_id": idx,
                    "overall_awareness_score": round(float(df.at[idx, "overall_awareness_score"]), 3),
                    "awareness_band": df.at[idx, "awareness_band"],
                    "flag_count": len(reasons),
                    "reasons": "; ".join(reasons),
                })

        suspicious_df = pd.DataFrame(suspicious_records)
        if not suspicious_df.empty:
            suspicious_df = suspicious_df.sort_values(by="flag_count", ascending=False).reset_index(drop=True)

        audit_summary = {
            "total_respondents": len(df),
            "total_suspicious_flagged": len(suspicious_records),
            "pct_suspicious": round((len(suspicious_records) / len(df)) * 100.0, 2) if len(df) > 0 else 0.0,
            "straightliner_count": len(straightliners),
            "iqr_outlier_count": len(iqr_outliers),
            "item_outlier_count": len(item_outliers_df),
        }

        logger.info(
            "Quality Audit complete. Identified %d suspicious respondents (%.1f%% of sample).",
            len(suspicious_records), audit_summary["pct_suspicious"]
        )

        return item_outliers_df, suspicious_df, audit_summary

    def run_sensitivity_analysis(
        self, df: pd.DataFrame, suspicious_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Rerun core statistics excluding flagged respondents to evaluate robustness:
        - Mean overall awareness
        - Cronbach's alpha
        - Dimension rankings
        - Awareness status
        """
        flagged_ids = set(suspicious_df["respondent_id"].tolist()) if not suspicious_df.empty else set()
        clean_df = df.loc[~df.index.isin(flagged_ids)].copy()

        n_full = len(df)
        n_clean = len(clean_df)

        # Baseline stats
        mean_full = float(df["overall_awareness_score"].mean())
        mean_clean = float(clean_df["overall_awareness_score"].mean()) if n_clean > 0 else np.nan

        # Full scale alpha
        likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
        alpha_full = cronbach_alpha_numpy(df[likert_cols].to_numpy(dtype=float))
        alpha_clean = cronbach_alpha_numpy(clean_df[likert_cols].to_numpy(dtype=float)) if n_clean > 0 else np.nan

        # Dimension rankings
        baseline_ranking = rank_dimensions_and_items(df)["ranked_dimensions"]
        clean_ranking = rank_dimensions_and_items(clean_df)["ranked_dimensions"] if n_clean > 0 else []

        rank_order_full = [d[0] for d in baseline_ranking]
        rank_order_clean = [d[0] for d in clean_ranking]
        ranking_changed = rank_order_full != rank_order_clean

        # Status check
        def get_status(score: float) -> str:
            if score < 2.34:
                return "HIGH RISK / LOW AWARENESS"
            elif score <= 3.66:
                return "MODERATE AWARENESS / ELEVATED RISK"
            else:
                return "STABLE / GOOD AWARENESS"

        status_full = get_status(mean_full)
        status_clean = get_status(mean_clean) if not np.isnan(mean_clean) else "N/A"
        status_changed = status_full != status_clean

        return {
            "n_full": n_full,
            "n_clean": n_clean,
            "n_removed": len(flagged_ids),
            "mean_full": round(mean_full, 3),
            "mean_clean": round(mean_clean, 3),
            "mean_delta": round(mean_clean - mean_full, 3),
            "alpha_full": round(alpha_full, 3),
            "alpha_clean": round(alpha_clean, 3),
            "alpha_delta": round(alpha_clean - alpha_full, 3),
            "baseline_status": status_full,
            "clean_status": status_clean,
            "status_changed": status_changed,
            "ranking_changed": ranking_changed,
            "baseline_dimension_ranking": [f"{d[0]} ({d[1]:.2f})" for d in baseline_ranking],
            "clean_dimension_ranking": [f"{d[0]} ({d[1]:.2f})" for d in clean_ranking],
            "conclusion_stable": not (status_changed or ranking_changed),
        }

