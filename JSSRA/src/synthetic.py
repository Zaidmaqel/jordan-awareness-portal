"""
JSSRA Synthetic Sample Generator.

Generates realistic survey response data for Jordan youth vulnerability modeling
using a latent risk-factor model to ensure authentic psychometric properties:
- D1 (online exposure) and D4 (isolation) correlate positively with vulnerability.
- D2 (critical thinking), D3 (trust official), and D5 (family support) correlate negatively.
- Realistic demographic distributions for Jordan (Amman-heavy, young age skew).
- Every synthetic row carries source="synthetic".
"""

import os
import random
import uuid
import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def generate_synthetic_cohort(
    n: int = 150,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic cohort modeling youth vulnerability in Jordan.

    Args:
        n: Number of synthetic respondents (default: 150).
        seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame of responses with demographic and item columns.
    """
    np.random.seed(seed)
    random.seed(seed)

    # 1. Demographic sampling probabilities
    gov_opts = config.DEMOGRAPHICS["governorate"]["options"]
    gov_probs = [0.42, 0.18, 0.14, 0.06, 0.03, 0.03, 0.02, 0.02, 0.03, 0.03, 0.02, 0.02]
    gov_probs = [p / sum(gov_probs) for p in gov_probs]

    resp_type_opts = config.DEMOGRAPHICS["respondent_type"]["options"]
    resp_type_probs = [0.55, 0.22, 0.13, 0.10]  # University student heavy

    age_opts = config.DEMOGRAPHICS["age_group"]["options"]
    age_probs = [0.45, 0.35, 0.14, 0.06]

    gender_opts = config.DEMOGRAPHICS["gender"]["options"]
    gender_probs = [0.49, 0.51]

    edu_opts = config.DEMOGRAPHICS["education"]["options"]
    edu_probs = [0.12, 0.15, 0.60, 0.13]

    hours_opts = config.DEMOGRAPHICS["daily_social_media_hours"]["options"]
    hours_probs = [0.08, 0.32, 0.40, 0.20]

    # Sample demographic arrays
    governorates = np.random.choice(gov_opts, size=n, p=gov_probs)
    resp_types = np.random.choice(resp_type_opts, size=n, p=resp_type_probs)
    age_groups = np.random.choice(age_opts, size=n, p=age_probs)
    genders = np.random.choice(gender_opts, size=n, p=gender_probs)
    educations = np.random.choice(edu_opts, size=n, p=edu_probs)
    social_hours = np.random.choice(hours_opts, size=n, p=hours_probs)

    # 2. Latent Factors Modeling
    # Latent vulnerability factor (v) ~ Normal(0, 1)
    # Plus subgroup shifts: non-working youth face higher economic anxiety / isolation (+0.4)
    # Graduate students and higher education show higher protective thinking (-0.3)
    type_shift = np.array([
        0.0 if t == "طالب جامعي" else
        0.1 if t == "شاب غير طالب يعمل" else
        0.45 if t == "شاب غير طالب لا يعمل" else -0.3
        for t in resp_types
    ])

    base_v = np.random.normal(0, 0.9, size=n)
    latent_vulnerability = base_v + type_shift

    # Timestamps spread over the past 30 days
    start_time = datetime.datetime.now() - datetime.timedelta(days=30)

    rows = []
    for i in range(n):
        row: Dict[str, Any] = {}
        row["response_id"] = str(uuid.uuid4())[:8]
        # Rounded to minute
        delta = datetime.timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        sub_time = (start_time + delta).replace(second=0, microsecond=0)
        row["timestamp"] = sub_time.strftime("%Y-%m-%d %H:%M")

        row["respondent_type"] = resp_types[i]
        row["age_group"] = age_groups[i]
        row["gender"] = genders[i]
        row["governorate"] = governorates[i]
        row["education"] = educations[i]
        row["daily_social_media_hours"] = social_hours[i]
        row["source"] = "synthetic"

        v = latent_vulnerability[i]

        # 3. Item responses generated from latent factor
        # For D1 (online exposure, risk): positive slope with v
        # For D4 (isolation, risk): strong positive slope with v
        # For D2 (critical thinking, protective): negative slope with v
        # For D3 (trust official, protective): negative slope with v
        # For D5 (family/community, protective): strong negative slope with v
        for item in config.SURVEY_ITEMS:
            item_id = item["id"]
            dim = item["dimension"]
            is_rev = item["reverse"]

            if dim == "online_exposure":
                item_mean = 2.4 + 0.55 * v + np.random.normal(0, 0.45)
            elif dim == "isolation_susceptibility":
                item_mean = 2.3 + 0.65 * v + np.random.normal(0, 0.45)
            elif dim == "critical_thinking":
                item_mean = 3.6 - 0.50 * v + np.random.normal(0, 0.45)
            elif dim == "trust_official":
                item_mean = 3.3 - 0.45 * v + np.random.normal(0, 0.50)
            elif dim == "family_community_support":
                item_mean = 3.7 - 0.60 * v + np.random.normal(0, 0.45)
            else:
                item_mean = 3.0 + np.random.normal(0, 0.5)

            # Bound item_mean to 1.0 - 5.0
            item_mean = max(1.0, min(5.0, item_mean))

            # If item is reverse-worded (R), invert target value before adding noise,
            # so that when the pipeline reverses (6 - x), it recovers the intended score!
            if is_rev:
                raw_target = 6.0 - item_mean
            else:
                raw_target = item_mean

            val = int(np.clip(np.round(raw_target + np.random.normal(0, 0.2)), 1, 5))
            row[item_id] = val

        rows.append(row)

    df = pd.DataFrame(rows)
    return df

