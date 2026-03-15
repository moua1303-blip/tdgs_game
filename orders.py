"""
نظام الأوامر الديناميكية - أوامر حقيقية غير مكررة
الملف: orders.py
"""

import random
from typing import Dict, List, Any, Optional
from utils import logger

# ============== 50 أمراً مختلفاً (ويمكن توليد المزيد) ==============

ORDERS_DB = [
    # أوامر هجومية
    {
        "id": "dawn_attack",
        "type": "هجوم",
        "title": "عملية فجر الصحراء",
        "template": "تقوم قواتنا بعملية 'فجر الصحراء' لتدمير {target}. قواتك ستكون {role} في هذه العملية.",
        "targets": ["مخابئ الصواريخ", "مركز القيادة", "مستودع الذخيرة", "بطارية الدفاع الجوي", "محطة الاتصالات"],
        "roles": ["طليعة الهجوم", "قوة الاقتحام", "الدعم الناري", "الاحتياط المتحرك", "قوات التطهير"],
        "risk_factors": ["العدو مستعد جيداً", "المنطقة ملغومة", "دعم جوي للعدو", "مدنيون في المنطقة"],
        "options": [
            "تنفيذ الهجوم فجراً كما هو مخطط",
            "تأجيل الهجوم ليلاً لزيادة عنصر المفاجأة",
            "تقسيم القوات إلى محورين",
            "طلب قصف مدفعي تمهيدي",
            "الانسحاب وإعادة التخطيط"
        ]
    },
    {
        "id": "valley_assault",
        "type": "هجوم",
        "title": "اقتحام الوادي",
        "template": "العدو يتحصن في {target} بالوادي. عليك تطهير المنطقة خلال {hours} ساعات.",
        "targets": ["كهوف الجبل", "قرية استراتيجية", "جسر رئيسي", "نفق تحت الأرض"],
        "hours": [6, 12, 24, 48],
        "options": [
            "هجوم أمامي مع قصف مدفعي",
            "التسلل من الخلف",
            "تطويق المنطقة وحصارهم",
            "طلب تعزيزات قبل الهجوم",
            "الانسحاب - المهمة انتحارية"
        ]
    },
    {
        "id": "night_raid",
        "type": "هجوم",
        "title": "غارة ليلية",
        "template": "فرصة ذهبية! معسكر العدو في {location} يعاني من ضعف في الحراسة الليلية. نريد غارة خاطفة.",
        "location": ["المنطقة الشرقية", "التلال المحيطة", "وادي الملح", "سهل البقاع"],
        "options": [
            "تنفيذ الغارة بفرقة النخبة",
            "قصف بالهاون ثم اقتحام",
            "تأجيل الغارة لدراسة الوضع",
            "طلب دعم ناري من المدفعية",
            "إلغاء المهمة - قد يكون كمين"
        ]
    },
    
    # أوامر دفاعية
    {
        "id": "defend_base",
        "type": "دفاع",
        "title": "الدفاع عن القطاع الشمالي",
        "template": "العدو يحشد قواته لمهاجمة {location}. مهمتك الدفاع عن الموقع حتى وصول التعزيزات.",
        "locations": ["القطاع الشمالي", "المعبر الحدودي", "محطة الوقود", "مستودع المؤن"],
        "enemy_forces": ["كتيبة مشاة", "قوات النخبة", "ميليشيا محلية", "مرتزقة"],
        "options": [
            "الدفاع الثابت بحفر الخنادق",
            "الدفاع المتحرك والانسحاب التكتيكي",
            "نصب كمائن للعدو",
            "تفخيخ المنطقة قبل الانسحاب",
            "طلب دعم جوي عاجل"
        ]
    },
    {
        "id": "protect_village",
        "type": "دفاع",
        "title": "حماية المدنيين",
        "template": "قرية {village_name} تتعرض لهجوم. {civilians_count} مدني عالقون. أوامر القيادة: حماية المدنيين بأي ثمن.",
        "village_names": ["الناصرة", "الكرامة", "السلام", "الأمل", "الزيتون"],
        "civilians_count": [50, 100, 200, 500],
        "options": [
            "إخلاء المدنيين أولاً ثم المواجهة",
            "الدفاع عن القرية مع المدنيين",
            "طلب إخلاء جوي للمدنيين",
            "مهاجمة العدو لتشتيتهم",
            "الانسحاب وترك المدنيين (غير أخلاقي)"
        ]
    },
    {
        "id": "hold_the_line",
        "type": "دفاع",
        "title": "صمود حتى النهاية",
        "template": "العدو يشن هجوماً كاسحاً. أوامر القيادة: الصمود في {position} حتى آخر رصاصة.",
        "position": ["الخط الأمامي", "التلة 307", "جسر الشهداء", "مفرق النصر"],
        "options": [
            "القتال حتى آخر جندي",
            "الانسحاب المنظم تحت النار",
            "تفجير الجسر ومنع تقدمهم",
            "طلب قصف مدفعي على موقعنا",
            "محاولة اختراق الحصار"
        ]
    },
    
    # أوامر استطلاع
    {
        "id": "recon_mission",
        "type": "استطلاع",
        "title": "استطلاع عميق",
        "template": "معلوماتنا عن {target} قديمة. عليك بقيادة دورية استطلاع وجمع معلومات عن {info_needed}.",
        "targets": ["معسكر العدو", "تحركات العدو", "المنطقة الجبلية", "الطريق الساحلي"],
        "info_needed": ["القوة الفعلية", "تحركاتهم", "نقاط ضعفهم", "مخابئهم"],
        "options": [
            "التسلل ليلاً مع فريق صغير",
            "التمويه كمدنيين",
            "استخدام طائرة استطلاع",
            "إرسال جاسوس من السكان",
            "إلغاء المهمة - الخطر كبير"
        ]
    },
    {
        "id": "find_hideout",
        "type": "استطلاع",
        "title": "البحث عن مخبأ",
        "template": "الاستخبارات تشتبه بوجود {hideout_type} في المنطقة {region}. حدد الموقع بدقة.",
        "hideout_types": ["مخبأ صواريخ", "مستشفى ميداني", "مركز قيادة بديل", "مخزن ذخيرة"],
        "regions": ["أ", "ب", "ج", "د"],
        "options": [
            "تمشيط المنطقة بالكامل",
            "الاستعانة بطائرة بدون طيار",
            "الاستفسار من الأهالي",
            "نصب كمين لجاسوس العدو",
            "العودة - المنطقة ملغومة"
        ]
    },
    {
        "id": "scout_route",
        "type": "استطلاع",
        "title": "تأمين الطريق",
        "template": "قواتنا الرئيسية ستتحرك عبر {route} خلال {hours} ساعات. تأكد من خلو الطريق من الألغام والكمائن.",
        "route": ["الطريق الساحلي", "ممر جبلي", "طريق الإمدادات", "الخط الأخضر"],
        "hours": [12, 24, 48],
        "options": [
            "تمشيط الطريق بالكامل",
            "نقاط تفتيش مؤقتة",
            "الاستعانة بالكلاب البوليسية",
            "مرافقة القوات الرئيسية",
            "تأجيل التحرك - الوضع غير آمن"
        ]
    },
    
    # أوامر إنقاذ
    {
        "id": "rescue_pilot",
        "type": "إنقاذ",
        "title": "إنقاذ طيار",
        "template": "طائرتنا {plane_type} أسقطت خلف خطوط العدو. الطيار {pilot_name} حي ويختبئ في {location}.",
        "plane_types": ["إف-16", "مروحية أباتشي", "طائرة استطلاع", "طائرة شحن"],
        "pilot_names": ["العقيد أحمد", "النقيب عمر", "الرائد خالد", "الملازم أول سعيد"],
        "locations": ["غابة كثيفة", "قرية معادية", "منطقة جبلية", "وادٍ سري"],
        "options": [
            "فريق إنقاذ سريع بالتسلل",
            "طلب دعم جوي لتأمين المنطقة",
            "الهجوم على المنطقة لتشتيت العدو",
            "تفاوض مع أهالي القرية",
            "تركه - لا يمكن المجازفة"
        ]
    },
    {
        "id": "save_unit",
        "type": "إنقاذ",
        "title": "وحدة محاصرة",
        "template": "الوحدة {unit_name} محاصرة في {location} منذ {hours} ساعات. ذخيرتهم على وشك النفاد.",
        "unit_names": ["الضفادع البشرية", "المظليين", "القوات الخاصة", "كتيبة الهندسة"],
        "locations": ["مبنى محاصر", "تل استراتيجي", "منطقة صناعية", "مستودع قديم"],
        "hours": [12, 24, 48, 72],
        "options": [
            "اقتحام المنطقة لإخراجهم",
            "إسقاط ذخيرة جواً",
            "طلب دعم جوي كثيف",
            "تسلل ليلي لاختراق الحصار",
            "تضحية - لا يمكن الوصول"
        ]
    },
    {
        "id": "hostage_rescue",
        "type": "إنقاذ",
        "title": "رهائن مدنيين",
        "template": "مجموعة إرهابية تحتجز {hostages_count} مدني في {building}. عملية إنقاذ فورية مطلوبة.",
        "hostages_count": [10, 20, 35, 50],
        "building": ["مدرسة", "جامع", "مستشفى", "مبنى سكني"],
        "options": [
            "اقتحام سريع ومفاجئ",
            "محاولة التفاوض مع الخاطفين",
            "حصر المنطقة وقطع الإمدادات",
            "طلب فريق إنقاذ رهائن متخصص",
            "قصف المبنى - لا تفاوض مع الإرهابيين"
        ]
    },
    
    # أوامر انسحاب
    {
        "id": "strategic_withdrawal",
        "type": "انسحاب",
        "title": "انسحاب تكتيكي",
        "template": "العدو يتفوق علينا عدداً {enemy_ratio} مرات. أمر من القيادة: انسحاب منظم إلى {new_position}.",
        "enemy_ratio": [3, 5, 7, 10],
        "new_positions": ["الخط الدفاعي الثاني", "التلال الشرقية", "القرية الآمنة", "نقطة التجمع"],
        "options": [
            "انسحاب سريع مع تغطية نارية",
            "ترك قوة خلفية لتأخير العدو",
            "تفخيخ الموقع قبل المغادرة",
            "الانسحاب تحت جنح الظلام",
            "القتال حتى آخر جندي (عصيان)"
        ]
    },
    {
        "id": "retreat_with_civilians",
        "type": "انسحاب",
        "title": "إجلاء المدنيين",
        "template": "أمر بإخلاء {city} قبل وصول العدو. {civilians} مدني بحاجة للنقل. لديك {hours} ساعات فقط.",
        "cities": ["المدينة القديمة", "الحي السكني", "مخيم اللاجئين", "البلدة"],
        "civilians": [100, 250, 500, 1000],
        "hours": [6, 12, 24],
        "options": [
            "إخلاء المدنيين أولاً ثم الانسحاب",
            "الانسحاب فوراً وترك المدنيين",
            "طلب حافلات من القيادة",
            "تأمين ممر آمن للمدنيين",
            "القتال لتأخير العدو أثناء الإخلاء"
        ]
    },
    {
        "id": "fall_back",
        "type": "انسحاب",
        "title": "إعادة انتشار",
        "template": "القيادة تأمر بإعادة انتشار القوات إلى مواقع أكثر تحصيناً في {area}. انسحاب منظم خلال {hours} ساعات.",
        "area": ["التلال المرتفعة", "المنطقة الآمنة", "خلف النهر", "المعسكر الرئيسي"],
        "hours": [8, 16, 24],
        "options": [
            "انسحاب تدريجي مع تغطية",
            "قصف المواقع قبل المغادرة",
            "ترك ألغام في الطرق",
            "الانسحاب ليلاً",
            "البقاء - الموقع استراتيجي"
        ]
    },
    
    # أوامر استخباراتية
    {
        "id": "capture_officer",
        "type": "استخبارات",
        "title": "أسر ضابط",
        "template": "العميد {officer_name} موجود في {location}. القبض عليه حياً أولوية قصوى للاستخبارات.",
        "officer_names": ["سمير الجبور", "وليد الحسن", "رياض الأسد", "مروان عبدو"],
        "locations": ["منزله", "مقر القيادة", "اجتماع سري", "نقطة تفتيش"],
        "options": [
            "اقتحام المنزل ليلاً",
            "نصب كمين في الطريق",
            "تجنيد جاسوس من حراسه",
            "مراقبته أولاً لمعرفة تحركاته",
            "إلغاء المهمة - حمايته مشددة"
        ]
    },
    {
        "id": "intercept_message",
        "type": "استخبارات",
        "title": "اعتراض اتصالات",
        "template": "تمكن المهندسون من اختراق تردد العدو. لديك {hours} ساعات لاعتراض {message_type}.",
        "hours": [2, 4, 6],
        "message_types": ["خطة الهجوم القادمة", "تحركات القوات", "موعد الإمدادات", "كلمات السر"],
        "options": [
            "مراقبة والاستماع فقط",
            "محاولة تشويش اتصالاتهم",
            "بث معلومات مضللة",
            "تحديد موقع البث وقصفه",
            "طلب فريق استخبارات متخصص"
        ]
    },
    {
        "id": "double_agent",
        "type": "استخبارات",
        "title": "عميل مزدوج",
        "template": "أحد عملائنا في صفوف العدو يبلغ عن {info}. يطلب مقابلة عاجلة في {meeting_point}.",
        "info": ["خطة هجوم وشيكة", "نقاط ضعف في الدفاعات", "تحركات قيادة العدو", "مخازن سرية"],
        "meeting_point": ["مقهى قديم", "مزرعة مهجورة", "جسر ليلي", "منطقة محايدة"],
        "options": [
            "الذهاب للمقابلة بنفسك",
            "إرسال ضابط استخبارات",
            "طلب تأكيد هويته أولاً",
            "نصب كمين للعميل",
            "تجاهل الرسالة - قد تكون فخاً"
        ]
    },
    
    # أوامر إنسانية
    {
        "id": "medical_aid",
        "type": "إنساني",
        "title": "مساعدات طبية",
        "template": "وباء {disease} ينتشر في {area}. المستشفى يطلب مساعدة عاجلة.",
        "diseases": ["كوليرا", "حمى", "التهاب رئوي", "جفاف"],
        "areas": ["مخيم اللاجئين", "المناطق المتضررة", "القرى النائية", "الأحياء الفقيرة"],
        "options": [
            "إرسال المسعف مع أدوية",
            "تأمين وصول منظمة الصحة",
            "إخلاء الحالات الخطيرة",
            "طلب طائرة إخلاء طبي",
            "لا يمكن المساعدة - المهمة أولاً"
        ]
    },
    {
        "id": "orphanage",
        "type": "إنساني",
        "title": "دار أيتام",
        "template": "دار الأيتام في المدينة بحاجة لمواد غذائية وأدوية. الأطفال {children_count} يتيم بلا رعاية.",
        "children_count": [30, 50, 80, 100],
        "options": [
            "تخصيص جزء من المؤن لهم",
            "زيارة الدار ورفع معنوياتهم",
            "طلب منظمة اليونيسف للمساعدة",
            "تبني قضيتهم إعلامياً",
            "لا يوجد وقت للأعمال الخيرية"
        ]
    },
    {
        "id": "water_well",
        "type": "إنساني",
        "title": "مياه الشرب",
        "template": "قرية {village} تعاني من تلوث المياه. آبارهم توقفت عن العمل.",
        "village": ["المرج", "بيسان", "عرابة", "كفر كما"],
        "options": [
            "إرسال صهاريج مياه",
            "حفر بئر جديدة",
            "تنقية الآبار الموجودة",
            "طلب مساعدة منظمة اليونيسف",
            "لا يوجد موارد كافية"
        ]
    },
    
    # أوامر طارئة
    {
        "id": "chemical_attack",
        "type": "طارئ",
        "title": "هجوم كيميائي",
        "template": "تحذير! العدو قد يستخدم {weapon} في المنطقة. استعدوا للإجراءات الوقائية.",
        "weapons": ["غاز سام", "أسلحة كيميائية", "قنابل فسفورية", "مواد محظورة"],
        "options": [
            "توزيع أقنعة الغاز فوراً",
            "الانسحاب من المنطقة",
            "الاحتماء في الملاجئ",
            "طلب فرقة مكافحة الكيماوي",
            "تجاهل التحذير - قد يكون خدعة"
        ]
    },
    {
        "id": "ambush",
        "type": "طارئ",
        "title": "كمين مفاجئ",
        "template": "الوحدة المتقدمة وقعت في كمين في {location}. {casualties} إصابات حتى الآن.",
        "locations": ["مضيق جبلي", "شارع رئيسي", "مدخل القرية", "جسر استراتيجي"],
        "casualties": [2, 3, 5, 7],
        "options": [
            "التوجه فوراً لإنقاذهم",
            "طلب دعم جوي عاجل",
            "قصف مواقع الكمين",
            "الانسحاب وإعادة التجميع",
            "الاستسلام - الوضع ميؤوس منه"
        ]
    },
    {
        "id": "enemy_breakthrough",
        "type": "طارئ",
        "title": "اختراق للدفاعات",
        "template": "العدو اخترق الخط الدفاعي في {sector}! الوضع حرج جداً!",
        "sector": ["القطاع الغربي", "الجبهة الجنوبية", "منطقة التماس", "المحور الأوسط"],
        "options": [
            "التوجه personally لسد الثغرة",
            "قصف المنطقة بالمدفعية",
            "طلب تعزيزات فورية",
            "إخلاء المواقع القريبة",
            "الاستشهاد - سنقاتل حتى النهاية"
        ]
    },
    
    # أوامر لوجستية
    {
        "id": "supply_shortage",
        "type": "لوجستي",
        "title": "نقص مؤن",
        "template": "المؤن بدأت تنفد. لدينا طعام يكفي {days} أيام فقط.",
        "days": [3, 5, 7, 10],
        "options": [
            "تقليل الحصص اليومية",
            "إرسال فريق لجمع مؤن",
            "طلب إمدادات عاجلة",
            "مشاركة المؤن مع المدنيين",
            "الاستيلاء على مؤن العدو"
        ]
    },
    {
        "id": "ammo_count",
        "type": "لوجستي",
        "title": "عد الذخيرة",
        "template": "تقرير الذخيرة: {rifle_ammo} طلقة للرشاشات، {heavy_ammo} قذيفة للمدفعية.",
        "rifle_ammo": [500, 1000, 2000, 5000],
        "heavy_ammo": [50, 100, 200],
        "options": [
            "توزيع الذخيرة بالتساوي",
            "توفير الذخيرة للمدافع فقط",
            "طلب إعادة تموين عاجل",
            "محاولة أسر ذخيرة من العدو",
            "الاستعداد للقتال حتى آخر طلقة"
        ]
    },
    {
        "id": "vehicle_repair",
        "type": "لوجستي",
        "title": "أعطال ميكانيكية",
        "template": "{vehicles_count} آليات عسكرية بحاجة لصيانة عاجلة. قطع الغيار غير متوفرة.",
        "vehicles_count": [2, 3, 5, 8],
        "options": [
            "محاولة الإصلاح بقطع بديلة",
            "سحب الآليات للخلف",
            "طلب ورشة متنقلة",
            "التخلي عن الآليات",
            "تفخيخها وتركها للعدو"
        ]
    }
]


class DynamicOrderSystem:
    """نظام الأوامر الديناميكي"""
    
    def __init__(self, game):
        self.game = game
        self.used_orders = []
        
    def generate_order(self) -> Dict:
        """توليد أمر جديد فريد"""
        
        # اختيار أمر غير مكرر
        available = [o for o in ORDERS_DB if o["id"] not in self.used_orders[-5:]]
        if not available:
            available = ORDERS_DB
            
        order = random.choice(available).copy()
        self.used_orders.append(order["id"])
        
        # تخصيص الأمر
        personalized = self._personalize_order(order)
        return personalized
    
    def _personalize_order(self, order: Dict) -> Dict:
        """تخصيص الأمر بإضافة تفاصيل عشوائية"""
        
        order = order.copy()
        
        # توليد الوصف حسب القالب
        if "template" in order:
            template = order["template"]
            
            # استبدال المتغيرات
            if "target" in order.get("targets", []):
                template = template.replace("{target}", random.choice(order["targets"]))
            
            if "role" in order.get("roles", []):
                template = template.replace("{role}", random.choice(order["roles"]))
                
            if "hours" in order.get("hours", []):
                template = template.replace("{hours}", str(random.choice(order["hours"])))
                
            if "location" in order.get("locations", []):
                template = template.replace("{location}", random.choice(order["locations"]))
                
            if "enemy_forces" in order.get("enemy_forces", []):
                template = template.replace("{enemy_forces}", random.choice(order["enemy_forces"]))
                
            if "village_name" in order.get("village_names", []):
                template = template.replace("{village_name}", random.choice(order["village_names"]))
                
            if "civilians_count" in order.get("civilians_count", []):
                template = template.replace("{civilians_count}", str(random.choice(order["civilians_count"])))
                
            if "info_needed" in order.get("info_needed", []):
                template = template.replace("{info_needed}", random.choice(order["info_needed"]))
                
            if "hideout_type" in order.get("hideout_types", []):
                template = template.replace("{hideout_type}", random.choice(order["hideout_types"]))
                
            if "region" in order.get("regions", []):
                template = template.replace("{region}", random.choice(order["regions"]))
                
            if "plane_type" in order.get("plane_types", []):
                template = template.replace("{plane_type}", random.choice(order["plane_types"]))
                
            if "pilot_name" in order.get("pilot_names", []):
                template = template.replace("{pilot_name}", random.choice(order["pilot_names"]))
                
            if "unit_name" in order.get("unit_names", []):
                template = template.replace("{unit_name}", random.choice(order["unit_names"]))
                
            if "enemy_ratio" in order.get("enemy_ratio", []):
                template = template.replace("{enemy_ratio}", str(random.choice(order["enemy_ratio"])))
                
            if "new_position" in order.get("new_positions", []):
                template = template.replace("{new_position}", random.choice(order["new_positions"]))
                
            if "city" in order.get("cities", []):
                template = template.replace("{city}", random.choice(order["cities"]))
                
            if "civilians" in order.get("civilians", []):
                template = template.replace("{civilians}", str(random.choice(order["civilians"])))
                
            if "officer_name" in order.get("officer_names", []):
                template = template.replace("{officer_name}", random.choice(order["officer_names"]))
                
            if "message_type" in order.get("message_types", []):
                template = template.replace("{message_type}", random.choice(order["message_types"]))
                
            if "disease" in order.get("diseases", []):
                template = template.replace("{disease}", random.choice(order["diseases"]))
                
            if "area" in order.get("areas", []):
                template = template.replace("{area}", random.choice(order["areas"]))
                
            if "children_count" in order.get("children_count", []):
                template = template.replace("{children_count}", str(random.choice(order["children_count"])))
                
            if "weapon" in order.get("weapons", []):
                template = template.replace("{weapon}", random.choice(order["weapons"]))
                
            if "casualties" in order.get("casualties", []):
                template = template.replace("{casualties}", str(random.choice(order["casualties"])))
                
            if "position" in order.get("position", []):
                template = template.replace("{position}", random.choice(order["position"]))
                
            if "route" in order.get("route", []):
                template = template.replace("{route}", random.choice(order["route"]))
                
            if "hostages_count" in order.get("hostages_count", []):
                template = template.replace("{hostages_count}", str(random.choice(order["hostages_count"])))
                
            if "building" in order.get("building", []):
                template = template.replace("{building}", random.choice(order["building"]))
                
            if "meeting_point" in order.get("meeting_point", []):
                template = template.replace("{meeting_point}", random.choice(order["meeting_point"]))
                
            if "village" in order.get("village", []):
                template = template.replace("{village}", random.choice(order["village"]))
                
            if "sector" in order.get("sector", []):
                template = template.replace("{sector}", random.choice(order["sector"]))
                
            if "days" in order.get("days", []):
                template = template.replace("{days}", str(random.choice(order["days"])))
                
            if "rifle_ammo" in order.get("rifle_ammo", []):
                template = template.replace("{rifle_ammo}", str(random.choice(order["rifle_ammo"])))
                
            if "heavy_ammo" in order.get("heavy_ammo", []):
                template = template.replace("{heavy_ammo}", str(random.choice(order["heavy_ammo"])))
                
            if "vehicles_count" in order.get("vehicles_count", []):
                template = template.replace("{vehicles_count}", str(random.choice(order["vehicles_count"])))
                
            order["description"] = template
            # لا نحذف template فقد نحتاجها مستقبلاً
        
        # إضافة تفاصيل الموقع والطقس
        location_name = self.game.map.locations[self.game.map.current_location]['name']
        
        order["full_description"] = (
            f"📋 الأمر: {order['title']}\n\n"
            f"{order['description']}\n\n"
            f"📍 موقعك الحالي: {location_name}\n"
            f"🌤️  حالة الطقس: {self.game.weather.icon} {self.game.weather.arabic_name}\n"
        )
        
        # توليد خيارات مخصصة (خلط عشوائي)
        options = order["options"].copy()
        random.shuffle(options)
        order["display_options"] = options[:5]  # 5 خيارات
        
        return order


# دالة مساعدة للحصول على أمر جديد
def get_dynamic_order(game) -> Dict:
    """الحصول على أمر ديناميكي جديد"""
    system = DynamicOrderSystem(game)
    return system.generate_order()