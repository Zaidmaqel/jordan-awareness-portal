"""
JSSAA Comprehensive Pytest Validation Suite.

Tests psychometric algorithms, quality auditing, data ingestion, reverse-coding,
Cronbach's alpha, anomaly detection, threshold categorization, and pipeline integration.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from src.preprocessing import reverse_code, assign_awareness_band, Preprocessor
from src.data_loader import DataLoader, normalize_arabic_text
from src.statistics import (
    cronbach_alpha_numpy,
    compute_descriptive_stats,
    compute_scale_reliability,
    rank_dimensions_and_items,
    run_demographic_tests,
)
from src.outliers import QualityAuditor
from src.decision_engine import DecisionEngine


class TestPsychometricsAndScoring:
    """Tests for psychometric transformations and scoring rules."""

    def test_reverse_coding_exactness(self):
        """Verify (LIKERT_MAX + LIKERT_MIN - x) formula on 1-5 scale."""
        # 1 -> 5, 2 -> 4, 3 -> 3, 4 -> 2, 5 -> 1
        assert reverse_code(1, 1, 5) == 5.0
        assert reverse_code(2, 1, 5) == 4.0
        assert reverse_code(3, 1, 5) == 3.0
        assert reverse_code(4, 1, 5) == 2.0
        assert reverse_code(5, 1, 5) == 1.0
        assert np.isnan(reverse_code(np.nan, 1, 5))

    def test_awareness_band_categorization(self):
        """Verify risk band threshold boundaries: Low (<=2.33), Moderate (2.34-3.66), High (>=3.67)."""
        assert assign_awareness_band(1.0, 2.33, 3.66) == "Low"
        assert assign_awareness_band(2.33, 2.33, 3.66) == "Low"
        assert assign_awareness_band(2.34, 2.33, 3.66) == "Moderate"
        assert assign_awareness_band(3.00, 2.33, 3.66) == "Moderate"
        assert assign_awareness_band(3.66, 2.33, 3.66) == "Moderate"
        assert assign_awareness_band(3.67, 2.33, 3.66) == "High"
        assert assign_awareness_band(5.00, 2.33, 3.66) == "High"

    def test_cronbach_alpha_known_values(self):
        """Verify vectorized Cronbach's alpha on synthetic test matrix."""
        # Perfectly correlated items -> alpha should approach 1.0
        perfect_items = np.array([
            [1, 1, 1],
            [2, 2, 2],
            [3, 3, 3],
            [4, 4, 4],
            [5, 5, 5],
        ], dtype=float)
        alpha = cronbach_alpha_numpy(perfect_items)
        assert pytest.approx(alpha, abs=1e-3) == 1.0

        # Uncorrelated random items -> alpha should be low
        np.random.seed(42)
        uncorrelated = np.random.randint(1, 6, size=(100, 5)).astype(float)
        alpha_rand = cronbach_alpha_numpy(uncorrelated)
        assert alpha_rand < 0.40


class TestDataQualityAndAuditing:
    """Tests for anomaly detection, straight-lining, and consistency checking."""

    def test_arabic_header_normalization(self):
        """Verify normalization handles tatweel, whitespace, and non-breaking spaces."""
        raw_text = " أتابع  الأخبار   عبر مواقعـ التواصل\u00a0"
        normalized = normalize_arabic_text(raw_text)
        assert "ـ" not in normalized
        assert "\u00a0" not in normalized
        assert "  " not in normalized
        assert normalized == "أتابع الأخبار عبر مواقع التواصل"

    def test_straightlining_detection(self):
        """Verify straight-lining flags respondents with zero variance across raw items."""
        auditor = QualityAuditor()
        likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values()]

        # Create dummy df where respondent 0 is straightlining all 3s, respondent 1 varies
        raw_data = {col: [3, 2] for col in likert_cols}
        raw_data[likert_cols[0]] = [3, 4]  # respondent 1 varies
        raw_df = pd.DataFrame(raw_data)

        df = raw_df.copy()
        df["overall_awareness_score"] = [3.0, 3.2]
        df["awareness_band"] = ["Moderate", "Moderate"]

        _, suspicious_df, summary = auditor.audit(df, raw_df)
        flagged_ids = suspicious_df["respondent_id"].tolist()
        assert 0 in flagged_ids
        assert summary["straightliner_count"] >= 1

    def test_consistency_pairs_detection(self):
        """Verify contradictory answers (|normal - reversed| >= 3 after reversing) are flagged."""
        auditor = QualityAuditor(consistency_diff_threshold=3.0)
        likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values()]

        # Clean baseline df
        df = pd.DataFrame(np.full((3, len(likert_cols)), 3.0), columns=likert_cols)
        raw_df = df.copy()

        # In respondent 1, introduce severe contradiction on RD1 (distinguish) and RD5 (difficulty)
        # After reversing, RD1 = 5, RD5 = 1 -> |5 - 1| = 4 >= 3
        df.at[1, "RD1_distinguish"] = 5.0
        df.at[1, "RD5_difficulty"] = 1.0  # (originally raw was 5, reversed to 1)

        df["overall_awareness_score"] = [3.0, 3.0, 3.0]
        df["awareness_band"] = ["Moderate", "Moderate", "Moderate"]

        _, suspicious_df, _ = auditor.audit(df, raw_df)
        flagged_ids = suspicious_df["respondent_id"].tolist()
        assert 1 in flagged_ids


class TestDecisionAndPolicyEngine:
    """Tests for threshold escalation and prioritized recommendations."""

    def test_escalation_rule(self):
        """Verify severity escalates when Low-band percentage > 30%."""
        engine = DecisionEngine(low_band_escalation_pct=30.0)

        # Dataset with 40% Low band respondents
        bands = ["Low"] * 40 + ["Moderate"] * 60
        scores = [2.0] * 40 + [3.0] * 60
        df = pd.DataFrame({
            "overall_awareness_score": scores,
            "awareness_band": bands,
        })

        status = engine.determine_system_status(df)
        assert status["escalated"] is True
        assert "ESCALATED" in status["final_status"]

    def test_priority_score_formula(self):
        """Verify Priority Score = (TARGET_SCORE - mean) * (1 + pct_low / 100)."""
        engine = DecisionEngine(target_score=4.0)
        # Dimension with mean = 3.0 and pct_low = 20%
        # Priority = (4.0 - 3.0) * (1 + 0.20) = 1.20
        dim_scores = [2.0] * 20 + [3.25] * 80
        dim_bands = ["Low"] * 20 + ["Moderate"] * 80
        df = pd.DataFrame({
            "dim_rumor_detection": dim_scores,
            "band_rumor_detection": dim_bands,
            "dim_digital_threat_awareness": [3.5] * 100,
            "band_digital_threat_awareness": ["Moderate"] * 100,
            "dim_official_source_trust": [3.5] * 100,
            "band_official_source_trust": ["Moderate"] * 100,
            "dim_verification_behavior": [3.5] * 100,
            "band_verification_behavior": ["Moderate"] * 100,
        })
        recs = engine.generate_prioritized_recommendations(df)
        rd_rec = [r for r in recs if r["dimension"] == "rumor_detection"][0]
        assert pytest.approx(rd_rec["priority_score"], abs=0.05) == 1.20


class TestPipelineIntegrationSmoke:
    """Full end-to-end smoke test on sample data."""

    def test_full_pipeline_run(self, tmp_path):
        """Test full pipeline runs with output creation and sensitivity analysis."""
        from main import run_pipeline

        sample_file = "data/sample_survey_responses.xlsx"
        assert os.path.exists(sample_file), "Sample survey responses file must exist."

        out_dir = str(tmp_path / "test_outputs")
        result = run_pipeline(
            input_path=sample_file,
            output_dir=out_dir,
            sheet_name=0,
            no_pdf=False,
            sensitivity=True,
        )

        assert result["status"] == "SUCCESS"
        assert os.path.exists(os.path.join(out_dir, "jordan_awareness_dashboard.png"))
        assert os.path.exists(os.path.join(out_dir, "dimension_radar_chart.png"))
        assert os.path.exists(os.path.join(out_dir, "demographic_boxplots.png"))
        assert os.path.exists(os.path.join(out_dir, "perceived_vs_actual_scatter.png"))
        assert os.path.exists(os.path.join(out_dir, "pca_scree_plot.png"))
        assert os.path.exists(os.path.join(out_dir, "JSSAA_results.xlsx"))
        assert os.path.exists(os.path.join(out_dir, "executive_report.txt"))
        assert os.path.exists(os.path.join(out_dir, "executive_report.md"))
        assert os.path.exists(os.path.join(out_dir, "analysis_log.txt"))

