"""
JSSRA Dark Design System & Theme Engine.

Implements consistent dark theme styling, RTL Arabic support, Google Fonts
(Cairo + Inter), gradient verdict banners, numbered cards, and custom metric containers.
"""

from typing import Dict, Any, Optional
import streamlit as st

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def get_custom_css(lang: str = "ar") -> str:
    """
    Returns custom CSS for dark theme, typography, cards, and RTL/LTR layout.
    """
    direction = "rtl" if lang == "ar" else "ltr"
    text_align = "right" if lang == "ar" else "left"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, span, div {{
        font-family: 'Cairo', 'Inter', -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif !important;
        direction: {direction};
        text-align: {text_align};
    }}

    /* Main container background */
    .stApp {{
        background-color: {config.THEME["bg"]};
        color: {config.THEME["text"]};
    }}

    /* Sidebar background */
    section[data-testid="stSidebar"] {{
        background-color: {config.THEME["card"]};
        border-{ 'left' if lang == 'en' else 'right' }: 1px solid {config.THEME["border"]};
    }}

    /* Numbered Section Header Card */
    .section-header-card {{
        background: linear-gradient(90deg, rgba(18, 26, 51, 0.95), rgba(23, 34, 66, 0.7));
        border: 1px solid {config.THEME["border"]};
        border-top: 3px solid {config.THEME["accent_cyan"]};
        border-radius: 10px;
        padding: 16px 22px;
        margin-top: 24px;
        margin-bottom: 18px;
    }}
    .section-num {{
        display: inline-block;
        font-size: 14px;
        font-weight: 800;
        color: {config.THEME["accent_cyan"]};
        background: rgba(0, 194, 203, 0.12);
        padding: 3px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }}
    .section-title-en {{
        font-size: 20px;
        font-weight: 700;
        color: {config.THEME["text"]};
        margin: 2px 0;
    }}
    .section-title-ar {{
        font-size: 15px;
        font-weight: 600;
        color: {config.THEME["accent_cyan"]};
        margin: 0;
    }}

    /* Gradient Verdict Banner */
    .verdict-banner-low {{
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.18) 0%, rgba(18, 26, 51, 0.95) 100%);
        border: 1px solid #2ecc71;
        border-left: 6px solid #2ecc71;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 20px 0;
    }}
    .verdict-banner-moderate {{
        background: linear-gradient(135deg, rgba(255, 180, 0, 0.18) 0%, rgba(18, 26, 51, 0.95) 100%);
        border: 1px solid #ffb400;
        border-left: 6px solid #ffb400;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 20px 0;
    }}
    .verdict-banner-high {{
        background: linear-gradient(135deg, rgba(255, 77, 109, 0.22) 0%, rgba(18, 26, 51, 0.95) 100%);
        border: 1px solid #ff4d6d;
        border-left: 6px solid #ff4d6d;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 20px 0;
    }}

    /* Key Stats KPI Card */
    .kpi-card {{
        background: {config.THEME["card"]};
        border: 1px solid {config.THEME["border"]};
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .kpi-card:hover {{
        border-color: {config.THEME["accent_cyan"]};
        transform: translateY(-2px);
    }}
    .kpi-val {{
        font-size: 26px;
        font-weight: 800;
        color: {config.THEME["accent_cyan"]};
        margin: 6px 0;
    }}
    .kpi-lbl {{
        font-size: 13px;
        color: {config.THEME["muted"]};
        font-weight: 600;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: {config.THEME["accent_amber"]};
        margin-top: 4px;
    }}

    /* Synthetic Badge */
    .synthetic-badge {{
        display: inline-block;
        background: rgba(255, 180, 0, 0.18);
        color: #ffb400;
        border: 1px solid #ffb400;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        letter-spacing: 0.5px;
    }}

    /* Form Card Container */
    .form-item-container {{
        background: {config.THEME["card"]};
        border: 1px solid {config.THEME["border"]};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}

    /* Step indicator pill */
    .step-pill {{
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        margin: 0 4px;
    }}
    .step-pill-active {{
        background-color: {config.THEME["accent_cyan"]};
        color: #0b1020;
    }}
    .step-pill-inactive {{
        background-color: {config.THEME["card"]};
        color: {config.THEME["muted"]};
        border: 1px solid {config.THEME["border"]};
    }}

    /* Chart Caption */
    .chart-caption {{
        font-size: 12px;
        color: {config.THEME["muted"]};
        text-align: center;
        margin-top: -8px;
        margin-bottom: 16px;
        font-style: italic;
    }}
    </style>
    """
    return css


def render_section_header(num: str, title_en: str, title_ar: str):
    """Render a styled numbered section card."""
    st.markdown(
        f"""
        <div class="section-header-card">
            <div class="section-num">{num}</div>
            <div class="section-title-en">{title_en}</div>
            <div class="section-title-ar">{title_ar}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, subtext: str = "", accent_color: Optional[str] = None):
    """Render a styled KPI card."""
    col = accent_color if accent_color else config.THEME["accent_cyan"]
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-lbl">{label}</div>
            <div class="kpi-val" style="color: {col};">{value}</div>
            <div class="kpi-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_verdict_banner(band_key: str, score: float, z_score: float, percentile: float, lang: str = "ar"):
    """
    Renders the prominent gradient verdict banner (Section 01).
    Strictly adheres to academic framing: awareness/risk index, NOT a diagnosis.
    """
    band_map = {"low": "Low", "moderate": "Moderate", "high": "High"}
    band_key_mapped = band_map.get(band_key, "Moderate")
    band_info = config.RISK_BANDS.get(band_key_mapped, config.RISK_BANDS["Moderate"])
    color = band_info["color"]
    label = band_info["label_ar"] if lang == "ar" else band_info["label_en"]
    desc = band_info["summary_ar"] if lang == "ar" else band_info["summary_en"]
    
    banner_class = f"verdict-banner-{band_key}"
    
    disclaimer_text = (
        "تنبيه أخلاقي ومنهجي: هذه النتيجة تمثل مؤشراً توعوياً تحليلياً لعوامل الهشاشة المجتمعية، "
        "وليست بأي حال تشخيصاً نفسياً أو تصنيفاً أمنياً للشخص."
        if lang == "ar" else
        "Ethical & Methodological Notice: This result represents an awareness/risk-factor indicator, "
        "and is strictly NOT a psychological diagnosis or security classification."
    )

    score_badge_lbl = "درجة الهشاشة الفردية" if lang == "ar" else "Individual Vulnerability Score"
    z_lbl = "الدرجة المعيارية (Z-score)" if lang == "ar" else "Standard Z-score"
    pct_lbl = "الرتبة المئينية (Percentile)" if lang == "ar" else "Percentile Rank"

    st.markdown(
        f"""
        <div class="{banner_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 8px;">
                <span style="font-size: 24px; font-weight: 800; color: {color};">
                    {label}
                </span>
                <span style="background: {color}22; border: 1px solid {color}; color: {color}; padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 14px;">
                    {score:.2f} / 5.00
                </span>
            </div>
            <p style="font-size: 15px; color: #e8ecf8; margin: 8px 0 14px 0; line-height: 1.6;">
                {desc}
            </p>
            <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 12px; font-size: 13px; color: #a4b3d6;">
                <span><strong>{score_badge_lbl}:</strong> {score:.2f}</span>
                <span><strong>{z_lbl}:</strong> {z_score:+.2f}</span>
                <span><strong>{pct_lbl}:</strong> %{percentile:.1f}</span>
            </div>
            <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; margin-top: 10px; font-size: 12px; color: #8892b0; font-style: italic;">
                🛡️ {disclaimer_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(current_step: int, lang: str = "ar"):
    """Render a clean 4-step progress header in Streamlit."""
    steps_ar = [
        ("1", "استبيان القياس"),
        ("2", "الإحصاء الوصفي"),
        ("3", "التوزيع والمعيارية"),
        ("4", "التقرير والتوصيات"),
    ]
    steps_en = [
        ("1", "Questionnaire"),
        ("2", "Descriptive Stats"),
        ("3", "Z-Scores & Normality"),
        ("4", "Report & Actions"),
    ]
    steps = steps_ar if lang == "ar" else steps_en

    cols = st.columns(4)
    for idx, (num, name) in enumerate(steps, start=1):
        with cols[idx - 1]:
            if idx == current_step:
                status_style = f"background: {config.THEME['accent_cyan']}; color: #0b1020; font-weight: 800; border: 1px solid {config.THEME['accent_cyan']};"
                pill_symbol = f"▶ {num}"
            elif idx < current_step:
                status_style = "background: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid #2ecc71;"
                pill_symbol = f"✓ {num}"
            else:
                status_style = f"background: {config.THEME['card']}; color: {config.THEME['muted']}; border: 1px solid {config.THEME['border']};"
                pill_symbol = f"{num}"

            st.markdown(
                f"""
                <div style="{status_style} padding: 8px 12px; border-radius: 8px; text-align: center; margin-bottom: 12px; font-size: 13px;">
                    <div>{pill_symbol}</div>
                    <div style="font-weight: 600; margin-top: 2px;">{name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

