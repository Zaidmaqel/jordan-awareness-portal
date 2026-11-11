"""
JSSAA Synthetic Sample Survey Data Generator.

Generates realistic survey response data for Jordan Social & Security Awareness Analysis
using the exact Arabic headers from config.py.
Incorporates demographic distributions, latent correlation structures, and deliberate
quality defects (duplicates, missingness, straight-lining, inconsistencies, out-of-range)
to validate the analysis pipeline.
"""

import os
import random
import datetime
from typing import List, Dict, Any
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def generate_synthetic_data(
    n_clean: int = 240,
    seed: int = 42,
    output_path: str = "data/sample_survey_responses.xlsx",
) -> pd.DataFrame:
    """
    Generate synthetic survey responses modeling Jordanian community dynamics.

    Args:
        n_clean: Number of base clean respondents (~240, plus duplicates = ~250 total).
        seed: Random seed for reproducibility.
        output_path: Path to save the Excel file.

    Returns:
        pd.DataFrame containing the generated dataset.
    """
    np.random.seed(seed)
    random.seed(seed)

    # 1. Demographic distributions
    govs = config.DEMOGRAPHIC_OPTIONS["governorate"]
    # Amman heavy (~42%), Irbid (~19%), Zarqa (~14%), Balqa (~6%), others 1-4%
    gov_probs = [0.42, 0.19, 0.14, 0.06, 0.03, 0.03, 0.02, 0.02, 0.03, 0.03, 0.02, 0.03]
    gov_probs = [p / sum(gov_probs) for p in gov_probs]

    age_cats = config.DEMOGRAPHIC_OPTIONS["age_group"]
    age_probs = [0.38, 0.32, 0.18, 0.12]  # Young-skewed distribution

    edu_cats = config.DEMOGRAPHIC_OPTIONS["education_level"]
    edu_probs = [0.15, 0.15, 0.55, 0.15]  # Bachelor heavy

    gender_cats = config.DEMOGRAPHIC_OPTIONS["gender"]
    gender_probs = [0.49, 0.51]

    major_cats = config.DEMOGRAPHIC_OPTIONS["major"]
    major_probs = [0.25, 0.22, 0.23, 0.20, 0.10]

    hours_cats = config.DEMOGRAPHIC_OPTIONS["social_media_hours"]
    hours_probs = [0.10, 0.32, 0.38, 0.20]

    # Sample demographics
    governorates = np.random.choice(govs, size=n_clean, p=gov_probs)
    age_groups = np.random.choice(age_cats, size=n_clean, p=age_probs)
    education_levels = np.random.choice(edu_cats, size=n_clean, p=edu_probs)
    genders = np.random.choice(gender_cats, size=n_clean, p=gender_probs)
    majors = np.random.choice(major_cats, size=n_clean, p=major_probs)
    social_hours = np.random.choice(hours_cats, size=n_clean, p=hours_probs)

    # 2. Latent traits generation
    # Underlying factors: general awareness (g), official trust (t), media immersion (m)
    # Correlation between general awareness and official trust: positive (~0.35)
    # Media immersion slightly negative to verification / slightly positive to rumor belief
    cov_matrix = [
        [1.0, 0.35, -0.15],
        [0.35, 1.0, 0.10],
        [-0.15, 0.10, 1.0],
    ]
    latent_traits = np.random.multivariate_normal(mean=[0, 0, 0], cov=cov_matrix, size=n_clean)
    latent_awareness = latent_traits[:, 0]
    latent_trust = latent_traits[:, 1]
    latent_media = latent_traits[:, 2]

    # Education bonus to digital threat awareness
    edu_bonus = np.array([
        0.0 if e == "ثانوية فأقل" else 0.2 if e == "دبلوم" else 0.4 if e == "بكالوريوس" else 0.6
        for e in education_levels
    ])
    # Age effect: older respondents have higher official trust, younger have higher media immersion
    age_trust_bonus = np.array([
        -0.2 if a == "18–24" else 0.0 if a == "25–34" else 0.2 if a == "35–44" else 0.4
        for a in age_groups
    ])

    rows = []
    base_time = datetime.datetime(2026, 10, 1, 9, 0, 0)

    for i in range(n_clean):
        row: Dict[str, Any] = {}
        # Timestamp
        time_offset = datetime.timedelta(
            days=random.randint(0, 14),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        row["الطابع الزمني"] = (base_time + time_offset).strftime("%Y/%m/%d %I:%M:%S %p")

        # Demographics
        row["الجنس"] = genders[i]
        row["الفئة العمرية"] = age_groups[i]
        row["المستوى التعليمي"] = education_levels[i]
        row["مجال التخصص أو العمل"] = majors[i]
        row["محافظة السكن"] = governorates[i]
        row["ساعات استخدام السوشال ميديا يومياً"] = social_hours[i]

        law = latent_awareness[i]
        ltr = latent_trust[i] + age_trust_bonus[i]
        lmed = latent_media[i]
        ebonus = edu_bonus[i]

        # Generate Likert items based on latent factors
        for q_text, q_info in config.QUESTION_MAP.items():
            dim = q_info["dimension"]
            is_rev = q_info["reverse"]

            # Compute targeted latent score (scale roughly 1 to 5, center ~3.4)
            if dim == "media_exposure":
                base_score = 3.6 + 0.6 * lmed + np.random.normal(0, 0.5)
            elif dim == "rumor_detection":
                base_score = 3.4 + 0.7 * law + np.random.normal(0, 0.5)
            elif dim == "digital_threat_awareness":
                base_score = 3.3 + 0.6 * law + 0.5 * ebonus + np.random.normal(0, 0.5)
            elif dim == "official_source_trust":
                base_score = 3.2 + 0.8 * ltr + np.random.normal(0, 0.5)
            elif dim == "verification_behavior":
                base_score = 3.2 + 0.7 * law - 0.2 * lmed + np.random.normal(0, 0.5)
            else:
                base_score = 3.0 + np.random.normal(0, 0.6)

            # Bound base_score to [1.0, 5.0]
            base_score = max(1.0, min(5.0, base_score))

            # Convert to raw response: if item is reverse, the raw response must be inverted!
            # so that when the pipeline does (6 - raw), it recovers base_score.
            # i.e., raw = 6 - base_score
            if is_rev:
                raw_continuous = (config.LIKERT_MAX + config.LIKERT_MIN) - base_score
            else:
                raw_continuous = base_score

            # Add noise and round to nearest integer 1..5
            val = int(np.clip(np.round(raw_continuous + np.random.normal(0, 0.2)), 1, 5))
            row[q_text] = val

        # Generate Knowledge questions (Objective test)
        # Probability of answering correctly is linked to latent awareness
        for k_text, k_info in config.KNOWLEDGE_QUESTIONS.items():
            corr_ans = k_info["correct"]
            incorr_ans = "صح" if corr_ans == "خطأ" else "خطأ"
            
            prob_correct = 1.0 / (1.0 + np.exp(-(0.8 + 0.7 * law + 0.4 * ebonus)))
            prob_correct = max(0.40, min(0.92, prob_correct))
            prob_dont_know = 0.08

            rnd = np.random.rand()
            if rnd < prob_correct:
                row[k_text] = corr_ans
            elif rnd < prob_correct + prob_dont_know:
                row[k_text] = "لا أعرف"
            else:
                row[k_text] = incorr_ans

        rows.append(row)

    df = pd.DataFrame(rows)

    # 3. Inject deliberate defects for quality auditing validation

    # Defect A: ~8 Straight-liners (all 3s, all 4s, all 5s across Likert items)
    straightline_indices = [10, 25, 45, 70, 95, 120, 150, 180]
    straightline_vals = [3, 4, 5, 3, 4, 3, 5, 4]
    for idx, s_val in zip(straightline_indices, straightline_vals):
        for q_text in config.QUESTION_MAP.keys():
            df.at[idx, q_text] = s_val

    # Defect B: ~5 Contradictory respondents (violating consistency pairs)
    # E.g. RD1 (normal)=5 and RD5 (reverse)=5 -> after reverse coding, RD5 becomes 1 -> |5 - 1| = 4 >= 3
    # E.g. OT1 (normal)=5 and OT4 (reverse)=5 -> after reverse coding, OT4 becomes 1 -> |5 - 1| = 4 >= 3
    contra_indices = [15, 55, 85, 135, 165]
    rd1_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "RD1_distinguish"][0]
    rd5_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "RD5_difficulty"][0]
    ot1_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "OT1_trust"][0]
    ot4_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "OT4_distrust"][0]
    vb3_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "VB3_hold_share"][0]
    vb5_key = [k for k, v in config.QUESTION_MAP.items() if v["short_name"] == "VB5_impulsive_share"][0]

    df.at[contra_indices[0], rd1_key] = 5
    df.at[contra_indices[0], rd5_key] = 5  # Contradiction on RD

    df.at[contra_indices[1], ot1_key] = 5
    df.at[contra_indices[1], ot4_key] = 5  # Contradiction on OT

    df.at[contra_indices[2], vb3_key] = 5
    df.at[contra_indices[2], vb5_key] = 5  # Contradiction on VB

    df.at[contra_indices[3], rd1_key] = 5
    df.at[contra_indices[3], rd5_key] = 5

    df.at[contra_indices[4], ot1_key] = 1
    df.at[contra_indices[4], ot4_key] = 1

    # Defect C: Out-of-range values (0, 6, 7)
    oor_q1 = list(config.QUESTION_MAP.keys())[0]
    oor_q2 = list(config.QUESTION_MAP.keys())[4]
    oor_q3 = list(config.QUESTION_MAP.keys())[8]
    df.at[30, oor_q1] = 0
    df.at[60, oor_q2] = 6
    df.at[110, oor_q3] = 7

    # Defect D: Missing values
    # Randomly introduce 1-2 missing items in a few rows (below 20% threshold -> median imputed)
    for row_idx in [5, 12, 22, 37, 51, 68, 88, 102, 140, 160, 175, 195]:
        target_q = random.choice(list(config.QUESTION_MAP.keys()))
        df.at[row_idx, target_q] = np.nan

    # Introduce 1 respondent with severe missingness (> 20% missing -> dropped)
    severe_missing_idx = 200
    for q_text in list(config.QUESTION_MAP.keys())[:8]:
        df.at[severe_missing_idx, q_text] = np.nan

    # Defect E: Exact duplicates (~5 duplicate rows)
    dup_rows = df.iloc[[8, 19, 42, 64, 82]].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Save to Excel
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"Synthetic survey data successfully generated at '{output_path}'. Total rows: {len(df)}")
    return df


if __name__ == "__main__":
    generate_synthetic_data()

