import random
from typing import List, Optional
from enums import Personality, Weapon, Equipment, Rank, Wound
from constants import WEAPONS_BY_ROLE, EQUIPMENT_BY_ROLE
from utils import clamp, logger

class Soldier:
    """فئة الجندي المتطورة"""
    
    def __init__(self, name: str, role: str, age: int, 
                 family_status: str, personality: Personality):
        
        # معلومات أساسية
        self.name = name
        self.role = role
        self.age = age
        self.family_status = family_status
        self.personality = personality
        
        # إحصائيات حيوية
        self.health = random.randint(80, 100)
        self.mental = random.randint(70, 100)
        self.morale = random.randint(60, 100)
        self.loyalty = random.randint(70, 100)
        self.is_alive = True
        
        # نظام التطوير
        self.experience = random.randint(0, 30)
        self.rank = self._calculate_rank()
        self.kills = 0
        self.battles_participated = 0
        self.medals = []
        
        # المعدات
        self.weapon = WEAPONS_BY_ROLE.get(role, Weapon.AK47)
        self.equipment = EQUIPMENT_BY_ROLE.get(role)
        
        # الإصابات
        self.wounds: List[Wound] = []
        
        # إحصائيات إضافية
        self.saves_count = 0  # مرات إنقاذ زملاء
        self.battles_won = 0
        
        logger.info(f"تم إنشاء جندي جديد: {self.name} - {self.role} ({personality.arabic_name})")
    
    def __str__(self) -> str:
        status = "✅" if self.is_alive else "💀"
        wounds_str = f" | إصابات: {len(self.wounds)}" if self.wounds else ""
        weapon_name = self.weapon.arabic_name
        
        return (f"{status} {self.name:<8} | {self.role:<12} | "
                f"{self.personality.arabic_name:<6} | "
                f"رتبة: {self.rank.arabic_name:<8} | {weapon_name} | "
                f"صحة:{self.health:3}% | نفسية:{self.mental:3}% | "
                f"ولاء:{self.loyalty:3}%{wounds_str}")
    
    def _calculate_rank(self) -> Rank:
        """تحديد الرتبة بناءً على الخبرة"""
        if self.experience >= 350:
            return Rank.LEGEND
        elif self.experience >= 200:
            return Rank.ELITE
        elif self.experience >= 100:
            return Rank.VETERAN
        elif self.experience >= 50:
            return Rank.SOLDIER
        else:
            return Rank.RECRUIT
    
    def combat_power(self, weather_mult: float = 1.0, 
                     location_mult: float = 1.0) -> float:
        """حساب القوة القتالية للجندي"""
        
        # القاعدة الأساسية
        power = 50.0
        
        # خبرة
        power += self.experience * 0.5
        
        # سلاح
        power += self.weapon.damage * self.weapon.multiplier
        
        # شخصية
        if self.personality == Personality.BRAVE:
            power *= 1.2
        elif self.personality == Personality.COWARD:
            power *= 0.7
            
        # رتبة
        power *= self.rank.multiplier
        
        # الصحة
        power *= (self.health / 100.0)
        power *= (self.mental / 100.0)
        
        # معنويات
        power *= (self.morale / 100.0)
        
        # إصابات
        for wound in self.wounds:
            power *= wound.combat_mult
        
        # مؤثرات خارجية
        power *= weather_mult
        power *= location_mult
        
        return max(5, power)  # لا تقل عن 5
    
    def add_experience(self, amount: int) -> Optional[str]:
        """إضافة خبرة وترقية محتملة"""
        old_rank = self.rank
        self.experience += amount
        self.rank = self._calculate_rank()
        
        if old_rank != self.rank:
            msg = f"🌟 {self.name} ترقى إلى رتبة {self.rank.arabic_name}!"
            logger.info(msg)
            return msg
        return None
    
    def add_wound(self, wound: Wound):
        """إصابة جديدة"""
        self.wounds.append(wound)
        
        # تأثيرات الإصابة
        self.health = clamp(self.health - wound.health_damage)
        self.mental = clamp(self.mental - wound.mental_damage)
        
        logger.warning(f"{self.name} أصيب بـ {wound.arabic_name}")
        
        if self.health <= 0:
            self.is_alive = False
            logger.error(f"{self.name} استشهد!")
    
    def treat_wounds(self, medic_skill: float = 1.0) -> str:
        """علاج الإصابات"""
        if not self.wounds:
            return "لا يوجد إصابات"
        
        healed = []
        for wound in self.wounds[:]:
            if random.random() < 0.7 * medic_skill:
                self.wounds.remove(wound)
                healed.append(wound.arabic_name)
        
        if healed:
            self.health = clamp(self.health + 20)
            self.mental = clamp(self.mental + 10)
            logger.info(f"✅ تم علاج {self.name}: {', '.join(healed)}")
            return f"✅ تم علاج: {', '.join(healed)}"
        
        return "❌ فشل العلاج"
    
    def take_damage(self, amount: int) -> bool:
        """تلقي الضرر"""
        # تخفيف الضرر حسب الرتبة
        amount = int(amount / self.rank.multiplier)
        
        self.health = clamp(self.health - amount)
        
        # احتمال إصابة إضافية
        if random.random() < 0.3 and self.health > 0:
            wound = random.choice(list(Wound))
            self.add_wound(wound)
        
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            logger.error(f"{self.name} استشهد!")
            return True
        
        return False
    
    def mental_damage(self, amount: int) -> bool:
        """ضرر نفسي"""
        self.mental = clamp(self.mental - amount)
        if self.mental <= 0:
            logger.warning(f"{self.name} يعاني من انهيار نفسي!")
        return self.mental == 0
    
    def boost_morale(self, amount: int):
        """رفع المعنويات"""
        self.morale = clamp(self.morale + amount)
        self.loyalty = clamp(self.loyalty + amount // 2)
        self.mental = clamp(self.mental + amount // 3)
    
    def to_dict(self) -> dict:
        """تحويل إلى قاموس للحفظ"""
        return {
            'name': self.name,
            'role': self.role,
            'age': self.age,
            'family_status': self.family_status,
            'personality': self.personality.name,
            'health': self.health,
            'mental': self.mental,
            'morale': self.morale,
            'loyalty': self.loyalty,
            'is_alive': self.is_alive,
            'experience': self.experience,
            'kills': self.kills,
            'wounds': [w.name for w in self.wounds]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """إنشاء جندي من قاموس محفوظ"""
        personality = Personality[data['personality']]
        soldier = cls(
            data['name'],
            data['role'],
            data['age'],
            data['family_status'],
            personality
        )
        soldier.health = data['health']
        soldier.mental = data['mental']
        soldier.morale = data['morale']
        soldier.loyalty = data['loyalty']
        soldier.is_alive = data['is_alive']
        soldier.experience = data['experience']
        soldier.kills = data['kills']
        soldier.wounds = [Wound[w] for w in data['wounds']]
        soldier.rank = soldier._calculate_rank()
        
        return soldier