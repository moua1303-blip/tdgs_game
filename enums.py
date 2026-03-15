from enum import Enum

class Weather(Enum):
    """حالات الطقس"""
    SUNNY = ("☀️", "مشمس", 1.0, 1.0, 1.0)
    RAINY = ("🌧️", "ممطر", 0.8, 0.9, 0.7)
    FOGGY = ("🌫️", "ضباب", 0.6, 0.8, 0.3)
    NIGHT = ("🌙", "ليل", 0.9, 0.7, 0.4)
    STORM = ("⛈️", "عاصفة", 0.5, 0.6, 0.2)
    
    def __init__(self, icon, name, attack, defense, visibility):
        self.icon = icon
        self.arabic_name = name
        self.attack_mult = attack
        self.defense_mult = defense
        self.visibility = visibility

class Wound(Enum):
    """أنواع الإصابات"""
    LIGHT = ("🩹", "جرح طفيف", 5, 0, 0.9)
    BLEEDING = ("🩸", "نزيف", 2, 0, 0.7)
    FRACTURE = ("🦴", "كسر", 15, 0, 0.5)
    SHELL_SHOCK = ("💥", "صدمة نفسية", 0, 10, 0.8)
    CRITICAL = ("🚑", "إصابة خطيرة", 30, 0, 0.3)
    
    def __init__(self, icon, name, health_damage, mental_damage, combat_mult):
        self.icon = icon
        self.arabic_name = name
        self.health_damage = health_damage
        self.mental_damage = mental_damage
        self.combat_mult = combat_mult

class Weapon(Enum):
    """الأسلحة"""
    AK47 = ("AK-47", "rifle", 20, "متوسط", 1.0)
    SNIPER = ("قناص", "sniper", 40, "بعيد", 1.5)
    MACHINE_GUN = ("رشاش", "heavy", 30, "قصير", 1.2)
    SHOTGUN = ("شوزن", "shotgun", 25, "قصير جداً", 1.1)
    PISTOL = ("مسدس", "pistol", 10, "قصير", 0.8)
    
    def __init__(self, name, weapon_type, damage, range_desc, multiplier):
        self.arabic_name = name
        self.type = weapon_type
        self.damage = damage
        self.range_desc = range_desc
        self.multiplier = multiplier

class Equipment(Enum):
    """المعدات الخاصة"""
    MEDKIT = ("حقيبة إسعاف", "medical", 30, "يعالج 30%")
    GRENADE = ("قنبلة", "explosive", 50, "ضرر شامل")
    RADIO = ("راديو", "communication", 15, "تعزيزات أسرع")
    BINOCULARS = ("منظار", "recon", 25, "استطلاع أفضل")
    
    def __init__(self, name, equip_type, bonus, description):
        self.arabic_name = name
        self.type = equip_type
        self.bonus = bonus
        self.description = description

class Rank(Enum):
    """الرتب العسكرية"""
    RECRUIT = (0, "مجند", 1.0, 10)
    SOLDIER = (50, "جندي", 1.2, 20)
    VETERAN = (100, "محارب قديم", 1.5, 30)
    ELITE = (200, "نخبة", 2.0, 40)
    LEGEND = (350, "أسطورة", 3.0, 50)
    
    def __init__(self, xp, name, multiplier, bonus_damage):
        self.xp = xp
        self.arabic_name = name
        self.multiplier = multiplier
        self.bonus_damage = bonus_damage

class Personality(Enum):
    """شخصيات الجنود"""
    BRAVE = ("شجاع", 1.2, 0.9, 15, "بأمرك قائد! سأقتحمهم!")
    RATIONAL = ("عقلاني", 1.0, 1.1, 5, "لنخطط جيداً قبل الهجوم")
    EMOTIONAL = ("عاطفي", 0.9, 1.2, 10, "فكر في الجنود الجرحى أولاً")
    COWARD = ("جبان", 0.7, 0.8, -10, "أخاف أن نموت جميعاً...")
    RELIGIOUS = ("متدين", 1.1, 1.1, 15, "الله معنا، لن نخاف")
    RECKLESS = ("متهور", 1.3, 0.8, 5, "اقتحام! لا توقف!")
    WISE = ("حكيم", 1.0, 1.2, 20, "سأحمي الجميع، ثق بي")
    
    def __init__(self, name, attack_mult, defense_mult, morale_boost, phrase):
        self.arabic_name = name
        self.attack_mult = attack_mult
        self.defense_mult = defense_mult
        self.morale_boost = morale_boost
        self.phrase = phrase

class Location(Enum):
    """مواقع الخريطة"""
    BASE = ("🏠", "القاعدة", "آمن نسبياً", 0)
    VALLEY = ("⛰️", "الوادي", "منطقة مكشوفة", 50)
    FOREST = ("🌳", "الغابة", "غطاء طبيعي", 25)
    MOUNTAINS = ("🏔️", "الجبال", "موقع استراتيجي", 35)
    ENEMY_CAMP = ("⚠️", "معسكر العدو", "قلب الخطر", 90)
    
    def __init__(self, icon, name, description, danger):
        self.icon = icon
        self.arabic_name = name
        self.description = description
        self.danger = danger