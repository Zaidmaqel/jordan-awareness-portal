"""
JSSRA Data Persistence & Storage Engine.

Safely handles atomic/locked logging of anonymous survey responses,
data partitioning between real and synthetic demo submissions,
and administrative import/export operations.
"""

import os
import threading
import uuid
import datetime
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.synthetic import generate_synthetic_cohort

_file_lock = threading.Lock()

RESPONSE_COLUMNS = [
    "response_id",
    "timestamp",
    "respondent_type",
    "age_group",
    "gender",
    "governorate",
    "education",
    "daily_social_media_hours",
    # 20 items
    "E1", "E2", "E3", "E4",
    "C1", "C2", "C3", "C4",
    "T1", "T2", "T3", "T4",
    "S1", "S2", "S3", "S4",
    "F1", "F2", "F3", "F4",
    "source",  # "real" or "synthetic"
]


class StorageManager:
    """Manages anonymous CSV storage with thread safety."""

    def __init__(self, data_path: str = config.DATA_FILE):
        self.data_path = data_path
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self._ensure_file_initialized()

    def _ensure_file_initialized(self):
        """Initializes response CSV file with headers if missing."""
        with _file_lock:
            if not os.path.exists(self.data_path) or os.path.getsize(self.data_path) == 0:
                empty_df = pd.DataFrame(columns=RESPONSE_COLUMNS)
                empty_df.to_csv(self.data_path, index=False, encoding="utf-8-sig")

    def append_response(self, respondent_data: Dict[str, Any], source: str = "real") -> str:
        """
        Atomically appends one anonymous respondent submission to the CSV.

        Args:
            respondent_data: Dictionary containing demographic selections and 20 item values.
            source: "real" for live submissions, "synthetic" for demo runs.

        Returns:
            Assigned anonymous response ID string.
        """
        resp_id = str(uuid.uuid4())[:8]
        now_rounded = datetime.datetime.now().replace(second=0, microsecond=0)
        timestamp_str = now_rounded.strftime("%Y-%m-%d %H:%M")

        row = {
            "response_id": resp_id,
            "timestamp": timestamp_str,
            "respondent_type": respondent_data.get("respondent_type", ""),
            "age_group": respondent_data.get("age_group", ""),
            "gender": respondent_data.get("gender", ""),
            "governorate": respondent_data.get("governorate", ""),
            "education": respondent_data.get("education", ""),
            "daily_social_media_hours": respondent_data.get("daily_social_media_hours", ""),
            "source": source,
        }

        # Items E1..F4
        for item in config.SURVEY_ITEMS:
            item_id = item["id"]
            row[item_id] = int(respondent_data.get(item_id, 3))

        row_df = pd.DataFrame([row], columns=RESPONSE_COLUMNS)

        with _file_lock:
            row_df.to_csv(self.data_path, mode="a", header=False, index=False, encoding="utf-8-sig")

        return resp_id

    def load_responses(self, include_synthetic: bool = False) -> pd.DataFrame:
        """
        Loads responses from disk.

        Args:
            include_synthetic: If True, includes synthetic demo rows; otherwise real rows only.
        """
        self._ensure_file_initialized()
        with _file_lock:
            try:
                df = pd.read_csv(self.data_path, encoding="utf-8-sig")
            except Exception:
                df = pd.read_csv(self.data_path, encoding="utf-8")

        if df.empty:
            return df

        # Ensure correct column typing
        item_cols = [item["id"] for item in config.SURVEY_ITEMS]
        for col in item_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(3).astype(int)

        if not include_synthetic:
            df = df[df["source"] == "real"].copy().reset_index(drop=True)

        return df

    def seed_synthetic_data(self, n: int = 150) -> pd.DataFrame:
        """Seeds synthetic cohort into storage if no synthetic data exists."""
        synth_df = generate_synthetic_cohort(n=n)
        with _file_lock:
            synth_df.to_csv(self.data_path, mode="a", header=False, index=False, encoding="utf-8-sig")
        return synth_df

    def clear_all(self):
        """Clears all stored data (Admin function)."""
        with _file_lock:
            empty_df = pd.DataFrame(columns=RESPONSE_COLUMNS)
            empty_df.to_csv(self.data_path, index=False, encoding="utf-8-sig")

