"""
JSSAA Data Ingestion and Quality Cleaning Module.

Handles robust loading of survey response files (.xlsx or .csv), normalization
of Arabic headers, schema validation, duplicate detection, range enforcement,
missingness filtering, median imputation, and objective knowledge scoring.
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

logger = logging.getLogger("JSSAA.data_loader")


def normalize_arabic_text(text: str) -> str:
    """
    Normalize Arabic text to handle common typographic variants,
    trailing whitespace, tatweel, and non-breaking spaces.
    """
    if not isinstance(text, str):
        return str(text)
    # Strip whitespace and normalize unicode spaces
    s = text.strip().replace("\u00a0", " ")
    # Remove tatweel (kashida)
    s = re.sub(r"[\u0640]", "", s)
    # Collapse multiple whitespace characters into single space
    s = re.sub(r"\s+", " ", s)
    return s


class DataLoader:
    """
    Loads and cleans JSSAA survey responses from Excel or CSV files.
    """

    def __init__(
        self,
        filepath: str = config.INPUT_FILE,
        sheet_name: Any = config.SHEET_NAME,
        max_missing_ratio: float = config.MAX_MISSING_RATIO,
        likert_min: int = config.LIKERT_MIN,
        likert_max: int = config.LIKERT_MAX,
    ):
        self.filepath = filepath
        self.sheet_name = sheet_name
        self.max_missing_ratio = max_missing_ratio
        self.likert_min = likert_min
        self.likert_max = likert_max

        self.quality_summary: Dict[str, Any] = {
            "raw_count": 0,
            "duplicate_count": 0,
            "dropped_missing_count": 0,
            "out_of_range_count": 0,
            "final_count": 0,
            "item_missing_pct_before_imputation": {},
            "timestamp_col": None,
        }

    def load_raw_data(self) -> pd.DataFrame:
        """
        Load dataframe from file path based on extension (.xlsx or .csv).
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(
                f"Data file '{self.filepath}' was not found. "
                f"Please ensure survey responses are placed in '{self.filepath}'."
            )

        ext = os.path.splitext(self.filepath)[-1].lower()
        logger.info("Loading survey response data from %s (format: %s)", self.filepath, ext)

        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(self.filepath, sheet_name=self.sheet_name, engine="openpyxl")
        elif ext == ".csv":
            try:
                df = pd.read_csv(self.filepath, encoding="utf-8")
            except UnicodeDecodeError:
                logger.warning("UTF-8 decoding failed, attempting utf-8-sig / cp1256 encoding.")
                df = pd.read_csv(self.filepath, encoding="utf-8-sig")
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Must be .xlsx, .xls, or .csv.")

        self.quality_summary["raw_count"] = len(df)
        logger.info("Raw response records loaded: %d", len(df))
        return df

    def match_and_rename_columns(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Map Arabic survey question columns to standardized short names.
        Raises friendly error listing any missing columns.
        """
        normalized_df_cols = {normalize_arabic_text(col): col for col in df.columns}
        rename_map: Dict[str, str] = {}
        missing_likert: List[str] = []
        missing_demographics: List[str] = []
        missing_knowledge: List[str] = []

        # 1. Match Likert questions
        for ar_q, info in config.QUESTION_MAP.items():
            norm_q = normalize_arabic_text(ar_q)
            if norm_q in normalized_df_cols:
                original_col = normalized_df_cols[norm_q]
                rename_map[original_col] = info["short_name"]
            else:
                missing_likert.append(ar_q)

        # 2. Match Demographic columns
        for ar_demo, short_demo in config.DEMOGRAPHIC_COLUMNS.items():
            norm_demo = normalize_arabic_text(ar_demo)
            if norm_demo in normalized_df_cols:
                original_col = normalized_df_cols[norm_demo]
                rename_map[original_col] = short_demo
            else:
                missing_demographics.append(ar_demo)

        # 3. Match Knowledge questions
        for ar_k, k_info in config.KNOWLEDGE_QUESTIONS.items():
            norm_k = normalize_arabic_text(ar_k)
            if norm_k in normalized_df_cols:
                original_col = normalized_df_cols[norm_k]
                rename_map[original_col] = k_info["short_name"]
            else:
                missing_knowledge.append(ar_k)

        # Check for missing required columns
        total_missing = len(missing_likert) + len(missing_demographics) + len(missing_knowledge)
        if total_missing > 0:
            err_msg = (
                f"\n[SCHEMA MISMATCH ERROR] {total_missing} required survey columns could not be mapped:\n"
            )
            if missing_likert:
                err_msg += f"  - Missing Likert Questions ({len(missing_likert)}):\n" + "\n".join(
                    [f"    * {q}" for q in missing_likert[:5]]
                )
                if len(missing_likert) > 5:
                    err_msg += f"\n    ... and {len(missing_likert)-5} more."
            if missing_demographics:
                err_msg += f"\n  - Missing Demographic Columns:\n" + "\n".join(
                    [f"    * {d}" for d in missing_demographics]
                )
            if missing_knowledge:
                err_msg += f"\n  - Missing Knowledge Items:\n" + "\n".join(
                    [f"    * {k}" for k in missing_knowledge]
                )
            err_msg += (
                "\n\nPlease verify that the Google Forms headers match config.py QUESTION_MAP keys exactly."
            )
            logger.error(err_msg)
            raise KeyError(err_msg)

        # Check for Timestamp column
        for ts_col in config.TIMESTAMP_COLUMNS:
            norm_ts = normalize_arabic_text(ts_col)
            if norm_ts in normalized_df_cols:
                original_col = normalized_df_cols[norm_ts]
                rename_map[original_col] = "timestamp"
                self.quality_summary["timestamp_col"] = ts_col
                break

        renamed_df = df.rename(columns=rename_map)
        return renamed_df, rename_map

    def process(self) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Execute full data loading, cleaning, and quality auditing pipeline.

        Returns:
            Tuple of:
            - cleaned_df: Cleaned and median-imputed DataFrame with standardized column names
            - raw_likert_df: Raw numeric Likert DataFrame before imputation and reverse coding
            - quality_summary: Quality summary statistics dict
        """
        raw_df = self.load_raw_data()
        df, _ = self.match_and_rename_columns(raw_df)

        likert_cols = [info["short_name"] for info in config.QUESTION_MAP.values()]
        demo_cols = list(config.DEMOGRAPHIC_COLUMNS.values())
        knowledge_cols = [k_info["short_name"] for k_info in config.KNOWLEDGE_QUESTIONS.values()]

        # 1. Exact Duplicate Detection
        # Check duplicate rows across content columns (demographics + likert + knowledge)
        content_cols = [c for c in (demo_cols + likert_cols + knowledge_cols) if c in df.columns]
        initial_count = len(df)
        df_no_dups = df.drop_duplicates(subset=content_cols, keep="first").copy()
        dup_count = initial_count - len(df_no_dups)
        self.quality_summary["duplicate_count"] = dup_count
        if dup_count > 0:
            logger.info("Removed %d exact duplicate respondent rows.", dup_count)
        df = df_no_dups.reset_index(drop=True)

        # 2. Likert Coercion & Out-of-Range Handling
        out_of_range_count = 0
        raw_likert_df = pd.DataFrame(index=df.index)

        for col in likert_cols:
            numeric_s = pd.to_numeric(df[col], errors="coerce")
            # Identify values outside [likert_min, likert_max]
            oor_mask = (numeric_s < self.likert_min) | (numeric_s > self.likert_max)
            col_oor = oor_mask.sum()
            if col_oor > 0:
                out_of_range_count += col_oor
                logger.warning(
                    "Item '%s' contained %d out-of-range value(s); coerced to NaN.",
                    col, col_oor
                )
                numeric_s[oor_mask] = np.nan
            df[col] = numeric_s
            raw_likert_df[col] = numeric_s.copy()

        self.quality_summary["out_of_range_count"] = out_of_range_count

        # 3. Assess Missingness before Imputation
        for col in likert_cols:
            pct_missing = (df[col].isna().sum() / len(df)) * 100.0
            self.quality_summary["item_missing_pct_before_imputation"][col] = round(pct_missing, 2)

        # 4. Drop Respondents with Missing Ratio > MAX_MISSING_RATIO
        likert_missing_ratio = df[likert_cols].isna().mean(axis=1)
        drop_mask = likert_missing_ratio > self.max_missing_ratio
        dropped_count = int(drop_mask.sum())
        self.quality_summary["dropped_missing_count"] = dropped_count

        if dropped_count > 0:
            logger.warning(
                "Dropping %d respondent(s) exceeding missingness threshold (> %.0f%% missing).",
                dropped_count, self.max_missing_ratio * 100.0
            )
            df = df[~drop_mask].reset_index(drop=True)
            raw_likert_df = raw_likert_df[~drop_mask].reset_index(drop=True)

        # 5. Median Imputation for Remaining Missing Likert Values
        imputed_cells = 0
        for col in likert_cols:
            missing_count = int(df[col].isna().sum())
            if missing_count > 0:
                med_val = df[col].median()
                df[col] = df[col].fillna(med_val)
                imputed_cells += missing_count
                logger.info("Imputed %d missing value(s) in '%s' with median %.1f.", missing_count, col, med_val)

        self.quality_summary["imputed_cells_count"] = imputed_cells

        # 6. Objective Knowledge Scoring (1 = Correct, 0 = Incorrect / Don't Know)
        for ar_k, k_info in config.KNOWLEDGE_QUESTIONS.items():
            short_k = k_info["short_name"]
            correct_val = k_info["correct"]
            raw_k_col = f"{short_k}_raw"
            df[raw_k_col] = df[short_k].astype(str).str.strip()
            # 1 if answer matches correct Arabic string, 0 otherwise (including 'لا أعرف' and NaN)
            df[short_k] = (df[raw_k_col] == correct_val).astype(int)

        self.quality_summary["final_count"] = len(df)
        logger.info(
            "Data ingestion complete. Final valid sample size: n = %d", len(df)
        )

        # Sample size warning check
        if len(df) < config.MIN_SAMPLE_SIZE_WARNING:
            logger.warning(
                "[SAMPLE SIZE WARNING] Final sample size (n = %d) is below recommended minimum (%d). "
                "Statistical tests may have limited power.",
                len(df), config.MIN_SAMPLE_SIZE_WARNING
            )

        return df, raw_likert_df, self.quality_summary


def print_data_quality_summary(summary: Dict[str, Any]) -> None:
    """Print an executive data-quality summary to stdout/logs."""
    print("\n" + "=" * 60)
    print(" JSSAA DATA QUALITY & INGESTION AUDIT SUMMARY")
    print("=" * 60)
    print(f" Raw Responses Loaded       : {summary['raw_count']}")
    print(f" Exact Duplicates Removed   : {summary['duplicate_count']}")
    print(f" Out-of-Range Likert Values : {summary['out_of_range_count']}")
    print(f" Dropped (>20% Missing)     : {summary['dropped_missing_count']}")
    print(f" Imputed Missing Cells      : {summary.get('imputed_cells_count', 0)}")
    print(f" Final Valid Sample Size (n): {summary['final_count']}")
    print("=" * 60 + "\n")

