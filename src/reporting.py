"""
JSSAA Comprehensive Reporting & Artifact Export Module.

Exports all analytical, statistical, and policy outputs to the outputs/ directory:
1. Multi-tab Excel workbook: JSSAA_results.xlsx
2. Executive Decision Report: executive_report.txt
3. Executive Decision Report: executive_report.md
4. PDF Executive Decision Report: executive_report.pdf (via ReportLab, Arabic-safe)
5. Execution and Analysis Log: analysis_log.txt
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
from src.visualization import ar

logger = logging.getLogger("JSSAA.reporting")


class ReportGenerator:
    """
    Coordinates multi-format exporting of analytical results, tables, and reports.
    """

    def __init__(self, output_dir: str = config.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_excel(
        self,
        cleaned_df: pd.DataFrame,
        descriptive_stats_df: pd.DataFrame,
        reliability_dict: Dict[str, Any],
        spearman_corr: pd.DataFrame,
        pearson_corr: pd.DataFrame,
        group_tests_df: pd.DataFrame,
        suspicious_df: pd.DataFrame,
        prioritized_recs: List[Dict[str, Any]],
        action_plan: List[Dict[str, Any]],
        filename: str = "JSSAA_results.xlsx",
    ) -> str:
        """
        Exports all analytical datasets and statistical models to a
        professional, multi-tab Excel workbook.
        """
        out_path = os.path.join(self.output_dir, filename)
        logger.info("Writing multi-tab analytical results to Excel at: %s", out_path)

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            # 1. Cleaned Data
            cleaned_df.to_excel(writer, sheet_name="Cleaned_Data", index=True)

            # 2. Descriptive Statistics
            descriptive_stats_df.to_excel(writer, sheet_name="Descriptive_Stats", index=False)

            # 3. Dimension Scores Summary
            dim_cols = [f"dim_{d}" for d in config.DIMENSIONS if f"dim_{d}" in cleaned_df.columns]
            score_summary_cols = dim_cols + ["overall_awareness_score", "awareness_band"]
            if "actual_knowledge_score" in cleaned_df.columns:
                score_summary_cols.append("actual_knowledge_score")
            if "perception_reality_gap" in cleaned_df.columns:
                score_summary_cols.append("perception_reality_gap")

            dim_summary_df = cleaned_df[[c for c in score_summary_cols if c in cleaned_df.columns]].copy()
            dim_summary_df.to_excel(writer, sheet_name="Dimension_Scores", index=True)

            # 4. Reliability Table
            rel_rows = []
            for k_scale, v_info in reliability_dict.items():
                rel_rows.append({
                    "scale_name": k_scale,
                    "k_items": v_info.get("k_items", 0),
                    "cronbach_alpha": v_info.get("alpha", np.nan),
                    "interpretation": v_info.get("interpretation", "N/A"),
                })
            pd.DataFrame(rel_rows).to_excel(writer, sheet_name="Reliability", index=False)

            # 5. Spearman Correlation Matrix
            spearman_corr.to_excel(writer, sheet_name="Correlation_Spearman", index=True)

            # 6. Pearson Correlation Matrix
            pearson_corr.to_excel(writer, sheet_name="Correlation_Pearson", index=True)

            # 7. Group Tests
            group_tests_df.to_excel(writer, sheet_name="Group_Tests", index=False)

            # 8. Outliers and Quality Flags
            suspicious_df.to_excel(writer, sheet_name="Outliers_Flags", index=False)

            # 9. Prioritized Recommendations
            rec_rows = []
            for r in prioritized_recs:
                rec_rows.append({
                    "priority_score": r["priority_score"],
                    "dimension": r["dimension"],
                    "mean_score": r["dimension_mean"],
                    "pct_in_low_band": r["pct_low_band"],
                    "title": r["title"],
                    "lead_stakeholders": r["stakeholders"],
                    "key_interventions": "; ".join(r["interventions"]),
                })
            pd.DataFrame(rec_rows).to_excel(writer, sheet_name="Recommendations", index=False)

            # 10. Action Plan
            pd.DataFrame(action_plan).to_excel(writer, sheet_name="Action_Plan", index=False)

        logger.info("Excel workbook successfully created at: %s", out_path)
        return out_path

    def export_text_reports(
        self,
        txt_content: str,
        md_content: str,
        txt_filename: str = "executive_report.txt",
        md_filename: str = "executive_report.md",
    ) -> Tuple[str, str]:
        """
        Writes executive decision report in Plain Text (.txt) and Markdown (.md).
        """
        txt_path = os.path.join(self.output_dir, txt_filename)
        md_path = os.path.join(self.output_dir, md_filename)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info("Saved text report: %s", txt_path)
        logger.info("Saved markdown report: %s", md_path)
        return txt_path, md_path

    def export_pdf(
        self,
        system_status: Dict[str, Any],
        quality_summary: Dict[str, Any],
        reliability_dict: Dict[str, Any],
        ranking_results: Dict[str, Any],
        prioritized_recs: List[Dict[str, Any]],
        action_plan: List[Dict[str, Any]],
        filename: str = "executive_report.pdf",
    ) -> Optional[str]:
        """
        Generates an executive PDF report using ReportLab.
        If ReportLab is unavailable or fails, skips gracefully with an informative log message.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            logger.info("ReportLab is not installed; skipping PDF generation.")
            return None

        out_path = os.path.join(self.output_dir, filename)

        try:
            # Register TrueType font if available
            font_name = "Helvetica"
            font_name_bold = "Helvetica-Bold"

            # Check Windows Fonts directory for Arial
            for f_cand in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
                if os.path.exists(f_cand):
                    try:
                        pdfmetrics.registerFont(TTFont("WinSysFont", f_cand))
                        font_name = "WinSysFont"
                        font_name_bold = "WinSysFont"
                        break
                    except Exception:
                        pass

            doc = SimpleDocTemplate(
                out_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40,
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Heading1"],
                fontName=font_name_bold,
                fontSize=18,
                textColor=colors.HexColor("#2C3E50"),
                spaceAfter=12,
            )
            h2_style = ParagraphStyle(
                "SectionH2",
                parent=styles["Heading2"],
                fontName=font_name_bold,
                fontSize=13,
                textColor=colors.HexColor("#2C3E50"),
                spaceBefore=12,
                spaceAfter=6,
            )
            body_style = ParagraphStyle(
                "BodyTextCustom",
                parent=styles["Normal"],
                fontName=font_name,
                fontSize=9.5,
                leading=13,
                textColor=colors.HexColor("#333333"),
            )

            story = []

            # Document Header
            story.append(Paragraph("JSSAA EXECUTIVE DECISION REPORT", title_style))
            story.append(Paragraph("<b>Jordan Social & Security Awareness Analysis</b> | Strategic Assessment", body_style))
            story.append(Spacer(1, 10))

            # Strategic Status Table
            status_data = [
                ["Metric / Indicator", "Evaluated Value"],
                ["National Awareness Status", system_status["final_status"]],
                ["Severity Rating", system_status["final_severity"]],
                ["Sample Mean Score", f"{system_status['mean_score']} / 5.000 (SD = {system_status['sd_score']})"],
                ["95% Confidence Interval", f"[{system_status['ci_95'][0]}, {system_status['ci_95'][1]}]"],
                ["High Risk / Low Band (<= 2.33)", f"{system_status['pct_low']}% of sample"],
                ["Moderate Risk Band (2.34 - 3.66)", f"{system_status['pct_moderate']}% of sample"],
                ["Stable Awareness Band (>= 3.67)", f"{system_status['pct_high']}% of sample"],
                ["Valid Analytic Cohort", f"n = {quality_summary['final_count']} (Duplicates Removed: {quality_summary['duplicate_count']})"],
            ]
            t_status = Table(status_data, colWidths=[200, 330])
            t_status.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
            ]))
            story.append(t_status)
            story.append(Spacer(1, 12))

            # Dimensional Rankings
            story.append(Paragraph("Dimensional Awareness Performance", h2_style))
            dim_rank_data = [["Rank", "Dimension Name", "Mean Score (1-5)", "Target Benchmark"]]
            for idx, (d_name, d_val) in enumerate(ranking_results["ranked_dimensions"], start=1):
                dim_rank_data.append([str(idx), d_name, f"{d_val:.3f}", str(config.TARGET_SCORE)])

            t_rank = Table(dim_rank_data, colWidths=[40, 240, 120, 130])
            t_rank.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
            ]))
            story.append(t_rank)
            story.append(Spacer(1, 12))

            # Action Plan Table
            story.append(Paragraph("Three-Horizon Implementation Roadmap", h2_style))
            plan_data = [["Horizon", "Action Description", "Focus Dimension", "Lead Owner"]]
            for p in action_plan:
                plan_data.append([
                    p["horizon"].split(":")[0],
                    p["action"][:48] + "...",
                    p["focus_dimension"],
                    p["lead_owner"][:30] + "...",
                ])

            t_plan = Table(plan_data, colWidths=[90, 200, 110, 130])
            t_plan.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16A085")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), font_name_bold),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
            ]))
            story.append(t_plan)

            doc.build(story)
            logger.info("PDF Executive Report successfully built at: %s", out_path)
            return out_path

        except Exception as e:
            logger.warning("PDF generation failed: %s; proceeding without PDF.", e)
            return None

    def export_analysis_log(self, log_content: str, filename: str = "analysis_log.txt") -> str:
        """Saves execution runtime log to output directory."""
        out_path = os.path.join(self.output_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(log_content)
        return out_path

