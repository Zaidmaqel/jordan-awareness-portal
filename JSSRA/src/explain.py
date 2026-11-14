"""
JSSRA Calculation Trace & Step-by-Step Educational Explainer.

Provides a transparent visual audit trail and detailed mathematical justifications:
- Raw responses -> Reverse coding -> Protective dimension inversion -> Overall Index -> Z-score -> Percentile -> Band
- Relative contribution to risk index relative to neutral benchmark (3.0)
- Popover calculation breakdowns (Formula + Substitution + Result) for every single indicator
- Designed for university students presenting to the course instructor and classmates.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.stats_engine import reverse_item


def trace_respondent_calculations(
    respondent_answers: Dict[str, Any],
    community_mean: float,
    community_sd: float,
) -> Dict[str, Any]:
    """
    Constructs a complete audit trace of how a respondent's results were derived.

    Args:
        respondent_answers: Dict of E1..F4 raw responses (1-5).
        community_mean: Community sample mean overall risk index.
        community_sd: Community sample standard deviation (ddof=1).

    Returns:
        Structured trace dictionary with item tables, dimension contributions,
        step-by-step formulas, and popover texts.
    """
    # Step 1: Item-level processing
    items_table_rows = []
    dim_scored_items: Dict[str, List[float]] = {d: [] for d in config.DIMENSIONS.keys()}

    for item in config.SURVEY_ITEMS:
        it_id = item["id"]
        raw_val = float(respondent_answers.get(it_id, 3))
        is_rev = item["reverse"]
        scored_val = reverse_item(raw_val) if is_rev else raw_val

        dim_key = item["dimension"]
        dim_scored_items[dim_key].append(scored_val)

        # Contribution of this item relative to neutral midpoint 3
        # If dimension is protective, lower raw score = higher risk
        if config.DIMENSIONS[dim_key]["type"] == "protective":
            item_risk_impact = round(3.0 - scored_val, 2)
        else:
            item_risk_impact = round(scored_val - 3.0, 2)

        items_table_rows.append({
            "Item Code": it_id,
            "Dimension": config.DIMENSIONS[dim_key]["name_ar"],
            "Question Text (Arabic)": item["text_ar"],
            "Raw Answer (1-5)": int(raw_val),
            "Reverse-Coded?": "نعم (6 - x)" if is_rev else "لا",
            "Scored Value": scored_val,
            "Impact vs Neutral (3)": item_risk_impact,
        })

    items_df = pd.DataFrame(items_table_rows)

    # Step 2: Dimension-level processing
    dimensions_trace = []
    dim_risk_scores = {}

    for dim_key, dim_info in config.DIMENSIONS.items():
        vals = dim_scored_items[dim_key]
        raw_mean = float(np.mean(vals))

        if dim_info["type"] == "protective":
            risk_score = 6.0 - raw_mean
            inversion_note_ar = f"بعد وقائي: تم العكس للخطورة (6 - {raw_mean:.2f} = {risk_score:.2f})"
            inversion_note_en = f"Protective: inverted for risk (6 - {raw_mean:.2f} = {risk_score:.2f})"
        else:
            risk_score = raw_mean
            inversion_note_ar = f"بعد خطورة مباشر: المتوسّط المباشر = {risk_score:.2f}"
            inversion_note_en = f"Direct risk: raw mean = {risk_score:.2f}"

        dim_risk_scores[dim_key] = risk_score
        # Relative contribution compared to neutral value 3.0
        # Positive = elevates risk above neutral; Negative = lowers risk below neutral
        contribution = risk_score - 3.0

        dimensions_trace.append({
            "dim_key": dim_key,
            "code": dim_info["code"],
            "name_ar": dim_info["name_ar"],
            "name_en": dim_info["name_en"],
            "type": dim_info["type"],
            "item_values": vals,
            "raw_mean": round(raw_mean, 2),
            "risk_score": round(risk_score, 2),
            "contribution": round(contribution, 2),
            "inversion_note_ar": inversion_note_ar,
            "inversion_note_en": inversion_note_en,
        })

    # Step 3: Overall Risk Index calculation
    all_risks = [d["risk_score"] for d in dimensions_trace]
    overall_risk = float(np.mean(all_risks))

    # Step 4: Z-score & Percentile relative to community sample
    if community_sd > 0:
        z_score = (overall_risk - community_mean) / community_sd
    else:
        z_score = 0.0

    from scipy import stats
    percentile = float(stats.norm.cdf(z_score) * 100.0)

    # Step 5: Risk Band
    if overall_risk <= config.LOW_RISK_MAX:
        risk_band = "Low"
    elif overall_risk <= config.MODERATE_RISK_MAX:
        risk_band = "Moderate"
    else:
        risk_band = "High"

    # Step 6: Identify Top 2 Risk Drivers and Top 2 Protective Factors
    sorted_dims = sorted(dimensions_trace, key=lambda x: x["risk_score"], reverse=True)
    top_risk_drivers = sorted_dims[:2]  # Highest risk scores
    top_protective_factors = sorted_dims[-2:]  # Lowest risk scores (best protection)

    # Step 7: Popover Explainer Dictionary
    popovers = {
        "overall_risk": {
            "title_ar": "كيف حُسب مؤشر القابلية الكلي؟",
            "title_en": "How was the Overall Risk Index computed?",
            "formula": "Overall Risk = (D1 + D2_risk + D3_risk + D4 + D5_risk) / 5",
            "substitution": f"({all_risks[0]:.2f} + {all_risks[1]:.2f} + {all_risks[2]:.2f} + {all_risks[3]:.2f} + {all_risks[4]:.2f}) / 5",
            "result": f"{overall_risk:.2f} من 5.00",
            "explanation_ar": "يمثل المؤشر الكلي متوسط درجات الخطورة للأبعاد الخمسة، بعد عكس أبعاد الوقاية لتكون جميعها بنفس الاتجاه.",
            "explanation_en": "The overall index is the unweighted mean of all 5 dimension risk scores, after inverting protective scales.",
        },
        "z_score": {
            "title_ar": "كيف حُسبت الدرجة المعيارية (Z)؟",
            "title_en": "How was the Z-Score calculated?",
            "formula": "Z = (X - X̄) / σ",
            "substitution": f"({overall_risk:.2f} - {community_mean:.2f}) / {community_sd:.2f}",
            "result": f"Z = {z_score:+.2f}",
            "explanation_ar": f"توضح كم انحرافاً معيارياً تبعد نتيجتك ({overall_risk:.2f}) عن متوسط المجتمع الأردني ({community_mean:.2f}).",
            "explanation_en": f"Indicates how many standard deviations the score ({overall_risk:.2f}) deviates from the community mean ({community_mean:.2f}).",
        },
        "percentile": {
            "title_ar": "كيف حُسبت الرتبة المئينية؟",
            "title_en": "How was the Percentile Rank derived?",
            "formula": "Percentile = Φ(Z) × 100",
            "substitution": f"Φ({z_score:+.2f}) × 100",
            "result": f"{percentile:.1f}%",
            "explanation_ar": f"تعني أن نتيجتك أعلى من {percentile:.1f}% من أفراد عينة المجتمع، وأقل من {100 - percentile:.1f}%.",
            "explanation_en": f"Means your score is higher than {percentile:.1f}% of community peers, and lower than {100 - percentile:.1f}%.",
        },
    }

    return {
        "items_table": items_df,
        "dimensions_trace": dimensions_trace,
        "overall_risk": round(overall_risk, 2),
        "z_score": round(z_score, 2),
        "percentile": round(percentile, 1),
        "risk_band": risk_band,
        "top_risk_drivers": top_risk_drivers,
        "top_protective_factors": top_protective_factors,
        "popovers": popovers,
    }

