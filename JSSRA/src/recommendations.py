"""
JSSRA Preventive Recommendations & Strategic Action Engine.

Generates evidence-driven, Jordan-specific interventions:
- Personalized advice mapped to the respondent's weakest protective or highest risk dimensions
- University counseling, youth engagement, and cyber reporting pathways
- Immediate emergency protocol ("in immediate danger call 911"; no invented hotlines)
- 3-Horizon Strategic Action Roadmap for academic and civic policy stakeholders
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


# Comprehensive dimension-level recommendation repository
INTERVENTION_REPOSITORY = {
    "online_exposure": {
        "title_ar": "تعزيز الحماية والوعي الرقمي لمواجهة الاستقطاب الإلكتروني",
        "title_en": "Digital Safety & Counter-Recruitment Awareness",
        "personal_ar": [
            "تجنب الانضمام إلى مجموعات أو قنوات مجهولة على منصات تيليجرام أو ديسكورد التي تروج لخطابات الكراهية أو العنف.",
            "استخدم خاصية حظر الحسابات المشبوهة والإبلاغ عنها فوراً عبر إدارة المنصة ووحدة مكافحة الجرائم الإلكترونية (مديرية الأمن العام).",
            "فعّل فلاتر الأمان والخصوصية على وسائل التواصل الاجتماعي لتفادي استهدافك بإعلانات أو رسائل استقطابية.",
        ],
        "community_ar": [
            "تنظيم ورش عمل متخصصة بالأمان الرقمي في الجامعات والمراكز الشبابية بالتعاون مع وحدة مكافحة الجرائم الإلكترونية.",
            "إطلاق حملات توعية إلكترونية تسلط الضوء على الأساليب الحديثة التي تستخدمها الجماعات المتطرفة لاستدراج الشباب.",
        ],
        "owner_ar": "مديرية الأمن العام (الجرائم الإلكترونية) + وزارة الاقتصاد الرقمي والريادة",
    },
    "critical_thinking": {
        "title_ar": "تنمية التفكير النقدي وتفكيك الخطاب المضلل",
        "title_en": "Critical Thinking & Counter-Disinformation",
        "personal_ar": [
            "تدرّب على التشكيك المنهجي في العناوين المثيرة ولا تتسرع في تصديق أو إعادة نشر أي معلومة قبل التحقق من مصدرها الأولي.",
            "اعتمد على منصات التحقق الأردنية المستقلة مثل (مسبار) و(أكيد) للتأكد من الأخبار والصور المتداولة.",
            "احرص على الاستماع للآراء المخالفة بمرونة فكرية دون تشنج أو تصنيف الآخرين كأعداء.",
        ],
        "community_ar": [
            "إدراج مساقات عملية إلزامية في التربية الإعلامية والمعلوماتية في الجامعات والمدارس الأردنية.",
            "عقد مخيمات ومناظرات فكرية شبابية تدرب على تفكيك الحجج المنطقية الزائفة وبناء الوعي النقدي.",
        ],
        "owner_ar": "وزارة التربية والتعليم + وزارة التعليم العالي + معهد الإعلام الأردني ومبادرات التحقق (مسبار وأكيد)",
    },
    "trust_official": {
        "title_ar": "تعزيز الثقة بالمؤسسات التعليمية والتوجيه الديني المعتدل",
        "title_en": "Institutional Trust & Moderate Guidance",
        "personal_ar": [
            "احرص على أخذ الفتاوى والأفكار الدينية والاجتماعية من المراجع المعتمدة (مثل دائرة الإفتاء العام ووزارة الأوقاف).",
            "شارك في الفعاليات والندوات الحوارية التي تقيمها عمادات شؤون الطلبة في الجامعات لطرح استفساراتك بشفافية.",
            "تعرّف على القنوات الرسمية للاستفسار وطلب المشورة الآمنة عند مواجهة أي ضغوط فكرية.",
        ],
        "community_ar": [
            "تطوير منصات رقمية تفاعلية حديثة للخطاب الديني والفكري المعتدل يقودها شباب وعلماء معتدلون بأسلوب عصري.",
            "تعزيز التواصل المباشر بين المسؤولين وممثلي الجامعات لمعالجة هموم الشباب ومخاوفهم بمصداقية وشفافية.",
        ],
        "owner_ar": "دائرة الإفتاء العام + وزارة الأوقاف والشؤون والمقدسات الإسلامية + الجامعات الرسمية والخاصة",
    },
    "isolation_susceptibility": {
        "title_ar": "التغلب على العزلة وبناء شبكات الدعم النفسي والاجتماعي",
        "title_en": "Overcoming Isolation & Mental Health Support",
        "personal_ar": [
            "تحدث بصراحة مع صديق موثوق، أو أحد أفراد الأسرة، أو راجع مكتب الإرشاد النفسي والطلابي في جامعتك لتفريغ الضغوط.",
            "انضم إلى أنشطة تطوعية أو نوادٍ طلابية لتوسيع دائرة علاقاتك الإيجابية وكسر حواجز العزلة والانطواء.",
            "تذكر أن الإحباط الاقتصادي أو الأكاديمي تحدٍ يواجهه الكثيرون، ويمكن تجاوزه بتطوير المهارات دون اللجوء لحلول وهمية.",
        ],
        "community_ar": [
            "توسيع خدمات مكاتب الإرشاد النفسي والاجتماعي في جميع الجامعات وكليات المجتمع بخصوصية وسرية تامة.",
            "إنشاء نوادي دعم الأقران (Peer Support) لمساعدة الطلاب الجدد والشباب الباحثين عن عمل على تجاوز ضغوط المرحلة.",
        ],
        "owner_ar": "وزارة الصحة (وحدات الدعم النفسي) + عمادات شؤون الطلبة + وزارة الشباب",
    },
    "family_community_support": {
        "title_ar": "تمتين الروابط الأسرية وتعميق الانتماء والمشاركة المجتمعية",
        "title_en": "Family Connectedness & Civic Engagement",
        "personal_ar": [
            "خصص وقتاً يومياً للحوار المفتوح مع عائلتك ومشاركتهم أفكارك واهتماماتك وتطلعاتك المستقبلية.",
            "انخرط في الأنشطة الرياضية والمبادرات المجتمعية في محافظتك عبر المراكز الشبابية ومؤسسة ولي العهد.",
            "ساهم في خدمة مجتمعك المحلي عبر العمل التطوعي، مما يعزز شعورك بالقيمة الذاتية والانتماء الإيجابي للوطن.",
        ],
        "community_ar": [
            "تفعيل مراكز الشباب والأندية الرياضية في كافة المحافظات وتقديم برامج مجانية جاذبة للشباب.",
            "برامج إرشاد أسري تدرب الآباء والأمهات على آليات الاستماع الإيجابي للأبناء وملاحظة أي تغيرات فكرية مبكراً.",
        ],
        "owner_ar": "مؤسسة ولي العهد + وزارة الشباب + وزارة التنمية الاجتماعية",
    },
}


def generate_personalized_recommendations(
    top_risk_drivers: List[Dict[str, Any]],
    risk_band: str,
) -> Dict[str, Any]:
    """
    Generates targeted personalized advice based on the respondent's top risk drivers
    and overall risk category.
    """
    advice_cards = []

    for d in top_risk_drivers:
        dim_key = d["dim_key"]
        repo = INTERVENTION_REPOSITORY.get(dim_key, {})
        advice_cards.append({
            "dimension": dim_key,
            "title_ar": repo.get("title_ar", ""),
            "title_en": repo.get("title_en", ""),
            "personal_actions": repo.get("personal_ar", []),
        })

    # High vulnerability protocol
    urgent_warning = None
    if risk_band == "High":
        urgent_warning = {
            "title_ar": "توجيه إرشادي هام للفئة ذات القابلية المرتفعة",
            "message_ar": (
                "تُظهر نتائجك مؤشرات ضغط أو عزلة أو تعرض مرتفع للمحتوى المقلق. ننصحك بشدة بالتحدث مع مرشد نفسي "
                "أو أكاديمي في عمادة شؤون الطلبة، أو شخص راشد تثق به. "
                "وفي حال شعرت بتهديد مباشر أو خطر داهم عليك أو على سلامتك، يرجى الاتصال فوراً برقم الطوارئ الموحد: 911."
            ),
            "emergency_contact": "911 (رقم الطوارئ الموحد في الأردن)",
        }

    return {
        "advice_cards": advice_cards,
        "urgent_warning": urgent_warning,
    }


def get_3_horizon_action_plan(
    ranked_dimensions: List[Tuple[str, float]],
) -> List[Dict[str, Any]]:
    """
    Constructs an evidence-driven 3-horizon action roadmap with institutional owners and measurable KPIs.
    """
    # Weakest dimension (highest risk mean)
    primary_dim_key = ranked_dimensions[0][0] if ranked_dimensions else "online_exposure"
    primary_repo = INTERVENTION_REPOSITORY.get(primary_dim_key, {})

    plan = [
        {
            "horizon_num": "01",
            "horizon_en": "Horizon 1: Immediate Actions (0–3 Months)",
            "horizon_ar": "المرحلة الأولى: إجراءات عاجلة (0–3 أشهر)",
            "action_ar": f"إطلاق حملات توعوية سريعة ومكثفة تركز على ({primary_repo.get('title_ar', 'الوعي الرقمي')}) في الجامعات والمحافظات ذات المؤشرات الأكثر حاجة.",
            "action_en": f"Launch targeted awareness blitz addressing {primary_repo.get('title_en', 'Digital Hygiene')} across collegiate portals.",
            "owner_ar": "وحدة مكافحة الجرائم الإلكترونية (الأمن العام) + عمادات شؤون الطلبة",
            "owner_en": "PSD Cybercrime Unit & University Student Deanships",
            "kpi_ar": "الوصول إلى 50,000 طالب ومستفيد، وتوزيع 20,000 دليل إرشادي في الجامعات.",
            "kpi_en": "Reach 50,000 students; distribute 20,000 digital safety guides.",
        },
        {
            "horizon_num": "02",
            "horizon_en": "Horizon 2: Medium-Term Programs (3–12 Months)",
            "horizon_ar": "المرحلة الثانية: برامج متوسطة المدى (3–12 شهراً)",
            "action_ar": "تعميم ورش التربية الإعلامية والتفكير النقدي وشراكات التحقق من الأخبار مع منصات (مسبار وأكيد)، وتفعيل مكاتب الدعم النفسي الجامعي.",
            "action_en": "Scale university media literacy curricula and partnerships with fact-checking platforms (Misbar, Akeed).",
            "owner_ar": "وزارة التعليم العالي + معهد الإعلام الأردني + وزارة الشباب",
            "owner_en": "Ministry of Higher Education & Jordan Media Institute",
            "kpi_ar": "تدريب 1,000 سفير شبابي للتفكير النقدي، وتدشين نوادي مناظرة في 15 جامعة أردنية.",
            "kpi_en": "Train 1,000 peer mentors; establish debate societies across 15 universities.",
        },
        {
            "horizon_num": "03",
            "horizon_en": "Horizon 3: Long-Term Systemic Institutionalization (1–3 Years)",
            "horizon_ar": "المرحلة الثالثة: سياسات وطنية مستدامة (1–3 سنوات)",
            "action_ar": "تأسيس المرصد الوطني لمناعة الشباب ضد التطرف، وإجراء مسوحات دورية، وربط مخرجات التحليل بسياسات التشغيل والتمكين المجتمعي بالمحافظات.",
            "action_en": "Establish permanent National Youth Resilience Observatory with longitudinal statistical monitoring.",
            "owner_ar": "المجلس الأعلى للعلوم والتكنولوجيا + وزارة التخطيط + مؤسسة ولي العهد",
            "owner_en": "Higher Council for Science and Technology & Crown Prince Foundation",
            "kpi_ar": "خفض نسبة الفئة المعرضة للخطورة المرتفعة بالمجتمع لتكون أقل من 10% وطنياً.",
            "kpi_en": "Reduce High Vulnerability cohort below 10% nationwide on annual panel resurvey.",
        },
    ]

    return plan

