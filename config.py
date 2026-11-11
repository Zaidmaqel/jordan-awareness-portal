"""
JSSAA (Jordan Social & Security Awareness Analysis)
Configuration Module.

Contains all survey mappings, statistical thresholds, demographic categories,
knowledge items, and global settings. Nothing is hardcoded elsewhere.
"""

from typing import Dict, List, Tuple, Any

# ==========================================
# File Paths & I/O Settings
# ==========================================
INPUT_FILE: str = "data/survey_responses.xlsx"
SHEET_NAME: Any = 0
OUTPUT_DIR: str = "outputs"

# ==========================================
# Statistical & Likert Thresholds
# ==========================================
LIKERT_MIN: int = 1
LIKERT_MAX: int = 5
INCLUDE_EXPOSURE_IN_SCORE: bool = False

Z_THRESHOLD: float = 2.5
IQR_MULTIPLIER: float = 1.5
ALPHA: float = 0.05
MIN_GROUP_SIZE: int = 5
MIN_SAMPLE_SIZE_WARNING: int = 30
MAX_MISSING_RATIO: float = 0.20

# Awareness Band Thresholds
LOW_MAX: float = 2.33
MODERATE_MAX: float = 3.66
TARGET_SCORE: float = 4.0
LOW_BAND_ESCALATION_PCT: float = 30.0

# Execution Flags
ARABIC_SUPPORT: bool = True
RUN_PCA: bool = True
RUN_SENSITIVITY: bool = True

# Completion time in seconds (None for Google Forms without duration tracking)
MIN_COMPLETION_SECONDS: Any = None

# Timestamp column variations in Google Forms
TIMESTAMP_COLUMNS: List[str] = ["Timestamp", "الطابع الزمني"]

# ==========================================
# Core Dimensions
# ==========================================
DIMENSIONS: List[str] = [
    "media_exposure",
    "rumor_detection",
    "digital_threat_awareness",
    "official_source_trust",
    "verification_behavior",
]

# Awareness dimensions excluding context variable media_exposure
AWARENESS_DIMENSIONS: List[str] = [
    "rumor_detection",
    "digital_threat_awareness",
    "official_source_trust",
    "verification_behavior",
]

# ==========================================
# Question Mapping (Exact Arabic Google Form Headers)
# ==========================================
QUESTION_MAP: Dict[str, Dict[str, Any]] = {
    # media_exposure (context variable)
    "أتابع الأخبار عبر مواقع التواصل الاجتماعي عدة مرات يومياً": {
        "short_name": "ME1_news_freq",
        "dimension": "media_exposure",
        "reverse": False,
    },
    "مواقع التواصل الاجتماعي هي مصدري الرئيسي للأخبار": {
        "short_name": "ME2_main_source",
        "dimension": "media_exposure",
        "reverse": False,
    },
    "أقضي وقتاً طويلاً يومياً في تصفح المحتوى الإخباري": {
        "short_name": "ME3_time_spent",
        "dimension": "media_exposure",
        "reverse": False,
    },
    "تصلني الأخبار والرسائل المتداولة عبر مجموعات واتساب وتليجرام باستمرار": {
        "short_name": "ME4_groups",
        "dimension": "media_exposure",
        "reverse": False,
    },

    # rumor_detection
    "أستطيع التمييز بين الخبر الصحيح والخبر المضلل": {
        "short_name": "RD1_distinguish",
        "dimension": "rumor_detection",
        "reverse": False,
    },
    "أنتبه إلى مصدر الخبر وتاريخه قبل أن أصدقه": {
        "short_name": "RD2_check_source",
        "dimension": "rumor_detection",
        "reverse": False,
    },
    "أعرف علامات الصور أو الفيديوهات المعدلة أو المنشورة خارج سياقها": {
        "short_name": "RD3_fake_media",
        "dimension": "rumor_detection",
        "reverse": False,
    },
    "أصدق الخبر إذا شاركه عدد كبير من الناس": {
        "short_name": "RD4_crowd_belief",
        "dimension": "rumor_detection",
        "reverse": True,
    },
    "أجد صعوبة في معرفة إن كان الخبر الذي أقرأه صحيحاً أم لا": {
        "short_name": "RD5_difficulty",
        "dimension": "rumor_detection",
        "reverse": True,
    },

    # digital_threat_awareness
    "أعرف كيف أميز رسائل الاحتيال والتصيد الإلكتروني": {
        "short_name": "DT1_phishing",
        "dimension": "digital_threat_awareness",
        "reverse": False,
    },
    "أستخدم كلمات مرور قوية ومختلفة لحساباتي المهمة": {
        "short_name": "DT2_passwords",
        "dimension": "digital_threat_awareness",
        "reverse": False,
    },
    "أفعّل التحقق بخطوتين على حساباتي الرئيسية": {
        "short_name": "DT3_2fa",
        "dimension": "digital_threat_awareness",
        "reverse": False,
    },
    "لا أشارك رموز التحقق أو بيانات بطاقتي أو محفظتي الإلكترونية مع أي شخص": {
        "short_name": "DT4_no_sharing",
        "dimension": "digital_threat_awareness",
        "reverse": False,
    },
    "لا أرى خطراً كبيراً في الضغط على روابط تصلني من أرقام أو حسابات لا أعرفها": {
        "short_name": "DT5_risky_links",
        "dimension": "digital_threat_awareness",
        "reverse": True,
    },

    # official_source_trust
    "أثق بالمعلومات التي تصدر عن الجهات الرسمية الأردنية": {
        "short_name": "OT1_trust",
        "dimension": "official_source_trust",
        "reverse": False,
    },
    "أعتمد على القنوات الرسمية للتأكد من الأخبار المهمة": {
        "short_name": "OT2_use_official",
        "dimension": "official_source_trust",
        "reverse": False,
    },
    "أرى أن الجهات الرسمية توضح المعلومات للناس بسرعة ووضوح": {
        "short_name": "OT3_clarity",
        "dimension": "official_source_trust",
        "reverse": False,
    },
    "لا أثق بأي معلومة تصدر عن جهة رسمية مهما كانت": {
        "short_name": "OT4_distrust",
        "dimension": "official_source_trust",
        "reverse": True,
    },

    # verification_behavior
    "أتحقق من صحة الخبر من مصدر آخر قبل مشاركته": {
        "short_name": "VB1_cross_check",
        "dimension": "verification_behavior",
        "reverse": False,
    },
    "أستخدم مواقع تدقيق المعلومات (مثل مسبار وأكيد) عند الشك في خبر": {
        "short_name": "VB2_factcheck_sites",
        "dimension": "verification_behavior",
        "reverse": False,
    },
    "أمتنع عن مشاركة الخبر إذا لم أتأكد من صحته": {
        "short_name": "VB3_hold_share",
        "dimension": "verification_behavior",
        "reverse": False,
    },
    "أنبّه من حولي عندما ينشرون معلومة غير صحيحة": {
        "short_name": "VB4_correct_others",
        "dimension": "verification_behavior",
        "reverse": False,
    },
    "أشارك الأخبار المثيرة فوراً دون التأكد منها": {
        "short_name": "VB5_impulsive_share",
        "dimension": "verification_behavior",
        "reverse": True,
    },
}

# Number of items required for straightline variance check (default: all 23 items)
STRAIGHTLINE_MIN_ITEMS: int = len(QUESTION_MAP)

# ==========================================
# Demographic Columns Mapping & Categories
# ==========================================
DEMOGRAPHIC_COLUMNS: Dict[str, str] = {
    "الجنس": "gender",
    "الفئة العمرية": "age_group",
    "المستوى التعليمي": "education_level",
    "مجال التخصص أو العمل": "major",
    "محافظة السكن": "governorate",
    "ساعات استخدام السوشال ميديا يومياً": "social_media_hours",
}

DEMOGRAPHIC_OPTIONS: Dict[str, List[str]] = {
    "gender": ["ذكر", "أنثى"],
    "age_group": ["18–24", "25–34", "35–44", "45 فأكثر"],
    "education_level": ["ثانوية فأقل", "دبلوم", "بكالوريوس", "دراسات عليا"],
    "major": ["علمي وطبي", "هندسي وتقني", "إنساني واجتماعي", "إداري واقتصادي", "أخرى"],
    "governorate": [
        "عمّان", "إربد", "الزرقاء", "البلقاء", "مأدبا",
        "الكرك", "الطفيلة", "معان", "العقبة", "جرش",
        "عجلون", "المفرق"
    ],
    "social_media_hours": ["أقل من ساعة", "1–3 ساعات", "3–5 ساعات", "أكثر من 5 ساعات"],
}

# Ordered categories for ordinal statistical analyses
ORDERED_CATEGORIES: Dict[str, List[str]] = {
    "age_group": ["18–24", "25–34", "35–44", "45 فأكثر"],
    "education_level": ["ثانوية فأقل", "دبلوم", "بكالوريوس", "دراسات عليا"],
    "social_media_hours": ["أقل من ساعة", "1–3 ساعات", "3–5 ساعات", "أكثر من 5 ساعات"],
}

# ==========================================
# Objective Knowledge Questions (Actual Awareness)
# ==========================================
KNOWLEDGE_QUESTIONS: Dict[str, Dict[str, str]] = {
    "إرسال رمز التحقق (OTP) لشخص يدّعي أنه من البنك آمن إذا كان يطلبه لإلغاء عملية مشبوهة": {
        "short_name": "K1_otp",
        "correct": "خطأ",
    },
    "كثرة مشاركة الخبر على واتساب دليل على صحته": {
        "short_name": "K2_shares",
        "correct": "خطأ",
    },
    "استخدام كلمة المرور نفسها في عدة حسابات يزيد خطر الاختراق": {
        "short_name": "K3_password_reuse",
        "correct": "صح",
    },
    "قد يكون الفيديو المتداول قديماً أو من حدث آخر ويُنشر على أنه حدث جديد": {
        "short_name": "K4_old_video",
        "correct": "صح",
    },
    "الرابط الذي يبدو احترافياً لا يمكن أن يكون موقع احتيال": {
        "short_name": "K5_pro_link",
        "correct": "خطأ",
    },
}

# Knowledge answer options allowed
KNOWLEDGE_OPTIONS: List[str] = ["صح", "خطأ", "لا أعرف"]

# ==========================================
# Inconsistency Pairs for Quality Auditing
# ==========================================
CONSISTENCY_PAIRS: List[Tuple[str, str]] = [
    ("RD1_distinguish", "RD5_difficulty"),
    ("RD2_check_source", "RD4_crowd_belief"),
    ("OT1_trust", "OT4_distrust"),
    ("VB3_hold_share", "VB5_impulsive_share"),
]
# Inconsistency threshold: after reverse coding, absolute difference >= 3 indicates contradiction.
CONSISTENCY_DIFF_THRESHOLD: float = 3.0

