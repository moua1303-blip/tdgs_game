"""
نظام تدريب وتطوير الجنود
"""

import random
import time
from typing import List, Optional
from enums import Personality, Rank
from soldier import Soldier
from utils import logger, clamp

class TrainingType:
    """أنواع التدريب"""
    MARKSMANSHIP = "🎯 قناصة"
    COMBAT = "⚔️ قتال متقدم"
    MEDICAL = "🏥 إسعافات"
    TACTICS = "🧠 تكتيكات"
    PHYSICAL = "💪 لياقة بدنية"
    LEADERSHIP = "👑 قيادة"

class TrainingSystem:
    """نظام تدريب الجنود"""
    
    def __init__(self, platoon: List[Soldier]):
        self.platoon = platoon
        self.training_log = []
        self.training_facilities = {
            TrainingType.MARKSMANSHIP: {"level": 1, "max_level": 5},
            TrainingType.COMBAT: {"level": 1, "max_level": 5},
            TrainingType.MEDICAL: {"level": 1, "max_level": 5},
            TrainingType.TACTICS: {"level": 1, "max_level": 5},
            TrainingType.PHYSICAL: {"level": 1, "max_level": 5},
            TrainingType.LEADERSHIP: {"level": 1, "max_level": 5}
        }
        
    def get_available_trainings(self) -> List[str]:
        """الحصول على التدريبات المتاحة"""
        available = []
        for training, info in self.training_facilities.items():
            if info["level"] < info["max_level"]:
                available.append(training)
        return available
    
    def upgrade_facility(self, training: str) -> bool:
        """تطوير منشأة تدريب"""
        if training not in self.training_facilities:
            return False
        
        facility = self.training_facilities[training]
        if facility["level"] >= facility["max_level"]:
            return False
        
        facility["level"] += 1
        logger.info(f"✅ تم تطوير {training} إلى المستوى {facility['level']}")
        return True
    
    def train_soldier(self, soldier: Soldier, training: str) -> str:
        """تدريب جندي"""
        if not soldier.is_alive:
            return "❌ لا يمكن تدريب جندي شهيد"
        
        if training not in self.training_facilities:
            return "❌ تدريب غير موجود"
        
        facility_level = self.training_facilities[training]["level"]
        
        # حساب التحسن حسب نوع التدريب
        improvements = []
        
        if training == TrainingType.MARKSMANSHIP:
            # تحسين دقة القنص
            soldier.experience += 20 * facility_level
            soldier.kills += random.randint(0, 2)  # خبرة إضافية
            improvements.append(f"دقة قنص +{5 * facility_level}%")
            
        elif training == TrainingType.COMBAT:
            # تحسين القتال
            soldier.experience += 30 * facility_level
            soldier.health = clamp(soldier.health + 5 * facility_level)
            improvements.append(f"قدرات قتالية +{10 * facility_level}%")
            
        elif training == TrainingType.MEDICAL:
            # تحسين الإسعاف
            soldier.experience += 25 * facility_level
            if soldier.wounds:
                soldier.wounds.clear()  # تدريب متقدم يعالج
                improvements.append("تم علاج جميع الإصابات")
            else:
                soldier.health = clamp(soldier.health + 10 * facility_level)
                improvements.append(f"صحة +{10 * facility_level}%")
            
        elif training == TrainingType.TACTICS:
            # تحسين التكتيكات
            soldier.experience += 40 * facility_level
            soldier.morale = clamp(soldier.morale + 15 * facility_level)
            improvements.append(f"ذكاء تكتيكي +{15 * facility_level}%")
            
        elif training == TrainingType.PHYSICAL:
            # تحسين اللياقة
            soldier.health = clamp(soldier.health + 15 * facility_level)
            soldier.morale = clamp(soldier.morale + 10 * facility_level)
            improvements.append(f"قوة بدنية +{20 * facility_level}%")
            
        elif training == TrainingType.LEADERSHIP:
            # تحسين القيادة
            soldier.experience += 50 * facility_level
            soldier.loyalty = clamp(soldier.loyalty + 20 * facility_level)
            improvements.append(f"كاريزما قيادية +{15 * facility_level}%")
        
        # ترقية الرتبة
        old_rank = soldier.rank
        soldier.rank = soldier._calculate_rank()
        
        # تسجيل التدريب
        self.training_log.append({
            'soldier': soldier.name,
            'training': training,
            'day': len(self.training_log) + 1
        })
        
        # رسالة النتيجة
        result = f"✅ {soldier.name} أكمل تدريب {training}\n"
        result += f"   التحسن: {', '.join(improvements)}\n"
        
        if old_rank != soldier.rank:
            result += f"   🌟 ترقى إلى رتبة {soldier.rank.arabic_name}!"
        
        logger.info(f"تدريب: {soldier.name} - {training}")
        return result
    
    def train_platoon(self, training: str) -> List[str]:
        """تدريب الكتيبة بأكملها"""
        results = []
        for soldier in self.platoon:
            if soldier.is_alive:
                results.append(self.train_soldier(soldier, training))
        return results
    
    def get_training_menu(self) -> str:
        """عرض قائمة التدريب"""
        menu = "\n🏋️  مركز التدريب:\n"
        menu += "─" * 40 + "\n"
        
        for i, (training, info) in enumerate(self.training_facilities.items(), 1):
            level_display = "⬛" * info["level"] + "⬜" * (info["max_level"] - info["level"])
            menu += f"{i}. {training} [مستوى {info['level']}] {level_display}\n"
        
        return menu