"""
نظام الذخيرة المتقدم
الملف: ammo.py
"""

import random
from enum import Enum
from typing import Dict, List, Optional
from utils import clamp, logger


class AmmoType(Enum):
    """أنواع الذخيرة"""
    RIFLE = ("طلقة رشاش", 500, 10)      # الاسم، الكمية الابتدائية، استهلاك كل معركة
    SNIPER = ("طلقة قناص", 50, 2)
    HEAVY = ("قذيفة مدفع", 30, 1)
    GRENADE = ("قنبلة", 20, 1)
    PISTOL = ("طلقة مسدس", 200, 5)
    SHOTGUN = ("طلقة شوزن", 100, 3)
    
    def __init__(self, name: str, initial: int, consumption: int):
        self.arabic_name = name
        self.initial = initial
        self.base_consumption = consumption


class AmmoSystem:
    """نظام إدارة الذخيرة"""
    
    def __init__(self):
        self.ammo: Dict[AmmoType, int] = {}
        self.max_capacity: Dict[AmmoType, int] = {}
        self.initialize_ammo()
        logger.info("🔫 نظام الذخيرة initialized")
    
    def initialize_ammo(self):
        """تهيئة الذخيرة الأولية"""
        for ammo_type in AmmoType:
            self.ammo[ammo_type] = ammo_type.initial
            self.max_capacity[ammo_type] = ammo_type.initial * 2
    
    def initialize_for_platoon(self, platoon: List) -> Dict[str, int]:
        """
        تهيئة الذخيرة بناءً على أفراد الكتيبة
        هذه الدالة تستدعى من game.py
        """
        # تقدير احتياجات الكتيبة
        rifle_count = 0
        sniper_count = 0
        heavy_count = 0
        pistol_count = 0
        shotgun_count = 0
        
        for soldier in platoon:
            if hasattr(soldier, 'role'):
                role = soldier.role
                if role == "قناص":
                    sniper_count += 1
                elif role == "مدفعي":
                    heavy_count += 1
                elif role in ["مسعف", "اتصالات"]:
                    pistol_count += 1
                elif role == "مهندس قتالي":
                    shotgun_count += 1
                else:  # استطلاع، جندي مشاة
                    rifle_count += 1
        
        # زيادة الذخيرة حسب عدد الجنود
        self.ammo[AmmoType.RIFLE] += rifle_count * 100
        self.ammo[AmmoType.SNIPER] += sniper_count * 15
        self.ammo[AmmoType.HEAVY] += heavy_count * 8
        self.ammo[AmmoType.PISTOL] += pistol_count * 40
        self.ammo[AmmoType.SHOTGUN] += shotgun_count * 25
        
        # تحديث السعة القصوى
        for ammo_type in AmmoType:
            self.max_capacity[ammo_type] = max(
                self.max_capacity[ammo_type],
                self.ammo[ammo_type] * 2
            )
        
        logger.info(f"تم تهيئة الذخيرة لـ {len(platoon)} جنود")
        return self.get_status()
    
    def has_ammo(self, ammo_type: AmmoType, amount: int = 1) -> bool:
        """التحقق من وجود ذخيرة كافية"""
        return self.ammo.get(ammo_type, 0) >= amount
    
    def use_ammo(self, ammo_type: AmmoType, amount: int = 1) -> bool:
        """استخدام ذخيرة"""
        if self.has_ammo(ammo_type, amount):
            self.ammo[ammo_type] -= amount
            self.ammo[ammo_type] = max(0, self.ammo[ammo_type])
            return True
        return False
    
    def use_for_battle(self, weapon_category: str, intensity: float = 1.0) -> bool:
        """
        استخدام الذخيرة في معركة حسب فئة السلاح
        intensity: شدة المعركة (0.5 = معركة خفيفة، 1.0 = معركة عادية، 2.0 = معركة شرسة)
        """
        # تحديد نوع الذخيرة حسب الفئة
        ammo_map = {
            "rifle": AmmoType.RIFLE,
            "sniper": AmmoType.SNIPER,
            "heavy": AmmoType.HEAVY,
            "grenade": AmmoType.GRENADE,
            "pistol": AmmoType.PISTOL,
            "shotgun": AmmoType.SHOTGUN
        }
        
        ammo_type = ammo_map.get(weapon_category, AmmoType.RIFLE)
        consumption = max(1, int(ammo_type.base_consumption * intensity))
        
        # استهلاك عشوائي +/- 20%
        consumption = random.randint(
            max(1, int(consumption * 0.8)),
            int(consumption * 1.2)
        )
        
        return self.use_ammo(ammo_type, consumption)
    
    def add_ammo(self, ammo_type: AmmoType, amount: int):
        """إضافة ذخيرة"""
        current = self.ammo.get(ammo_type, 0)
        max_cap = self.max_capacity.get(ammo_type, ammo_type.initial * 3)
        self.ammo[ammo_type] = min(current + amount, max_cap)
        logger.info(f"✅ تم إضافة {amount} {ammo_type.arabic_name}")
    
    def get_status(self) -> Dict[str, int]:
        """الحصول على حالة الذخيرة"""
        return {amt.arabic_name: self.ammo.get(amt, 0) for amt in AmmoType}
    
    def display_status(self) -> str:
        """عرض حالة الذخيرة بشكل نصي"""
        lines = ["🔫  حالة الذخيرة:"]
        for ammo_type in AmmoType:
            count = self.ammo.get(ammo_type, 0)
            max_cap = self.max_capacity.get(ammo_type, ammo_type.initial * 2)
            
            # شريط تقدم
            if max_cap > 0:
                percent = int((count / max_cap) * 10)
                bar = "█" * percent + "░" * (10 - percent)
            else:
                bar = "░" * 10
            
            warning = ""
            if count < ammo_type.base_consumption * 3:
                warning = " ⚠️"
            elif count == 0:
                warning = " ❌"
            
            lines.append(f"   {ammo_type.arabic_name}: [{bar}] {count}/{max_cap}{warning}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """تحويل إلى قاموس للحفظ"""
        return {
            'ammo': {amt.name: self.ammo.get(amt, 0) for amt in AmmoType},
            'max_capacity': {amt.name: self.max_capacity.get(amt, amt.initial * 2) for amt in AmmoType}
        }
    
    def from_dict(self, data: dict):
        """تحميل من قاموس محفوظ"""
        for amt in AmmoType:
            if amt.name in data['ammo']:
                self.ammo[amt] = data['ammo'][amt.name]
            if amt.name in data['max_capacity']:
                self.max_capacity[amt] = data['max_capacity'][amt.name]