import random
from typing import List, Dict, Any, Optional
from enums import Personality

class SoldierAI:
    """نظام الذكاء للجنود"""
    
    def __init__(self, soldier):
        self.soldier = soldier
        
    def suggest_action(self, situation: Dict[str, Any]) -> str:
        """اقتراح إجراء بناءً على الشخصية والموقف"""
        
        suggestions = {
            Personality.BRAVE: self._brave_suggestion,
            Personality.RATIONAL: self._rational_suggestion,
            Personality.EMOTIONAL: self._emotional_suggestion,
            Personality.COWARD: self._coward_suggestion,
            Personality.RELIGIOUS: self._religious_suggestion,
            Personality.RECKLESS: self._reckless_suggestion,
            Personality.WISE: self._wise_suggestion
        }
        
        suggester = suggestions.get(self.soldier.personality, self._default_suggestion)
        return suggester(situation)
    
    def _brave_suggestion(self, situation):
        if situation.get('enemy_visible', False):
            return "اهجم الآن! لنفاجئهم!"
        return "تقدم بثقة، أنا معك"
    
    def _rational_suggestion(self, situation):
        if situation.get('casualties', 0) > 2:
            return "انسحب مؤقتاً، نعيد التجميع"
        return "دعنا نخطط أولاً، ثم نتحرك"
    
    def _emotional_suggestion(self, situation):
        if situation.get('civilians_nearby', False):
            return "أنقذ المدنيين أولاً! هذا أهم"
        return "فكر في عائلاتنا"
    
    def _coward_suggestion(self, situation):
        if situation.get('enemy_force', 0) > 20:
            return "أرجوك... انسحب قبل فوات الأوان"
        return "لنطلب تعزيزات، الوضع خطير"
    
    def _religious_suggestion(self, situation):
        return "توكل على الله ثم اقتحم"
    
    def _reckless_suggestion(self, situation):
        return "على طول! الموت أفضل من التراجع!"
    
    def _wise_suggestion(self, situation):
        if situation.get('night', False):
            return "استغل الظلام للتسلل"
        return "الروح المعنوية أهم من أي شيء"
    
    def _default_suggestion(self, situation):
        return "القرار لك يا قائد"

class PlatoonAI:
    """ذكاء جماعي للكتيبة"""
    
    def __init__(self, platoon):
        self.platoon = platoon
        self.collective_morale = 100
        
    def get_collective_advice(self, situation: Dict[str, Any]) -> str:
        """الحصول على نصيحة جماعية من الكتيبة"""
        
        suggestions = []
        for soldier in self.platoon:
            if soldier.is_alive:
                ai = SoldierAI(soldier)
                suggestions.append(ai.suggest_action(situation))
        
        # تحليل النصائح
        attack_count = sum(1 for s in suggestions if 'هجوم' in s or 'اقتحام' in s)
        retreat_count = sum(1 for s in suggestions if 'انسحاب' in s)
        
        if attack_count > retreat_count * 2:
            return "معظم الكتيبة تريد الهجوم!"
        elif retreat_count > attack_count * 2:
            return "معظم الكتيبة تريد الانسحاب!"
        elif attack_count > retreat_count:
            return "أغلبية بسيطة تفضل الهجوم"
        elif retreat_count > attack_count:
            return "أغلبية بسيطة تفضل الانسحاب"
        else:
            return "الآراء منقسمة، القرار لك"