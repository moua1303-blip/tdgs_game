"""
نظام الأحداث المتطور - نسخة موحدة ومطورة
تم تعديلها لتعمل مع بقية ملفات اللعبة
"""

import random
from typing import Dict, List, Any, Optional
from utils import logger, clamp

# ============== أحداث فريدة - 20 حدثاً مختلفاً ==============

EVENTS_DATABASE = [
    # 1️⃣ قرية تحت الهجوم
    {
        "id": "village_under_attack",
        "title": "🏘️  نداء استغاثة: قرية تحت الهجوم",
        "header": "══════════════════════════════\n📢 تقرير عاجل من الاستخبارات\n══════════════════════════════",
        "description": "قرية {village_name} تتعرض لهجوم من ميليشيا محلية.\nالمدنيون يحتمون في منازلهم ويطلبون المساعدة.\nالوضع خطير جداً.",
        "details": {
            "location": "وادي النخيل",
            "time": "الغروب 🌅",
            "enemy_force": "40-60 مسلح",
            "civilians": "120 مدني"
        },
        "choices": [
            {
                "text": "⚔️ الدفاع عن القرية - اشتباك مباشر",
                "risk": 70,
                "effects": {
                    "command": 15,
                    "civilians": 25,
                    "soldiers": 10,
                    "civilians_saved": 50
                }
            },
            {
                "text": "🛡️ إخلاء المدنيين وتأمينهم",
                "risk": 40,
                "effects": {
                    "civilians": 30,
                    "self_respect": 20,
                    "command": -5,
                    "civilians_saved": 80
                }
            },
            {
                "text": "🎯 نصب كمين للمهاجمين",
                "risk": 50,
                "effects": {
                    "enemy_killed": 25,
                    "command": 20
                }
            },
            {
                "text": "🚶 تجاهل النداء - المهمة أولاً",
                "risk": 0,
                "effects": {
                    "civilians": -40,
                    "self_respect": -30,
                    "mental": -25,
                    "civilians_killed": 120
                }
            }
        ]
    },
    
    # 2️⃣ قافلة إمدادات
    {
        "id": "supply_convoy",
        "title": "🚚  فرصة ذهبية: قافلة إمدادات للعدو",
        "header": "══════════════════════════════\n📢 معلومات استخباراتية سرية\n══════════════════════════════",
        "description": "علمنا من مصدر موثوق أن قافلة إمدادات ضخمة للعدو\nستمر عبر ممر الجبل خلال ساعتين.\nحمايتها خفيفة.",
        "details": {
            "location": "ممر الجبل",
            "time": "الفجر 🌄",
            "enemy_force": "10-15 جندي حراسة",
            "supplies": "طعام، ذخيرة، أدوية"
        },
        "choices": [
            {
                "text": "💥 هجوم شامل على القافلة",
                "risk": 60,
                "effects": {
                    "supplies": 50,
                    "enemy_killed": 15,
                    "command": 15
                }
            },
            {
                "text": "🎯 نصب كمين محكم",
                "risk": 40,
                "effects": {
                    "supplies": 40,
                    "enemy_killed": 12,
                    "command": 10
                }
            },
            {
                "text": "👁️ مراقبة القافلة فقط",
                "risk": 20,
                "effects": {
                    "intel": 25,
                    "command": 5
                }
            },
            {
                "text": "🚫 تجاهل القافلة",
                "risk": 0,
                "effects": {
                    "command": -10,
                    "supplies": -20
                }
            }
        ]
    },
    
    # 3️⃣ جندي مصاب خلف خطوط العدو
    {
        "id": "wounded_soldier",
        "title": "🆘  إشارة استغاثة: جندي مصاب",
        "header": "══════════════════════════════\n📢 رسالة مشفرة من الخطوط الخلفية\n══════════════════════════════",
        "description": "أحد جنودكم، {soldier_name}، مصاب بجروح خطيرة\nوخلف خطوط العدو. يرسل إشارات استغاثة.\nالعدو يبحث عنه.",
        "details": {
            "location": "المنطقة المحايدة",
            "time": "ليل 🌙",
            "enemy_force": "دوريات متفرقة",
            "soldier_status": "نزيف، كسر في الساق"
        },
        "choices": [
            {
                "text": "🏃 إرسال فريق إنقاذ فوراً",
                "risk": 70,
                "effects": {
                    "soldiers_loyalty": 30,
                    "self_respect": 25,
                    "rescue_chance": 80
                }
            },
            {
                "text": "🚁 طلب دعم جوي لإخلائه",
                "risk": 50,
                "effects": {
                    "command": 10,
                    "rescue_chance": 60
                }
            },
            {
                "text": "💣 قصف المنطقة لتغطية هروبه",
                "risk": 40,
                "effects": {
                    "enemy_killed": 10,
                    "rescue_chance": 40,
                    "civilians": -15
                }
            },
            {
                "text": "😔 تركه لمصيره",
                "risk": 0,
                "effects": {
                    "soldiers_loyalty": -40,
                    "self_respect": -35,
                    "mental": -30
                }
            }
        ]
    },
    
    # 4️⃣ كمين في الوادي
    {
        "id": "ambush_warning",
        "title": "⚠️  تحذير: كمين محتمل",
        "header": "══════════════════════════════\n📢 تقرير من الكشافة\n══════════════════════════════",
        "description": "الكشافة لاحظوا تحركات غير طبيعية في الوادي.\nيبدو أن العدو يعد كميناً لكم.\nالطريق الوحيد هو عبر هذا الوادي.",
        "details": {
            "location": "الوادي الضيق",
            "time": "الغسق 🌆",
            "enemy_estimated": "20-30 مسلح",
            "visibility": "ضعيفة"
        },
        "choices": [
            {
                "text": "🔄 تغيير الطريق - طريق أطول",
                "risk": 20,
                "effects": {
                    "soldiers": 10,
                    "time_loss": 2,
                    "command": -5
                }
            },
            {
                "text": "🔍 إرسال استطلاع متقدم",
                "risk": 40,
                "effects": {
                    "intel": 30
                }
            },
            {
                "text": "🎯 قلب الطاولة - تطويقهم",
                "risk": 60,
                "effects": {
                    "enemy_killed": 20,
                    "command": 25
                }
            },
            {
                "text": "⚡ التقدم بحذر شديد",
                "risk": 70,
                "effects": {}
            }
        ]
    },
    
    # 5️⃣ عاصفة رملية
    {
        "id": "sandstorm",
        "title": "🌪️  تحذير: عاصفة رملية قادمة",
        "header": "══════════════════════════════\n📢 حالة الطقس\n══════════════════════════════",
        "description": "الأرصاد الجوية تحذر من عاصفة رملية شديدة\nخلال ساعة. الرؤية ستنعدم تماماً.\nالرياح تزداد سرعة.",
        "details": {
            "duration": "6-8 ساعات",
            "visibility": "0-5 أمتار",
            "temperature": "45°C"
        },
        "choices": [
            {
                "text": "🏕️ الاحتماء وانتظار انتهاء العاصفة",
                "risk": 10,
                "effects": {
                    "soldiers": 15,
                    "time_loss": 1
                }
            },
            {
                "text": "🚶 مواصلة التقدم بصعوبة",
                "risk": 60,
                "effects": {
                    "soldiers": -20,
                    "time_loss": 2
                }
            },
            {
                "text": "👤 استغلال العاصفة للتسلل",
                "risk": 50,
                "effects": {
                    "enemy_killed": 15,
                    "command": 20
                }
            }
        ]
    },
    
    # 6️⃣ شجار بين الجنود
    {
        "id": "soldiers_fight",
        "title": "🤜🤛  مشكلة داخلية: شجار في الكتيبة",
        "header": "══════════════════════════════\n📢 تقرير داخلي\n══════════════════════════════",
        "description": "{soldier1} و {soldier2} تشاجرا بشدة.\nالسبب: خلاف شخصي قديم.\nالجنود منقسمون بينهما.",
        "details": {
            "issue": "خلاف شخصي",
            "tension": "عالية جداً"
        },
        "choices": [
            {
                "text": "⚖️ محاكمة عسكرية للطرفين",
                "risk": 30,
                "effects": {
                    "command": 20,
                    "soldiers": -20,
                    "cohesion": -10
                }
            },
            {
                "text": "🤝 محاولة المصالحة بينهما",
                "risk": 40,
                "effects": {
                    "soldiers": 25,
                    "self_respect": 15,
                    "cohesion": 20
                }
            },
            {
                "text": "👁️ تجاهل المشكلة",
                "risk": 60,
                "effects": {
                    "cohesion": -25,
                    "soldiers": -15
                }
            },
            {
                "text": "🔄 نقل أحدهما لوحدة أخرى",
                "risk": 20,
                "effects": {
                    "soldiers": 10,
                    "command": 5
                }
            }
        ]
    },
    
    # 7️⃣ مخبأ ذخيرة قديم
    {
        "id": "old_cache",
        "title": "💣  اكتشاف: مخبأ ذخيرة قديم",
        "header": "══════════════════════════════\n📢 تقرير من الدوريات\n══════════════════════════════",
        "description": "أثناء تمشيط المنطقة، عثر الجنود على مخبأ قديم.\nيبدو من بقايا الحرب السابقة.\nقد يحتوي على ذخيرة ومعدات.",
        "details": {
            "location": "كهف منسي",
            "age": "5-10 سنوات",
            "condition": "غير معروف"
        },
        "choices": [
            {
                "text": "🔍 تفتيش المخبأ بالكامل",
                "risk": 50,
                "effects": {
                    "supplies": 50,
                    "ammo": 40
                }
            },
            {
                "text": "👁️ فتح الصندوق الأول فقط",
                "risk": 25,
                "effects": {
                    "supplies": 20,
                    "ammo": 15
                }
            },
            {
                "text": "🚫 إبلاغ خبراء المتفجرات",
                "risk": 10,
                "effects": {
                    "supplies": 30,
                    "time_loss": 1
                }
            },
            {
                "text": "🚶 تركه والاستمرار",
                "risk": 0,
                "effects": {}
            }
        ]
    },
    
    # 8️⃣ قناص العدو
    {
        "id": "enemy_sniper",
        "title": "🎯  تهديد: قناص معادٍ",
        "header": "══════════════════════════════\n📢 تحذير أمني عاجل\n══════════════════════════════",
        "description": "قناص العدو يستهدف المنطقة.\nأصاب جنديين خلال الساعة الأخيرة.\nموقعه غير معروف بدقة.",
        "details": {
            "location": "التلال الشرقية",
            "victims": "جريحان",
            "status": "نشط"
        },
        "choices": [
            {
                "text": "🔍 إرسال فريق لتعقبه",
                "risk": 60,
                "effects": {
                    "enemy_killed": 2,
                    "command": 20
                }
            },
            {
                "text": "🛡️ تغيير التموضع والاختباء",
                "risk": 20,
                "effects": {
                    "time_loss": 1,
                    "command": -5
                }
            },
            {
                "text": "💣 قصف المنطقة بالمدفعية",
                "risk": 30,
                "effects": {
                    "enemy_killed": 5,
                    "civilians": -20,
                    "self_respect": -15,
                    "civilians_killed": 5
                }
            },
            {
                "text": "🌙 انتظار الليل للتحرك",
                "risk": 40,
                "effects": {
                    "time_loss": 1
                }
            }
        ]
    },
    
    # 9️⃣ رسالة من القيادة
    {
        "id": "command_message",
        "title": "📨  أمر عاجل من القيادة",
        "header": "══════════════════════════════\n📢 اتصال مشفر من القيادة\n══════════════════════════════",
        "description": "وصلت رسالة مباشرة من القيادة العليا:\n'تقدموا فوراً واقضوا على تجمع العدو\nفي المنطقة الشمالية. هذا أمر مباشر.'",
        "details": {
            "order": "هجوم شمالاً",
            "deadline": "24 ساعة",
            "consequences": "محاكمة عسكرية"
        },
        "choices": [
            {
                "text": "⚡ تنفيذ الأمر فوراً",
                "risk": 70,
                "effects": {
                    "command": 30
                }
            },
            {
                "text": "🤔 طلب توضيح وتأجيل",
                "risk": 50,
                "effects": {
                    "command": -15,
                    "time_loss": 1
                }
            },
            {
                "text": "💬 الرد بأن الوضع خطير",
                "risk": 40,
                "effects": {
                    "command": -10
                }
            },
            {
                "text": "🚫 تجاهل الأمر",
                "risk": 80,
                "effects": {
                    "command": -40,
                    "soldiers": 30,
                    "self_respect": 20,
                    "disobeyed_orders": 1
                }
            }
        ]
    },
    
    # 🔟 طفل ضائع
    {
        "id": "lost_child",
        "title": "👶  طفل في خطر",
        "header": "══════════════════════════════\n📢 تقرير من الدوريات\n══════════════════════════════",
        "description": "رصدنا طفلاً صغيراً يبكي في منطقة القتال.\nيبدو ضائعاً وخائفاً.\nالقتال يقترب منه.",
        "details": {
            "age": "5-7 سنوات",
            "location": "منطقة مكشوفة",
            "danger": "نيران متبادلة"
        },
        "choices": [
            {
                "text": "🏃 إنقاذ الطفل فوراً",
                "risk": 70,
                "effects": {
                    "civilians": 40,
                    "self_respect": 35,
                    "civilians_saved": 1
                }
            },
            {
                "text": "🛡️ تغطية نارية ثم إنقاذه",
                "risk": 50,
                "effects": {
                    "civilians": 30,
                    "command": 10,
                    "civilians_saved": 1
                }
            },
            {
                "text": "📢 مناداته للاختباء",
                "risk": 40,
                "effects": {
                    "civilians": 15
                }
            },
            {
                "text": "😔 تجاهل الطفل",
                "risk": 0,
                "effects": {
                    "civilians": -50,
                    "self_respect": -40,
                    "mental": -35,
                    "civilians_killed": 1
                }
            }
        ]
    },
    
    # 1️⃣1️⃣ فرصة تدريب
    {
        "id": "training_opportunity",
        "title": "🏋️  فرصة تدريب متقدم",
        "header": "══════════════════════════════\n📢 وصول مدرب محترف\n══════════════════════════════",
        "description": "مدرب قديم وصل إلى المنطقة ويعرض تدريب الكتيبة.\nيمكنه تحسين مهاراتكم بشكل كبير.\nيطلب أجراً زهيداً.",
        "details": {
            "trainer": "عميد متقاعد",
            "duration": "3 أيام",
            "specialty": "قتال متقدم"
        },
        "choices": [
            {
                "text": "✅ تدريب الكتيبة بأكملها",
                "risk": 20,
                "effects": {
                    "training_all": 50,
                    "time_loss": 3
                }
            },
            {
                "text": "🎯 تدريب القناصة فقط",
                "risk": 15,
                "effects": {
                    "training_snipers": 40,
                    "time_loss": 2
                }
            },
            {
                "text": "🏥 تدريب المسعفين",
                "risk": 10,
                "effects": {
                    "training_medics": 35,
                    "time_loss": 2
                }
            },
            {
                "text": "🚫 لا وقت للتدريب",
                "risk": 0,
                "effects": {}
            }
        ]
    },
    
    # 1️⃣2️⃣ خلاف بين صديقين
    {
        "id": "friends_conflict",
        "title": "💔  خلاف بين صديقين",
        "header": "══════════════════════════════\n📢 تقرير عن العلاقات\n══════════════════════════════",
        "description": "{soldier1} و {soldier2}، الصديقان المقربان،\nعلى خلاف شديد. هذا يؤثر على الكتيبة.",
        "details": {
            "impact": "معنويات منخفضة",
            "urgency": "متوسطة"
        },
        "choices": [
            {
                "text": "💬 التحدث معهما معاً",
                "risk": 30,
                "effects": {
                    "cohesion": 25,
                    "friendship_boost": 30
                }
            },
            {
                "text": "👥 التحدث مع كل على حدة",
                "risk": 20,
                "effects": {
                    "cohesion": 20,
                    "friendship_boost": 20
                }
            },
            {
                "text": "🎯 تكليفهما بمهمة معاً",
                "risk": 50,
                "effects": {
                    "cohesion": 40,
                    "risk_of_failure": 30
                }
            },
            {
                "text": "👁️ تجاهل المشكلة",
                "risk": 40,
                "effects": {
                    "cohesion": -30,
                    "friendship_boost": -20
                }
            }
        ]
    },
    
    # 1️⃣3️⃣ ذخيرة منخفضة
    {
        "id": "low_ammo",
        "title": "⚠️  تحذير: الذخيرة منخفضة",
        "header": "══════════════════════════════\n📢 تقرير لوجستي\n══════════════════════════════",
        "description": "الذخيرة بدأت تنفد. لدينا ما يكفي لمعركتين فقط.\nالتموين لن يصل قبل أسبوع.",
        "details": {
            "rifle_ammo": "300 طلقة",
            "heavy_ammo": "15 قذيفة",
            "grenades": "8 قنابل"
        },
        "choices": [
            {
                "text": "📦 ترشيد الاستهلاك - أوامر صارمة",
                "risk": 20,
                "effects": {
                    "ammo_save": 30,
                    "morale": -10
                }
            },
            {
                "text": "🔫 مهاجمة العدو لأخذ ذخيرته",
                "risk": 60,
                "effects": {
                    "ammo_gain": 50,
                    "enemy_killed": 15
                }
            },
            {
                "text": "🛡️ الدفاع فقط - لا هجوم",
                "risk": 30,
                "effects": {
                    "ammo_save": 50,
                    "command": -15
                }
            },
            {
                "text": "🚁 طلب إنزال جوي عاجل",
                "risk": 40,
                "effects": {
                    "ammo_gain": 80,
                    "command": -20
                }
            }
        ]
    },
    
    # 1️⃣4️⃣ جاسوس في الكتيبة
    {
        "id": "spy_suspicion",
        "title": "🕵️  شبهة جاسوس",
        "header": "══════════════════════════════\n📢 تقرير استخباراتي حساس\n══════════════════════════════",
        "description": "وصلتنا معلومات عن وجود جاسوس في الكتيبة.\nالشكوك تحوم حول {soldier_name}.",
        "details": {
            "evidence": "غير مؤكد",
            "risk": "عالي"
        },
        "choices": [
            {
                "text": "🔍 التحقيق معه رسمياً",
                "risk": 40,
                "effects": {
                    "command": 15,
                    "soldiers": -20,
                    "intel": 30
                }
            },
            {
                "text": "👁️ مراقبته سراً",
                "risk": 30,
                "effects": {
                    "intel": 50,
                    "time_loss": 3
                }
            },
            {
                "text": "💬 مواجهته مباشرة",
                "risk": 50,
                "effects": {
                    "intel": 40,
                    "soldiers": -10
                }
            },
            {
                "text": "🤝 إظهار الثقة به",
                "risk": 60,
                "effects": {
                    "soldiers": 25,
                    "intel": -20
                }
            }
        ]
    },
    
    # 1️⃣5️⃣ هجوم ليلي
    {
        "id": "night_attack",
        "title": "🌙  فرصة: هجوم ليلي",
        "header": "══════════════════════════════\n📢 تقرير تكتيكي\n══════════════════════════════",
        "description": "العدو غير مستعد ليلاً. فرصة ذهبية للهجوم.\nالرؤية منخفضة لكن عنصر المفاجأة معكم.",
        "details": {
            "enemy_readiness": "ضعيفة",
            "moonlight": "غائم",
            "advantage": "مفاجأة كاملة"
        },
        "choices": [
            {
                "text": "⚔️ هجوم شامل ليلي",
                "risk": 50,
                "effects": {
                    "enemy_killed": 30,
                    "command": 25
                }
            },
            {
                "text": "🎯 غارة محدودة على القيادة",
                "risk": 40,
                "effects": {
                    "enemy_killed": 15,
                    "command": 20,
                    "intel": 30
                }
            },
            {
                "text": "🔍 استطلاع ليلي فقط",
                "risk": 25,
                "effects": {
                    "intel": 40
                }
            },
            {
                "text": "😴 الانتظار للصباح",
                "risk": 10,
                "effects": {
                    "command": -10
                }
            }
        ]
    },
    
    # 1️⃣6️⃣ جنود مرهقون
    {
        "id": "exhausted_troops",
        "title": "😴  إنذار: الجنود مرهقون",
        "header": "══════════════════════════════\n📢 تقرير طبي\n══════════════════════════════",
        "description": "الجنود مرهقون من القتال المتواصل.\nالإرهاق يؤثر على أدائهم وقدرتهم على القتال.",
        "details": {
            "fatigue_level": "شديد",
            "sleep_debt": "3 أيام",
            "effect": "تأخر في ردود الفعل"
        },
        "choices": [
            {
                "text": "😴 راحة 24 ساعة",
                "risk": 10,
                "effects": {
                    "soldiers": 30,
                    "morale": 25,
                    "time_loss": 1
                }
            },
            {
                "text": "🔄 تقسيم المهام - نصف يرتاح",
                "risk": 20,
                "effects": {
                    "soldiers": 20
                }
            },
            {
                "text": "⚡ مواصلة الضغط",
                "risk": 50,
                "effects": {
                    "soldiers": -30,
                    "morale": -20
                }
            },
            {
                "text": "💊 منشطات مؤقتة",
                "risk": 40,
                "effects": {
                    "soldiers": 15,
                    "mental": -15
                }
            }
        ]
    },
    
    # 1️⃣7️⃣ مدنيون يحتمون
    {
        "id": "civilians_shelter",
        "title": "👨‍👩‍👧  عائلات تحتمي",
        "header": "══════════════════════════════\n📢 تقرير إنساني\n══════════════════════════════",
        "description": "عشرات العائلات تحتمي في مبنى قريب.\nالقتال يقترب منهم.\nيطلبون المساعدة.",
        "details": {
            "families": "15 عائلة",
            "children": "20 طفلاً",
            "elderly": "8 مسنين"
        },
        "choices": [
            {
                "text": "🛡️ حماية المبنى وتأمينه",
                "risk": 50,
                "effects": {
                    "civilians": 40,
                    "self_respect": 30,
                    "command": 10,
                    "civilians_saved": 50
                }
            },
            {
                "text": "🚌 إخلائهم إلى مكان آمن",
                "risk": 40,
                "effects": {
                    "civilians": 35,
                    "self_respect": 25,
                    "time_loss": 2,
                    "civilians_saved": 50
                }
            },
            {
                "text": "🍞 تزويدهم بالطعام والماء",
                "risk": 20,
                "effects": {
                    "civilians": 25,
                    "supplies": -15
                }
            },
            {
                "text": "🚫 لا يمكن المساعدة",
                "risk": 0,
                "effects": {
                    "civilians": -40,
                    "self_respect": -30,
                    "mental": -20,
                    "civilians_killed": 50
                }
            }
        ]
    },
    
    # 1️⃣8️⃣ سلاح جديد
    {
        "id": "new_weapon",
        "title": "🔫  اكتشاف: سلاح متطور",
        "header": "══════════════════════════════\n📢 تقرير استثنائي\n══════════════════════════════",
        "description": "عثرنا على سلاح متطور في مخبأ سري.\nيمكنه تغيير موازين القوى.\nلكن استخدامه يحتاج تدريباً.",
        "details": {
            "weapon": "قناصة متطورة",
            "range": "2000 متر",
            "condition": "جديد"
        },
        "choices": [
            {
                "text": "🎯 تدريب قناص على استخدامه",
                "risk": 30,
                "effects": {
                    "new_weapon": 100,
                    "training": 30,
                    "time_loss": 2
                }
            },
            {
                "text": "🔬 دراسته أولاً",
                "risk": 20,
                "effects": {
                    "intel": 50,
                    "time_loss": 3
                }
            },
            {
                "text": "💣 بيعه في السوق السوداء",
                "risk": 40,
                "effects": {
                    "supplies": 80,
                    "command": -20
                }
            },
            {
                "text": "🎁 إرساله للقيادة",
                "risk": 10,
                "effects": {
                    "command": 40,
                    "self_respect": 15
                }
            }
        ]
    },
    
    # 1️⃣9️⃣ مرض في الكتيبة
    {
        "id": "illness",
        "title": "🤒  مرض منتشر",
        "header": "══════════════════════════════\n📢 تقرير طبي عاجل\n══════════════════════════════",
        "description": "مرض معوي ينتشر بين الجنود.\nالطعام الملوث هو السبب المحتمل.\nالوضع يزداد سوءاً.",
        "details": {
            "infected": "5 جنود",
            "severity": "متوسطة",
            "spread_rate": "سريع"
        },
        "choices": [
            {
                "text": "🏥 عزل المصابين وعلاجهم",
                "risk": 30,
                "effects": {
                    "soldiers": 20,
                    "time_loss": 2
                }
            },
            {
                "text": "💊 تطعيم الجميع",
                "risk": 20,
                "effects": {
                    "soldiers": 30,
                    "supplies": -20
                }
            },
            {
                "text": "🔄 تعقيم شامل للمعسكر",
                "risk": 15,
                "effects": {
                    "soldiers": 25,
                    "time_loss": 1
                }
            },
            {
                "text": "🚶 تجاهل المشكلة",
                "risk": 60,
                "effects": {
                    "soldiers": -40
                }
            }
        ]
    },
    
    # 2️⃣0️⃣ تكريم من القيادة
    {
        "id": "honor",
        "title": "🎖️  تكريم عسكري",
        "header": "══════════════════════════════\n📢 إعلان من القيادة\n══════════════════════════════",
        "description": "القيادة العليا تكرّم الكتيبة على بطولاتها.\nوسام شجاعة سيُمنح لأحد الجنود.\nعليك اختيار الجندي المستحق.",
        "details": {
            "award": "وسام الشجاعة",
            "ceremony": "غداً",
            "prestige": "عالي"
        },
        "choices": [
            {
                "text": "🏅 اختيار {soldier_name}",
                "risk": 10,
                "effects": {
                    "command": 30,
                    "soldiers": 25,
                    "morale": 30
                }
            },
            {
                "text": "👥 تصويت الجنود",
                "risk": 20,
                "effects": {
                    "soldiers": 35,
                    "cohesion": 30
                }
            },
            {
                "text": "🎲 اختيار عشوائي",
                "risk": 30,
                "effects": {
                    "soldiers": 15,
                    "cohesion": -10
                }
            },
            {
                "text": "🙏 رفض التكريم",
                "risk": 40,
                "effects": {
                    "command": -30,
                    "self_respect": 20
                }
            }
        ]
    }
]


def clamp(value: int, min_val: int = 0, max_val: int = 100) -> int:
    """دالة مساعدة لتقييد القيم"""
    return max(min_val, min(max_val, value))


class DynamicEventSystem:
    """نظام الأحداث الديناميكي - الاسم المطلوب في game.py"""
    
    def __init__(self, game):
        self.game = game
        self.event_history = []
        self.used_events = []
        
    def get_village_name(self) -> str:
        """توليد اسم قرية عشوائي"""
        villages = ["النخيل", "الزيتون", "الينابيع", "الرمال", "الواحة", 
                   "الأمل", "السلام", "الفجر", "الهلال", "الكرامة"]
        return random.choice(villages)
    
    def personalize_event(self, event: Dict) -> Dict:
        """تخصيص الحدث بإضافة عناصر ديناميكية"""
        event = event.copy()
        
        # استبدال اسم القرية
        if "{village_name}" in event.get("description", ""):
            event["description"] = event["description"].format(
                village_name=self.get_village_name()
            )
        
        # استبدال أسماء الجنود
        alive = [s for s in self.game.platoon if s.is_alive]
        
        if "{soldier_name}" in event.get("description", ""):
            if alive:
                soldier = random.choice(alive)
                event["description"] = event["description"].format(
                    soldier_name=soldier.name
                )
                event["soldier"] = soldier
                
        if "{soldier1}" in event.get("description", ""):
            if len(alive) >= 2:
                s1, s2 = random.sample(alive, 2)
                event["description"] = event["description"].format(
                    soldier1=s1.name,
                    soldier2=s2.name
                )
                event["soldier1"] = s1
                event["soldier2"] = s2
                
        return event
    
    def get_random_event(self) -> Optional[Dict]:
        """اختيار حدث عشوائي غير مكرر"""
        
        # 30% فرصة حدث
        if random.random() > 0.3:
            return None
        
        # تجنب تكرار آخر 3 أحداث
        available = [e for e in EVENTS_DATABASE if e["id"] not in self.used_events[-3:]]
        
        if not available:
            available = EVENTS_DATABASE
        
        event = random.choice(available)
        self.used_events.append(event["id"])
        
        return event
    
    def apply_effects(self, event: Dict, choice_index: int) -> List[str]:
        """تطبيق تأثيرات الاختيار"""
        
        choice = event["choices"][choice_index]
        effects = choice.get("effects", {})
        messages = []
        
        # نجاح المخاطرة
        risk = choice.get("risk", 0)
        success = random.randint(1, 100) > risk
        
        if not success and risk > 0:
            messages.append("❌ المخاطرة فشلت! الوضع أصبح أسوأ.")
            return messages
        
        # تطبيق التأثيرات
        for effect, value in effects.items():
            if effect == "command":
                self.game.reputation["among_command"] = clamp(
                    self.game.reputation["among_command"] + value
                )
                messages.append(f"🎖️  القيادة: {value:+d}%")
                
            elif effect == "soldiers":
                self.game.reputation["among_soldiers"] = clamp(
                    self.game.reputation["among_soldiers"] + value
                )
                messages.append(f"👥  الجنود: {value:+d}%")
                
            elif effect == "civilians":
                self.game.reputation["among_civilians"] = clamp(
                    self.game.reputation["among_civilians"] + value
                )
                messages.append(f"👨‍👩‍👧  المدنيون: {value:+d}%")
                
            elif effect == "soldiers_loyalty":
                for s in self.game.platoon:
                    if s.is_alive:
                        s.loyalty = clamp(s.loyalty + value)
                messages.append(f"❤️  الولاء: {value:+d}%")
                
            elif effect == "self_respect":
                self.game.self_respect = clamp(self.game.self_respect + value)
                messages.append(f"🎯  احترام الذات: {value:+d}%")
                
            elif effect == "mental":
                self.game.mental_health = clamp(self.game.mental_health + value)
                messages.append(f"🧠  الصحة النفسية: {value:+d}%")
                
            elif effect == "cohesion":
                self.game.platoon_cohesion = clamp(self.game.platoon_cohesion + value)
                messages.append(f"🔗  التماسك: {value:+d}%")
                
            elif effect == "supplies":
                messages.append(f"📦  إمدادات: +{value}")
                
            elif effect == "ammo":
                messages.append(f"💣  ذخيرة: +{value}")
                
            elif effect == "enemy_killed":
                self.game.enemies_killed += value
                messages.append(f"💀  قتلى العدو: +{value}")
                
            elif effect == "intel":
                messages.append(f"🔍  معلومات استخباراتية: +{value}")
                
            elif effect == "time_loss":
                self.game.days_in_service += value
                messages.append(f"⏳  تأخير: {value} يوم")
                
            elif effect == "training_all":
                for s in self.game.platoon:
                    if s.is_alive:
                        s.experience += value
                messages.append(f"🏋️  كل الجنود: +{value} خبرة")
                    
            elif effect == "training_snipers":
                for s in self.game.platoon:
                    if s.is_alive and s.role == "قناص":
                        s.experience += value
                messages.append(f"🎯  القناصة: +{value} خبرة")
                    
            elif effect == "training_medics":
                for s in self.game.platoon:
                    if s.is_alive and s.role == "مسعف":
                        s.experience += value
                messages.append(f"🏥  المسعفون: +{value} خبرة")
                    
            elif effect == "friendship_boost":
                messages.append(f"💞  علاقات محسنة")
                    
            elif effect == "new_weapon":
                messages.append(f"🔫  سلاح متطور: تم اكتسابه")
                    
            elif effect == "morale":
                for s in self.game.platoon:
                    if s.is_alive:
                        s.morale = clamp(s.morale + value)
                messages.append(f"📈  معنويات: {value:+d}%")
                
            elif effect == "civilians_saved":
                self.game.civilians_saved_total += value
                self.game.civilians_saved += value
                messages.append(f"🆘  مدنيون منقذون: +{value}")
                
            elif effect == "civilians_killed":
                self.game.civilians_killed_total += value
                self.game.civilian_casualties += value
                messages.append(f"💔  ضحايا مدنيون: +{value}")
                
            elif effect == "disobeyed_orders":
                self.game.disobeyed_orders += value
                messages.append(f"🛑  عصيان أوامر: +{value}")
                
            elif effect == "ethical_violations":
                self.game.ethical_violations_total += value
                self.game.ethical_violations += value
                messages.append(f"⚖️  انتهاكات أخلاقية: +{value}")
                
            elif effect == "ammo_gain":
                messages.append(f"🔫  ذخيرة مكتسبة: +{value}")
                
            elif effect == "ammo_save":
                messages.append(f"📦  توفير ذخيرة: +{value}%")
                
            elif effect == "rescue_chance":
                if random.randint(1, 100) < value:
                    messages.append("✅  تم إنقاذ الجندي!")
                else:
                    messages.append("❌  فشل الإنقاذ...")
        
        # إصابات محتملة
        if "risk_of_failure" in effects and random.randint(1, 100) < effects["risk_of_failure"]:
            casualties = random.randint(1, 2)
            self.game.soldiers_killed += casualties
            messages.append(f"💔  خسارة {casualties} جنود!")
                
        return messages
    
    def handle_event(self, event: Dict):
        """معالجة حدث كامل"""
        
        # تخصيص الحدث
        event = self.personalize_event(event)
        
        # عرض الحدث
        self.game._clear_screen()
        
        print(event.get("header", "═" * 70))
        print(f"\n{event['title']}\n")
        print("═" * 70)
        
        print(f"\n{event['description']}\n")
        
        # التفاصيل
        print("📋  التفاصيل:")
        for key, value in event.get("details", {}).items():
            print(f"   • {key}: {value}")
        
        print("\n" + "─" * 70)
        print("🎯  خياراتك:")
        print("─" * 70)
        
        # عرض الخيارات
        for i, choice in enumerate(event["choices"], 1):
            risk = choice.get("risk", 0)
            print(f"\n{i}. {choice['text']}")
            print(f"   ⚠️  مستوى الخطر: {risk}%")
        
        # اختيار اللاعب
        choice = self.game._get_input("\nاختر قرارك (1-{}): ".format(len(event["choices"])), 1, len(event["choices"])) - 1
        
        # تطبيق التأثيرات
        print("\n" + "─" * 40)
        print("📊  النتائج:")
        print("─" * 40)
        
        messages = self.apply_effects(event, choice)
        for msg in messages:
            print(msg)
        
        # تسجيل الحدث
        self.event_history.append({
            "event": event["id"],
            "choice": choice,
            "day": self.game.days_in_service
        })
        
        print("\n" + "─" * 40)
        input("\nاضغط Enter للمتابعة...")


# دالة مساعدة للتوافق مع الكود القديم
def get_random_event(game) -> Optional[Dict]:
    """الحصول على حدث عشوائي (للاستخدام في اللعبة)"""
    if random.random() < 0.3:  # 30% فرصة حدث
        system = DynamicEventSystem(game)
        return system.get_random_event()
    return None