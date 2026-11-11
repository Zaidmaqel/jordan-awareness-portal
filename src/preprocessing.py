"""
JSSAA Preprocessing and Feature Engineering Module.

Handles reverse-coding of Likert items, computation of per-respondent
dimension scores, calculation of Overall Awareness Score, classification
into awareness risk bands, objective knowledge scoring, Perception-Reality Gap,
and categorical typing for demographic analysis.
"""

import os
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

logger = logging.getLogger("JSSAA.preprocessing")


def reverse_code(val: float, likert_min: int = config.LIKERT_MIN, likert_max: int = config.LIKERT_MAX) -> float:
    """
    Standard psychometric reverse coding: (likert_max + likert_min) - x.
    For a 1-5 scale: (5 + 1) - x = 6 - x.
    """
    if pd.isna(val):
        return np.nan
    return float((likert_max + likert_min) - val)


def assign_awareness_band(
    score: float,
    low_max: float = config.LOW_MAX,
    moderate_max: float = config.MODERATE_MAX,
) -> str:
    """
    Assign awareness risk band based on defined score thresholds.
    - Low: score <= low_max (e.g. <= 2.33)
    - Moderate: low_max < score <= moderate_max (e.g. 2.34 - 3.66)
    - High: score > moderate_max (e.g. >= 3.67)
    """
    if pd.isna(score):
        return "Unknown"
    if score <= low_max:
        return "Low"
    elif score <= moderate_max:
        return "Moderate"
    else:
        return "High"


class Preprocessor:
    """
    Applies psychometric transformations and scoring algorithms to the survey dataset.
    """

    def __init__(
        self,
        include_exposure_in_score: bool = config.INCLUDE_EXPOSURE_IN_SCORE,
        low_max: float = config.LOW_MAX,
        moderate_max: float = config.MODERATE_MAX,
    ):
        self.include_exposure = include_exposure_in_score
        self.low_max = low_max
        self.moderate_max = moderate_max

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute full transformation pipeline on cleaned survey responses.

        Args:
            df: Cleaned dataframe from DataLoader.

        Returns:
            Preprocessed dataframe with scored dimensions, awareness bands,
            actual knowledge score, and perception-reality gap.
        """
        processed_df = df.copy()

        # 1. Reverse-code specified Likert items
        # Store both raw (already preserved in raw_likert_df) and reverse-coded in current columns
        for _, q_info in config.QUESTION_MAP.items():
            short_name = q_info["short_name"]
            is_reverse = q_info["reverse"]
            if is_reverse and short_name in processed_df.columns:
                # Save raw version before reversing for auditing
                processed_df[f"{short_name}_raw"] = processed_df[short_name].copy()
                processed_df[short_name] = processed_df[short_name].apply(
                    lambda x: reverse_code(x, config.LIKERT_MIN, config.LIKERT_MAX)
                )

        # 2. Compute Dimension Scores (item means per respondent)
        for dim in config.DIMENSIONS:
            dim_items = [
                q_info["short_name"]
                for q_info in config.QUESTION_MAP.values()
                if q_info["dimension"] == dim and q_info["short_name"] in processed_df.columns
            ]
            if dim_items:
                processed_df[f"dim_{dim}"] = processed_df[dim_items].mean(axis=1)

        # 3. Overall Awareness Score
        # Mean of the 4 awareness dimensions (excluding media_exposure unless configured)
        if self.include_exposure:
            target_dims = [f"dim_{d}" for d in config.DIMENSIONS]
        else:
            target_dims = [f"dim_{d}" for d in config.AWARENESS_DIMENSIONS]

        processed_df["overall_awareness_score"] = processed_df[target_dims].mean(axis=1)

        # 4. Awareness Risk Bands (Per-respondent and Dimension bands)
        processed_df["awareness_band"] = processed_df["overall_awareness_score"].apply(
            lambda s: assign_awareness_band(s, self.low_max, self.moderate_max)
        )
        for dim in config.DIMENSIONS:
            processed_df[f"band_{dim}"] = processed_df[f"dim_{dim}"].apply(
                lambda s: assign_awareness_band(s, self.low_max, self.moderate_max)
            )

        # 5. Actual Awareness (Objective Knowledge Score: % correct 0.0 - 1.0)
        knowledge_cols = [k_info["short_name"] for k_info in config.KNOWLEDGE_QUESTIONS.values()]
        valid_k_cols = [k for k in knowledge_cols if k in processed_df.columns]
        if valid_k_cols:
            processed_df["actual_knowledge_sum"] = processed_df[valid_k_cols].sum(axis=1)
            processed_df["actual_knowledge_score"] = processed_df[valid_k_cols].mean(axis=1)
            processed_df["actual_knowledge_pct"] = processed_df["actual_knowledge_score"] * 100.0
        else:
            processed_df["actual_knowledge_score"] = np.nan
            processed_df["actual_knowledge_pct"] = np.nan

        # 6. Perception–Reality Gap = z(perceived overall awareness) - z(actual knowledge score)
        # z = (x - mean) / std
        def calc_z(series: pd.Series) -> pd.Series:
            sd = series.std(ddof=1)
            if sd == 0 or pd.isna(sd):
                return pd.Series(0.0, index=series.index)
            return (series - series.mean()) / sd

        z_perceived = calc_z(processed_df["overall_awareness_score"])
        z_actual = calc_z(processed_df["actual_knowledge_score"])
        processed_df["perception_reality_gap"] = z_perceived - z_actual

        # 7. Convert demographic columns to ordered / standard categories
        for col, cats in config.ORDERED_CATEGORIES.items():
            if col in processed_df.columns:
                processed_df[col] = pd.Categorical(
                    processed_df[col], categories=cats, ordered=True
                )

        logger.info(
            "Preprocessing complete. Mean Overall Awareness: %.2f (SD = %.2f)",
            processed_df["overall_awareness_score"].mean(),
            processed_df["overall_awareness_score"].std(ddof=1),
        )
        return processed_df

