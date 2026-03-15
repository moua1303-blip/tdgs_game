"""
نظام العلاقات بين الجنود - نسخة محسنة
الملف: relationships.py
"""

import random
from typing import List, Dict, Optional, Tuple
from utils import clamp, logger
from soldier import Soldier

class Relationship:
    """فئة تمثل علاقة بين جنديين"""
    
    def __init__(self, soldier1: Soldier, soldier2: Soldier):
        self.soldier1 = soldier1
        self.soldier2 = soldier2
        self.trust = random.randint(30, 70)  # 0-100
        self.respect = random.randint(30, 70)
        self.interactions = 0
        self.type = self.determine_type()
        
    def determine_type(self) -> str:
        """تحديد نوع العلاقة بناءً على القيم"""
        avg = (self.trust + self.respect) / 2
        
        if avg > 80:
            return "friends"
        elif avg > 60:
            return "close"
        elif avg > 40:
            return "neutral"
        elif avg > 20:
            return "tense"
        else:
            return "rivals"
    
    def update(self):
        """تحديث العلاقة"""
        self.interactions += 1
        
        # تغير طفيف مع الوقت
        if random.random() < 0.1:
            self.trust += random.randint(-2, 2)
            self.respect += random.randint(-2, 2)
            
        self.trust = clamp(self.trust)
        self.respect = clamp(self.respect)
        self.type = self.determine_type()
    
    def get_effect(self) -> float:
        """تأثير العلاقة على المعنويات"""
        effects = {
            "friends": 0.15,   # +15% معنويات
            "close": 0.10,      # +10%
            "neutral": 0.0,
            "tense": -0.10,     # -10%
            "rivals": -0.15     # -15%
        }
        return effects.get(self.type, 0.0)
    
    def get_morale_effect(self, soldier: Soldier) -> int:
        """تأثير العلاقة على جندي معين"""
        base_effect = self.get_effect() * 100
        
        # من هو الصديق؟
        if soldier == self.soldier1:
            other = self.soldier2
        else:
            other = self.soldier1
        
        # تأثير إضافي إذا كان الآخر في خطر
        if not other.is_alive:
            return -30  # حزن شديد
        
        return int(base_effect)


class RelationshipManager:
    """مدير العلاقات بين الجنود"""
    
    def __init__(self):
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.max_relationships = 50  # حد أقصى لتجنب تضخم الذاكرة
    
    def get_relationship(self, soldier1: Soldier, soldier2: Soldier) -> Optional[Relationship]:
        """الحصول على العلاقة بين جنديين"""
        key = tuple(sorted([soldier1.name, soldier2.name]))
        return self.relationships.get(key)
    
    def create_relationship(self, soldier1: Soldier, soldier2: Soldier) -> Relationship:
        """إنشاء علاقة جديدة"""
        key = tuple(sorted([soldier1.name, soldier2.name]))
        
        # إذا تجاوزنا الحد الأقصى، نحذف أقدم علاقة
        if len(self.relationships) >= self.max_relationships:
            oldest_key = min(self.relationships.keys(), 
                           key=lambda k: self.relationships[k].interactions)
            del self.relationships[oldest_key]
        
        rel = Relationship(soldier1, soldier2)
        self.relationships[key] = rel
        return rel
    
    def update_relationships(self, active_soldiers: List[Soldier]):
        """تحديث العلاقات فقط للجنود الذين شاركوا في المهمة"""
        for i, s1 in enumerate(active_soldiers):
            for s2 in active_soldiers[i+1:]:
                rel = self.get_relationship(s1, s2)
                if rel:
                    # زيادة التفاعل بناءً على العمل الجماعي
                    rel.interactions += 1
                    rel.trust = clamp(rel.trust + random.randint(1, 3))
                    rel.respect = clamp(rel.respect + random.randint(1, 2))
                    rel.determine_type()
                else:
                    # إنشاء علاقة جديدة إذا لم تكن موجودة
                    self.create_relationship(s1, s2)
    
    def get_platoon_morale_effect(self, platoon: List[Soldier]) -> int:
        """تأثير جميع العلاقات على معنويات الكتيبة"""
        total_effect = 0
        
        for i, s1 in enumerate(platoon):
            if not s1.is_alive:
                continue
                
            soldier_effect = 0
            for j, s2 in enumerate(platoon):
                if i == j or not s2.is_alive:
                    continue
                    
                rel = self.get_relationship(s1, s2)
                if rel:
                    soldier_effect += rel.get_morale_effect(s1)
            
            # متوسط التأثير على الجندي
            soldier_effect = soldier_effect / max(1, len([s for s in platoon if s.is_alive]) - 1)
            total_effect += soldier_effect
        
        return int(total_effect / max(1, len([s for s in platoon if s.is_alive])))
    
    def handle_death(self, deceased: Soldier, platoon: List[Soldier]) -> List[str]:
        """معالجة وفاة جندي وتأثيرها على العلاقات"""
        messages = []
        
        for soldier in platoon:
            if soldier.is_alive and soldier != deceased:
                rel = self.get_relationship(soldier, deceased)
                if rel:
                    effect = rel.get_morale_effect(soldier)
                    soldier.morale = clamp(soldier.morale + effect)
                    soldier.mental = clamp(soldier.mental + effect // 2)
                    
                    if effect < -20:
                        messages.append(f"💔 {soldier.name} حزين جداً لوفاة {deceased.name}")
                    elif effect < -10:
                        messages.append(f"😢 {soldier.name} متأثر باستشهاد {deceased.name}")
        
        return messages
    
    def trigger_interaction(self, event_type: str, day: int) -> List[str]:
        """تفاعل عشوائي بين الجنود (للأحداث)"""
        messages = []
        
        # اختيار علاقة عشوائية
        if not self.relationships:
            return messages
            
        rel = random.choice(list(self.relationships.values()))
        
        if event_type == "argue":
            # خلاف
            rel.trust -= random.randint(5, 15)
            rel.respect -= random.randint(5, 10)
            rel.trust = clamp(rel.trust)
            rel.respect = clamp(rel.respect)
            rel.type = rel.determine_type()
            messages.append(f"🗣️  خلاف بين {rel.soldier1.name} و {rel.soldier2.name}")
            
        elif event_type == "one_saved_other":
            # أحدهم أنقذ الآخر
            rel.trust += random.randint(10, 20)
            rel.respect += random.randint(10, 15)
            rel.trust = clamp(rel.trust)
            rel.respect = clamp(rel.respect)
            rel.type = rel.determine_type()
            messages.append(f"🤝 {rel.soldier1.name} أنقذ {rel.soldier2.name} في المعركة")
            
        elif event_type == "shared_hardship":
            # تقاسم المشقة
            rel.trust += random.randint(5, 10)
            rel.respect += random.randint(5, 10)
            rel.trust = clamp(rel.trust)
            rel.respect = clamp(rel.respect)
            rel.type = rel.determine_type()
            messages.append(f"⚔️  {rel.soldier1.name} و {rel.soldier2.name} تقاسما المشقة")
            
        return messages