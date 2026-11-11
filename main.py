"""
JSSAA (Jordan Social & Security Awareness Analysis)
Main Orchestration & Command-Line Interface.

Usage:
    python main.py [--input PATH] [--output DIR] [--no-pdf] [--sensitivity] [--sheet NAME/INDEX]

Autonomous pipeline executing ingestion, cleaning, psychometrics, inferential tests,
quality auditing, sensitivity analysis, visualization, and decision reporting.
"""

import os
import sys
import argparse
import logging
import io
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import config
from src.data_loader import DataLoader, print_data_quality_summary
from src.preprocessing import Preprocessor
from src.statistics import (
    compute_descriptive_stats,
    compute_all_reliabilities,
    compute_correlation_matrices,
    extract_top_correlations,
    analyze_media_exposure_relations,
    run_demographic_tests,
    run_pca_analysis,
    rank_dimensions_and_items,
    CAUSATION_WARNING,
)
from src.outliers import QualityAuditor
from src.decision_engine import DecisionEngine
from src.visualization import Visualizer
from src.reporting import ReportGenerator


def setup_logging() -> Tuple[logging.Logger, io.StringIO]:
    """Configure console logging and in-memory log capture buffer."""
    log_capture_buffer = io.StringIO()

    logger = logging.getLogger("JSSAA")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Stream Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # In-memory buffer handler for analysis_log.txt
    bh = logging.StreamHandler(log_capture_buffer)
    bh.setLevel(logging.INFO)
    bh.setFormatter(formatter)
    logger.addHandler(bh)

    return logger, log_capture_buffer


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="JSSAA: Jordan Social & Security Awareness Analysis Analytics Pipeline."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=config.INPUT_FILE,
        help=f"Path to input survey Excel or CSV file (default: {config.INPUT_FILE}).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=config.OUTPUT_DIR,
        help=f"Directory for generated reports, tables, and charts (default: {config.OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--sheet",
        default=config.SHEET_NAME,
        help=f"Sheet name or index for Excel files (default: {config.SHEET_NAME}).",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF executive report generation.",
    )
    parser.add_argument(
        "--sensitivity",
        action="store_true",
        default=config.RUN_SENSITIVITY,
        help="Execute sensitivity analysis re-estimating models without suspicious respondents.",
    )
    return parser.parse_args()


def run_pipeline(
    input_path: str,
    output_dir: str,
    sheet_name: Any,
    no_pdf: bool,
    sensitivity: bool,
) -> Dict[str, Any]:
    """
    Executes the complete end-to-end JSSAA analytics and decision pipeline.
    """
    logger, log_buffer = setup_logging()
    logger.info("==================================================================")
    logger.info("STARTING JSSAA PIPELINE: Jordan Social & Security Awareness Analysis")
    logger.info("==================================================================")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Input File Validation & Fallback Handling
    actual_input_path = input_path
    if not os.path.exists(actual_input_path):
        synthetic_path = "data/sample_survey_responses.xlsx"
        logger.warning(
            "[INPUT WARNING] Specified input file '%s' was not found.",
            actual_input_path
        )
        if os.path.exists(synthetic_path):
            logger.warning("Falling back to synthetic sample dataset at '%s'.", synthetic_path)
            actual_input_path = synthetic_path
        else:
            logger.info("Generating synthetic dataset dynamically at '%s'...", synthetic_path)
            from data.sample_generator import generate_synthetic_data
            generate_synthetic_data(output_path=synthetic_path)
            actual_input_path = synthetic_path

    # 2. Data Ingestion & Quality Cleaning
    loader = DataLoader(
        filepath=actual_input_path,
        sheet_name=sheet_name,
        max_missing_ratio=config.MAX_MISSING_RATIO,
        likert_min=config.LIKERT_MIN,
        likert_max=config.LIKERT_MAX,
    )
    cleaned_df, raw_likert_df, quality_summary = loader.process()
    print_data_quality_summary(quality_summary)

    # 3. Preprocessing & Psychometric Feature Engineering
    preprocessor = Preprocessor(
        include_exposure_in_score=config.INCLUDE_EXPOSURE_IN_SCORE,
        low_max=config.LOW_MAX,
        moderate_max=config.MODERATE_MAX,
    )
    processed_df = preprocessor.transform(cleaned_df)

    # 4. Descriptive Statistics
    logger.info("Calculating comprehensive item and dimension descriptive statistics...")
    likert_cols = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in processed_df.columns]
    dim_cols = [f"dim_{d}" for d in config.DIMENSIONS if f"dim_{d}" in processed_df.columns]
    eval_cols = likert_cols + dim_cols + ["overall_awareness_score"]
    if "actual_knowledge_score" in processed_df.columns:
        eval_cols.append("actual_knowledge_score")

    descriptive_stats_df = compute_descriptive_stats(processed_df, eval_cols)

    # 5. Psychometric Reliability (Cronbach's Alpha)
    logger.info("Evaluating scale and dimensional reliability coefficients...")
    reliability_results = compute_all_reliabilities(processed_df)

    # 6. Correlation Analysis (Spearman Primary + Pearson)
    logger.info("Computing Spearman and Pearson correlation matrices...")
    analysis_vars = [f"dim_{d}" for d in config.DIMENSIONS if f"dim_{d}" in processed_df.columns] + ["overall_awareness_score"]
    if "actual_knowledge_score" in processed_df.columns:
        analysis_vars.append("actual_knowledge_score")

    s_corr, s_pval, p_corr, p_pval = compute_correlation_matrices(processed_df, analysis_vars)
    top_correlations = extract_top_correlations(s_corr, s_pval, top_k=5)
    media_exposure_relations = analyze_media_exposure_relations(processed_df)

    # 7. Inferential Demographic Group Tests
    logger.info("Running inferential hypothesis tests across demographic cohorts...")
    group_tests_df = run_demographic_tests(
        processed_df,
        dependent_var="overall_awareness_score",
        min_group_size=config.MIN_GROUP_SIZE,
        alpha=config.ALPHA,
    )

    # 8. Principal Component Analysis (PCA)
    pca_data = {}
    if config.RUN_PCA:
        logger.info("Performing Principal Component Analysis (PCA)...")
        pca_data = run_pca_analysis(processed_df)

    # 9. Dimensional Rankings & Extremes
    ranking_results = rank_dimensions_and_items(processed_df)

    # 10. Anomaly Detection & Quality Auditing
    logger.info("Auditing data quality anomalies and response patterns...")
    auditor = QualityAuditor(
        z_threshold=config.Z_THRESHOLD,
        iqr_multiplier=config.IQR_MULTIPLIER,
        consistency_diff_threshold=config.CONSISTENCY_DIFF_THRESHOLD,
        min_completion_seconds=config.MIN_COMPLETION_SECONDS,
    )
    item_outliers_df, suspicious_df, audit_summary = auditor.audit(processed_df, raw_likert_df)

    # Sensitivity Analysis
    sensitivity_results = {}
    if sensitivity:
        logger.info("Running sensitivity analysis without suspicious respondents...")
        sensitivity_results = auditor.run_sensitivity_analysis(processed_df, suspicious_df)

    # 11. Decision & Policy Recommendation Engine
    logger.info("Synthesizing strategic findings and authoring executive decision report...")
    engine = DecisionEngine(
        target_score=config.TARGET_SCORE,
        low_band_escalation_pct=config.LOW_BAND_ESCALATION_PCT,
    )
    system_status = engine.determine_system_status(processed_df)
    prioritized_recs = engine.generate_prioritized_recommendations(processed_df)
    context_recs = engine.generate_context_recommendations(processed_df)
    demographic_recs = engine.generate_demographic_targeted_recommendations(processed_df, group_tests_df)
    action_plan = engine.construct_action_plan(prioritized_recs)

    txt_report, md_report = engine.compile_executive_report(
        system_status=system_status,
        quality_summary=quality_summary,
        reliability_results=reliability_results,
        ranking_results=ranking_results,
        group_tests_df=group_tests_df,
        audit_summary=audit_summary,
        sensitivity_results=sensitivity_results,
        prioritized_recs=prioritized_recs,
        context_recs=context_recs,
        demographic_recs=demographic_recs,
        action_plan=action_plan,
    )

    # 12. Visualization Generation
    logger.info("Generating publication-grade charts and multi-panel dashboard...")
    visualizer = Visualizer(output_dir=output_dir)
    dashboard_path = visualizer.generate_dashboard(
        processed_df, s_corr, s_pval, system_status, filename="jordan_awareness_dashboard.png"
    )
    radar_path = visualizer.generate_radar_chart(processed_df, filename="dimension_radar_chart.png")
    boxplots_path = visualizer.generate_demographic_boxplots(processed_df, filename="demographic_boxplots.png")
    scatter_path = visualizer.generate_perceived_vs_actual_scatter(processed_df, filename="perceived_vs_actual_scatter.png")
    pca_plot_path = ""
    if config.RUN_PCA and "eigenvalues" in pca_data:
        pca_plot_path = visualizer.generate_pca_scree_plot(pca_data, filename="pca_scree_plot.png")

    # 13. Artifact Export & Reporting
    logger.info("Exporting multi-tab Excel workbook and written decision reports...")
    reporter = ReportGenerator(output_dir=output_dir)
    excel_path = reporter.export_excel(
        cleaned_df=processed_df,
        descriptive_stats_df=descriptive_stats_df,
        reliability_dict=reliability_results,
        spearman_corr=s_corr,
        pearson_corr=p_corr,
        group_tests_df=group_tests_df,
        suspicious_df=suspicious_df,
        prioritized_recs=prioritized_recs,
        action_plan=action_plan,
        filename="JSSAA_results.xlsx",
    )
    txt_path, md_path = reporter.export_text_reports(
        txt_content=txt_report,
        md_content=md_report,
        txt_filename="executive_report.txt",
        md_filename="executive_report.md",
    )

    pdf_path = None
    if not no_pdf:
        pdf_path = reporter.export_pdf(
            system_status=system_status,
            quality_summary=quality_summary,
            reliability_dict=reliability_results,
            ranking_results=ranking_results,
            prioritized_recs=prioritized_recs,
            action_plan=action_plan,
            filename="executive_report.pdf",
        )

    # 14. Save Execution Log
    log_content = log_buffer.getvalue()
    log_file_path = reporter.export_analysis_log(log_content, filename="analysis_log.txt")

    logger.info("==================================================================")
    logger.info("JSSAA PIPELINE COMPLETED SUCCESSFULLY.")
    logger.info("All output artifacts generated in directory: '%s'", os.path.abspath(output_dir))
    logger.info("  1. Dashboard Image      : %s", dashboard_path)
    logger.info("  2. Radar Chart          : %s", radar_path)
    logger.info("  3. Demographic Boxplots : %s", boxplots_path)
    logger.info("  4. Perceived Scatter    : %s", scatter_path)
    if pca_plot_path:
        logger.info("  5. PCA Scree Plot       : %s", pca_plot_path)
    logger.info("  6. Results Excel        : %s", excel_path)
    logger.info("  7. Text Executive Report: %s", txt_path)
    logger.info("  8. Markdown Report      : %s", md_path)
    if pdf_path:
        logger.info("  9. PDF Executive Report : %s", pdf_path)
    logger.info(" 10. Execution Runtime Log: %s", log_file_path)
    logger.info("==================================================================")

    return {
        "status": "SUCCESS",
        "system_status": system_status,
        "dashboard_path": dashboard_path,
        "excel_path": excel_path,
        "txt_path": txt_path,
        "md_path": md_path,
        "pdf_path": pdf_path,
        "log_path": log_file_path,
    }


def main():
    args = parse_arguments()
    try:
        run_pipeline(
            input_path=args.input,
            output_dir=args.output,
            sheet_name=args.sheet,
            no_pdf=args.no_pdf,
            sensitivity=args.sensitivity,
        )
    except Exception as e:
        logging.error("Fatal error during pipeline execution: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

