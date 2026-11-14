"""
JSSRA Configuration Module.
Course: Statistics & Data Analysis (University Project, Jordan)
Project: Measuring Youth Vulnerability to Extremism & Community Risk in Jordan: A Statistical Analysis
(قياس قابلية الشباب للتطرف والمخاطر المجتمعية في الأردن: تحليل إحصائي)

Contains all survey mappings, statistical thresholds, design tokens, texts,
and academic framing disclaimers. Nothing is hardcoded elsewhere.
"""

from typing import Dict, List, Tuple, Any

# ==========================================
# 1. Project Metadata & Framing
# ==========================================
PROJECT_TITLE_EN = "Measuring Youth Vulnerability to Extremism & Community Risk in Jordan: A Statistical Analysis"
PROJECT_TITLE_AR = "قياس قابلية الشباب للتطرف والمخاطر المجتمعية في الأردن: تحليل إحصائي"
PROJECT_SHORT = "JSSRA"
ACADEMIC_COURSE = "Statistics & Data Analysis (جامعة أردنية)"
TEAM_MEMBERS = [
    {"role": "Member 1", "name": "زيد مهيرات (Zaid)", "topic": "Step 1: Data Collection & Sampling"},
    {"role": "Member 2", "name": "أحمد الخالد (Ahmad)", "topic": "Step 2: Descriptive Statistics & Variance"},
    {"role": "Member 3", "name": "سارة القضاة (Sara)", "topic": "Step 3: Z-scores, Normal Curve & Correlation"},
    {"role": "Member 4", "name": "عمر المجالي (Omar)", "topic": "Step 4: Strategic Results & Recommendations"},
]

# Strict academic framing & ethical disclaimer
FRAMING_DISCLAIMER_EN = (
    "ACADEMIC & ETHICAL NOTICE: The generated index represents an awareness and statistical risk-factor "
    "indicator, NOT a psychological diagnosis and NOT a security screening. It never labels any respondent "
    "an extremist or terrorist. All responses are 100% anonymous; no names, phone numbers, emails, IPs, or "
    "locations are ever collected. Outliers represent anonymous statistical deviations only."
)

FRAMING_DISCLAIMER_AR = (
    "إخلاء مسؤولية أكاديمي وأخلاقي: النتيجة المستخرجة تمثل مؤشراً توعوياً وإحصائياً لعوامل الخطر والوقاية، "
    "وليست تشخيصاً نفسياً ولا فحصاً أمنياً، ولا تصنف أي شخص مطلقاً كمتطرف أو إرهابي. الاستبانة مجهولة الهوية بالكامل "
    "(Anonymous)؛ لا نجمع أسماء أو هواتف أو بريداً إلكترونياً أو عناوين IP أو مواقع جغرافية. النقاط الشاذة "
    "تمثل انحرافاً إحصائياً مجهولاً فقط لأغراض تدقيق جودة البيانات."
)

# Admin password for data management / reset
ADMIN_PASSWORD = "admin"

# ==========================================
# 2. File Paths
# ==========================================
DATA_FILE = "data/responses.csv"
OUTPUT_DIR = "outputs"
PRESENTATION_DIR = "presentation"

# ==========================================
# 3. Demographic Classifications
# ==========================================
DEMOGRAPHICS = {
    "respondent_type": {
        "name_en": "Respondent Category",
        "name_ar": "فئة المستجيب",
        "options": [
            "طالب جامعي",
            "شاب غير طالب يعمل",
            "شاب غير طالب لا يعمل",
            "طالب دراسات عليا",
        ],
    },
    "age_group": {
        "name_en": "Age Cohort",
        "name_ar": "الفئة العمرية",
        "options": ["18–21", "22–25", "26–30", "31–35"],
    },
    "gender": {
        "name_en": "Gender",
        "name_ar": "الجنس",
        "options": ["ذكر", "أنثى"],
    },
    "governorate": {
        "name_en": "Governorate of Residence",
        "name_ar": "محافظة الإقامة",
        "options": [
            "عمّان", "إربد", "الزرقاء", "البلقاء", "مأدبا",
            "الكرك", "الطفيلة", "معان", "العقبة", "جرش",
            "عجلون", "المفرق"
        ],
    },
    "education": {
        "name_en": "Education Level",
        "name_ar": "المستوى التعليمي",
        "options": ["ثانوية فأقل", "دبلوم", "بكالوريوس", "دراسات عليا"],
    },
    "daily_social_media_hours": {
        "name_en": "Daily Social Media Usage",
        "name_ar": "ساعات استخدام وسائل التواصل يومياً",
        "options": ["أقل من ساعة", "1–3 ساعات", "3–5 ساعات", "أكثر من 5 ساعات"],
    },
}

# ==========================================
# 4. Dimensions & Likert Survey Items
# ==========================================
DIMENSIONS = {
    "online_exposure": {
        "code": "D1",
        "name_en": "Online Radical Exposure",
        "name_ar": "التعرض للمحتوى المتطرف عبر الإنترنت",
        "type": "risk",  # Higher means higher risk
        "description_en": "Frequency of encountering violent extremist discourse or recruitment attempts online.",
        "description_ar": "معدل مصادفة محتوى يحث على العنف أو تلقي دعوات استقطاب فكري مجهولة.",
    },
    "critical_thinking": {
        "code": "D2",
        "name_en": "Critical & Analytical Thinking",
        "name_ar": "التفكير النقدي والمناعة الفكرية",
        "type": "protective",  # Higher means protective (inverted in risk index)
        "description_en": "Ability to deconstruct manipulative narratives and verify claims objectively.",
        "description_ar": "القدرة على كشف أساليب الخداع والتحقق من مصادر المعلومات ومناقشة الآراء بهدوء.",
    },
    "trust_official": {
        "code": "D3",
        "name_en": "Trust in Moderate & Official Institutions",
        "name_ar": "الثقة بالمؤسسات الرسمية والدينية المعتدلة",
        "type": "protective",
        "description_en": "Trust in official awareness channels, universities, and recognized religious bodies.",
        "description_ar": "الثقة ببرامج التوعية الرسمية ومعرفة الجهات المعتمدة لطلب المشورة.",
    },
    "isolation_susceptibility": {
        "code": "D4",
        "name_en": "Social Alienation & Frustration",
        "name_ar": "الشعور بالعزلة والضغط النفسي/المستقبلي",
        "type": "risk",
        "description_en": "Feelings of social isolation, economic anxiety, and vulnerability to instant promises.",
        "description_ar": "مشاعر العزلة أو الإحباط من الأوضاع المستقبلية التي قد تدفع للبحث عن حلول سريعة.",
    },
    "family_community_support": {
        "code": "D5",
        "name_en": "Family & Civic Attachment",
        "name_ar": "الدعم الأسري والمشاركة المجتمعية",
        "type": "protective",
        "description_en": "Strength of family communication, civic participation, and national belonging.",
        "description_ar": "جودة التواصل مع الأسرة والمشاركة في الأنشطة التطوعية والشعور بالانتماء للوطن.",
    },
}

# Exactly 20 Likert items (4 items per dimension)
SURVEY_ITEMS = [
    # D1: online_exposure (RISK)
    {
        "id": "E1",
        "dimension": "online_exposure",
        "text_ar": "أصادف بشكل متكرر محتوى على الإنترنت يمجّد العنف أو يدعو للتشدد",
        "text_en": "I frequently encounter online content glorifying violence or advocating extremism",
        "reverse": False,
    },
    {
        "id": "E2",
        "dimension": "online_exposure",
        "text_ar": "وصلتني رسائل أو دعوات من حسابات مجهولة تحاول استقطابي لأفكار متشددة",
        "text_en": "I received messages or invitations from unknown accounts attempting to recruit me to extremist ideas",
        "reverse": False,
    },
    {
        "id": "E3",
        "dimension": "online_exposure",
        "text_ar": "أتابع مجموعات أو قنوات على الإنترنت تنشر خطاباً حاداً ضد المجتمع أو الدولة",
        "text_en": "I follow online channels or groups disseminating aggressive rhetoric against society or the state",
        "reverse": False,
    },
    {
        "id": "E4",
        "dimension": "online_exposure",
        "text_ar": "نادراً ما أصادف محتوى متشدداً أثناء تصفحي للإنترنت",
        "text_en": "I rarely encounter extremist material during my routine internet browsing",
        "reverse": True,  # (R)
    },

    # D2: critical_thinking (PROTECTIVE)
    {
        "id": "C1",
        "dimension": "critical_thinking",
        "text_ar": "أستطيع كشف أساليب الخداع والتأثير في الخطابات والمنشورات المتشددة",
        "text_en": "I can identify deceptive manipulation techniques in extremist propaganda and speeches",
        "reverse": False,
    },
    {
        "id": "C2",
        "dimension": "critical_thinking",
        "text_ar": "أتحقق من مصدر المعلومة وهدف ناشرها قبل أن أصدّقها",
        "text_en": "I verify the source and intent of information before accepting or sharing it",
        "reverse": False,
    },
    {
        "id": "C3",
        "dimension": "critical_thinking",
        "text_ar": "أناقش الأفكار المخالفة لرأيي بهدوء دون اعتبار أصحابها أعداء",
        "text_en": "I engage calmly with opposing perspectives without considering others as enemies",
        "reverse": False,
    },
    {
        "id": "C4",
        "dimension": "critical_thinking",
        "text_ar": "أصدّق الفكرة إذا كررها كثير من الناس في صفحات التواصل",
        "text_en": "I believe an idea if it is widely shared and repeated by many social media accounts",
        "reverse": True,  # (R)
    },

    # D3: trust_official (PROTECTIVE)
    {
        "id": "T1",
        "dimension": "trust_official",
        "text_ar": "أثق بالإرشاد والتوعية التي تقدمها الجهات الرسمية والمؤسسات التعليمية والدينية المعتدلة",
        "text_en": "I trust the guidance provided by official, academic, and recognized moderate religious bodies",
        "reverse": False,
    },
    {
        "id": "T2",
        "dimension": "trust_official",
        "text_ar": "أرى أن برامج التوعية الأمنية والمجتمعية في منطقتي مفيدة",
        "text_en": "I believe institutional community and cyber awareness programs in my area are beneficial",
        "reverse": False,
    },
    {
        "id": "T3",
        "dimension": "trust_official",
        "text_ar": "أعرف الجهات التي أستطيع اللجوء لها إذا شعرت بخطر أو ضغط فكري",
        "text_en": "I know which official/civic institutions to contact if I face ideological coercion or risk",
        "reverse": False,
    },
    {
        "id": "T4",
        "dimension": "trust_official",
        "text_ar": "لا أثق بأي جهة رسمية أو مجتمعية مهما كانت",
        "text_en": "I place zero trust in any governmental or civic institution under any circumstances",
        "reverse": True,  # (R)
    },

    # D4: isolation_susceptibility (RISK)
    {
        "id": "S1",
        "dimension": "isolation_susceptibility",
        "text_ar": "أشعر بالعزلة أو أن لا أحد يفهمني أو يهتم بي",
        "text_en": "I frequently feel isolated or that nobody understands or cares about me",
        "reverse": False,
    },
    {
        "id": "S2",
        "dimension": "isolation_susceptibility",
        "text_ar": "أشعر بالغضب أو الإحباط الشديد من أوضاعي (دراسة، عمل، مستقبل) بشكل يؤثر على تفكيري",
        "text_en": "I experience acute frustration or anger regarding my academic/employment future",
        "reverse": False,
    },
    {
        "id": "S3",
        "dimension": "isolation_susceptibility",
        "text_ar": "قد أقتنع بأي جهة تعدني بحل مشاكلي حتى لو كانت مجهولة",
        "text_en": "I might listen to any group offering to solve my problems even if they are unknown",
        "reverse": False,
    },
    {
        "id": "S4",
        "dimension": "isolation_susceptibility",
        "text_ar": "لدي أصدقاء أو أشخاص قريبون أتحدث معهم بصراحة",
        "text_en": "I have trustworthy friends or close confidants with whom I communicate openly",
        "reverse": True,  # (R)
    },

    # D5: family_community_support (PROTECTIVE)
    {
        "id": "F1",
        "dimension": "family_community_support",
        "text_ar": "أتواصل مع أسرتي بشكل جيد وأستطيع مناقشتهم في مواضيعي الشخصية",
        "text_en": "I maintain healthy communication with my family and can discuss personal topics openly",
        "reverse": False,
    },
    {
        "id": "F2",
        "dimension": "family_community_support",
        "text_ar": "أشارك في أنشطة جامعية أو تطوعية أو رياضية أو مجتمعية",
        "text_en": "I participate in university clubs, sports, volunteering, or civic community initiatives",
        "reverse": False,
    },
    {
        "id": "F3",
        "dimension": "family_community_support",
        "text_ar": "أشعر بالانتماء لمجتمعي وبلدي",
        "text_en": "I feel a profound sense of civic belonging and loyalty to my community and country",
        "reverse": False,
    },
    {
        "id": "F4",
        "dimension": "family_community_support",
        "text_ar": "لا أحد في محيطي يهتم بما أفعله أو أفكر به",
        "text_en": "Nobody in my immediate environment cares about what I achieve or think",
        "reverse": True,  # (R)
    },
]

# Quick lookup dictionary for items by ID
ITEM_DICT = {item["id"]: item for item in SURVEY_ITEMS}

# ==========================================
# 5. Statistical & Scoring Thresholds
# ==========================================
LIKERT_MIN = 1
LIKERT_MAX = 5
NEUTRAL_SCORE = 3.0  # Center of Likert scale for waterfall contribution trace

# Standard 3-Band Likert Split
# Mathematical Rationale: Standard equidistant division of 5-point Likert scale (width = 4/3 = 1.33)
LOW_RISK_MAX = 2.33
MODERATE_RISK_MAX = 3.66

RISK_BANDS = {
    "Low": {
        "min": 1.00,
        "max": LOW_RISK_MAX,
        "label_en": "Low Vulnerability / Well-Protected",
        "label_ar": "قابلية منخفضة / مستوى حماية مرتفع",
        "color": "#2ecc71",  # Green
        "badge_bg": "rgba(46, 204, 113, 0.15)",
        "badge_border": "#2ecc71",
        "summary_en": "Demonstrates strong critical thinking, civic connectedness, and low radical exposure.",
        "summary_ar": "يتمتع بوعي نقدي عالٍ، ودعم أسري ومجتمعي متين، مع انخفاض التعرض للمحتوى المتطرف.",
    },
    "Moderate": {
        "min": 2.34,
        "max": MODERATE_RISK_MAX,
        "label_en": "Moderate Vulnerability / Needs Awareness",
        "label_ar": "قابلية متوسطة / يتطلب تعزيز التوعية",
        "color": "#ffb400",  # Amber
        "badge_bg": "rgba(255, 180, 0, 0.15)",
        "badge_border": "#ffb400",
        "summary_en": "Shows vulnerability in specific areas (e.g. high exposure or digital alienation).",
        "summary_ar": "توجد مؤشرات تحتاج إلى انتباه وتوعية استباقية في بعض الأبعاد (مثل التعرض الرقمي أو العزلة).",
    },
    "High": {
        "min": 3.67,
        "max": 5.00,
        "label_en": "High Vulnerability / Needs Immediate Support",
        "label_ar": "قابلية مرتفعة / يتطلب تدخلاً وتوجيهاً وقائياً عاجلاً",
        "color": "#ff4d6d",  # Coral / Red
        "badge_bg": "rgba(255, 77, 109, 0.15)",
        "badge_border": "#ff4d6d",
        "summary_en": "Accumulates multiple risk drivers alongside weakened protective ties. Counseling recommended.",
        "summary_ar": "تراكم لعوامل الخطورة وضعف شبكات الحماية المجتمعية. يُنصح بالتواصل مع مرشد أكاديمي أو أخصائي موثوق.",
    },
}

# Community escalation trigger
COMMUNITY_ESCALATION_PCT = 25.0  # If % High Vulnerability > 25%, escalate community status

# Correlation strength thresholds
CORRELATION_THRESHOLDS = {
    "weak": {"max": 0.299, "label_en": "Weak correlation", "label_ar": "ارتباط ضعيف"},
    "moderate": {"min": 0.300, "max": 0.599, "label_en": "Moderate correlation", "label_ar": "ارتباط متوسط"},
    "strong": {"min": 0.600, "label_en": "Strong correlation", "label_ar": "ارتباط قوي"},
}

# Outlier parameters
DEFAULT_Z_OUTLIER_THRESHOLD = 2.0
STRICT_Z_OUTLIER_THRESHOLD = 3.0
IQR_MULTIPLIER = 1.5

# Progressive unlock minimum sample sizes
PROGRESSIVE_UNLOCK = {
    "personal_only": 0,       # < 10: only personal score vs theoretical bands
    "descriptive_z": 10,      # >= 10: descriptive stats & Z-scores unlocked
    "inferential_rel": 30,    # >= 30: Cronbach's alpha & inferential tests unlocked
    "min_subgroup_size": 5,   # Minimum respondents per subgroup for ANOVA / t-test
}

# ==========================================
# 6. UI Dark Design Tokens & Colors
# ==========================================
THEME = {
    "bg": "#0b1020",
    "card": "#121a33",
    "card_hover": "#172242",
    "border": "#22305a",
    "text": "#e8ecf8",
    "muted": "#8b97b8",
    "accent_cyan": "#00c2cb",
    "accent_blue": "#0a84ff",
    "accent_amber": "#ffb400",
    "accent_coral": "#ff4d6d",
    "accent_purple": "#a78bfa",
    "accent_green": "#2ecc71",
}

# Plotly dark theme layout defaults
PLOTLY_DARK_LAYOUT = {
    "paper_bgcolor": THEME["card"],
    "plot_bgcolor": THEME["card"],
    "font": {"family": "Cairo, Inter, Segoe UI, sans-serif", "color": THEME["text"], "size": 12},
    "xaxis": {"gridcolor": THEME["border"], "zerolinecolor": THEME["border"]},
    "yaxis": {"gridcolor": THEME["border"], "zerolinecolor": THEME["border"]},
    "margin": {"l": 40, "r": 40, "t": 50, "b": 40},
}

