"""
نظام المعارك المتطور - نسخة معدلة بربط الذخيرة
الملف: battle.py
"""

import random
from typing import List, Tuple, Optional
from utils import logger, clamp
from soldier import Soldier
from enums import Weather, Location, Wound

class BattleSystem:
    """نظام المعارك المتطور - نسخة معدلة بربط الذخيرة"""
    
    def __init__(self, platoon: List[Soldier], ammo_system=None):
        self.platoon = platoon
        self.ammo_system = ammo_system  # ربط نظام الذخيرة
        self.battle_log = []
        self.enemy_force = 0
    
    def _get_weapon_category(self, role: str) -> str:
        """تحويل الدور إلى فئة سلاح لنظام الذخيرة"""
        mapping = {
            "قناص": "sniper",
            "مدفعي": "heavy",
            "مسعف": "pistol",
            "اتصالات": "pistol",
            "مهندس قتالي": "shotgun",
            "استطلاع": "rifle",
            "جندي مشاة": "rifle"
        }
        return mapping.get(role, "rifle")
    
    def calculate_platoon_power(self, weather: Weather, location: Location) -> float:
        """حساب قوة الكتيبة مع مراعاة الذخيرة"""
        total_power = 0.0
        
        for soldier in self.platoon:
            if soldier.is_alive:
                # التحقق من نوع سلاح الجندي واستهلاك الذخيرة
                weapon_type = self._get_weapon_category(soldier.role)
                
                # إذا لم تكن هناك ذخيرة، تضعف القوة جداً
                has_ammo = True
                if self.ammo_system:
                    has_ammo = self.ammo_system.use_for_battle(weapon_type, intensity=0.5)
                
                ammo_mult = 1.0 if has_ammo else 0.2
                
                weather_mult = weather.attack_mult
                location_mult = 1.0 - (location.danger / 200)
                
                # حساب القوة النهائية
                power = soldier.combat_power(weather_mult, location_mult) * ammo_mult
                total_power += power
                
                if not has_ammo and self.ammo_system:
                    logger.warning(f"⚠️ {soldier.name} يقاتل بدون ذخيرة كافية!")
        
        return total_power
    
    def generate_enemy_force(self, location: Location) -> int:
        """توليد قوة العدو حسب الموقع"""
        base = location.danger * 2
        variation = random.randint(-10, 10)
        return max(20, base + variation)
    
    def battle_round(self, platoon_power: float, enemy_power: float) -> Tuple[bool, dict]:
        """جولة قتال واحدة"""
        
        # حساب النتيجة
        total_power = platoon_power + enemy_power
        if total_power <= 0:
            return True, {'damage': 0, 'kills': 0}
            
        platoon_ratio = platoon_power / total_power
        enemy_ratio = enemy_power / total_power
        
        # نتيجة الجولة
        if random.random() < platoon_ratio:
            # الكتيبة أصابت
            damage = random.randint(10, 30)
            kills = random.randint(1, 3)
            return True, {'damage': damage, 'kills': kills}
        else:
            # العدو أصاب
            damage = random.randint(15, 40)
            kills = random.randint(1, 4)
            return False, {'damage': damage, 'kills': kills}
    
    def simulate_battle(self, weather: Weather, location: Location) -> Tuple[bool, dict]:
        """محاكاة معركة كاملة"""
        
        logger.info(f"⚔️ بدء المعركة في {location.arabic_name} - {weather.arabic_name}")
        
        # قوة الكتيبة
        platoon_power = self.calculate_platoon_power(weather, location)
        
        # قوة العدو
        self.enemy_force = self.generate_enemy_force(location)
        enemy_power = self.enemy_force * 10 * random.uniform(0.8, 1.2)
        
        logger.info(f"قوة الكتيبة: {platoon_power:.0f}")
        logger.info(f"قوة العدو: {enemy_power:.0f}")
        
        # جولات القتال
        rounds = random.randint(3, 6)
        results = {
            'platoon_damage': 0,
            'enemy_damage': 0,
            'platoon_kills': 0,
            'enemy_kills': 0,
            'rounds': rounds
        }
        
        for round_num in range(rounds):
            platoon_win, round_result = self.battle_round(platoon_power, enemy_power)
            
            if platoon_win:
                results['enemy_damage'] += round_result['damage']
                results['enemy_kills'] += round_result['kills']
                enemy_power -= round_result['damage'] * 5
                logger.info(f"جولة {round_num+1}: ✅ إصابة! قتل {round_result['kills']} من العدو")
            else:
                results['platoon_damage'] += round_result['damage']
                results['platoon_kills'] += round_result['kills']
                platoon_power -= round_result['damage'] * 5
                logger.info(f"جولة {round_num+1}: ❌ العدو أصاب! خسارة {round_result['kills']} جنود")
            
            if platoon_power <= 0 or enemy_power <= 0:
                break
        
        # تحديد الفائز
        victory = platoon_power > enemy_power
        
        if victory:
            logger.info(f"🏆 انتصار! قتل {results['enemy_kills']} من العدو")
        else:
            logger.warning(f"💔 هزيمة... خسارة {results['platoon_kills']} جنود")
        
        return victory, results
    
    def apply_battle_results(self, victory: bool, results: dict) -> Tuple[int, int]:
        """تطبيق نتائج المعركة على الجنود"""
        
        if victory:
            # خسائر أقل في الانتصار
            casualties = results.get('platoon_kills', 0)
            wounded = random.randint(0, 2)
            
            # خبرة للجميع
            for soldier in self.platoon:
                if soldier.is_alive:
                    xp_gain = 20 + random.randint(0, 20)
                    soldier.add_experience(xp_gain)
                    soldier.battles_participated += 1
                    soldier.battles_won += 1
            
        else:
            # خسائر أكبر في الهزيمة
            casualties = results.get('platoon_kills', 0) + random.randint(1, 2)
            wounded = random.randint(1, 3)
            
            # خبرة أقل
            for soldier in self.platoon:
                if soldier.is_alive:
                    xp_gain = 10 + random.randint(0, 10)
                    soldier.add_experience(xp_gain)
                    soldier.battles_participated += 1
        
        # تطبيق الخسائر
        alive_soldiers = [s for s in self.platoon if s.is_alive]
        
        # قتلى
        if casualties > 0 and alive_soldiers:
            killed_count = min(casualties, len(alive_soldiers))
            killed = random.sample(alive_soldiers, killed_count)
            for soldier in killed:
                soldier.is_alive = False
                logger.error(f"💔 {soldier.name} استشهد في المعركة!")
        
        # جرحى
        alive_soldiers = [s for s in self.platoon if s.is_alive]
        if wounded > 0 and alive_soldiers:
            wounded_count = min(wounded, len(alive_soldiers))
            wounded_soldiers = random.sample(alive_soldiers, wounded_count)
            for soldier in wounded_soldiers:
                soldier.add_wound(random.choice(list(Wound)))
        
        return casualties, wounded