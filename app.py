"""
YOUTH AWARENESS & EXTREMISM RISK ASSESSMENT PORTAL
البوابة الإحصائية لدراسة وعي الشباب حول مخاطر التطرف والإرهاب
Applied Statistics & Probability for Engineers | مساق الإحصاء والاحتمالات للمهندسين
"""

import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PAGE CONFIGURATION & DARK-SLATE INSTITUTIONAL THEME
# ==============================================================================
st.set_page_config(
    page_title="Youth Awareness & Extremism Risk Assessment Portal",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Targeted CSS rules strictly avoiding global body direction:rtl or universal '*' font selector
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Cairo:wght@400;600;700;800&display=swap');

    /* Global Dark Slate Canvas */
    .stApp {
        background-color: #0b1120;
        color: #f8fafc;
    }

    h1, h2, h3, h4, p, label, .portal-header, .q-card, .kpi-card, .rec-card {
        font-family: 'Inter', 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Portal Banner */
    .portal-header {
        background: linear-gradient(135deg, #111a2e 0%, #162032 100%);
        border: 1px solid #283548;
        border-top: 4px solid #3b82f6;
        padding: 24px 30px;
        border-radius: 8px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .portal-title-en {
        color: #f8fafc;
        font-size: 21px;
        font-weight: 800;
        letter-spacing: 0.03em;
        margin: 0 0 4px 0;
        text-transform: uppercase;
    }
    .portal-title-ar {
        color: #38bdf8;
        font-size: 20px;
        font-weight: 700;
        margin: 0 0 6px 0;
        direction: rtl;
        text-align: right;
    }
    .portal-subtitle {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
        margin: 0;
    }

    /* Unified Dark Question Card */
    .q-card {
        background-color: #162032;
        border: 1px solid #283548;
        border-radius: 8px;
        padding: 16px 20px 12px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .q-badge {
        display: inline-block;
        color: #38bdf8;
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: 0.05em;
    }
    .q-text-en {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 600;
        line-height: 1.5;
        margin-bottom: 4px;
    }
    .q-text-ar {
        color: #cbd5e1;
        font-size: 15px;
        font-weight: 600;
        line-height: 1.6;
        direction: rtl;
        text-align: right;
        margin-bottom: 10px;
    }

    /* Unified KPI Card */
    .kpi-card {
        background-color: #162032;
        border: 1px solid #334155;
        border-top: 3px solid #3b82f6;
        border-radius: 8px;
        padding: 16px 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-sub {
        color: #64748b;
        font-size: 11px;
        margin-top: 6px;
    }

    /* Structured Recommendation Panel */
    .rec-card {
        background-color: #162032;
        border-radius: 8px;
        padding: 22px 26px;
        margin: 20px 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .rec-card-low {
        border: 1px solid #10b981;
        border-top: 4px solid #10b981;
    }
    .rec-card-mod {
        border: 1px solid #f59e0b;
        border-top: 4px solid #f59e0b;
    }
    .rec-card-high {
        border: 1px solid #ef4444;
        border-top: 4px solid #ef4444;
    }

    .rec-header {
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #283548;
    }
    .rec-col-en {
        color: #e2e8f0;
        font-size: 13.5px;
        line-height: 1.8;
    }
    .rec-col-ar {
        color: #e2e8f0;
        font-size: 14px;
        line-height: 1.9;
        direction: rtl;
        text-align: right;
    }

    /* High contrast primary submit button */
    div.stButton > button:first-child {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. SURVEY ITEMS REPOSITORY (10 QUANTITATIVE DIMENSIONS)
# ==============================================================================
QUESTIONS = [
    {
        "id": "Q1",
        "en": "Exposure to extremist or radical recruitment discourse online",
        "ar": "التعرض لخطابات التطرف أو التحريض الفكري عبر المنصات الرقمية"
    },
    {
        "id": "Q2",
        "en": "Tendency toward intellectual isolation or closed radical groups",
        "ar": "القابلية للانعزال الفكري أو الانضمام لمجموعات مغلقة متشددة"
    },
    {
        "id": "Q3",
        "en": "Accepting unverified rumors that incite division and extremism",
        "ar": "التسرع في تصديق الشائعات المضللة التي تثير الفتنة والتطرف"
    },
    {
        "id": "Q4",
        "en": "Influence of emotional propaganda justifying violence or terrorism",
        "ar": "التأثر بالخطابات العاطفية التي تستغل الأزمات لتبرير العنف أو الإرهاب"
    },
    {
        "id": "Q5",
        "en": "Absence of family and community dialogue on extremism risks",
        "ar": "غياب الحوار الأسري والمجتمعي حول مخاطر الفكر المتطرف"
    },
    {
        "id": "Q6",
        "en": "Low participation in university seminars promoting moderation",
        "ar": "قلة المشاركة في الندوات التوعوية والجامعية التي تعزز الوسطية"
    },
    {
        "id": "Q7",
        "en": "Tolerance of hate speech or ideological exclusion in public discussions",
        "ar": "التسامح مع عبارات الكراهية أو الإقصاء الفكري في النقاشات العامة"
    },
    {
        "id": "Q8",
        "en": "Reliance on anonymous unverified sources for ideological topics",
        "ar": "الاعتماد على مصادر مجهولة وغير موثوقة في فهم القضايا الفكرية"
    },
    {
        "id": "Q9",
        "en": "Belief that social or economic grievances justify radicalization",
        "ar": "الاعتقاد بأن التهميش أو الأزمات يبرران الانجرار وراء التطرف"
    },
    {
        "id": "Q10",
        "en": "Low awareness of psychological recruitment methods used by extremists",
        "ar": "ضعف الوعي بأساليب الاستقطاب الفكري التي تستخدمها التنظيمات المتطرفة"
    }
]

QUESTION_KEYS = [q["id"] for q in QUESTIONS]

SCALE_LABELS = {
    1: {"en": "1 - Low Risk / Strong Awareness", "ar": "1 - وعي مرتفع / مخاطر منخفضة"},
    2: {"en": "2 - Good Awareness", "ar": "2 - وعي جيد"},
    3: {"en": "3 - Moderate / Neutral", "ar": "3 - مستوى متوسط / محايد"},
    4: {"en": "4 - Noticeable Vulnerability", "ar": "4 - مؤشر قابلية ملحوظ"},
    5: {"en": "5 - High Vulnerability / Risk", "ar": "5 - مؤشر خطورة مرتفع"}
}

# Reference baseline parameters
INITIAL_BASELINE = [2.1, 2.4, 2.0, 3.6, 2.3, 3.2, 1.9, 3.8, 2.6, 2.2, 3.1, 1.7, 3.7, 2.5, 2.8]

if "baseline_pool" not in st.session_state:
    st.session_state.baseline_pool = list(INITIAL_BASELINE)

if "latest_scores" not in st.session_state:
    st.session_state.latest_scores = [3] * 10

# ==============================================================================
# 3. SIDEBAR CONFIGURATION
# ==============================================================================
with st.sidebar:
    st.markdown("### Interface Configuration")
    lang_mode = st.radio(
        "Interface Language / لغة الواجهة",
        ["Bilingual (English & العربية)", "English Only", "العربية فقط"],
        index=0
    )

    show_en = lang_mode in ["Bilingual (English & العربية)", "English Only"]
    show_ar = lang_mode in ["Bilingual (English & العربية)", "العربية فقط"]

    st.markdown("---")
    st.markdown("### Model Specifications")
    st.markdown(r"""
    - **Inference Standard:** Continuous Gaussian ($Z$-Score)
    - **Scale Range:** 1.00 to 5.00
    - **Classification Tiers:**
      - Low Risk: $\bar{X} < 2.50$
      - Moderate Risk: $2.50 \le \bar{X} \le 3.50$
      - High Risk: $\bar{X} > 3.50$
    """)

    st.markdown("---")
    if st.button("Reset Questionnaire Sliders", use_container_width=True):
        for idx in range(1, 11):
            st.session_state[f"slider_q{idx}"] = 3
        st.session_state.latest_scores = [3] * 10
        st.rerun()

# ==============================================================================
# 4. PORTAL HEADER
# ==============================================================================
header_markup = '<div class="portal-header">'
if show_en:
    header_markup += '<div class="portal-title-en">Youth Awareness & Extremism Risk Assessment Portal</div>'
if show_ar:
    header_markup += '<div class="portal-title-ar">البوابة الإحصائية لدراسة وعي الشباب حول مخاطر التطرف والإرهاب</div>'
header_markup += '<div class="portal-subtitle">Applied Statistics & Probability for Engineers | نظام التحليل الإحصائي والاحتمالي المباشر</div>'
header_markup += '</div>'
st.markdown(header_markup, unsafe_allow_html=True)

# ==============================================================================
# 5. SECTION 1: REDESIGNED SURVEY QUESTION CARDS
# ==============================================================================
if show_en and show_ar:
    sec1_heading = "Section 1: Assessment Survey | أولاً: استبانة تقييم الوعي الفكري"
    sec1_sub = "Evaluate the 10 dimensions below using the unified 1 to 5 sliders."
elif show_ar:
    sec1_heading = "أولاً: استبانة تقييم الوعي الفكري ومخاطر التطرف (10 محاور)"
    sec1_sub = "حدد درجة التقييم لكل محور عبر المؤشر المنزلق (1 = وعي مرتفع / أمان، 5 = قابلية مرتفعة للتأثر)."
else:
    sec1_heading = "Section 1: Assessment Survey (10 Extremism Awareness Items)"
    sec1_sub = "Evaluate the 10 dimensions below using the unified 1 to 5 sliders."

st.subheader(sec1_heading)
st.caption(sec1_sub)

col_left, col_right = st.columns(2)
form_inputs = []

with st.form("survey_form"):
    for idx, q_item in enumerate(QUESTIONS):
        target_col = col_left if (idx % 2 == 0) else col_right
        with target_col:
            # Clean dark container for each question
            card_html = '<div class="q-card">'
            card_html += f'<span class="q-badge">{q_item["id"]}</span>'
            if show_en:
                card_html += f'<div class="q-text-en">{q_item["en"]}</div>'
            if show_ar:
                card_html += f'<div class="q-text-ar">{q_item["ar"]}</div>'
            card_html += '</div>'
            st.markdown(card_html, unsafe_allow_html=True)

            val = st.slider(
                label=f"Slider for {q_item['id']}",
                min_value=1,
                max_value=5,
                value=int(st.session_state.latest_scores[idx]),
                step=1,
                key=f"slider_q{idx+1}",
                label_visibility="collapsed"
            )
            form_inputs.append(val)

            # Live scale label
            lbl_en = SCALE_LABELS[val]["en"]
            lbl_ar = SCALE_LABELS[val]["ar"]
            if show_en and show_ar:
                st.caption(f"Active Selection: {lbl_en} | {lbl_ar}")
            elif show_ar:
                st.caption(f"الخيار النشط: {lbl_ar}")
            else:
                st.caption(f"Active Selection: {lbl_en}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if show_en and show_ar:
        btn_label = "Execute Statistical & Probabilistic Analysis | تنفيذ التحليل الإحصائي والاحتمالي"
    elif show_ar:
        btn_label = "تنفيذ التحليل الإحصائي والاحتمالي المباشر"
    else:
        btn_label = "Execute Statistical & Probabilistic Analysis"

    submitted = st.form_submit_button(btn_label, use_container_width=True)

if submitted:
    st.session_state.latest_scores = form_inputs
    new_mean = float(np.mean(form_inputs))
    st.session_state.baseline_pool.append(new_mean)

# ==============================================================================
# 6. MATHEMATICAL ENGINE & MOMENTS
# ==============================================================================
scores = np.array(st.session_state.latest_scores, dtype=float)
n_q = len(scores)

# 1. Respondent Mean (X_bar)
X_bar = float(np.mean(scores))

# 2. Sample Variance (S^2) & Standard Deviation (S)
S2 = float(np.var(scores, ddof=1)) if n_q > 1 else 0.0
S = float(np.std(scores, ddof=1)) if n_q > 1 else 0.0

# 3. Population Parameters (mu, sigma)
base_arr = np.array(st.session_state.baseline_pool, dtype=float)
mu = float(np.mean(base_arr))
sigma = float(np.std(base_arr, ddof=1)) if len(base_arr) > 1 else 0.50
if sigma <= 0.001:
    sigma = 0.50

# 4. Standardized Z-Score
Z = float((X_bar - mu) / sigma)

# 5. Normal Cumulative & Exceedance Probabilities
prob_cdf = float(stats.norm.cdf(Z))
prob_sf = float(stats.norm.sf(Z))

# 6. Empirical Proportions
k_high = int(np.sum(scores >= 4))
p_empirical_high = float(k_high / n_q)

count_low = int(np.sum(scores <= 2))
count_mod = int(np.sum(scores == 3))
count_high = int(np.sum(scores >= 4))

p_low = float(count_low / n_q)
p_mod = float(count_mod / n_q)
p_high = float(count_high / n_q)

# ==============================================================================
# 7. SECTION 2: 5 UNIFIED KPI CARDS
# ==============================================================================
st.markdown("---")
if show_en and show_ar:
    sec2_title = "Section 2: Engineering Moments & Key Indicators | ثانياً: المؤشرات الإحصائية الرئيسية"
elif show_ar:
    sec2_title = "ثانياً: المؤشرات الإحصائية وعزوم المعاينة الرئيسية"
else:
    sec2_title = "Section 2: Quantitative Moments & Key Indicators"

st.subheader(sec2_title)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    t_en = "Respondent Mean" if show_en else ""
    t_ar = "المتوسط الحسابي" if show_ar else ""
    t_both = f"{t_en}<br>{t_ar}" if (show_en and show_ar) else (t_ar if show_ar else t_en)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{t_both}</div>
        <div class="kpi-value">{X_bar:.2f}</div>
        <div class="kpi-sub">Scale: [1.00, 5.00]</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    t_en = "Std Deviation (S)" if show_en else ""
    t_ar = "الانحراف المعياري" if show_ar else ""
    t_both = f"{t_en}<br>{t_ar}" if (show_en and show_ar) else (t_ar if show_ar else t_en)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{t_both}</div>
        <div class="kpi-value">{S:.2f}</div>
        <div class="kpi-sub">Variance S² = {S2:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    t_en = "Reference Mean (μ)" if show_en else ""
    t_ar = "متوسط العينة المرجعية" if show_ar else ""
    t_both = f"{t_en}<br>{t_ar}" if (show_en and show_ar) else (t_ar if show_ar else t_en)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{t_both}</div>
        <div class="kpi-value">{mu:.2f}</div>
        <div class="kpi-sub">σ = {sigma:.2f} (N={len(base_arr)})</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    z_col = "#ef4444" if Z > 1.0 else ("#f59e0b" if Z > 0 else "#10b981")
    t_en = "Standard Z-Score" if show_en else ""
    t_ar = "الدرجة المعيارية" if show_ar else ""
    t_both = f"{t_en}<br>{t_ar}" if (show_en and show_ar) else (t_ar if show_ar else t_en)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{t_both}</div>
        <div class="kpi-value" style="color: {z_col};">{Z:+.2f}</div>
        <div class="kpi-sub">Z = (X̄ - μ) / σ</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    t_en = "Exceedance P(Z > z)" if show_en else ""
    t_ar = "احتمالية تجاوز المعدل" if show_ar else ""
    t_both = f"{t_en}<br>{t_ar}" if (show_en and show_ar) else (t_ar if show_ar else t_en)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{t_both}</div>
        <div class="kpi-value">{prob_sf * 100:.1f}%</div>
        <div class="kpi-sub">Percentile: {prob_cdf * 100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Mathematical formulations
exp_title = (
    "Mathematical Derivations & Calculations | تفكيك العمليات الحسابية والمعادلات"
    if show_en and show_ar else
    ("تفكيك المعادلات الإحصائية والاحتمالية" if show_ar else "Mathematical Derivations & Calculations")
)
with st.expander(exp_title):
    st.latex(r"\bar{X} = \frac{1}{10}\sum_{i=1}^{10} X_i = \frac{" + f"{np.sum(scores):.0f}" + r"}{10} = " + f"{X_bar:.3f}")
    st.latex(r"S^2 = \frac{\sum_{i=1}^{10} (X_i - \bar{X})^2}{10 - 1} = " + f"{S2:.4f}" + r" \implies S = \sqrt{S^2} = " + f"{S:.4f}")
    st.latex(r"Z = \frac{\bar{X} - \mu}{\sigma} = \frac{" + f"{X_bar:.2f} - {mu:.2f}" + r"}{" + f"{sigma:.3f}" + r"} = " + f"{Z:+.4f}")
    st.latex(r"P(Z \le " + f"{Z:.2f}" + r") = \Phi(" + f"{Z:.2f}" + r") = " + f"{prob_cdf:.4f}" + r" \implies P(Z > " + f"{Z:.2f}" + r") = 1 - \Phi(" + f"{Z:.2f}" + r") = " + f"{prob_sf:.4f}")
    st.latex(r"P(X \ge 4) = \frac{k}{10} = \frac{" + f"{k_high}" + r"}{10} = " + f"{p_empirical_high:.2f}" + r" \quad (" + f"{p_empirical_high * 100:.1f}" + r"\%)")

# ==============================================================================
# 8. SECTION 3: 3 PERFECTLY ALIGNED, EQUAL-SIZE STATISTICAL CHARTS
# ==============================================================================
st.markdown("---")
if show_en and show_ar:
    sec3_title = "Section 3: Statistical Visualizations (Live Synchronization) | ثالثاً: الرسوم البيانية الإحصائية"
elif show_ar:
    sec3_title = "ثالثاً: الرسوم البيانية الإحصائية التفاعلية (تحديث مباشر مع كل استجابة)"
else:
    sec3_title = "Section 3: Symmetrical Statistical Visualizations"

st.subheader(sec3_title)

# Common Matplotlib styling parameters for dark-slate background
plt.style.use("dark_background")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial"],
    "axes.edgecolor": "#283548",
    "axes.linewidth": 1.0,
    "grid.color": "#222f44",
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})

chart_col1, chart_col2, chart_col3 = st.columns(3)

# ------------------------------------------------------------------------------
# Chart 1: Mean & Standard Deviation Profile (Bar Chart + SD Band)
# ------------------------------------------------------------------------------
with chart_col1:
    fig1, ax1 = plt.subplots(figsize=(5.5, 4.2), dpi=150)
    fig1.patch.set_facecolor("#162032")
    ax1.set_facecolor("#162032")

    colors_list = ["#10b981" if v <= 2 else ("#f59e0b" if v == 3 else "#ef4444") for v in scores]
    bar_plots = ax1.bar(QUESTION_KEYS, scores, color=colors_list, edgecolor="#0b1120", linewidth=0.8, width=0.62)

    # Standard Deviation Band around Mean
    sd_lower = max(1.0, X_bar - S)
    sd_upper = min(5.0, X_bar + S)
    ax1.axhspan(sd_lower, sd_upper, color="#38bdf8", alpha=0.16, label=f"SD Band (X̄ ± S: [{sd_lower:.2f}, {sd_upper:.2f}])")

    # Mean line
    ax1.axhline(X_bar, color="#38bdf8", linestyle="-", linewidth=2.0, label=f"Mean (X̄ = {X_bar:.2f})")
    ax1.axhline(mu, color="#94a3b8", linestyle=":", linewidth=1.2, label=f"Baseline (μ = {mu:.2f})")

    ax1.set_ylim(0, 5.8)
    ax1.set_ylabel("Likert Score (1.0 to 5.0)", fontsize=9, color="#f8fafc", fontweight="bold")
    ax1.set_title("Question Scores & SD Band", fontsize=10.5, fontweight="bold", color="#f8fafc", pad=12)
    ax1.tick_params(colors="#cbd5e1", labelsize=8)
    ax1.grid(axis="y")
    ax1.legend(loc="upper right", fontsize=7.2, facecolor="#111a2e", edgecolor="#283548", framealpha=0.95)

    for b in bar_plots:
        height = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2.0, height + 0.12, f"{int(height)}", ha="center", va="bottom", fontsize=8, color="#f8fafc", fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

# ------------------------------------------------------------------------------
# Chart 2: Z-Score & Standard Normal Distribution Curve N(0,1)
# ------------------------------------------------------------------------------
with chart_col2:
    fig2, ax2 = plt.subplots(figsize=(5.5, 4.2), dpi=150)
    fig2.patch.set_facecolor("#162032")
    ax2.set_facecolor("#162032")

    z_vals = np.linspace(-3.5, 3.5, 300)
    pdf_vals = stats.norm.pdf(z_vals)

    ax2.plot(z_vals, pdf_vals, color="#38bdf8", linewidth=2.2, label="Gaussian N(0, 1)")

    # Exceedance tail shading
    z_limit = max(-3.5, min(3.5, Z))
    shade_z = np.linspace(z_limit, 3.5, 150)
    ax2.fill_between(shade_z, stats.norm.pdf(shade_z), color="#ef4444", alpha=0.35, label=f"P(Z > {Z:.2f}) = {prob_sf*100:.1f}%")

    # Live Z line
    ax2.axvline(Z, color="#ef4444", linestyle="--", linewidth=2.0, label=f"Live Z = {Z:+.2f}")
    ax2.axvline(0, color="#64748b", linestyle=":", linewidth=1.0)

    # Annotation box for Z-score
    ax2.text(0.04, 0.92, f"Z = {Z:+.2f}\nPercentile = {prob_cdf*100:.1f}%", transform=ax2.transAxes, fontsize=8,
             verticalalignment="top", bbox=dict(boxstyle="round,pad=0.4", facecolor="#111a2e", edgecolor="#38bdf8", alpha=0.9))

    ax2.set_xlim(-3.5, 3.5)
    ax2.set_ylim(0, 0.44)
    ax2.set_xlabel("Standard Deviations (Z)", fontsize=9, color="#f8fafc", fontweight="bold")
    ax2.set_ylabel("Probability Density f(z)", fontsize=9, color="#f8fafc", fontweight="bold")
    ax2.set_title("Standard Normal Curve N(0,1)", fontsize=10.5, fontweight="bold", color="#f8fafc", pad=12)
    ax2.tick_params(colors="#cbd5e1", labelsize=8)
    ax2.grid(True)
    ax2.legend(loc="upper right", fontsize=7.2, facecolor="#111a2e", edgecolor="#283548", framealpha=0.95)

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

# ------------------------------------------------------------------------------
# Chart 3: Empirical Risk Probability Breakdown P(E) (Fixed 3-Tier Bar)
# ------------------------------------------------------------------------------
with chart_col3:
    fig3, ax3 = plt.subplots(figsize=(5.5, 4.2), dpi=150)
    fig3.patch.set_facecolor("#162032")
    ax3.set_facecolor("#162032")

    tier_labels = ["Low Risk [1-2]", "Moderate [3]", "High Risk [4-5]"]
    tier_probs = [p_low * 100, p_mod * 100, p_high * 100]
    tier_counts = [count_low, count_mod, count_high]
    tier_colors = ["#10b981", "#f59e0b", "#ef4444"]

    y_pos = np.arange(len(tier_labels))
    h_bars = ax3.barh(y_pos, tier_probs, color=tier_colors, edgecolor="#0b1120", linewidth=0.8, height=0.55)

    ax3.set_xlim(0, 105)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(tier_labels, fontsize=8.5, color="#f8fafc", fontweight="bold")
    ax3.set_xlabel("Empirical Probability Percentage (%)", fontsize=9, color="#f8fafc", fontweight="bold")
    ax3.set_title("Empirical Risk Proportions P(E)", fontsize=10.5, fontweight="bold", color="#f8fafc", pad=12)
    ax3.tick_params(colors="#cbd5e1", labelsize=8)
    ax3.grid(axis="x")

    for bar, pct, cnt in zip(h_bars, tier_probs, tier_counts):
        w = bar.get_width()
        ax3.text(w + 2.5, bar.get_y() + bar.get_height() / 2.0, f"P = {pct/100:.2f} ({cnt}/10)",
                 ha="left", va="center", fontsize=8, color="#f8fafc", fontweight="bold")

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

# ==============================================================================
# 9. SECTION 4: REDESIGNED BILINGUAL RECOMMENDATIONS PANEL
# ==============================================================================
st.markdown("---")
if show_en and show_ar:
    sec4_title = "Section 4: Strategic Prevention Directives | رابعاً: التقييم الإحصائي والتوصيات الوقائية"
elif show_ar:
    sec4_title = "رابعاً: التقييم الإحصائي والتوجيهات الوقائية لمكافحة التطرف"
else:
    sec4_title = "Section 4: Strategic Prevention Directives & Assessment"

st.subheader(sec4_title)

if X_bar < 2.50:
    card_tier = "rec-card-low"
    header_color = "#10b981"
    badge_en = f"CATEGORY 1: ADVANCED INTELLECTUAL IMMUNITY (SCORE: {X_bar:.2f})"
    badge_ar = f"المستوى الأول: وعي فكري متقدم ومناعة قوية ضد التطرف (الدرجة: {X_bar:.2f})"

    bullets_en = [
        "<strong>1. Statistical Diagnosis:</strong> Quantitatively demonstrates robust intellectual immunity and resilient analytical judgment against extremist propaganda and disinformation.",
        "<strong>2. Digital & Intellectual Habits:</strong> Maintain rigorous source verification and continue abstaining from unverified, emotionally charged online forums.",
        "<strong>3. University & Community Role:</strong> Engage as an active peer advocate in university workshops and civic initiatives to foster moderate discourse."
    ]

    bullets_ar = [
        "<strong>1. التشخيص الإحصائي:</strong> تشير الدرجة إلى وعي فكري مرتفع ومناعة قوية ضد خطابات التطرف والشائعات المضللة.",
        "<strong>2. السلوك الرقمي:</strong> الاستمرار في التحقق النقدي من المصادر وعدم التفاعل مع الصفحات المشبوهة أو السرديات الاستقطابية.",
        "<strong>3. الدور المجتمعي:</strong> المساهمة الإيجابية في نشر قيم الحوار والاعتدال والتفكير الموضوعي داخل البيئة الجامعية والمجتمعية."
    ]

elif X_bar <= 3.50:
    card_tier = "rec-card-mod"
    header_color = "#f59e0b"
    badge_en = f"CATEGORY 2: MODERATE VULNERABILITY REQUIRING REINFORCEMENT (SCORE: {X_bar:.2f})"
    badge_ar = f"المستوى الثاني: قابلية متوسطة تتطلب تعزيز التحصين المعرفي (الدرجة: {X_bar:.2f})"

    bullets_en = [
        "<strong>1. Statistical Diagnosis:</strong> Metrics reflect moderate vulnerability indicators, suggesting occasional susceptibility to emotional exploitation or unverified crisis narratives.",
        "<strong>2. Preventative Actions:</strong> Disengage from insular or anonymous ideological communication channels and verify news through authenticated institutional portals.",
        "<strong>3. University & Family Engagement:</strong> Participate regularly in collegiate dialogue circles and academic seminars designed to dismantle radical recruitment methodologies."
    ]

    bullets_ar = [
        "<strong>1. التشخيص الإحصائي:</strong> وجود مؤشرات متوسطة تستدعي رفع مستوى الحذر الفكري والوعي بطرق الاستقطاب الرقمي.",
        "<strong>2. التوعية الوقائية:</strong> تجنب المجموعات المغلقة أو مجهولة المصدر، والتثبت من الأخبار عبر القنوات الرسمية المعتمدة.",
        "<strong>3. الدور الأسري والجامعي:</strong> زيادة المشاركة في الندوات الفكرية والحوارات المفتوحة التي تعزز التفكير النقدي وتفكيك الأفكار المتطرفة."
    ]

else:
    card_tier = "rec-card-high"
    header_color = "#ef4444"
    badge_en = f"CATEGORY 3: ELEVATED RISK INDEX REQUIRING PROMPT INTERVENTION (SCORE: {X_bar:.2f})"
    badge_ar = f"المستوى الثالث: قابلية مرتفعة تستدعي تدخلاً توعوياً عاجلاً (الدرجة: {X_bar:.2f})"

    bullets_en = [
        "<strong>1. Statistical Diagnosis:</strong> Data captures elevated vulnerability, identifying ideological withdrawal, tolerance for radical justifications, and reliance on suspicious entities.",
        "<strong>2. Immediate Preventative Action:</strong> Cease participation in closed extremist groups immediately and reject manipulative propaganda exploiting socioeconomic grievances.",
        "<strong>3. Guidance & Institutional Support:</strong> Re-establish open communication with family mentors and university counselors, relying exclusively on recognized educational and national authorities."
    ]

    bullets_ar = [
        "<strong>1. التشخيص الإحصائي:</strong> تسجل الإجابات مؤشرات مرتفعة للقابلية الفكرية للتأثر بخطابات التشدد أو الانعزال المجتمعي.",
        "<strong>2. الإجراء الوقائي المباشر:</strong> الابتعاد الفوري عن المنصات والغرف الرقمية التي تبث الكراهية أو تستغل الأزمات للتحريض.",
        "<strong>3. الدعم الأسري والأكاديمي:</strong> تفعيل قنوات الحوار المباشر مع الأسرة والمرشدين الأكاديميين، والرجوع للمؤسسات الفكرية والوطنية الموثوقة لتصحيح المفاهيم."
    ]

# Construct 2-column recommendation layout
rec_markup = f'<div class="rec-card {card_tier}">'
rec_markup += f'<div class="rec-header" style="color: {header_color};">'
if show_en and show_ar:
    rec_markup += f'{badge_en} | {badge_ar}'
elif show_ar:
    rec_markup += f'{badge_ar}'
else:
    rec_markup += f'{badge_en}'
rec_markup += '</div>'

col_rec_en, col_rec_ar = st.columns(2)

if show_en and show_ar:
    with col_rec_en:
        st.markdown('<div class="rec-col-en"><strong>Institutional Directives (English):</strong><br>' + '<br>'.join(bullets_en) + '</div>', unsafe_allow_html=True)
    with col_rec_ar:
        st.markdown('<div class="rec-col-ar"><strong>التوجيهات الوقائية (العربية):</strong><br>' + '<br>'.join(bullets_ar) + '</div>', unsafe_allow_html=True)
elif show_ar:
    st.markdown('<div class="rec-col-ar">' + '<br>'.join(bullets_ar) + '</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="rec-col-en">' + '<br>'.join(bullets_en) + '</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 10. SYSTEM FOOTER
# ==============================================================================
st.markdown("""
<div style="border-top: 1px solid #1e293b; margin-top: 40px; padding: 20px 0; text-align: center; color: #64748b; font-size: 11.5px; line-height: 1.6;">
    Applied Statistics & Probability for Engineers | مساق الإحصاء والاحتمالات للمهندسين (2026)<br>
    Academic & Institutional Decision-Support System for Youth Awareness & Extremism Risk Modeling
</div>
""", unsafe_allow_html=True)
