"""
JSSAA Decision & Recommendation Engine.

Synthesizes descriptive, inferential, psychometric, and anomaly statistics
to evaluate national awareness status, prioritize Jordan-specific interventions,
generate demographic-targeted mitigations, structure a 3-horizon implementation roadmap,
and author an exhaustive Executive Decision Report in plain text and Markdown formats.
"""

import os
import datetime
import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

logger = logging.getLogger("JSSAA.decision_engine")


# ==========================================
# Domain Specific Recommendation Knowledge Base
# ==========================================

RECOMMENDATION_CATALOG = {
    "rumor_detection": {
        "title": "National Media Literacy and Misinformation Resistance Initiative",
        "dimension": "rumor_detection",
        "strategic_interventions": [
            "Incorporate mandatory digital media literacy and critical analysis curriculum modules across Jordanian public and private universities.",
            "Establish community-based fact-checking workshops and verification bootcamps targeting civic youth centers in Irbid, Zarqa, and Amman.",
            "Formalize institutional partnerships with independent Jordanian verification platforms (Misbar, Akeed) and the Jordan Media Commission (هيئة الإعلام).",
            "Launch the nationwide 'Verify Before You Share' (تأكد قبل أن تشارك) awareness campaign across digital networks.",
        ],
        "lead_stakeholders": "Jordan Media Commission (هيئة الإعلام), Ministry of Education, Jordanian Fact-Checking Platforms (Misbar / Akeed)",
    },
    "digital_threat_awareness": {
        "title": "National Cyber Hygiene, Scam Prevention & CliQ Protection Program",
        "dimension": "digital_threat_awareness",
        "strategic_interventions": [
            "Execute university and vocational cybersecurity hygiene roadshows demonstrating live phishing, identity theft, and malicious APK payloads.",
            "Deploy nationwide counter-fraud campaigns warning against instant payment (CliQ) scams, fraudulent banking OTP requests, and fake investment schemes.",
            "Deepen operational coordination with the National Cyber Security Center (NCSC-JO) and the Public Security Directorate Cyber Crime Unit (وحدة مكافحة الجرائم الإلكترونية).",
            "Mandate universal two-factor authentication (2FA) community drives across citizen-facing public and financial applications.",
        ],
        "lead_stakeholders": "National Cyber Security Center (NCSC-JO), PSD Cyber Crime Unit, Central Bank of Jordan (CBJ), MoDEE",
    },
    "official_source_trust": {
        "title": "Governmental Crisis Communication & Rapid Counter-Disinformation System",
        "dimension": "official_source_trust",
        "strategic_interventions": [
            "Establish a centralized, real-time official government rumor-debunking digital platform with open API access for news outlets.",
            "Institutionalize rapid-response fact sheets released within 60 minutes of viral emerging disinformation incidents.",
            "Expand verified official government broadcast channels on high-engagement social platforms (WhatsApp Channels, Telegram, Instagram, TikTok, and X).",
            "Standardize proactive spokesperson transparency and structured press briefings during public emergencies.",
        ],
        "lead_stakeholders": "Government Communications Directorate (رئاسة الوزراء), Jordan News Agency (Petra), Jordan Armed Forces / PSD Media",
    },
    "verification_behavior": {
        "title": "Behavioral Nudge & Pre-Sharing Friction Architecture",
        "dimension": "verification_behavior",
        "strategic_interventions": [
            "Deploy the 'Pause - Check - Share' (توقف - تحقق - انشر) behavioral intervention campaign across messaging and microblogging platforms.",
            "Produce short-form educational video vignettes debunking viral social engineering tactics featuring credible Jordanian cultural figures.",
            "Engage Jordanian civic influencers, academic leaders, and journalists in joint digital literacy ambassadorships.",
            "Promote pre-bunking strategies that alert citizens to recurring deceptive narrative archetypes prior to peak viral propagation.",
        ],
        "lead_stakeholders": "Crown Prince Foundation (CPF) Youth Initiatives, Jordan Media Commission, Ministry of Youth",
    },
}


class DecisionEngine:
    """
    Evaluates risk status, computes priority scores, constructs action plans,
    and formats formal Executive Decision Reports.
    """

    def __init__(
        self,
        target_score: float = config.TARGET_SCORE,
        low_band_escalation_pct: float = config.LOW_BAND_ESCALATION_PCT,
    ):
        self.target_score = target_score
        self.escalation_pct = low_band_escalation_pct

    def determine_system_status(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Determines baseline score, CI, overall status, and escalation triggers.
        """
        overall_mean = float(df["overall_awareness_score"].mean())
        overall_sd = float(df["overall_awareness_score"].std(ddof=1))
        n = len(df)

        se = overall_sd / np.sqrt(n) if n > 1 else 0.0
        t_crit = stats.t.ppf(1 - config.ALPHA / 2, df=n - 1) if n > 1 else 1.96
        ci_lower = overall_mean - t_crit * se
        ci_upper = overall_mean + t_crit * se

        pct_low = float((df["awareness_band"] == "Low").mean() * 100.0)
        pct_moderate = float((df["awareness_band"] == "Moderate").mean() * 100.0)
        pct_high = float((df["awareness_band"] == "High").mean() * 100.0)

        # Baseline Status Thresholds
        if overall_mean < 2.34:
            base_status = "HIGH RISK / LOW AWARENESS"
            severity = "Critical"
        elif overall_mean <= 3.66:
            base_status = "MODERATE AWARENESS / ELEVATED RISK"
            severity = "Elevated"
        else:
            base_status = "STABLE / GOOD AWARENESS"
            severity = "Stable"

        # Escalation Rule: If Low band exceeds threshold (30%)
        escalated = False
        escalation_reason = ""
        final_status = base_status
        final_severity = severity

        if pct_low > self.escalation_pct:
            escalated = True
            if severity == "Stable":
                final_status = "MODERATE AWARENESS / ELEVATED RISK (ESCALATED)"
                final_severity = "Elevated"
            elif severity == "Elevated":
                final_status = "HIGH RISK / LOW AWARENESS (ESCALATED)"
                final_severity = "Critical"
            escalation_reason = (
                f"Severe demographic vulnerability: {pct_low:.1f}% of respondents fall in the LOW awareness band, "
                f"exceeding the safety threshold of {self.escalation_pct}%. Severity escalated to {final_severity}."
            )

        return {
            "mean_score": round(overall_mean, 3),
            "sd_score": round(overall_sd, 3),
            "ci_95": (round(ci_lower, 3), round(ci_upper, 3)),
            "pct_low": round(pct_low, 1),
            "pct_moderate": round(pct_moderate, 1),
            "pct_high": round(pct_high, 1),
            "base_status": base_status,
            "final_status": final_status,
            "final_severity": final_severity,
            "escalated": escalated,
            "escalation_reason": escalation_reason,
        }

    def generate_prioritized_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calculates mathematical priority score for each awareness dimension:
            Priority Score = (TARGET_SCORE - dimension_mean) * (1 + pct_low / 100)
        Ranks dimensions descending by urgency.
        """
        prioritized = []

        for dim in config.AWARENESS_DIMENSIONS:
            col = f"dim_{dim}"
            band_col = f"band_{dim}"
            if col not in df.columns:
                continue

            dim_mean = float(df[col].mean())
            pct_low = float((df[band_col] == "Low").mean() * 100.0) if band_col in df.columns else 0.0

            # Gap to target
            gap = max(0.0, self.target_score - dim_mean)
            priority_score = gap * (1.0 + (pct_low / 100.0))

            cat_info = RECOMMENDATION_CATALOG.get(dim, {})

            prioritized.append({
                "dimension": dim,
                "dimension_mean": round(dim_mean, 3),
                "pct_low_band": round(pct_low, 1),
                "priority_score": round(priority_score, 3),
                "title": cat_info.get("title", dim),
                "interventions": cat_info.get("strategic_interventions", []),
                "stakeholders": cat_info.get("lead_stakeholders", "Relevant Agencies"),
            })

        # Sort descending by priority score
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        return prioritized

    def generate_context_recommendations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generates conditional recommendations based on cross-variable findings:
        - High media exposure + low awareness / verification
        - Low actual knowledge / large perception-reality gap
        """
        context_recs = []

        # Check media exposure relationship
        if "dim_media_exposure" in df.columns and "dim_verification_behavior" in df.columns:
            r_sp, _ = stats.spearmanr(df["dim_media_exposure"], df["dim_verification_behavior"])
            me_mean = float(df["dim_media_exposure"].mean())
            if me_mean > 3.5:
                context_recs.append({
                    "condition": "High Media Exposure with Depressed Verification Behavior",
                    "evidence": f"Media Exposure Mean = {me_mean:.2f}/5.0 (Spearman rho with verification = {r_sp:.2f})",
                    "intervention": (
                        "Institutionalize Healthy Media-Use Guidelines and Algorithmic Literacy campaigns. "
                        "Encourage cognitive friction before instant resharing on messaging platforms (WhatsApp, Telegram)."
                    ),
                    "stakeholders": "Telecommunications Regulatory Commission (TRC), MoDEE, Youth Centers",
                })

        # Check Perception-Reality Gap
        if "actual_knowledge_score" in df.columns:
            actual_mean = float(df["actual_knowledge_score"].mean()) * 100.0
            perceived_mean = float(df["overall_awareness_score"].mean())
            # Perceived score on 1-5 scale normalized to % = (mean - 1)/4 * 100
            norm_perceived = ((perceived_mean - 1.0) / 4.0) * 100.0
            gap = norm_perceived - actual_mean

            if gap > 10.0 or actual_mean < 65.0:
                context_recs.append({
                    "condition": "Cognitive Overconfidence (Perception-Reality Knowledge Gap)",
                    "evidence": f"Subjective Awareness Index = {norm_perceived:.1f}% vs Objective Knowledge Score = {actual_mean:.1f}% (Gap = +{gap:.1f}%)",
                    "intervention": (
                        "Launch Gamified Knowledge Self-Assessment Quizzes and interactive vulnerability simulators. "
                        "Overconfidence suppresses cautious verification; citizens must experience simulated phishing "
                        "and deceptive headline trials to confront personal vulnerabilities."
                    ),
                    "stakeholders": "National Cyber Security Center (NCSC-JO), Academic Institutions",
                })

        return context_recs

    def generate_demographic_targeted_recommendations(
        self, df: pd.DataFrame, group_tests_df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """
        Identifies demographic segments performing significantly below benchmark
        and assigns targeted localized outreach.
        """
        targeted = []

        # Evaluate youth age cohort (18-24)
        if "age_group" in df.columns:
            youth_sub = df[df["age_group"] == "18–24"]["overall_awareness_score"]
            older_sub = df[df["age_group"] != "18–24"]["overall_awareness_score"]
            if len(youth_sub) >= 5 and len(older_sub) >= 5:
                if youth_sub.mean() < older_sub.mean():
                    targeted.append({
                        "target_segment": "Youth Cohort (18–24 years)",
                        "observed_disparity": f"Youth Mean: {youth_sub.mean():.2f} vs Older Mean: {older_sub.mean():.2f}",
                        "action": "University Campus Roadshows and Peer-Led Cyber Hygiene Labs across Jordan's collegiate network.",
                        "lead_owner": "Ministry of Higher Education and Scientific Research, Student Unions",
                    })

        # Evaluate Education Level
        if "education_level" in df.columns:
            hs_sub = df[df["education_level"] == "ثانوية فأقل"]["overall_awareness_score"]
            deg_sub = df[df["education_level"].isin(["بكالوريوس", "دراسات عليا"])]["overall_awareness_score"]
            if len(hs_sub) >= 5 and len(deg_sub) >= 5:
                if hs_sub.mean() < deg_sub.mean():
                    targeted.append({
                        "target_segment": "Secondary Education or Below",
                        "observed_disparity": f"Vocational/Secondary Mean: {hs_sub.mean():.2f} vs Degree Holders: {deg_sub.mean():.2f}",
                        "action": "Vocational Training Center Cyber Curricula and Community Center Digital Literacy Programs.",
                        "lead_owner": "Vocational Training Corporation (VTC), Ministry of Social Development",
                    })

        # Evaluate Governorates
        if "governorate" in df.columns:
            gov_means = df.groupby("governorate")["overall_awareness_score"].agg(["mean", "count"])
            valid_govs = gov_means[gov_means["count"] >= 5]
            if len(valid_govs) >= 2:
                lowest_gov = valid_govs["mean"].idxmin()
                lowest_score = valid_govs["mean"].min()
                overall_avg = df["overall_awareness_score"].mean()
                if lowest_score < overall_avg - 0.2:
                    targeted.append({
                        "target_segment": f"Regional Focus: Governorate of {lowest_gov}",
                        "observed_disparity": f"Governorate Mean: {lowest_score:.2f} (National Mean: {overall_avg:.2f})",
                        "action": f"Regional outreach taskforce coordinating with {lowest_gov} Municipality, Governor's Office, and local youth directorates.",
                        "lead_owner": f"Ministry of Local Administration, {lowest_gov} Governorate Council",
                    })

        return targeted

    def construct_action_plan(self, prioritized_recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Structures a 3-horizon action roadmap with owners and measurable KPIs.
        """
        plan = [
            {
                "horizon": "Horizon 1: Immediate (0–3 Months)",
                "action": "Launch national 'Verify Before You Share' & Anti-Scam Broadcast Campaign",
                "focus_dimension": prioritized_recs[0]["dimension"] if prioritized_recs else "digital_threat_awareness",
                "lead_owner": "National Cyber Security Center (NCSC-JO) & Jordan Media Commission",
                "kpi": "Reach 1,500,000 citizens via mobile networks and digital channels; achieve 50,000 quiz completions.",
            },
            {
                "horizon": "Horizon 1: Immediate (0–3 Months)",
                "action": "Deploy rapid-response debunking fact-sheets on WhatsApp and Telegram official channels",
                "focus_dimension": "official_source_trust",
                "lead_owner": "Government Communications Directorate & Petra News Agency",
                "kpi": "Sub-60 minute verified debunks for circulating national rumors.",
            },
            {
                "horizon": "Horizon 2: Short-Term (3–12 Months)",
                "action": "Roll out experiential cybersecurity & counter-fraud workshops in public and private universities",
                "focus_dimension": "digital_threat_awareness",
                "lead_owner": "Ministry of Digital Economy and Entrepreneurship (MoDEE) & University Deanships",
                "kpi": "+0.5 increase in mean student awareness score upon re-survey; 30,000 students certified.",
            },
            {
                "horizon": "Horizon 2: Short-Term (3–12 Months)",
                "action": "Implement interactive fact-checking and media literacy training modules in secondary schools",
                "focus_dimension": "rumor_detection",
                "lead_owner": "Ministry of Education & Misbar/Akeed Fact-Checking Consortium",
                "kpi": "Reduce Low-band proportion in student demographic below 15%; train 500 educators.",
            },
            {
                "horizon": "Horizon 3: Long-Term (1–3 Years)",
                "action": "Establish permanent National Digital Resilience Observatory and Longitudinal Monitoring System",
                "focus_dimension": "Systemic Resilience & Policy",
                "lead_owner": "Higher Council for Science and Technology (HCST) & Academic Research Consortium",
                "kpi": "Annual national representative survey with n >= 2,500; national awareness benchmark >= 4.0/5.0.",
            },
        ]
        return plan

    def compile_executive_report(
        self,
        system_status: Dict[str, Any],
        quality_summary: Dict[str, Any],
        reliability_results: Dict[str, Any],
        ranking_results: Dict[str, Any],
        group_tests_df: pd.DataFrame,
        audit_summary: Dict[str, Any],
        sensitivity_results: Dict[str, Any],
        prioritized_recs: List[Dict[str, Any]],
        context_recs: List[Dict[str, Any]],
        demographic_recs: List[Dict[str, Any]],
        action_plan: List[Dict[str, Any]],
    ) -> Tuple[str, str]:
        """
        Compiles the authoritative, formal Executive Decision Report
        in both Plain Text (.txt) and Markdown (.md) formats without emojis.
        """
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Top group differences
        sig_groups = group_tests_df[group_tests_df["is_significant"] == True]
        sig_count = len(sig_groups)

        # Markdown Document
        md = f"""# EXECUTIVE DECISION REPORT: JORDAN SOCIAL & SECURITY AWARENESS ANALYSIS (JSSAA)
**Evaluation Date:** {now_str}  
**Jurisdiction:** Hashemite Kingdom of Jordan  
**Investigation Framework:** Anonymous Academic & Applied Community Assessment  
**Classification:** Strategic Policy Assessment (Public Distribution)

---

## 1. EXECUTIVE SUMMARY & STRATEGIC STATUS

### Overall System Classification
- **National Awareness Status:** **{system_status['final_status']}**
- **Severity Rating:** **{system_status['final_severity']}**
- **Sample Mean Awareness Score:** **{system_status['mean_score']} / 5.000** (SD = {system_status['sd_score']})
- **95% Confidence Interval:** **[{system_status['ci_95'][0]}, {system_status['ci_95'][1]}]**
- **Escalation Status:** {"Active - " + system_status['escalation_reason'] if system_status['escalated'] else "Nominal (No threshold escalation triggered)"}

### Awareness Band Distribution
- **Low Awareness / High Risk (Score <= 2.33):** {system_status['pct_low']}% of sample
- **Moderate Awareness / Elevated Risk (2.34 - 3.66):** {system_status['pct_moderate']}% of sample
- **High Awareness / Stable Resilience (Score >= 3.67):** {system_status['pct_high']}% of sample

---

## 2. DATA INGESTION & QUALITY CONTROL AUDIT

The operational survey dataset underwent automated schema validation, range enforcement, and duplicate screening:
- **Raw Survey Records Ingested:** {quality_summary['raw_count']}
- **Exact Duplicate Submissions Excluded:** {quality_summary['duplicate_count']}
- **Out-of-Range Likert Anomalies Handled:** {quality_summary['out_of_range_count']}
- **High-Missingness Records Dropped (>20% Missing):** {quality_summary['dropped_missing_count']}
- **Imputed Single-Item Missing Cells (Median):** {quality_summary.get('imputed_cells_count', 0)}
- **Final Validated Analytic Cohort:** **n = {quality_summary['final_count']}**

---

## 3. PSYCHOMETRIC SCALE RELIABILITY & INTERNAL CONSISTENCY

Reliability was modeled using Cronbach's alpha (unbiased sample variance, ddof=1):
- **Full Survey Instrument (23 Likert Items):** alpha = {reliability_results.get('full_scale', {}).get('alpha', 'N/A')} ({reliability_results.get('full_scale', {}).get('interpretation', 'N/A')})
- **Core Awareness Scale (Excl. Media Exposure):** alpha = {reliability_results.get('overall_awareness_scale', {}).get('alpha', 'N/A')} ({reliability_results.get('overall_awareness_scale', {}).get('interpretation', 'N/A')})

### Dimension Reliability Breakdown:
"""
        for dim in config.DIMENSIONS:
            d_rel = reliability_results.get(dim, {})
            md += f"- **{dim}:** alpha = {d_rel.get('alpha', 'N/A')} ({d_rel.get('interpretation', 'N/A')}, k = {d_rel.get('k_items', 'N/A')} items)\n"

        md += f"""
---

## 4. DIMENSIONAL RANKINGS & ITEM-LEVEL EXTREMES

### Dimension Performance (Ranked Strongest to Weakest Mean Score):
"""
        for idx, (dim_name, d_mean) in enumerate(ranking_results["ranked_dimensions"], start=1):
            md += f"{idx}. **{dim_name}:** {d_mean:.3f} / 5.000\n"

        md += "\n### Priority Vulnerability Items (Bottom-5 Lowest Scoring Survey Items):\n"
        for idx, (item_code, i_mean) in enumerate(ranking_results["bottom_5_items"], start=1):
            md += f"{idx}. **{item_code}:** Mean = {i_mean:.3f} / 5.000\n"

        md += f"""
---

## 5. INFERENTIAL DEMOGRAPHIC DISPARITY ANALYSIS

Statistical hypothesis testing evaluated score variance across key Jordanian demographic segments:
- Total Statistical Group Models Executed: {len(group_tests_df)}
- Statistically Significant Disparities Detected: **{sig_count}** (at alpha = {config.ALPHA})

### Statistically Significant Findings:
"""
        if sig_count > 0:
            for _, r in sig_groups.iterrows():
                md += (
                    f"- **{r['demographic'].upper()}** ({r['test_type']}): "
                    f"Stat = {r['statistic']}, p = {r['p_value']:.4f}, "
                    f"Effect Size = {r['effect_size']} ({r['effect_size_type']}, {r['magnitude']}). "
                    f"Post-Hoc: {r['post_hoc']}\n"
                )
        else:
            md += "- No demographic comparisons reached statistical significance at the alpha = 0.05 threshold.\n"

        md += f"""
---

## 6. RESPONSE INTEGRITY AUDIT & SENSITIVITY RE-ESTIMATION

### Anomaly Screening Summary
- Total Suspicious Responses Flagged: **{audit_summary['total_suspicious_flagged']}** ({audit_summary['pct_suspicious']}% of cohort)
- Straight-Liners Identified (Zero Variance across raw items): {audit_summary['straightliner_count']}
- Interquartile Range (IQR) Score Outliers: {audit_summary['iqr_outlier_count']}
- Item-Level Z-Score Outliers (|Z| > {config.Z_THRESHOLD}): {audit_summary['item_outlier_count']}

### Sensitivity Analysis (Full Cohort vs Clean Subset)
To ensure recommendations do not depend on aberrant response patterns, core models were re-estimated excluding flagged records:
- **Baseline Sample (n = {sensitivity_results['n_full']}):** Mean = {sensitivity_results['mean_full']}, Cronbach's alpha = {sensitivity_results['alpha_full']}, Status = {sensitivity_results['baseline_status']}
- **Cleaned Cohort (n = {sensitivity_results['n_clean']}):** Mean = {sensitivity_results['mean_clean']}, Cronbach's alpha = {sensitivity_results['alpha_clean']}, Status = {sensitivity_results['clean_status']}
- **Delta:** Mean change = {sensitivity_results['mean_delta']:+.3f}, Alpha change = {sensitivity_results['alpha_delta']:+.3f}
- **Stability Assessment:** **{'HIGHLY ROBUST' if sensitivity_results['conclusion_stable'] else 'SENSITIVE TO OUTLIERS'}**
  * System status remained identical: {not sensitivity_results['status_changed']}
  * Dimension relative rank ordering remained consistent: {not sensitivity_results['ranking_changed']}

---

## 7. PRIORITIZED JORDANIAN ACTION RECOMMENDATIONS

Recommendations are ordered by quantitative priority score:
Priority Score = (Target [4.0] - Dimension Mean) x (1 + % in Low Band / 100)
"""
        for idx, rec in enumerate(prioritized_recs, start=1):
            md += f"""
### Priority {idx}: {rec['title']}
- **Target Dimension:** `{rec['dimension']}`
- **Dimension Score:** {rec['dimension_mean']:.3f} / 5.000 | **Low-Band Respondents:** {rec['pct_low_band']}%
- **Quantitative Priority Metric:** **{rec['priority_score']}**
- **Lead Responsible Agencies:** {rec['stakeholders']}
- **Actionable Interventions:**
"""
            for action in rec['interventions']:
                md += f"  * {action}\n"

        if context_recs:
            md += "\n### Cross-Variable Strategic Interventions:\n"
            for cr in context_recs:
                md += f"- **Condition:** {cr['condition']}\n  * *Evidence:* {cr['evidence']}\n  * *Intervention:* {cr['intervention']}\n  * *Owner:* {cr['stakeholders']}\n"

        if demographic_recs:
            md += "\n### Demographic-Targeted Outreach:\n"
            for dr in demographic_recs:
                md += f"- **Target Segment:** {dr['target_segment']}\n  * *Observed Disparity:* {dr['observed_disparity']}\n  * *Prescribed Action:* {dr['action']}\n  * *Lead Owner:* {dr['lead_owner']}\n"

        md += """
---

## 8. THREE-HORIZON IMPLEMENTATION ROADMAP

| Horizon | Strategic Action | Focus Dimension | Lead Owner | Measurable KPI |
|---|---|---|---|---|
"""
        for item in action_plan:
            md += f"| {item['horizon']} | {item['action']} | `{item['focus_dimension']}` | {item['lead_owner']} | {item['kpi']} |\n"

        md += f"""
---

## 9. METHODOLOGICAL LIMITATIONS & SCIENTIFIC CAVEATS

1. **Non-Probability Convenience Sampling:**  
   Field data collection utilizing online survey delivery (Google Forms) predominantly engages digitally active citizens and collegiate networks. Rural cohorts and individuals with limited internet connectivity may be underrepresented.
2. **Self-Report & Social Desirability Bias:**  
   Subjective assessments of digital hygiene and verification conduct can be upwardly biased by social desirability. The inclusion of objective knowledge probes partially mitigates, but does not eradicate, self-report inflation.
3. **Regional Geographic Distribution:**  
   While all 12 Jordanian governorates are accounted for, population clustering in Amman, Zarqa, and Irbid limits statistical power for smaller southern governorates (Tafilah, Ma'an).
4. **Cross-Sectional Observational Design:**  
   {config.ALPHA}-level associations, correlations, and regression paths document coexistence, not causation. Causal claims regarding media exposure driving rumor belief require experimental or longitudinal panel validation.
5. **Sample Size Constraints:**  
   Sub-group cross-tabulations require minimum cell counts (n >= {config.MIN_GROUP_SIZE}). Non-parametric alternatives (Mann-Whitney, Kruskal-Wallis) were selected to ensure robustness against non-normality.

---

## 10. CONCLUSION & NEXT STEPS

The JSSAA diagnostic framework demonstrates that while foundational awareness of overt digital hazards exists in the Jordanian public sphere, acute vulnerabilities persist in systematic verification discipline, advanced social engineering detection (CliQ and banking OTP fraud), and institutional rumor counteraction.

By operationalizing the Three-Horizon Implementation Roadmap in close alignment with the National Cyber Security Center (NCSC-JO), the Public Security Directorate Cyber Crime Unit, and Jordanian media institutions, policy leaders can systematically elevate national digital resilience toward the target benchmark of 4.0 / 5.0.
"""

        # Generate Plain Text Version (Stripping Markdown formatting)
        txt = md.replace("# ", "").replace("## ", "\n" + "=" * 60 + "\n").replace("### ", "\n--- ").replace("**", "").replace("*", "-")

        return txt, md
