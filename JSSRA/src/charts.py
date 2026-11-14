"""
JSSRA Data Visualization & Security-Monitor Charting Engine.

Generates high-DPI Plotly and Matplotlib figures customized for the dark theme:
- Dimension risk means with error bars and respondent overlays
- Overall risk distribution with KDE and band lines
- Demographic boxplots
- Standard Normal distribution curve with shaded percentile area
- Empirical rule comparative bar chart (Observed vs Theoretical 68-95-99.7)
- Quality Control chart with ±1σ, ±2σ, ±3σ control limits
- Annotated Spearman correlation heatmap
- Plotly Gauge dial and 5-axis Radar profile
- Waterfall/Bar contribution chart
- Donut chart of vulnerability bands
- 4-Panel security monitor dashboard
"""

import os
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def ar(text: str) -> str:
    """Helper for Arabic text rendering in Matplotlib (preserving native HarfBuzz)."""
    return str(text)


def get_caption_text(n: int, is_synthetic: bool = False) -> str:
    """Standardized academic caption string."""
    src = "SYNTHETIC DEMO DATA" if is_synthetic else "REAL FIELD SUBMISSIONS"
    return f"Sample Size: n = {n} | Data Source: {src} | Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}"


# ==========================================
# 1. Dimension Risk Means Chart
# ==========================================

def create_dimension_means_chart(
    dimensions_df: pd.DataFrame,
    respondent_trace: Optional[Dict[str, Any]] = None,
    is_synthetic: bool = False,
) -> go.Figure:
    """Creates dimension risk bar chart with ±1σ error bars and respondent marker."""
    dims = dimensions_df.copy()
    names = [config.DIMENSIONS[d]["name_ar"] for d in dims["dimension"]]
    means = dims["mean"].tolist()
    sds = dims["sd"].tolist()

    fig = go.Figure()

    # Community mean bars
    fig.add_trace(go.Bar(
        x=names,
        y=means,
        error_y=dict(type="data", array=sds, visible=True, color=config.THEME["accent_cyan"], thickness=1.5, width=4),
        marker=dict(
            color=[config.RISK_BANDS["Low"]["color"] if m <= config.LOW_RISK_MAX else
                   (config.RISK_BANDS["Moderate"]["color"] if m <= config.MODERATE_RISK_MAX else config.RISK_BANDS["High"]["color"])
                   for m in means],
            line=dict(color=config.THEME["border"], width=1),
        ),
        name="Community Mean (متوسط المجتمع)",
        text=[f"{m:.2f}" for m in means],
        textposition="outside",
    ))

    # Respondent overlay markers
    if respondent_trace:
        resp_scores = [d["risk_score"] for d in respondent_trace["dimensions_trace"]]
        fig.add_trace(go.Scatter(
            x=names,
            y=resp_scores,
            mode="markers+lines",
            marker=dict(size=14, color=config.THEME["accent_coral"], symbol="diamond", line=dict(color="white", width=2)),
            line=dict(color=config.THEME["accent_coral"], width=2, dash="dash"),
            name="Your Score (نتيجتك الشخصية)",
        ))

    # Threshold horizontal reference lines
    fig.add_hline(y=config.LOW_RISK_MAX, line_dash="dot", line_color=config.THEME["accent_green"],
                  annotation_text=f"Low Risk (<= {config.LOW_RISK_MAX})", annotation_position="bottom left")
    fig.add_hline(y=config.MODERATE_RISK_MAX, line_dash="dot", line_color=config.THEME["accent_coral"],
                  annotation_text=f"High Risk (>= {config.MODERATE_RISK_MAX})", annotation_position="top left")

    n_tot = dims["n"].iloc[0] if not dims.empty else 0
    fig.update_layout(
        title=dict(text=f"Dimension Risk Breakdown with ±1σ Error Bars<br><sup>{get_caption_text(n_tot, is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        yaxis=dict(title="Vulnerability Risk Score (1 to 5)", range=[0.8, 5.5], gridcolor=config.THEME["border"]),
        xaxis=dict(gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 2. Overall Risk Histogram & KDE
# ==========================================

def create_risk_distribution_chart(
    scored_df: pd.DataFrame,
    respondent_score: Optional[float] = None,
    is_synthetic: bool = False,
) -> go.Figure:
    """Creates distribution histogram and KDE curve with risk band boundaries."""
    scores = scored_df["overall_risk_index"].dropna()
    mean_val = float(scores.mean())
    sd_val = float(scores.std(ddof=1))

    fig = go.Figure()

    # Histogram
    fig.add_trace(go.Histogram(
        x=scores,
        histnorm="probability density",
        nbinsx=16,
        marker=dict(color=config.THEME["accent_blue"], opacity=0.6, line=dict(color=config.THEME["border"], width=1)),
        name="Observed Distribution",
    ))

    # Theoretical Normal curve fit
    x_range = np.linspace(1.0, 5.0, 200)
    y_norm = stats.norm.pdf(x_range, mean_val, sd_val) if sd_val > 0 else np.zeros_like(x_range)
    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_norm,
        mode="lines",
        line=dict(color=config.THEME["accent_cyan"], width=2.5),
        name=f"Fitted Normal Curve (X̄={mean_val:.2f}, σ={sd_val:.2f})",
    ))

    # Community mean vertical line
    fig.add_vline(x=mean_val, line_dash="solid", line_color=config.THEME["text"], line_width=2,
                  annotation_text=f"Community Mean ({mean_val:.2f})", annotation_position="top right")

    # Respondent vertical marker
    if respondent_score is not None:
        fig.add_vline(x=respondent_score, line_dash="dash", line_color=config.THEME["accent_coral"], line_width=3,
                      annotation_text=f"Your Score ({respondent_score:.2f})", annotation_position="top left")

    # Risk band background shading
    fig.add_vrect(x0=1.0, x1=config.LOW_RISK_MAX, fillcolor=config.THEME["accent_green"], opacity=0.08, line_width=0,
                  annotation_text="Low Risk", annotation_position="bottom left")
    fig.add_vrect(x0=config.LOW_RISK_MAX, x1=config.MODERATE_RISK_MAX, fillcolor=config.THEME["accent_amber"], opacity=0.08, line_width=0,
                  annotation_text="Moderate Risk", annotation_position="bottom left")
    fig.add_vrect(x0=config.MODERATE_RISK_MAX, x1=5.0, fillcolor=config.THEME["accent_coral"], opacity=0.08, line_width=0,
                  annotation_text="High Vulnerability", annotation_position="bottom left")

    fig.update_layout(
        title=dict(text=f"Community Overall Risk Distribution & Fitted Normal Curve<br><sup>{get_caption_text(len(scores), is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        xaxis=dict(title="Overall Risk Index (1 to 5)", range=[1.0, 5.0], gridcolor=config.THEME["border"]),
        yaxis=dict(title="Probability Density", gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 3. Standard Normal Distribution & Z-Score
# ==========================================

def create_z_normal_curve_chart(
    z_score: float,
    all_z_scores: Optional[pd.Series] = None,
    is_synthetic: bool = False,
) -> go.Figure:
    """
    Renders standard normal distribution curve N(0,1) with:
    - Shaded percentile area from -infinity to respondent's Z
    - Respondent Z marker
    - Jittered dots for all community respondents along the axis
    """
    z_range = np.linspace(-3.5, 3.5, 300)
    pdf_vals = stats.norm.pdf(z_range)

    fig = go.Figure()

    # Full normal curve
    fig.add_trace(go.Scatter(
        x=z_range,
        y=pdf_vals,
        mode="lines",
        line=dict(color=config.THEME["accent_cyan"], width=2.5),
        name="Standard Normal Curve N(0, 1)",
    ))

    # Shaded cumulative percentile area
    z_shade = np.linspace(-3.5, min(3.5, max(-3.5, z_score)), 150)
    pdf_shade = stats.norm.pdf(z_shade)
    fig.add_trace(go.Scatter(
        x=np.concatenate(([z_shade[0]], z_shade, [z_shade[-1]])),
        y=np.concatenate(([0], pdf_shade, [0])),
        fill="toself",
        fillcolor="rgba(0, 194, 203, 0.25)",
        line=dict(color="rgba(255,255,255,0)"),
        name=f"Percentile Area: {stats.norm.cdf(z_score)*100:.1f}%",
    ))

    # Community respondents dots
    if all_z_scores is not None and not all_z_scores.empty:
        valid_z = all_z_scores.dropna()
        jitter_y = np.random.uniform(-0.02, -0.005, size=len(valid_z))
        fig.add_trace(go.Scatter(
            x=valid_z,
            y=jitter_y,
            mode="markers",
            marker=dict(size=5, color=config.THEME["muted"], opacity=0.4),
            name="Community Respondents",
            hoverinfo="x",
        ))

    # Respondent vertical marker
    fig.add_vline(x=z_score, line_dash="solid", line_color=config.THEME["accent_coral"], line_width=3,
                  annotation_text=f"Your Z = {z_score:+.2f} ({stats.norm.cdf(z_score)*100:.1f}%)",
                  annotation_position="top")

    n_val = len(all_z_scores) if all_z_scores is not None else 1
    fig.update_layout(
        title=dict(text=f"Standard Normal Curve: Position of Z-Score in Community<br><sup>{get_caption_text(n_val, is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        xaxis=dict(title="Z-Score (Standard Deviations from Mean)", range=[-3.5, 3.5], gridcolor=config.THEME["border"]),
        yaxis=dict(title="Density", range=[-0.03, 0.45], gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 4. Empirical Rule (68-95-99.7) Bar Chart
# ==========================================

def create_empirical_rule_chart(
    empirical_data: Dict[str, Any],
    is_synthetic: bool = False,
) -> go.Figure:
    """Renders comparative bar chart: Observed % vs Theoretical Empirical Rule."""
    bands = ["±1σ (Mean ± 1 SD)", "±2σ (Mean ± 2 SD)", "±3σ (Mean ± 3 SD)"]
    observed = [empirical_data["observed_1s"], empirical_data["observed_2s"], empirical_data["observed_3s"]]
    theoretical = [empirical_data["theoretical_1s"], empirical_data["theoretical_2s"], empirical_data["theoretical_3s"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bands,
        y=observed,
        name="Observed in Sample (النسبة الفعلية)",
        marker=dict(color=config.THEME["accent_cyan"], line=dict(color=config.THEME["border"], width=1)),
        text=[f"{v:.1f}%" for v in observed],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=bands,
        y=theoretical,
        name="Theoretical Empirical Rule (القاعدة النظرية)",
        marker=dict(color=config.THEME["accent_purple"], line=dict(color=config.THEME["border"], width=1)),
        text=[f"{v:.1f}%" for v in theoretical],
        textposition="outside",
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text=f"Empirical Rule Test: Observed vs. Theoretical 68–95–99.7%<br><sup>{get_caption_text(empirical_data['n'], is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        yaxis=dict(title="Percentage of Respondents (%)", range=[0, 115], gridcolor=config.THEME["border"]),
        xaxis=dict(gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 5. Quality Control Chart (Live Security Monitor)
# ==========================================

def create_control_chart(
    scored_df: pd.DataFrame,
    z_threshold: float = config.DEFAULT_Z_OUTLIER_THRESHOLD,
    is_synthetic: bool = False,
) -> go.Figure:
    """
    Renders statistical process control chart of submissions in order with:
    - Centerline X̄ (Mean)
    - ±1σ, ±2σ, ±3σ control lines
    - Outliers (|Z| > threshold) highlighted in coral
    """
    scores = scored_df["overall_risk_index"].reset_index(drop=True)
    n = len(scores)
    mean_val = float(scores.mean())
    sd_val = float(scores.std(ddof=1)) if n > 1 else 0.0

    z_scores = (scores - mean_val) / sd_val if sd_val > 0 else np.zeros(n)
    is_outlier = np.abs(z_scores) > z_threshold

    indices = np.arange(1, n + 1)
    colors = [config.THEME["accent_coral"] if out else config.THEME["accent_cyan"] for out in is_outlier]

    fig = go.Figure()

    # Submission sequence line
    fig.add_trace(go.Scatter(
        x=indices,
        y=scores,
        mode="lines+markers",
        line=dict(color=config.THEME["muted"], width=1.2),
        marker=dict(color=colors, size=8, line=dict(color="white", width=0.8)),
        name="Respondent Submissions",
        hovertext=[f"Row #{i}<br>Risk: {s:.2f}<br>Z: {z:+.2f}" for i, s, z in zip(indices, scores, z_scores)],
        hoverinfo="text",
    ))

    # Mean Centerline
    fig.add_hline(y=mean_val, line_dash="solid", line_color=config.THEME["accent_cyan"], line_width=2,
                  annotation_text=f"Mean X̄ = {mean_val:.2f}")

    # ±1σ, ±2σ, ±3σ lines
    fig.add_hline(y=mean_val + sd_val, line_dash="dot", line_color=config.THEME["accent_green"], annotation_text="+1σ")
    fig.add_hline(y=mean_val - sd_val, line_dash="dot", line_color=config.THEME["accent_green"], annotation_text="-1σ")
    fig.add_hline(y=mean_val + 2 * sd_val, line_dash="dash", line_color=config.THEME["accent_amber"], annotation_text="+2σ (Warning)")
    fig.add_hline(y=mean_val - 2 * sd_val, line_dash="dash", line_color=config.THEME["accent_amber"], annotation_text="-2σ")
    fig.add_hline(y=mean_val + 3 * sd_val, line_dash="longdash", line_color=config.THEME["accent_coral"], annotation_text="+3σ (Control Limit)")
    fig.add_hline(y=mean_val - 3 * sd_val, line_dash="longdash", line_color=config.THEME["accent_coral"], annotation_text="-3σ")

    fig.update_layout(
        title=dict(text=f"Statistical Quality Control Chart (Submissions Sequence Monitor)<br><sup>{get_caption_text(n, is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        xaxis=dict(title="Submission Sequence (Anonymous Respondent Index)", gridcolor=config.THEME["border"]),
        yaxis=dict(title="Overall Risk Index", range=[0.8, 5.2], gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 6. Correlation Heatmap
# ==========================================

def create_correlation_heatmap(
    corr_df: pd.DataFrame,
    p_values_df: pd.DataFrame,
    is_synthetic: bool = False,
) -> go.Figure:
    """Renders annotated Spearman correlation heatmap with significance stars."""
    z_vals = corr_df.values
    labels = corr_df.columns.tolist()

    # Form text matrix with r and stars
    text_matrix = []
    for i in range(len(labels)):
        row = []
        for j in range(len(labels)):
            r = z_vals[i, j]
            p = p_values_df.iloc[i, j]
            star = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
            row.append(f"{r:.2f}{star}" if i != j else "1.00")
        text_matrix.append(row)

    fig = px.imshow(
        z_vals,
        x=labels,
        y=labels,
        color_continuous_scale="RdBu_r",
        zmin=-0.5,
        zmax=1.0,
        text_auto=False,
    )
    fig.update_traces(text=text_matrix, texttemplate="%{text}")
    fig.update_layout(
        title=dict(text=f"Spearman Dimension Correlation Matrix (*p<0.05, **p<0.01, ***p<0.001)<br><sup>{get_caption_text(len(corr_df), is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 7. Gauge Chart
# ==========================================

def create_risk_gauge_chart(risk_score: float, risk_band: str) -> go.Figure:
    """Renders Plotly Gauge dial indicating personal vulnerability index."""
    color = config.RISK_BANDS[risk_band]["color"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Overall Risk Index: {risk_score:.2f} / 5.00<br><span style='font-size:14px;color:{color};'>{config.RISK_BANDS[risk_band]['label_ar']}</span>"},
        gauge={
            'axis': {'range': [1.0, 5.0], 'tickwidth': 1, 'tickcolor': config.THEME["muted"]},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': config.THEME["card"],
            'borderwidth': 1,
            'bordercolor': config.THEME["border"],
            'steps': [
                {'range': [1.0, config.LOW_RISK_MAX], 'color': 'rgba(46, 204, 113, 0.2)'},
                {'range': [config.LOW_RISK_MAX, config.MODERATE_RISK_MAX], 'color': 'rgba(255, 180, 0, 0.2)'},
                {'range': [config.MODERATE_RISK_MAX, 5.0], 'color': 'rgba(255, 77, 109, 0.2)'},
            ],
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'thickness': 0.75,
                'value': risk_score,
            },
        },
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=50, b=20),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 8. Radar Chart
# ==========================================

def create_radar_profile_chart(
    respondent_trace: Dict[str, Any],
    dimensions_df: pd.DataFrame,
    is_synthetic: bool = False,
) -> go.Figure:
    """Renders polar 5-axis spider plot comparing respondent against community mean."""
    dims = dimensions_df.copy()
    categories = [config.DIMENSIONS[d]["name_ar"] for d in dims["dimension"]]
    community_means = dims["mean"].tolist()
    resp_scores = [d["risk_score"] for d in respondent_trace["dimensions_trace"]]

    # Close the polygon loop
    categories_circ = categories + [categories[0]]
    community_circ = community_means + [community_means[0]]
    resp_circ = resp_scores + [resp_scores[0]]

    fig = go.Figure()

    # Community mean polygon
    fig.add_trace(go.Scatterpolar(
        r=community_circ,
        theta=categories_circ,
        fill="toself",
        fillcolor="rgba(0, 194, 203, 0.15)",
        line=dict(color=config.THEME["accent_cyan"], width=2),
        name="Community Mean (متوسط المجتمع)",
    ))

    # Respondent polygon
    fig.add_trace(go.Scatterpolar(
        r=resp_circ,
        theta=categories_circ,
        fill="toself",
        fillcolor="rgba(255, 77, 109, 0.25)",
        line=dict(color=config.THEME["accent_coral"], width=2.5),
        name="Your Profile (نتيجتك الشخصية)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[1.0, 5.0], gridcolor=config.THEME["border"]),
            bgcolor=config.THEME["card"],
        ),
        title=dict(text=f"Five-Dimensional Vulnerability Radar Profile<br><sup>{get_caption_text(dims['n'].iloc[0], is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 9. Waterfall / Contribution Chart
# ==========================================

def create_contribution_waterfall_chart(
    dimensions_trace: List[Dict[str, Any]],
) -> go.Figure:
    """Renders contribution bar chart relative to neutral value 3.0."""
    names = [d["name_ar"] for d in dimensions_trace]
    contribs = [d["contribution"] for d in dimensions_trace]
    colors = [config.THEME["accent_coral"] if c > 0 else config.THEME["accent_green"] for c in contribs]

    fig = go.Figure(go.Bar(
        x=names,
        y=contribs,
        marker=dict(color=colors, line=dict(color=config.THEME["border"], width=1)),
        text=[f"{c:+.2f}" for c in contribs],
        textposition="outside",
    ))
    fig.add_hline(y=0.0, line_dash="solid", line_color=config.THEME["text"], line_width=1.5)

    fig.update_layout(
        title=dict(text="Dimensional Contribution Relative to Neutral Midpoint (3.0)<br><sup>(Positive: Increases Risk | Negative: Lowers Risk)</sup>",
                    font=dict(color=config.THEME["text"], size=15)),
        yaxis=dict(title="Deviation from Neutral 3.0 (انحراف الدرجة)", gridcolor=config.THEME["border"]),
        xaxis=dict(gridcolor=config.THEME["border"]),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 10. Donut Risk Band Distribution Chart
# ==========================================

def create_risk_donut_chart(
    scored_df: pd.DataFrame,
    is_synthetic: bool = False,
) -> go.Figure:
    """Renders donut chart of Low / Moderate / High vulnerability bands."""
    band_counts = scored_df["risk_band"].value_counts()
    labels = ["Low Risk (منخفض)", "Moderate Risk (متوسط)", "High Vulnerability (مرتفع)"]
    counts = [band_counts.get("Low", 0), band_counts.get("Moderate", 0), band_counts.get("High", 0)]
    colors = [config.THEME["accent_green"], config.THEME["accent_amber"], config.THEME["accent_coral"]]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=counts,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=config.THEME["card"], width=2)),
        textinfo="label+percent+value",
        textfont=dict(color="white", size=12),
    ))
    fig.update_layout(
        title=dict(text=f"Community Risk Category Breakdown (Donut Distribution)<br><sup>{get_caption_text(len(scored_df), is_synthetic)}</sup>",
                    font=dict(color=config.THEME["text"], size=16)),
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 11. Demographic Boxplot Chart
# ==========================================

def create_demographic_boxplot(
    scored_df: pd.DataFrame,
    demo_column: str = "respondent_type",
    is_synthetic: bool = False,
) -> go.Figure:
    """Renders interactive boxplot of Overall Risk Index grouped by demographic cohort."""
    fig = px.box(
        scored_df,
        x=demo_column,
        y="overall_risk_index",
        color=demo_column,
        points="all",
        labels={"overall_risk_index": "Overall Risk Index (1 to 5)", demo_column: config.DEMOGRAPHICS.get(demo_column, {}).get("name_ar", demo_column)},
        title=f"Overall Risk Index Disparity across {config.DEMOGRAPHICS.get(demo_column, {}).get('name_en', demo_column)}<br><sup>{get_caption_text(len(scored_df), is_synthetic)}</sup>",
    )
    fig.add_hline(y=config.LOW_RISK_MAX, line_dash="dot", line_color=config.THEME["accent_green"])
    fig.add_hline(y=config.MODERATE_RISK_MAX, line_dash="dot", line_color=config.THEME["accent_coral"])
    fig.update_layout(
        yaxis=dict(range=[0.8, 5.2], gridcolor=config.THEME["border"]),
        xaxis=dict(gridcolor=config.THEME["border"]),
        showlegend=False,
        **config.PLOTLY_DARK_LAYOUT,
    )
    return fig


# ==========================================
# 12. Static Matplotlib Exporter for Deck & Reports
# ==========================================

def export_static_charts(
    scored_df: pd.DataFrame,
    respondent_trace: Optional[Dict[str, Any]] = None,
    is_synthetic: bool = False,
    output_dir: str = "outputs",
) -> Dict[str, str]:
    """
    Exports high-resolution, dark-themed static PNG charts for PowerPoint presentation
    and downloadable executive report packages.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    bg_color = config.THEME["bg"]
    card_color = config.THEME["card"]
    text_color = config.THEME["text"]
    cyan = config.THEME["accent_cyan"]
    coral = config.THEME["accent_coral"]
    amber = config.THEME["accent_amber"]
    green = config.THEME["accent_green"]
    border_color = config.THEME["border"]

    plt.rcParams.update({
        "figure.facecolor": bg_color,
        "axes.facecolor": card_color,
        "axes.edgecolor": border_color,
        "axes.labelcolor": text_color,
        "text.color": text_color,
        "xtick.color": text_color,
        "ytick.color": text_color,
        "grid.color": border_color,
        "grid.alpha": 0.5,
    })

    from src.stats_engine import compute_all_descriptive, evaluate_empirical_rule

    desc = compute_all_descriptive(scored_df)
    dim_df = desc["dimensions_table"]
    n = len(scored_df)

    # 1. Dimension Means
    p1 = os.path.join(output_dir, "dimension_means.png")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    d_names = [config.DIMENSIONS[d]["name_en"] for d in dim_df["dimension"]]
    d_means = dim_df["mean"].values
    d_sds = dim_df["sd"].values
    bars = ax.bar(d_names, d_means, yerr=d_sds, capsize=5, color=cyan, edgecolor="white", alpha=0.85)
    ax.axhline(config.LOW_RISK_MAX, color=green, linestyle="--", alpha=0.7, label=f"Low (<= {config.LOW_RISK_MAX})")
    ax.axhline(config.MODERATE_RISK_MAX, color=coral, linestyle="--", alpha=0.7, label=f"High (>= {config.MODERATE_RISK_MAX})")
    ax.set_ylim(0.8, 5.2)
    ax.set_ylabel("Risk Score (1-5)")
    ax.set_title(f"Dimension Risk Breakdown (n={n})", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", facecolor=card_color, edgecolor=border_color)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(p1, facecolor=bg_color)
    plt.close()
    paths["dimension_means"] = p1

    # 2. Risk Distribution
    p2 = os.path.join(output_dir, "risk_distribution.png")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    scores = scored_df["overall_risk_index"].dropna()
    m_val = float(scores.mean())
    s_val = float(scores.std(ddof=1))
    ax.hist(scores, bins=15, density=True, color="#3a86ff", alpha=0.6, edgecolor=border_color, label="Observed Density")
    xr = np.linspace(1.0, 5.0, 200)
    yr = stats.norm.pdf(xr, m_val, s_val)
    ax.plot(xr, yr, color=cyan, lw=2.5, label=f"Normal Fit (μ={m_val:.2f}, σ={s_val:.2f})")
    ax.axvline(m_val, color="white", lw=1.5, linestyle="-", label=f"Mean = {m_val:.2f}")
    if respondent_trace:
        r_sc = respondent_trace["overall_risk"]
        ax.axvline(r_sc, color=coral, lw=2.5, linestyle="--", label=f"Respondent ({r_sc:.2f})")
    ax.set_xlim(1.0, 5.0)
    ax.set_xlabel("Overall Vulnerability Index")
    ax.set_ylabel("Density")
    ax.set_title(f"Community Overall Risk Distribution (n={n})", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", facecolor=card_color, edgecolor=border_color)
    plt.tight_layout()
    plt.savefig(p2, facecolor=bg_color)
    plt.close()
    paths["risk_distribution"] = p2

    # 3. Z-Normal Curve
    p3 = os.path.join(output_dir, "z_normal_curve.png")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    z_user = respondent_trace["z_score"] if respondent_trace else 0.0
    zr = np.linspace(-3.5, 3.5, 300)
    yr_z = stats.norm.pdf(zr)
    ax.plot(zr, yr_z, color=cyan, lw=2.5, label="N(0, 1) Standard Normal")
    z_fill = np.linspace(-3.5, min(3.5, max(-3.5, z_user)), 150)
    ax.fill_between(z_fill, stats.norm.pdf(z_fill), color=cyan, alpha=0.3, label=f"Percentile ({stats.norm.cdf(z_user)*100:.1f}%)")
    ax.axvline(z_user, color=coral, lw=2.5, linestyle="-", label=f"Z = {z_user:+.2f}")
    ax.set_xlabel("Z-Score")
    ax.set_ylabel("Probability Density")
    ax.set_title("Standard Normal Curve N(0,1) with Individual Z-Score", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper left", facecolor=card_color, edgecolor=border_color)
    plt.tight_layout()
    plt.savefig(p3, facecolor=bg_color)
    plt.close()
    paths["z_normal_curve"] = p3

    # 4. Empirical Rule
    p4 = os.path.join(output_dir, "empirical_rule.png")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    emp = evaluate_empirical_rule(scored_df["overall_risk_index"])
    labels = ["±1σ", "±2σ", "±3σ"]
    obs = [emp["observed_1s"], emp["observed_2s"], emp["observed_3s"]]
    theo = [emp["theoretical_1s"], emp["theoretical_2s"], emp["theoretical_3s"]]
    x_pos = np.arange(len(labels))
    w = 0.35
    ax.bar(x_pos - w/2, obs, w, label="Observed in Sample (%)", color=cyan, edgecolor="white")
    ax.bar(x_pos + w/2, theo, w, label="Theoretical Empirical Rule (%)", color="#8338ec", edgecolor="white")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Percentage (%)")
    ax.set_ylim(0, 110)
    ax.set_title(f"Empirical Rule Test (68-95-99.7) | Shapiro-Wilk p = {emp['shapiro_p']:.4f}", fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="upper left", facecolor=card_color, edgecolor=border_color)
    plt.tight_layout()
    plt.savefig(p4, facecolor=bg_color)
    plt.close()
    paths["empirical_rule"] = p4

    # 5. Control Chart
    p5 = os.path.join(output_dir, "control_chart.png")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    seq = np.arange(1, n + 1)
    ax.plot(seq, scores.values, color=config.THEME["muted"], marker="o", markersize=5, lw=1.2, label="Submissions")
    ax.axhline(m_val, color=cyan, lw=2, label=f"Centerline (μ={m_val:.2f})")
    ax.axhline(m_val + s_val, color=green, linestyle=":", label="±1σ")
    ax.axhline(m_val - s_val, color=green, linestyle=":")
    ax.axhline(m_val + 2*s_val, color=amber, linestyle="--", label="±2σ (Warning)")
    ax.axhline(m_val - 2*s_val, color=amber, linestyle="--")
    ax.axhline(m_val + 3*s_val, color=coral, linestyle="-.", label="±3σ (Action)")
    ax.axhline(m_val - 3*s_val, color=coral, linestyle="-.")
    ax.set_xlabel("Anonymous Submission Sequence")
    ax.set_ylabel("Vulnerability Score")
    ax.set_title("Statistical Quality Control Chart (Security Process Monitor)", fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="upper right", facecolor=card_color, edgecolor=border_color, fontsize=8)
    plt.tight_layout()
    plt.savefig(p5, facecolor=bg_color)
    plt.close()
    paths["control_chart"] = p5

    # 6. Correlation Heatmap
    p6 = os.path.join(output_dir, "correlation_heatmap.png")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=200)
    dim_cols = [c for c in scored_df.columns if c.endswith("_risk") or c.startswith("D")]
    # Extract only the 5 dimensions
    active_dims = []
    for d in config.DIMENSIONS.keys():
        col = f"risk_{d}"
        if col in scored_df.columns:
            active_dims.append(col)
    if len(active_dims) >= 3:
        corr_mat = scored_df[active_dims].corr(method="spearman").values
        labels_corr = [config.DIMENSIONS[d.replace("risk_", "")]["code"] for d in active_dims]
        im = ax.imshow(corr_mat, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(labels_corr)))
        ax.set_yticks(range(len(labels_corr)))
        ax.set_xticklabels(labels_corr, fontsize=10)
        ax.set_yticklabels(labels_corr, fontsize=10)
        for i in range(len(labels_corr)):
            for j in range(len(labels_corr)):
                val = corr_mat[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="white" if abs(val)>0.4 else "black", fontsize=9, fontweight="bold")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title("Spearman Rank Correlation Matrix", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(p6, facecolor=bg_color)
    plt.close()
    paths["correlation_heatmap"] = p6

    # 7. Radar Profile
    p7 = os.path.join(output_dir, "radar_profile.png")
    fig = plt.figure(figsize=(7, 7), dpi=200)
    ax = fig.add_subplot(111, polar=True)
    d_codes = [config.DIMENSIONS[d]["code"] for d in dim_df["dimension"]]
    d_means_r = dim_df["mean"].tolist()
    d_means_r += d_means_r[:1]
    angles = np.linspace(0, 2 * np.pi, len(d_codes), endpoint=False).tolist()
    angles += angles[:1]
    ax.plot(angles, d_means_r, color=cyan, lw=2, label="Community Mean")
    ax.fill(angles, d_means_r, color=cyan, alpha=0.15)
    if respondent_trace:
        r_scores_r = [d["risk_score"] for d in respondent_trace["dimensions_trace"]]
        r_scores_r += r_scores_r[:1]
        ax.plot(angles, r_scores_r, color=coral, lw=2.5, linestyle="--", label="Respondent")
        ax.fill(angles, r_scores_r, color=coral, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(d_codes, fontsize=11, color=text_color)
    ax.set_ylim(1, 5)
    ax.set_title("5-Dimension Vulnerability Profile", fontsize=13, fontweight="bold", pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), facecolor=card_color, edgecolor=border_color)
    plt.tight_layout()
    plt.savefig(p7, facecolor=bg_color)
    plt.close()
    paths["radar_profile"] = p7

    # 8. Demographic Boxplot
    p8 = os.path.join(output_dir, "demographic_boxplot.png")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    types = scored_df["respondent_type"].unique()
    box_data = [scored_df[scored_df["respondent_type"] == t]["overall_risk_index"].dropna().values for t in types]
    bp = ax.boxplot(box_data, tick_labels=[t[:15] for t in types], patch_artist=True)
    for box in bp['boxes']:
        box.set(facecolor=cyan, alpha=0.7, edgecolor="white")
    ax.axhline(config.LOW_RISK_MAX, color=green, linestyle="--")
    ax.axhline(config.MODERATE_RISK_MAX, color=coral, linestyle="--")
    ax.set_ylabel("Overall Risk Index")
    ax.set_title("Vulnerability Disparity by Respondent Type", fontsize=13, fontweight="bold", pad=12)
    plt.xticks(rotation=15, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(p8, facecolor=bg_color)
    plt.close()
    paths["demographic_boxplot"] = p8

    # 9. 4-Panel Executive Dashboard
    p9 = os.path.join(output_dir, "dashboard_4panel.png")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=200)

    # Panel (0,0): Dimension Means
    axes[0, 0].bar(d_names, d_means, yerr=d_sds, capsize=4, color=cyan, alpha=0.85)
    axes[0, 0].axhline(config.LOW_RISK_MAX, color=green, linestyle="--")
    axes[0, 0].axhline(config.MODERATE_RISK_MAX, color=coral, linestyle="--")
    axes[0, 0].set_ylim(0.8, 5.2)
    axes[0, 0].set_title("Panel A: Dimension Risk Breakdown", fontsize=11, fontweight="bold")
    axes[0, 0].tick_params(axis='x', rotation=20, labelsize=8)

    # Panel (0,1): Risk Distribution
    axes[0, 1].hist(scores, bins=12, density=True, color="#3a86ff", alpha=0.6)
    axes[0, 1].plot(xr, yr, color=cyan, lw=2)
    axes[0, 1].axvline(m_val, color="white", lw=1.5, linestyle="-")
    axes[0, 1].set_title("Panel B: Community Risk Distribution & Normal Fit", fontsize=11, fontweight="bold")

    # Panel (1,0): Control Chart
    axes[1, 0].plot(seq, scores.values, color=config.THEME["muted"], marker="o", markersize=4, lw=1)
    axes[1, 0].axhline(m_val, color=cyan, lw=1.8)
    axes[1, 0].axhline(m_val + 2*s_val, color=amber, linestyle="--")
    axes[1, 0].axhline(m_val - 2*s_val, color=amber, linestyle="--")
    axes[1, 0].axhline(m_val + 3*s_val, color=coral, linestyle="-.")
    axes[1, 0].axhline(m_val - 3*s_val, color=coral, linestyle="-.")
    axes[1, 0].set_title("Panel C: Quality Control Chart (±1σ, ±2σ, ±3σ)", fontsize=11, fontweight="bold")

    # Panel (1,1): Empirical Rule
    axes[1, 1].bar(x_pos - w/2, obs, w, label="Observed", color=cyan)
    axes[1, 1].bar(x_pos + w/2, theo, w, label="Theoretical", color="#8338ec")
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(labels, fontsize=9)
    axes[1, 1].set_title("Panel D: Empirical Rule Test (68-95-99.7)", fontsize=11, fontweight="bold")
    axes[1, 1].legend(loc="upper left", facecolor=card_color, edgecolor=border_color, fontsize=8)

    plt.suptitle("JSSRA Youth Vulnerability & Community Risk Security Monitor", fontsize=15, fontweight="bold", y=0.98, color=cyan)
    plt.tight_layout()
    plt.savefig(p9, facecolor=bg_color)
    plt.close()
    paths["dashboard_4panel"] = p9

    return paths


