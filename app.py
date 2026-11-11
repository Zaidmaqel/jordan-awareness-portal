"""
JSSAA (Jordan Social & Security Awareness Analysis)
Streamlit Graphical User Interface.

Provides an interactive, bilingual (Arabic / English) analytics dashboard for
community awareness, misinformation resilience, and digital threat hygiene.
"""

import os
import sys
import io
import tempfile
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import config
from main import run_pipeline
from src.visualization import ar

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="JSSAA - Jordan Social & Security Awareness Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# Localization Dictionary (Bilingual Support)
# ==========================================
STRINGS = {
    "en": {
        "title": "Jordan Social & Security Awareness Analysis (JSSAA)",
        "subtitle": "Community Awareness & Digital Threat Hygiene Analytics Platform",
        "lang_switch": "Language / اللغة",
        "data_source": "Data Ingestion Source",
        "upload_file": "Upload Survey Responses (.xlsx or .csv)",
        "use_sample": "Use synthetic sample dataset (~245 records)",
        "settings_header": "Analytical Parameters & Thresholds",
        "z_thresh": "Item Outlier Z-Threshold",
        "iqr_mult": "IQR Multiplier (Overall Outliers)",
        "low_band": "Low Awareness Limit (Critical Threshold)",
        "mod_band": "Moderate Awareness Limit",
        "target_score": "National Target Score",
        "include_exp": "Include Media Exposure in Awareness Score",
        "run_sens": "Run Sensitivity Analysis (Audit Flagged Responses)",
        "run_pca": "Compute Principal Component Analysis (PCA)",
        "run_btn": "Run Analytics Pipeline",
        "template_btn": "Download Google Forms Survey Template (Markdown)",
        "welcome_title": "Welcome to the JSSAA Analytics Platform",
        "welcome_desc": (
            "This national intelligence platform evaluates community resilience against online rumors, "
            "misinformation, phishing, banking fraud (CliQ/OTP), and digital hazards across Jordan."
        ),
        "step1": "1. Upload Google Forms Responses",
        "step1_desc": "Export your survey responses from Google Sheets to Excel (.xlsx) and upload in the sidebar.",
        "step2": "2. Configure Diagnostic Thresholds",
        "step2_desc": "Fine-tune psychometric Z-scores, risk boundaries, and dimensional settings.",
        "step3": "3. Evaluate & Export Decisions",
        "step3_desc": "Inspect interactive charts, psychometric reliability, prioritized actions, and multi-tab Excel/PDF reports.",
        "kpi_sample": "Valid Sample Size (n)",
        "kpi_mean": "Community Awareness Score",
        "kpi_alpha": "Scale Reliability (Cronbach's α)",
        "kpi_low": "Population in Low-Risk Band",
        "tab_overview": "Overview & Radar",
        "tab_quality": "Data Quality Audit",
        "tab_stats": "Descriptive & Psychometrics",
        "tab_corr": "Correlations & Media",
        "tab_groups": "Demographic Disparities",
        "tab_anomalies": "Anomaly & Sensitivity",
        "tab_recs": "Strategic Recommendations",
        "tab_report": "Executive Report",
        "tab_downloads": "Export Center",
        "footer_ethics": "JSSAA Framework: Strictly anonymous data collection, voluntary participation, and aggregate policy reporting only.",
    },
    "ar": {
        "title": "نظام تحليل الوعي الأمني والمجتمعي في الأردن (JSSAA)",
        "subtitle": "منصة قياس الوعي المجتمعي حيال الشائعات والتهديدات الرقمية والأمان السيبراني",
        "lang_switch": "اللغة / Language",
        "data_source": "مصدر البيانات",
        "upload_file": "رفع ملف الاستبانة (.xlsx أو .csv)",
        "use_sample": "استخدام العينة التجريبية النموذجية (~245 مستجيب)",
        "settings_header": "المعايير الإحصائية والعتبات",
        "z_thresh": "عتبة الدرجة المعيارية (Z-Score)",
        "iqr_mult": "معامل المدى الربيعي (IQR)",
        "low_band": "حد الوعي المنخفض (العتبة الحرجة)",
        "mod_band": "حد الوعي المتوسط",
        "target_score": "الهدف الوطني المستهدف",
        "include_exp": "تضمين التعرض الإعلامي في درجة الوعي الكلي",
        "run_sens": "إجراء تحليل الحساسية واستبعاد الاستجابات المريبة",
        "run_pca": "إجراء تحليل المركبات الرئيسية (PCA)",
        "run_btn": "تشغيل التحليل الإحصائي",
        "template_btn": "تحميل نموذج استبانة Google Forms (ملف Markdown)",
        "welcome_title": "مرحباً بكم في منصة JSSAA الوطنية للتحليل السيكومتري والأمني",
        "welcome_desc": (
            "منصة وطنية متقدمة لقياس وتحليل مستوى الوعي المجتمعي الأردني بالتعامل مع الشائعات، "
            "والأخبار المضللة، وعمليات الاحتيال الإلكتروني ونظام كليك (CliQ)، وسلوك التحقق والوقاية الرقمية."
        ),
        "step1": "1. رفع ردود استبانة Google Forms",
        "step1_desc": "قم بتصدير الردود من Google Sheets إلى ملف Excel (.xlsx) وارفعه عبر القائمة الجانبية.",
        "step2": "2. ضبط معايير القياس والتصنيف",
        "step2_desc": "تعديل عتبات الشذوذ الإحصائي، وحدود تصنيف نطاقات الوعي، وأوزان الأبعاد.",
        "step3": "3. مراجعة المؤشرات وتصدير القرارات",
        "step3_desc": "استعراض لوحات المؤشرات التفاعلية، ومعاملات الثبات، وخارطة الطريق التنفيذية وتنزيل التقارير المعتمدة.",
        "kpi_sample": "حجم العينة المعتمدة (n)",
        "kpi_mean": "متوسط درجة الوعي المجتمعي",
        "kpi_alpha": "معامل ثبات المقياس (ألفا)",
        "kpi_low": "نسبة فئة الوعي المنخفض (حرج)",
        "tab_overview": "لوحة المؤشرات العامة",
        "tab_quality": "تدقيق جودة البيانات",
        "tab_stats": "الإحصاء والقياس السيكومتري",
        "tab_corr": "الارتباطات والتعرض الإعلامي",
        "tab_groups": "الفروق الديموغرافية",
        "tab_anomalies": "كشف الشذوذ والحساسية",
        "tab_recs": "التوصيات وخطة العمل",
        "tab_report": "التقرير التنفيذي",
        "tab_downloads": "مركز التحميل والتصدير",
        "footer_ethics": "إطار عمل JSSAA: جمع بيانات مجهول الهوية بالكامل، مشاركة طوعية، وتقارير سياسات تجميعية فقط.",
    },
}

# ==========================================
# Sidebar Controls & Settings
# ==========================================
with st.sidebar:
    st.markdown("## 🛡️ JSSAA Platform")
    lang_choice = st.radio(
        "Language / اللغة",
        options=["English", "العربية"],
        index=0,
        horizontal=True,
    )
    lang = "ar" if lang_choice == "العربية" else "en"
    L = STRINGS[lang]

    # Inject RTL CSS if Arabic selected
    if lang == "ar":
        st.markdown(
            """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
            html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, p {
                font-family: 'Cairo', sans-serif !important;
                direction: rtl;
                text-align: right;
            }
            .stMetric {
                direction: rtl;
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader(L["data_source"])

    use_sample = st.checkbox(L["use_sample"], value=True)
    uploaded_file = st.file_uploader(
        L["upload_file"],
        type=["xlsx", "xls", "csv"],
        disabled=use_sample,
    )

    with st.expander(f"⚙️ {L['settings_header']}", expanded=False):
        z_threshold = st.slider(L["z_thresh"], min_value=1.5, max_value=3.5, value=2.5, step=0.1)
        iqr_multiplier = st.slider(L["iqr_mult"], min_value=1.0, max_value=2.5, value=1.5, step=0.1)
        low_max = st.slider(L["low_band"], min_value=1.5, max_value=2.8, value=2.33, step=0.01)
        moderate_max = st.slider(L["mod_band"], min_value=2.9, max_value=4.2, value=3.66, step=0.01)
        target_score = st.slider(L["target_score"], min_value=3.5, max_value=5.0, value=4.0, step=0.1)
        include_exposure = st.checkbox(L["include_exp"], value=False)
        run_sens = st.checkbox(L["run_sens"], value=True)
        run_pca_flag = st.checkbox(L["run_pca"], value=True)

    run_clicked = st.button(f"🚀 {L['run_btn']}", type="primary", use_container_width=True)

    # Download Survey Template Button
    template_path = os.path.join(os.path.dirname(__file__), "SURVEY_TEMPLATE.md")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as tf:
            template_content = tf.read()
        st.download_button(
            label=f"📄 {L['template_btn']}",
            data=template_content,
            file_name="JSSAA_SURVEY_TEMPLATE.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ==========================================
# Execution Engine (Session State Cached)
# ==========================================
@st.cache_data(show_spinner=False)
def execute_pipeline_cached(
    file_bytes: Optional[bytes],
    filename: Optional[str],
    is_sample: bool,
    z_th: float,
    iqr_m: float,
    l_max: float,
    m_max: float,
    t_score: float,
    inc_exp: bool,
    r_sens: bool,
    r_pca: bool,
) -> Dict[str, Any]:
    """Execute analysis pipeline with runtime settings."""
    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if is_sample or file_bytes is None:
        target_input = os.path.join(os.path.dirname(__file__), "data", "sample_survey_responses.xlsx")
        if not os.path.exists(target_input):
            from data.sample_generator import generate_synthetic_data
            generate_synthetic_data(output_path=target_input)
    else:
        # Save uploaded bytes to a temp file
        ext = os.path.splitext(filename)[-1].lower() if filename else ".xlsx"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_file.write(file_bytes)
        temp_file.close()
        target_input = temp_file.name

    return run_pipeline(
        input_path=target_input,
        output_dir=out_dir,
        run_sensitivity=r_sens,
        run_pca=r_pca,
        make_pdf=True,
        z_threshold=z_th,
        iqr_multiplier=iqr_m,
        low_max=l_max,
        moderate_max=m_max,
        target_score=t_score,
        include_exposure_in_score=inc_exp,
    )


# Trigger execution if button pressed or if not already executed
if run_clicked:
    with st.spinner("Executing rigorous psychometric & inferential analytics pipeline..."):
        progress_bar = st.progress(15)
        f_bytes = uploaded_file.getvalue() if (uploaded_file and not use_sample) else None
        f_name = uploaded_file.name if (uploaded_file and not use_sample) else None

        try:
            progress_bar.progress(40)
            res = execute_pipeline_cached(
                file_bytes=f_bytes,
                filename=f_name,
                is_sample=use_sample,
                z_th=z_threshold,
                iqr_m=iqr_multiplier,
                l_max=low_max,
                m_max=moderate_max,
                t_score=target_score,
                inc_exp=include_exposure,
                r_sens=run_sens,
                r_pca=run_pca_flag,
            )
            progress_bar.progress(90)
            st.session_state["pipeline_results"] = res
            progress_bar.progress(100)
            progress_bar.empty()
            st.success("Analysis executed successfully!" if lang == "en" else "تم اكتمال التحليل بنجاح!")
        except Exception as e:
            st.error(f"Error during analysis: {e}")
            logger_err = str(e)
            if "required survey columns could not be mapped" in logger_err:
                st.error("Missing headers detected in the uploaded spreadsheet. Please ensure questions match SURVEY_TEMPLATE.md.")


# ==========================================
# Main Interface Area
# ==========================================
st.markdown(f"# {L['title']}")
st.markdown(f"*{L['subtitle']}*")
st.markdown("---")

results = st.session_state.get("pipeline_results", None)

if results is None:
    # Friendly Welcome Screen
    st.info(f"### ℹ️ {L['welcome_title']}\n{L['welcome_desc']}")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"#### 📂 {L['step1']}")
        st.write(L["step1_desc"])
    with c2:
        st.markdown(f"#### ⚙️ {L['step2']}")
        st.write(L["step2_desc"])
    with c3:
        st.markdown(f"#### 📊 {L['step3']}")
        st.write(L["step3_desc"])

    st.markdown(
        """
        > **Quick Start:** Keep *"Use synthetic sample data"* checked in the sidebar and click **"Run Analytics Pipeline"** to evaluate the complete demonstration dataset.
        """
    )

else:
    # -------------------------------------------------------------
    # Top KPI Metrics Cards
    # -------------------------------------------------------------
    b_stat = results["decision"]["baseline"]
    full_scale_alpha = results["reliability"].get("full_scale", {}).get("alpha", 0.0)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label=L["kpi_sample"], value=f"{results['quality_summary']['final_count']}")
    with m2:
        st.metric(
            label=L["kpi_mean"],
            value=f"{b_stat['mean_score']} / 5.0",
            delta=f"95% CI: [{b_stat['ci_95'][0]}, {b_stat['ci_95'][1]}]",
            delta_color="off",
        )
    with m3:
        st.metric(
            label=L["kpi_alpha"],
            value=f"{full_scale_alpha:.3f}",
            delta=results["reliability"].get("full_scale", {}).get("interpretation", "Good"),
            delta_color="normal",
        )
    with m4:
        st.metric(
            label=L["kpi_low"],
            value=f"{b_stat['pct_low']}%",
            delta=f"Threshold: {config.LOW_BAND_ESCALATION_PCT}%",
            delta_color="inverse",
        )

    # -------------------------------------------------------------
    # Strategic Status Banner
    # -------------------------------------------------------------
    severity = b_stat["final_severity"]
    if severity == "Critical":
        banner_bg = "#F8D7DA"
        banner_color = "#721C24"
        icon = "🚨"
    elif severity == "Elevated":
        banner_bg = "#FFF3CD"
        banner_color = "#856404"
        icon = "⚠️"
    else:
        banner_bg = "#D4EDDA"
        banner_color = "#155724"
        icon = "✅"

    escalate_txt = f" | {b_stat['escalation_reason']}" if b_stat["escalated"] else ""
    st.markdown(
        f"""
        <div style="background-color: {banner_bg}; color: {banner_color}; padding: 16px 20px; border-radius: 8px; margin: 15px 0 25px 0; border-left: 6px solid {banner_color};">
            <h3 style="margin: 0; padding-bottom: 5px; color: {banner_color};">{icon} {b_stat['final_status']} (Severity: {b_stat['final_severity']})</h3>
            <p style="margin: 0; font-size: 15px;">Mean Community Awareness Score is <b>{b_stat['mean_score']} / 5.000</b>. {b_stat['pct_low']}% in Low Band, {b_stat['pct_moderate']}% in Moderate Band, {b_stat['pct_high']}% in High Band.{escalate_txt}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------
    # 9 Tab Layout
    # -------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        f"📊 {L['tab_overview']}",
        f"🧹 {L['tab_quality']}",
        f"📈 {L['tab_stats']}",
        f"🔗 {L['tab_corr']}",
        f"👥 {L['tab_groups']}",
        f"🔍 {L['tab_anomalies']}",
        f"💡 {L['tab_recs']}",
        f"📝 {L['tab_report']}",
        f"📥 {L['tab_downloads']}",
    ])

    # -------------------------------------------------------------
    # TAB 1: Overview & Radar
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Publication-Grade Awareness Dashboard (300 DPI, 2x2)")
        dash_path = results["files"]["dashboard"]
        if os.path.exists(dash_path):
            st.image(dash_path, use_container_width=True)

        st.markdown("---")
        st.subheader("Five-Dimensional Radar Profile")
        col_rad, col_leg = st.columns([2, 1])
        with col_rad:
            radar_path = results["files"]["radar"]
            if os.path.exists(radar_path):
                st.image(radar_path, use_container_width=True)
        with col_leg:
            st.markdown("#### Dimensional Mean Scores")
            dim_order = results["cleaned_df"][[f"dim_{d}" for d in config.DIMENSIONS]].mean()
            for d in config.DIMENSIONS:
                st.write(f"- **{d}:** {dim_order[f'dim_{d}']:.2f} / 5.0")
            st.info("The purple line indicates the target benchmark (4.0/5.0). Dimensions with depressed polygon vertices represent acute vulnerabilities.")

    # -------------------------------------------------------------
    # TAB 2: Data Quality Audit
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Automated Ingestion & Cleaning Audit")
        q_sum = results["quality_summary"]
        q1, q2, q3, q4, q5 = st.columns(5)
        q1.metric("Raw Loaded", q_sum["raw_count"])
        q2.metric("Duplicates Removed", q_sum["duplicate_count"])
        q3.metric("Out-of-Range Coerced", q_sum["out_of_range_count"])
        q4.metric("Dropped (>20% Missing)", q_sum["dropped_missing_count"])
        q5.metric("Median Imputed Cells", q_sum.get("imputed_cells_count", 0))

        st.markdown("#### Item Missingness Rate Before Imputation")
        miss_df = pd.DataFrame(
            list(q_sum["item_missing_pct_before_imputation"].items()),
            columns=["Survey Item", "Missing %"],
        ).sort_values(by="Missing %", ascending=False)
        st.dataframe(miss_df.style.format({"Missing %": "{:.2f}%"}), use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: Descriptive & Psychometrics
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Scale Descriptive Statistics")
        desc_df = results["descriptive"]
        st.dataframe(desc_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Psychometric Internal Consistency (Cronbach's α)")
        rel_records = []
        for s_name, r_info in results["reliability"].items():
            rel_records.append({
                "Scale / Dimension": s_name,
                "Number of Items": r_info.get("k_items", 0),
                "Cronbach Alpha (α)": r_info.get("alpha", np.nan),
                "Benchmark Interpretation": r_info.get("interpretation", "N/A"),
            })
        rel_df = pd.DataFrame(rel_records)
        st.dataframe(rel_df, use_container_width=True)

        if os.path.exists(results["files"]["pca_scree"]):
            st.markdown("---")
            st.subheader("Principal Component Analysis (PCA) Scree Plot")
            st.image(results["files"]["pca_scree"], use_container_width=True)

    # -------------------------------------------------------------
    # TAB 4: Correlations & Media
    # -------------------------------------------------------------
    with tab4:
        st.subheader("Interactive Spearman Correlation Matrix")
        s_pack = results["corr_spearman"]
        corr_matrix = s_pack["matrix"]

        clean_labels = [
            c.replace("dim_", "").replace("_", " ").title() if c != "overall_awareness_score" else "Overall Awareness"
            for c in corr_matrix.columns
        ]

        # Interactive Plotly Heatmap
        fig_heat = px.imshow(
            corr_matrix,
            labels=dict(x="Dimension", y="Dimension", color="Spearman ρ"),
            x=clean_labels,
            y=clean_labels,
            color_continuous_scale="RdBu_r",
            zmin=-0.5,
            zmax=1.0,
            text_auto=".2f",
            title="Interactive Dimension Correlation Heatmap",
        )
        fig_heat.update_layout(height=550)
        st.plotly_chart(fig_heat, use_container_width=True)

        c_top, c_med = st.columns(2)
        with c_top:
            st.markdown("#### Top Strongest Correlation Pairs")
            top_p_df = pd.DataFrame(s_pack["top_pairs"])[["var1", "var2", "r", "sig"]]
            st.dataframe(top_p_df, use_container_width=True)
        with c_med:
            st.markdown("#### Media Exposure Interrelationships")
            med_df = pd.DataFrame(s_pack["media_exposure_relations"])[["target_variable", "spearman_rho", "sig"]]
            st.dataframe(med_df, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 5: Demographic Disparities
    # -------------------------------------------------------------
    with tab5:
        st.subheader("Inferential Demographic Disparity Analysis")
        group_df = results["group_tests"]

        # Demographic filter
        demo_cols = list(config.DEMOGRAPHIC_COLUMNS.values())
        selected_demo = st.selectbox("Select Demographic Variable for Breakdown:", options=demo_cols, index=1)

        # Interactive breakdown chart
        clean_d = results["cleaned_df"]
        if selected_demo in clean_d.columns:
            group_summary = clean_d.groupby(selected_demo, observed=True)["overall_awareness_score"].agg(["mean", "std", "count"]).reset_index()
            group_summary["ci"] = 1.96 * (group_summary["std"] / np.sqrt(group_summary["count"]))

            fig_bar = px.bar(
                group_summary,
                x=selected_demo,
                y="mean",
                error_y="ci",
                color="mean",
                color_continuous_scale="Blues",
                labels={"mean": "Mean Awareness Score (1-5)", selected_demo: selected_demo.replace("_", " ").title()},
                title=f"Mean Overall Awareness Score by {selected_demo.replace('_', ' ').title()} (with 95% CIs)",
            )
            fig_bar.add_hline(y=config.TARGET_SCORE, line_dash="dash", line_color="purple", annotation_text="Target (4.0)")
            fig_bar.add_hline(y=config.LOW_MAX, line_dash="dot", line_color="crimson", annotation_text="Low Limit (2.33)")
            fig_bar.update_layout(height=420)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### Inferential Hypothesis Test Table")
        # Highlight significant rows
        st.dataframe(
            group_df.style.apply(
                lambda row: ["background-color: #D4EDDA" if row["is_significant"] else "" for _ in row],
                axis=1,
            ),
            use_container_width=True,
        )

        if os.path.exists(results["files"]["boxplots"]):
            st.markdown("---")
            st.subheader("Demographic Score Boxplots")
            st.image(results["files"]["boxplots"], use_container_width=True)

    # -------------------------------------------------------------
    # TAB 6: Anomaly & Sensitivity
    # -------------------------------------------------------------
    with tab6:
        st.subheader("Data Integrity & Anomaly Screening")
        susp_df = results["outliers_table"]
        st.write(f"Flagged Suspicious Respondents: **{len(susp_df)}** ({len(susp_df)/len(results['cleaned_df'])*100:.1f}% of cohort)")

        if not susp_df.empty:
            st.dataframe(susp_df, use_container_width=True)
        else:
            st.success("No suspicious straight-lining or contradictory response patterns detected.")

        st.markdown("---")
        st.subheader("Sensitivity Analysis (Full Sample vs Clean Subset)")
        sens = results["sensitivity"]
        if sens:
            s_comp = pd.DataFrame([
                {"Metric": "Sample Size (n)", "Full Sample": sens["n_full"], "Clean Subset": sens["n_clean"], "Delta": -sens["n_removed"]},
                {"Metric": "Mean Awareness Score", "Full Sample": sens["mean_full"], "Clean Subset": sens["mean_clean"], "Delta": sens["mean_delta"]},
                {"Metric": "Cronbach's Alpha (α)", "Full Sample": sens["alpha_full"], "Clean Subset": sens["alpha_clean"], "Delta": sens["alpha_delta"]},
                {"Metric": "Awareness Status", "Full Sample": sens["baseline_status"], "Clean Subset": sens["clean_status"], "Delta": "Unchanged" if not sens["status_changed"] else "CHANGED"},
            ])
            st.table(s_comp)
            if sens["conclusion_stable"]:
                st.success("✅ **Robust Stability Confirmed:** Strategic status and dimensional rank ordering remain identical after excluding outliers.")
            else:
                st.warning("⚠️ **Sensitivity Alert:** Diagnostic outcomes are sensitive to aberrant responses.")

    # -------------------------------------------------------------
    # TAB 7: Strategic Recommendations
    # -------------------------------------------------------------
    with tab7:
        st.subheader("Prioritized National Interventions")
        st.caption("Ordered by Quantitative Priority Score = (Target [4.0] - Dimension Mean) x (1 + % in Low Band / 100)")

        for rec in results["decision"]["recommendations"]:
            with st.expander(f"📌 Priority: {rec['title']} (Score: {rec['priority_score']:.2f})"):
                col_r1, col_r2 = st.columns([3, 1])
                with col_r1:
                    st.markdown(f"**Lead Responsible Agencies:** `{rec['stakeholders']}`")
                    st.markdown("**Strategic Actions:**")
                    for act in rec["interventions"]:
                        st.write(f"- {act}")
                with col_r2:
                    st.metric("Dimension Mean", f"{rec['dimension_mean']:.2f}")
                    st.metric("In Low Band", f"{rec['pct_low_band']}%")

        st.markdown("---")
        st.subheader("Three-Horizon Implementation Roadmap")
        plan = results["decision"]["action_plan"]
        h1_items = [p for p in plan if "Horizon 1" in p["horizon"]]
        h2_items = [p for p in plan if "Horizon 2" in p["horizon"]]
        h3_items = [p for p in plan if "Horizon 3" in p["horizon"]]

        c_h1, c_h2, c_h3 = st.columns(3)
        with c_h1:
            st.markdown("### Horizon 1: Immediate\n*(0–3 Months)*")
            for item in h1_items:
                st.info(f"**{item['action']}**\n\n- Owner: {item['lead_owner']}\n- KPI: {item['kpi']}")
        with c_h2:
            st.markdown("### Horizon 2: Short-Term\n*(3–12 Months)*")
            for item in h2_items:
                st.warning(f"**{item['action']}**\n\n- Owner: {item['lead_owner']}\n- KPI: {item['kpi']}")
        with c_h3:
            st.markdown("### Horizon 3: Long-Term\n*(1–3 Years)*")
            for item in h3_items:
                st.success(f"**{item['action']}**\n\n- Owner: {item['lead_owner']}\n- KPI: {item['kpi']}")

    # -------------------------------------------------------------
    # TAB 8: Executive Report
    # -------------------------------------------------------------
    with tab8:
        st.subheader("Complete Executive Decision Report")
        st.markdown(results["report_md"])

    # -------------------------------------------------------------
    # TAB 9: Export Center
    # -------------------------------------------------------------
    with tab9:
        st.subheader("Artifact & Report Download Center")
        st.write("Download publication figures, multi-tab Excel workbooks, and executive decision briefs.")

        d1, d2 = st.columns(2)

        with d1:
            st.markdown("#### Analytical Reports & Workbooks")
            # Excel
            excel_path = results["files"]["excel"]
            if os.path.exists(excel_path):
                with open(excel_path, "rb") as ef:
                    st.download_button(
                        label="📊 Download Master Excel Workbook (.xlsx)",
                        data=ef.read(),
                        file_name="JSSAA_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

            # PDF
            pdf_path = results["files"]["report_pdf"]
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pf:
                    st.download_button(
                        label="📄 Download Executive Report PDF (.pdf)",
                        data=pf.read(),
                        file_name="JSSAA_executive_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            # Markdown Report
            st.download_button(
                label="📝 Download Executive Report (.md)",
                data=results["report_md"],
                file_name="JSSAA_executive_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

            # Plain Text Report
            st.download_button(
                label="📄 Download Executive Report (.txt)",
                data=results["report_text"],
                file_name="JSSAA_executive_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

            # Analysis Log
            log_path = results["files"]["log"]
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as lf:
                    st.download_button(
                        label="📋 Download Execution Runtime Log (.txt)",
                        data=lf.read(),
                        file_name="JSSAA_analysis_log.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

        with d2:
            st.markdown("#### High-Resolution Figures & Plots (300 DPI)")
            # Dashboard PNG
            if os.path.exists(results["files"]["dashboard"]):
                with open(results["files"]["dashboard"], "rb") as img_f:
                    st.download_button(
                        label="🖼️ Download 2x2 Dashboard Image (.png)",
                        data=img_f.read(),
                        file_name="jordan_awareness_dashboard.png",
                        mime="image/png",
                        use_container_width=True,
                    )

            # Radar Chart PNG
            if os.path.exists(results["files"]["radar"]):
                with open(results["files"]["radar"], "rb") as img_f:
                    st.download_button(
                        label="🎯 Download Radar Profile (.png)",
                        data=img_f.read(),
                        file_name="dimension_radar_chart.png",
                        mime="image/png",
                        use_container_width=True,
                    )

            # Boxplots PNG
            if os.path.exists(results["files"]["boxplots"]):
                with open(results["files"]["boxplots"], "rb") as img_f:
                    st.download_button(
                        label="📦 Download Demographic Boxplots (.png)",
                        data=img_f.read(),
                        file_name="demographic_boxplots.png",
                        mime="image/png",
                        use_container_width=True,
                    )

            # Perceived vs Actual Scatter PNG
            if os.path.exists(results["files"]["scatter"]):
                with open(results["files"]["scatter"], "rb") as img_f:
                    st.download_button(
                        label="📈 Download Perceived vs Actual Scatter (.png)",
                        data=img_f.read(),
                        file_name="perceived_vs_actual_scatter.png",
                        mime="image/png",
                        use_container_width=True,
                    )

            # PCA Scree PNG
            if results["files"]["pca_scree"] and os.path.exists(results["files"]["pca_scree"]):
                with open(results["files"]["pca_scree"], "rb") as img_f:
                    st.download_button(
                        label="📉 Download PCA Scree Plot (.png)",
                        data=img_f.read(),
                        file_name="pca_scree_plot.png",
                        mime="image/png",
                        use_container_width=True,
                    )

# ==========================================
# Footer & Research Governance
# ==========================================
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: gray; font-size: 13px;'>{L['footer_ethics']}</div>",
    unsafe_allow_html=True,
)

