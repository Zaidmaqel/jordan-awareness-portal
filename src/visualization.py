"""
JSSAA Data Visualization and Infographics Module.

Produces publication-grade, high-DPI figures and dashboards:
1. Multi-panel Executive Dashboard (outputs/jordan_awareness_dashboard.png, 2x2, 300 DPI)
2. Dimensional Radar Chart (outputs/dimension_radar_chart.png)
3. Demographic Boxplots (outputs/demographic_boxplots.png)
4. Perceived vs Actual Awareness Scatterplot (outputs/perceived_vs_actual_scatter.png)
5. PCA Scree Plot (outputs/pca_scree_plot.png)

Ensures robust Arabic typography using arabic_reshaper and python-bidi,
selecting native OS Arabic fonts (Segoe UI, Arial, Tahoma) to prevent tofu boxes.
"""

import os
import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

import arabic_reshaper
from bidi.algorithm import get_display

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

logger = logging.getLogger("JSSAA.visualization")

# ==========================================
# Font and Style Configuration
# ==========================================
# Configure matplotlib to prioritize Arabic-capable system fonts on Windows
plt.rcParams["font.sans-serif"] = [
    "Segoe UI",
    "Arial",
    "Tahoma",
    "Traditional Arabic",
    "Arabic Typesetting",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False  # Ensure minus signs render correctly
plt.rcParams["figure.autolayout"] = False

# Color Palette Constants
COLOR_LOW = "#D9534F"       # Muted Red / High Risk
COLOR_MODERATE = "#F0AD4E"  # Amber / Elevated Risk
COLOR_HIGH = "#5CB85C"      # Emerald Green / Stable
COLOR_PRIMARY = "#2C3E50"   # Dark Slate Blue
COLOR_ACCENT = "#3498DB"    # Vibrant Blue


def ar(text: str) -> str:
    """
    Helper for Arabic text rendering in Matplotlib using arabic_reshaper and python-bidi.
    Ensures correct cursive right-to-left rendering without reversed or boxed glyphs.
    In modern Matplotlib (>=3.8) with native HarfBuzz OpenType layout, passing text
    directly preserves perfect cursive Arabic without backwards double-reversal.
    """
    if not config.ARABIC_SUPPORT or not text:
        return text
    try:
        # Verify text can be shaped by arabic_reshaper / bidi
        _ = arabic_reshaper.reshape(str(text))
        _ = get_display(_)
        # In Matplotlib 3.11+ on Windows, native HarfBuzz shapes Arabic correctly.
        # Returning clean text prevents double-reversal (which produces backwards disconnected glyphs).
        return str(text)
    except Exception as e:
        logger.debug("Arabic reshaping failed for '%s': %s", text, e)
        return str(text)


class Visualizer:
    """
    Generates all charts, diagrams, and dashboards for the JSSAA study.
    """

    def __init__(self, output_dir: str = config.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_dashboard(
        self,
        df: pd.DataFrame,
        spearman_corr: pd.DataFrame,
        spearman_pval: pd.DataFrame,
        system_status: Dict[str, Any],
        filename: str = "jordan_awareness_dashboard.png",
    ) -> str:
        """
        Creates the main 2x2 publication dashboard (300 DPI, figsize=(20, 16)):
        1) Bar chart of mean per question with error bars, colored by band, threshold lines.
        2) Spearman correlation heatmap with lower-triangle mask and significance stars.
        3) Histogram + KDE of overall scores with mean and band boundary lines.
        4) Donut chart of Low / Moderate / High band distribution with counts & %.
        """
        out_path = os.path.join(self.output_dir, filename)
        fig, axes = plt.subplots(2, 2, figsize=(20, 16), dpi=300)
        plt.subplots_adjust(hspace=0.28, wspace=0.22, top=0.93, bottom=0.06, left=0.07, right=0.95)

        # Main Super Title
        super_title = f"{ar('لوحة مؤشرات الوعي الأمني والمجتمعي - الأردن')} | JSSAA National Awareness Dashboard"
        fig.suptitle(super_title, fontsize=18, fontweight="bold", color=COLOR_PRIMARY, y=0.97)

        # -------------------------------------------------------------
        # PANEL 1 (Top-Left): Question Item Means & Confidence Intervals
        # -------------------------------------------------------------
        ax1 = axes[0, 0]
        likert_items = [q["short_name"] for q in config.QUESTION_MAP.values() if q["short_name"] in df.columns]
        means = [df[col].mean() for col in likert_items]
        # Calculate 95% CI error bar half-width
        n = len(df)
        sems = [1.96 * (df[col].std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0 for col in likert_items]

        # Determine bar colors by band thresholds
        bar_colors = [
            COLOR_LOW if m <= config.LOW_MAX else (COLOR_MODERATE if m <= config.MODERATE_MAX else COLOR_HIGH)
            for m in means
        ]

        x_pos = np.arange(len(likert_items))
        bars = ax1.bar(x_pos, means, yerr=sems, capsize=3, color=bar_colors, edgecolor="black", linewidth=0.6, alpha=0.9)

        # Value labels above bars
        for b, m in zip(bars, means):
            ax1.text(
                b.get_x() + b.get_width() / 2.0,
                m + 0.12,
                f"{m:.2f}",
                ha="center",
                va="bottom",
                fontsize=7.5,
                fontweight="bold",
                rotation=90,
            )

        # Threshold reference lines
        ax1.axhline(config.LOW_MAX, color=COLOR_LOW, linestyle="--", linewidth=1.2, label=f"Low Band Limit ({config.LOW_MAX})")
        ax1.axhline(config.MODERATE_MAX, color=COLOR_HIGH, linestyle="--", linewidth=1.2, label=f"High Band Limit ({config.MODERATE_MAX})")
        ax1.axhline(config.TARGET_SCORE, color="purple", linestyle=":", linewidth=1.2, label=f"Target ({config.TARGET_SCORE})")

        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(likert_items, rotation=45, ha="right", fontsize=8)
        ax1.set_ylim(1.0, 5.5)
        ax1.set_ylabel(ar("متوسط الدرجة (1 إلى 5)") + " | Mean Likert Score", fontsize=10, fontweight="bold")
        ax1.set_title(
            f"1. {ar('متوسط درجات الأسئلة وفترات الثقة')} | Item Mean Scores & 95% CIs",
            fontsize=12,
            fontweight="bold",
            pad=10,
        )
        ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)
        ax1.grid(axis="y", linestyle=":", alpha=0.6)

        # -------------------------------------------------------------
        # PANEL 2 (Top-Right): Spearman Correlation Heatmap
        # -------------------------------------------------------------
        ax2 = axes[0, 1]
        dim_cols = [f"dim_{d}" for d in config.DIMENSIONS if f"dim_{d}" in df.columns]
        if "overall_awareness_score" in df.columns:
            dim_cols.append("overall_awareness_score")

        sub_corr, sub_pval, _, _ = [
            x for x in [
                spearman_corr.loc[dim_cols, dim_cols] if set(dim_cols).issubset(spearman_corr.index) else None
            ]
        ][0], None, None, None

        # Recompute cleanly for dimension columns
        n_dim = len(dim_cols)
        dim_corr = np.zeros((n_dim, n_dim))
        dim_annot = np.empty((n_dim, n_dim), dtype=object)

        from scipy import stats
        for i in range(n_dim):
            for j in range(n_dim):
                if i == j:
                    dim_corr[i, j] = 1.0
                    dim_annot[i, j] = "1.00"
                else:
                    r, p = stats.spearmanr(df[dim_cols[i]], df[dim_cols[j]])
                    dim_corr[i, j] = r
                    star = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
                    dim_annot[i, j] = f"{r:.2f}{star}"

        # Mask upper triangle
        mask = np.triu(np.ones_like(dim_corr, dtype=bool), k=1)

        # Clean display labels for axes
        clean_labels = [
            c.replace("dim_", "").replace("_", " ").title() if c != "overall_awareness_score" else "Overall Awareness"
            for c in dim_cols
        ]

        sns.heatmap(
            dim_corr,
            mask=mask,
            annot=dim_annot,
            fmt="",
            cmap="coolwarm",
            vmin=-0.3,
            vmax=0.8,
            center=0.0,
            cbar_kws={"label": "Spearman Rho (ρ)", "shrink": 0.8},
            ax=ax2,
            xticklabels=clean_labels,
            yticklabels=clean_labels,
            linewidths=0.5,
            linecolor="white",
        )
        ax2.set_title(
            f"2. {ar('مصفوفة ارتباط سبيرمان للأبعاد')} | Spearman Dimension Correlations (*p<0.05, **p<0.01, ***p<0.001)",
            fontsize=12,
            fontweight="bold",
            pad=10,
        )
        ax2.tick_params(axis="x", rotation=35, labelsize=8.5)
        ax2.tick_params(axis="y", rotation=0, labelsize=8.5)

        # -------------------------------------------------------------
        # PANEL 3 (Bottom-Left): Overall Awareness Distribution & KDE
        # -------------------------------------------------------------
        ax3 = axes[1, 0]
        scores = df["overall_awareness_score"].dropna()

        # Background color bands
        ax3.axvspan(1.0, config.LOW_MAX, color=COLOR_LOW, alpha=0.15, label=f"Low Band (<= {config.LOW_MAX})")
        ax3.axvspan(config.LOW_MAX, config.MODERATE_MAX, color=COLOR_MODERATE, alpha=0.15, label=f"Moderate Band ({config.LOW_MAX}-{config.MODERATE_MAX})")
        ax3.axvspan(config.MODERATE_MAX, 5.0, color=COLOR_HIGH, alpha=0.15, label=f"High Band (>= {config.MODERATE_MAX})")

        # Histogram + KDE
        sns.histplot(scores, kde=True, bins=16, color=COLOR_PRIMARY, stat="density", edgecolor="white", ax=ax3)

        # Mean vertical line
        score_mean = scores.mean()
        score_sd = scores.std(ddof=1)
        ax3.axvline(score_mean, color="black", linestyle="-", linewidth=2.0, label=f"Mean: {score_mean:.2f}")

        ax3.set_xlim(1.0, 5.0)
        ax3.set_xlabel(ar("درجة الوعي الكلي (من 5)") + " | Overall Awareness Score", fontsize=10, fontweight="bold")
        ax3.set_ylabel(ar("الكثافة الإحصائية") + " | Density", fontsize=10, fontweight="bold")
        ax3.set_title(
            f"3. {ar('توزيع درجات الوعي الكلي')} | Overall Awareness Score Distribution & KDE",
            fontsize=12,
            fontweight="bold",
            pad=10,
        )

        # Statistical summary text box
        stats_box = (
            f"n = {len(scores)}\n"
            f"Mean = {score_mean:.2f}\n"
            f"SD = {score_sd:.2f}\n"
            f"Median = {scores.median():.2f}\n"
            f"Status = {system_status['final_severity']}"
        )
        ax3.text(
            0.04,
            0.93,
            stats_box,
            transform=ax3.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9),
        )
        ax3.legend(loc="upper right", fontsize=8, framealpha=0.9)
        ax3.grid(axis="y", linestyle=":", alpha=0.6)

        # -------------------------------------------------------------
        # PANEL 4 (Bottom-Right): Donut Chart of Awareness Risk Bands
        # -------------------------------------------------------------
        ax4 = axes[1, 1]
        band_counts = df["awareness_band"].value_counts()
        band_order = ["Low", "Moderate", "High"]
        counts = [band_counts.get(b, 0) for b in band_order]
        colors = [COLOR_LOW, COLOR_MODERATE, COLOR_HIGH]
        labels = [
            f"{ar('منخفض')} (Low)\n{counts[0]} ({counts[0]/len(df)*100:.1f}%)",
            f"{ar('متوسط')} (Moderate)\n{counts[1]} ({counts[1]/len(df)*100:.1f}%)",
            f"{ar('مرتفع')} (High)\n{counts[2]} ({counts[2]/len(df)*100:.1f}%)",
        ]

        wedges, texts, autotexts = ax4.pie(
            counts,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            pctdistance=0.75,
            startangle=140,
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
            textprops=dict(fontsize=9.5, fontweight="bold"),
        )
        for at in autotexts:
            at.set_color("black")

        # Center circle text
        center_text = f"{ar('إجمالي العينة')}\nTotal Sample\nn = {len(df)}"
        ax4.text(0, 0, center_text, ha="center", va="center", fontsize=10, fontweight="bold", color=COLOR_PRIMARY)
        ax4.set_title(
            f"4. {ar('تصنيف مستويات الوعي')} | Awareness Band Distribution (Risk Categories)",
            fontsize=12,
            fontweight="bold",
            pad=10,
        )

        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved 2x2 awareness dashboard at: %s", out_path)
        return out_path

    def generate_radar_chart(
        self, df: pd.DataFrame, filename: str = "dimension_radar_chart.png"
    ) -> str:
        """
        Creates a 5-dimension radar / spider chart of awareness means against targets.
        """
        out_path = os.path.join(self.output_dir, filename)
        dims = config.DIMENSIONS
        dim_means = [df[f"dim_{d}"].mean() for d in dims if f"dim_{d}" in df.columns]

        # Arabic/English labels for radar axes
        labels = [
            f"{ar('التعرض الإعلامي')}\nMedia Exposure",
            f"{ar('كشف الشائعات')}\nRumor Detection",
            f"{ar('التهديدات الرقمية')}\nDigital Threats",
            f"{ar('الثقة بالرسمي')}\nOfficial Trust",
            f"{ar('سلوك التحقق')}\nVerification",
        ]

        angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
        dim_means += dim_means[:1]
        angles += angles[:1]
        labels_circ = labels + [labels[0]]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), dpi=300)

        # Plot sample mean polygon
        ax.plot(angles, dim_means, color=COLOR_PRIMARY, linewidth=2.5, linestyle="solid", label=f"Sample Mean ({np.mean(dim_means[:-1]):.2f})")
        ax.fill(angles, dim_means, color=COLOR_ACCENT, alpha=0.35)

        # Benchmark reference lines
        target_line = [config.TARGET_SCORE] * len(angles)
        low_line = [config.LOW_MAX] * len(angles)
        ax.plot(angles, target_line, color="purple", linewidth=1.5, linestyle="--", label=f"Target ({config.TARGET_SCORE})")
        ax.plot(angles, low_line, color=COLOR_LOW, linewidth=1.5, linestyle=":", label=f"Low Threshold ({config.LOW_MAX})")

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)
        ax.set_ylim(1.0, 5.0)
        ax.set_title(
            f"{ar('مخطط أبعاد الوعي الخماسي')} | Five-Dimension Awareness Radar Profile",
            fontsize=13,
            fontweight="bold",
            pad=20,
            color=COLOR_PRIMARY,
        )
        ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), fontsize=9)

        fig.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved radar chart at: %s", out_path)
        return out_path

    def generate_demographic_boxplots(
        self, df: pd.DataFrame, filename: str = "demographic_boxplots.png"
    ) -> str:
        """
        Creates 1x2 subplots with boxplots for Gender and Age Group.
        """
        out_path = os.path.join(self.output_dir, filename)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=300)

        # Subplot 1: Gender
        if "gender" in df.columns:
            sns.boxplot(x="gender", y="overall_awareness_score", hue="gender", data=df, palette="Blues", legend=False, ax=ax1, width=0.45)
            sns.stripplot(x="gender", y="overall_awareness_score", data=df, color="black", alpha=0.3, jitter=0.2, size=4, ax=ax1)
            # Reshape x-ticks for Arabic
            raw_labels = [str(item.get_text()) for item in ax1.get_xticklabels()]
            ax1.set_xticks(range(len(raw_labels)))
            ax1.set_xticklabels([ar(t) for t in raw_labels], fontsize=10)
            ax1.set_xlabel(ar("الجنس") + " | Gender", fontsize=11, fontweight="bold")
            ax1.set_ylabel(ar("درجة الوعي الكلي") + " | Overall Score", fontsize=11, fontweight="bold")
            ax1.set_title(f"A. {ar('الوعي حسب الجنس')} | Awareness by Gender", fontsize=12, fontweight="bold")
            ax1.grid(axis="y", linestyle=":", alpha=0.6)

        # Subplot 2: Age Group
        if "age_group" in df.columns:
            sns.boxplot(x="age_group", y="overall_awareness_score", hue="age_group", data=df, palette="YlGnBu", legend=False, ax=ax2, width=0.55)
            sns.stripplot(x="age_group", y="overall_awareness_score", data=df, color="black", alpha=0.3, jitter=0.2, size=4, ax=ax2)
            raw_labels = [str(item.get_text()) for item in ax2.get_xticklabels()]
            ax2.set_xticks(range(len(raw_labels)))
            ax2.set_xticklabels([ar(t) for t in raw_labels], fontsize=10)
            ax2.set_xlabel(ar("الفئة العمرية") + " | Age Group", fontsize=11, fontweight="bold")
            ax2.set_ylabel(ar("درجة الوعي الكلي") + " | Overall Score", fontsize=11, fontweight="bold")
            ax2.set_title(f"B. {ar('الوعي حسب الفئة العمرية')} | Awareness by Age Cohort", fontsize=12, fontweight="bold")
            ax2.grid(axis="y", linestyle=":", alpha=0.6)

        fig.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved demographic boxplots at: %s", out_path)
        return out_path

    def generate_perceived_vs_actual_scatter(
        self, df: pd.DataFrame, filename: str = "perceived_vs_actual_scatter.png"
    ) -> str:
        """
        Scatterplot of Perceived Overall Awareness vs Actual Knowledge Score with regression trendline.
        """
        out_path = os.path.join(self.output_dir, filename)
        if "actual_knowledge_pct" not in df.columns or "overall_awareness_score" not in df.columns:
            return ""

        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        x = df["actual_knowledge_pct"]
        y = df["overall_awareness_score"]

        # Regression scatter
        sns.regplot(
            x=x,
            y=y,
            ax=ax,
            scatter_kws={"alpha": 0.5, "color": COLOR_PRIMARY, "s": 35},
            line_kws={"color": "crimson", "linewidth": 2.0, "label": "Linear Fit Trendline"},
        )

        # Quadrant dividing lines (e.g. 60% actual, 3.0 perceived)
        ax.axvline(60.0, color="gray", linestyle="--", alpha=0.6)
        ax.axhline(3.0, color="gray", linestyle="--", alpha=0.6)

        # Quadrant labels
        ax.text(15, 4.4, "High Confidence / Low Actual Knowledge\n[OVERCONFIDENCE HAZARD]", color="darkred", fontsize=8.5, fontweight="bold")
        ax.text(65, 4.4, "High Confidence / High Knowledge\n[RESILIENT ADVOCATES]", color="darkgreen", fontsize=8.5, fontweight="bold")
        ax.text(15, 1.8, "Low Confidence / Low Knowledge\n[AWARENESS DEFICIT]", color="gray", fontsize=8.5, fontweight="bold")
        ax.text(65, 1.8, "Low Confidence / High Knowledge\n[PRUDENT SKEPTICS]", color="navy", fontsize=8.5, fontweight="bold")

        ax.set_xlabel(ar("نسبة إجابات المعرفة الموضوعية الصحيحة (%)") + " | Actual Knowledge Score (% Correct)", fontsize=11, fontweight="bold")
        ax.set_ylabel(ar("درجة الوعي الذاتي المدرك (1-5)") + " | Perceived Overall Awareness (1-5)", fontsize=11, fontweight="bold")
        ax.set_title(
            f"{ar('الوعي المدرك مقابل المعرفة الفعلية')} | Perceived Awareness vs. Actual Knowledge Score",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color=COLOR_PRIMARY,
        )
        ax.set_xlim(-5, 105)
        ax.set_ylim(0.8, 5.2)
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, linestyle=":", alpha=0.6)

        fig.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved perceived-vs-actual scatter at: %s", out_path)
        return out_path

    def generate_pca_scree_plot(
        self, pca_data: Dict[str, Any], filename: str = "pca_scree_plot.png"
    ) -> str:
        """
        Creates PCA Scree Plot showing Eigenvalues and Cumulative Explained Variance.
        """
        out_path = os.path.join(self.output_dir, filename)
        if "eigenvalues" not in pca_data:
            return ""

        eigenvals = pca_data["eigenvalues"]
        exp_var = [v * 100.0 for v in pca_data["explained_variance_ratio"]]
        cum_var = [v * 100.0 for v in pca_data["cumulative_variance_ratio"]]
        comps = np.arange(1, len(eigenvals) + 1)

        fig, ax1 = plt.subplots(figsize=(10, 6), dpi=300)

        # Bar chart: Explained variance per component
        bars = ax1.bar(comps, exp_var, color=COLOR_ACCENT, alpha=0.75, edgecolor="black", linewidth=0.5, label="Individual % Variance")
        ax1.set_xlabel("Principal Component", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Explained Variance Ratio (%)", fontsize=11, fontweight="bold", color=COLOR_ACCENT)
        ax1.set_xticks(comps)
        ax1.set_ylim(0, max(exp_var) * 1.3)

        # Line chart: Cumulative variance on secondary y-axis
        ax2 = ax1.twinx()
        ax2.plot(comps, cum_var, color="crimson", marker="o", linewidth=2.0, label="Cumulative % Variance")
        ax2.axhline(70.0, color="green", linestyle="--", linewidth=1.2, label="70% Variance Threshold")
        ax2.set_ylabel("Cumulative Explained Variance (%)", fontsize=11, fontweight="bold", color="crimson")
        ax2.set_ylim(0, 105)

        # Title
        plt.title(
            f"{ar('مخطط تباين المركبات الرئيسية (PCA)')} | PCA Scree & Cumulative Variance Plot",
            fontsize=13,
            fontweight="bold",
            pad=15,
            color=COLOR_PRIMARY,
        )

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="center right", fontsize=9)
        ax1.grid(axis="x", linestyle=":", alpha=0.5)

        fig.tight_layout()
        fig.savefig(out_path, dpi=300)
        plt.close(fig)
        logger.info("Saved PCA scree plot at: %s", out_path)
        return out_path
