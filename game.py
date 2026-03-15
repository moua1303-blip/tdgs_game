"""
ملف game.py - الفئة الرئيسية للعبة قائد الكتيبة
النسخة النهائية المتكاملة - مع جميع الأنظمة
"""

import random
import time
import os
import sys
from typing import Optional, Dict, Any, List

from soldier import Soldier
from battle import BattleSystem
from map import GameMap
from events import DynamicEventSystem
from orders import get_dynamic_order
from ai import PlatoonAI
from relationships import RelationshipManager
from enums import Weather, Location, Personality, Wound
from constants import SOLDIER_NAMES, ROLES, FAMILY_STATUSES, NIGHT_QUOTES, VICTORY_CONDITIONS
from utils import logger, GameSaver, clamp

# محاولة استيراد نظام الذخيرة (اختياري)
try:
    from ammo import AmmoSystem, AmmoType
    AMMO_AVAILABLE = True
except ImportError:
    AMMO_AVAILABLE = False
    logger.info("⚠️ نظام الذخيرة غير موجود - يتم التشغيل بدونه")


class PlatoonCommanderGame:
    """الفئة الرئيسية للعبة - قائد الكتيبة"""
    
    def __init__(self, load_slot: Optional[int] = None):
        
        # ========== المؤشرات الرئيسية ==========
        self.player_name = ""
        self.military_rank = random.randint(70, 100)
        self.mental_health = random.randint(60, 100)
        self.self_respect = random.randint(60, 100)
        self.family_love = random.randint(60, 100)
        self.platoon_cohesion = random.randint(60, 100)
        
        # ========== السمعة ==========
        self.reputation = {
            "among_soldiers": random.randint(50, 100),
            "among_civilians": random.randint(50, 100),
            "among_command": random.randint(50, 100)
        }
        
        # ========== إحصائيات ==========
        self.days_in_service = 0
        self.battles_fought = 0
        self.victories = 0
        self.orders_followed = 0
        self.orders_disobeyed = 0
        self.civilian_casualties = 0
        self.soldiers_killed = 0
        self.ethical_violations = 0
        self.enemies_killed = 0
        self.civilians_saved = 0
        
        # ========== متغيرات النهايات المتعددة ==========
        self.civilians_saved_total = 0      # إجمالي المدنيين المنقذين
        self.civilians_killed_total = 0     # إجمالي المدنيين الذين قتلوا (بسببك)
        self.disobeyed_orders = 0           # عدد المرات التي عصيت فيها أوامر مهمة
        self.ethical_violations_total = 0   # إجمالي الانتهاكات الأخلاقية
        self.chapter = 1                    # الفصل الحالي من اللعبة
        self.critical_decisions = []        # سجل القرارات المصيرية
        # ================================================
        
        # ========== أنظمة اللعبة ==========
        self.weather = random.choice(list(Weather))
        self.map = GameMap()
        self.event_system = DynamicEventSystem(self)
        self.platoon = self._create_platoon()
        
        # نظام الذخيرة (اختياري)
        # نظام الذخيرة (اختياري)
        self.ammo_system = AmmoSystem()          if AMMO_AVAILABLE else None
        if self.ammo_system:
    # تهيئة الذخيرة بناءً على الكتيبة
             self.ammo_system.initialize_for_platoon(self.platoon)
             logger.info("🔫 تم ربط نظام الذخيرة باللعبة")
        
        # نظام العلاقات
        self.relationship_manager = RelationshipManager()
        self._initialize_relationships()
        
        # نظام المعارك
        self.battle_system = BattleSystem(self.platoon, self.ammo_system)
        
        # ذكاء الكتيبة
        self.platoon_ai = PlatoonAI(self.platoon)
        
        # ========== حالة اللعبة ==========
        self.game_over = False
        self.game_won = False
        
        # ========== تحميل لعبة محفوظة ==========
        if load_slot:
            self._load_game(load_slot)
    
    # ========== دوال التهيئة الأساسية ==========
    
    def _create_platoon(self) -> List[Soldier]:
        """إنشاء الكتيبة"""
        platoon = []
        personalities = list(Personality)
        
        for i in range(7):
            personality = random.choice(personalities)
            name = SOLDIER_NAMES[i]
            role = ROLES[i]
            age = random.randint(21, 38)
            family = random.choice(FAMILY_STATUSES)
            
            soldier = Soldier(name, role, age, family, personality)
            platoon.append(soldier)
        
        return platoon
    
    def _initialize_relationships(self):
        """تهيئة العلاقات بين الجنود"""
        for i in range(len(self.platoon)):
            for j in range(i+1, len(self.platoon)):
                if random.random() < 0.4:  # 40% فرصة وجود علاقة
                    self.relationship_manager.create_relationship(
                        self.platoon[i], self.platoon[j]
                    )
    
    # ========== دوال الحفظ والتحميل ==========
    
    def _save_game(self, slot: int = 1):
        """حفظ اللعبة - مع جميع المتغيرات"""
        game_state = {
            'player_name': self.player_name,
            'military_rank': self.military_rank,
            'mental_health': self.mental_health,
            'self_respect': self.self_respect,
            'family_love': self.family_love,
            'platoon_cohesion': self.platoon_cohesion,
            'reputation': self.reputation,
            'days_in_service': self.days_in_service,
            'battles_fought': self.battles_fought,
            'victories': self.victories,
            'soldiers_killed': self.soldiers_killed,
            'civilian_casualties': self.civilian_casualties,
            'civilians_saved': self.civilians_saved,
            'enemies_killed': self.enemies_killed,
            'weather': self.weather.name,
            'current_location': self.map.current_location.name,
            'platoon': [s.to_dict() for s in self.platoon],
            # متغيرات النهايات
            'civilians_saved_total': self.civilians_saved_total,
            'civilians_killed_total': self.civilians_killed_total,
            'disobeyed_orders': self.disobeyed_orders,
            'ethical_violations_total': self.ethical_violations_total,
            'chapter': self.chapter,
            'critical_decisions': self.critical_decisions
        }
        
        # إضافة نظام الذخيرة إذا موجود
        if self.ammo_system:
            game_state['ammo'] = self.ammo_system.to_dict()
        
        GameSaver.save_game(game_state, slot)
        self._slow_print(f"💾 تم حفظ اللعبة في slot {slot}")
    
    def _load_game(self, slot: int):
        """تحميل لعبة محفوظة"""
        data = GameSaver.load_game(slot)
        if not data:
            return
        
        self.player_name = data['player_name']
        self.military_rank = data['military_rank']
        self.mental_health = data['mental_health']
        self.self_respect = data['self_respect']
        self.family_love = data['family_love']
        self.platoon_cohesion = data['platoon_cohesion']
        self.reputation = data['reputation']
        self.days_in_service = data['days_in_service']
        self.battles_fought = data['battles_fought']
        self.victories = data['victories']
        self.soldiers_killed = data['soldiers_killed']
        self.civilian_casualties = data['civilian_casualties']
        self.civilians_saved = data.get('civilians_saved', 0)
        self.enemies_killed = data.get('enemies_killed', 0)
        self.weather = Weather[data['weather']]
        self.map.current_location = Location[data['current_location']]
        
        # تحميل متغيرات النهايات
        self.civilians_saved_total = data.get('civilians_saved_total', 0)
        self.civilians_killed_total = data.get('civilians_killed_total', 0)
        self.disobeyed_orders = data.get('disobeyed_orders', 0)
        self.ethical_violations_total = data.get('ethical_violations_total', 0)
        self.chapter = data.get('chapter', 1)
        self.critical_decisions = data.get('critical_decisions', [])
        
        # إعادة بناء الجنود
        self.platoon = [Soldier.from_dict(s) for s in data['platoon']]
        
        # إعادة بناء العلاقات
        self._initialize_relationships()
        
        # تحميل نظام الذخيرة
        if self.ammo_system and 'ammo' in data:
            self.ammo_system.from_dict(data['ammo'])
        
        # تحديث الأنظمة
        self.battle_system = BattleSystem(self.platoon, self.ammo_system)
        self.platoon_ai = PlatoonAI(self.platoon)
        
        self._slow_print(f"📂 تم تحميل اللعبة من slot {slot}")
        time.sleep(2)
    
    # ========== دوال العرض والطباعة ==========
    
    def _slow_print(self, text: str, delay: float = 0.02):
        """طباعة بطيئة"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def _clear_screen(self):
        """مسح الشاشة"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def _print_header(self, title: str):
        """طباعة رأس"""
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def _get_input(self, prompt: str, min_val: int, max_val: int) -> int:
        """دالة آمنة للحصول على مدخلات اللاعب"""
        while True:
            try:
                user_input = input(prompt).strip()
                
                # السماح بالخروج السريع
                if user_input.lower() == 'exit':
                    print("\n👋  تم إنهاء اللعبة بأمر منك.")
                    sys.exit(0)
                
                if user_input.lower() == 'menu':
                    return 0  # العودة للقائمة الرئيسية
                
                choice = int(user_input)
                if min_val <= choice <= max_val:
                    return choice
                else:
                    print(f"❌ الرجاء اختيار رقم بين {min_val} و {max_val}")
            except ValueError:
                print("❌ إدخال غير صالح! يرجى إدخال رقم فقط.")
    
    # ========== دالة العرض الرئيسية ==========
    
    def display_status(self):
        """عرض جميع المؤشرات"""
        self._clear_screen()
        
        # المؤشرات الأساسية
        self._print_header("📊  المؤشرات الحيوية")
        
        rank_bar = "⬛" * (self.military_rank // 10) + "⬜" * (10 - self.military_rank // 10)
        print(f"🎖️  التقييم العسكري: [{rank_bar}] {self.military_rank}%")
        
        mental_bar = "💚" * (self.mental_health // 10) + "🩶" * (10 - self.mental_health // 10)
        print(f"🧠  الصحة النفسية:   [{mental_bar}] {self.mental_health}%")
        
        respect_bar = "⭐" * (self.self_respect // 10) + "⚪" * (10 - self.self_respect // 10)
        print(f"🎯  احترام الذات:    [{respect_bar}] {self.self_respect}%")
        
        family_bar = "❤️" * (self.family_love // 10) + "🩶" * (10 - self.family_love // 10)
        print(f"👪  حب العائلة:      [{family_bar}] {self.family_love}%")
        
        cohesion_bar = "🔗" * (self.platoon_cohesion // 10) + "⛓️" * (10 - self.platoon_cohesion // 10)
        print(f"⚔️  تماسك الكتيبة:   [{cohesion_bar}] {self.platoon_cohesion}%")
        
        # السمعة
        print("\n" + "─" * 70)
        print("📢  السمعة")
        print("─" * 70)
        
        print(f"👥 بين الجنود:  {self.reputation['among_soldiers']}%")
        print(f"👨‍👩‍👧 بين المدنيين: {self.reputation['among_civilians']}%")
        print(f"🎖️ لدى القيادة:  {self.reputation['among_command']}%")
        
        # الطقس والموقع
        print("\n" + "─" * 70)
        print(f"🌤️  الطقس: {self.weather.icon} {self.weather.arabic_name}")
        print(f"🗺️  الموقع: {self.map.locations[self.map.current_location]['name']}")
        
        # إحصائيات متقدمة
        print("─" * 70)
        print(f"📅 الأيام: {self.days_in_service} | ⚔️ معارك: {self.battles_fought} | "
              f"🏆 انتصارات: {self.victories} | 💀 خسائر: {self.soldiers_killed}")
        print(f"👨‍👩‍👧 ضحايا مدنيون: {self.civilian_casualties} | "
              f"🆘 مدنيون منقذون: {self.civilians_saved} | "
              f"💀 قتلى العدو: {self.enemies_killed}")
        print(f"⚖️ انتهاكات أخلاقية: {self.ethical_violations_total} | "
              f"🛑 عصيان أوامر: {self.disobeyed_orders}")
        
        # عرض الذخيرة إذا كانت موجودة
        if self.ammo_system:
            print("─" * 70)
            print(self.ammo_system.display_status())
        
        print("─" * 70)
        
        # حالة الكتيبة
        self._display_platoon()
    
    def _display_platoon(self):
        """عرض حالة الكتيبة"""
        print("\n👥  حالة الكتيبة:")
        print("─" * 70)
        
        for soldier in sorted(self.platoon, key=lambda x: (not x.is_alive, -x.health)):
            print(f"  {soldier}")
        
        alive = [s for s in self.platoon if s.is_alive]
        print("─" * 70)
        print(f"إجمالي الأحياء: {len(alive)}/7")
        
        # تحذيرات
        for soldier in self.platoon:
            if soldier.is_alive:
                if soldier.mental < 30:
                    print(f"⚠️  {soldier.name} يعاني من انهيار نفسي!")
                if soldier.health < 30:
                    print(f"🚑  {soldier.name} بحاجة لعناية طبية!")
                if soldier.wounds:
                    wounds = ", ".join([w.value[1] for w in soldier.wounds])
                    print(f"🩺  {soldier.name} مصاب: {wounds}")
    
    # ========== دوال نهاية اللعبة ==========
    
    def check_game_over(self) -> bool:
        """التحقق من شروط انتهاء اللعبة"""
        
        # خسارة كل الكتيبة
        alive = [s for s in self.platoon if s.is_alive]
        if len(alive) == 0:
            self._slow_print("\n💔  لقد قُتلت كل كتيبتك... الفشل الأكبر.")
            self.game_over = True
            return True
        
        # انهيار نفسي
        if self.mental_health <= 0:
            self._slow_print("\n🧠  لقد انهارت نفسياً... تم إجلاؤك من الجبهة.")
            self.game_over = True
            return True
        
        # فقدان احترام الذات
        if self.self_respect <= 0:
            self._slow_print("\n💔  لم تعد تحترم نفسك كإنسان... تستقيل من الجيش.")
            self.game_over = True
            return True
        
        # فقدان العائلة
        if self.family_love <= 0:
            self._slow_print("\n💔  عائلتك تخلت عنك... لا أحد ينتظر عودتك.")
            self.game_over = True
            return True
        
        # شروط النصر
        if (self.days_in_service >= VICTORY_CONDITIONS['min_days'] and 
            self.victories >= VICTORY_CONDITIONS['min_victories'] and 
            len(alive) >= VICTORY_CONDITIONS['min_soldiers'] and
            self.reputation['among_soldiers'] >= VICTORY_CONDITIONS['min_reputation']):
            
            self._slow_print(f"\n🏆  لقد وصلت إلى نهاية الحرب بعد {self.days_in_service} يوماً!")
            self.game_over = True
            self.game_won = True
            return True
        
        return False
    
    def determine_ending(self) -> str:
        """تحديد نوع النهاية بناءً على الإحصائيات"""
        alive_count = sum(1 for s in self.platoon if s.is_alive)
        total_reputation = sum(self.reputation.values()) / 3
        ethical_score = self.civilians_saved_total - self.civilians_killed_total * 3 - self.ethical_violations_total * 5
        
        if self.game_won:
            if ethical_score > 150 and self.mental_health > 70 and alive_count >= 4:
                return "hero_savior"          # المنقذ البطل
            elif self.victories > 12 and alive_count <= 1:
                return "last_standing"        # الوحيد الباقي
            elif total_reputation > 85:
                return "legend_respected"     # أسطورة محترمة
            elif self.civilians_saved_total > 50 and self.self_respect > 80:
                return "guardian_angel"       # الملاك الحارس
            elif self.military_rank > 95 and self.reputation['among_command'] > 90:
                return "perfect_soldier"      # الجندي المثالي
            else:
                return "standard_victory"     # انتصار عادي
        else:
            if self.mental_health < 20:
                return "broken_mind"          # انهيار نفسي
            elif self.disobeyed_orders > 8:
                return "mutiny_deserter"      # تمرد / هارب
            elif ethical_score < -100:
                return "war_criminal"         # مجرم حرب
            elif self.soldiers_killed > 5 and self.self_respect < 30:
                return "haunted_commander"    # قائد مسكون بالذنب
            elif self.family_love < 20:
                return "alone_in_dark"        # وحيد في الظلام
            else:
                return "defeat_survivor"      # هزيمة لكن نجا
    
    def _show_ending_story(self):
        """عرض قصة النهاية حسب نوعها"""
        self._clear_screen()
        ending_type = self.determine_ending()
        
        endings = {
            "hero_savior": (
                "🏆 أنت المنقذ 🏆\n\n"
                "عندما عُدت إلى الوطن، استقبلتك الحشود بالزهور.\n"
                "المدنيون الذين أنقذتهم يروون قصتك لأبنائهم.\n"
                "اسمك أصبح رمزاً للأمل في زمن الحرب.\n"
                "في كل عام، تقيم البلدة التي أنقذتها حفلاً تكريماً لك.\n"
                "أطفالك فخورون بك، وزوجتك تنظر إليك وكأنك بطل خارق.\n"
                "لقد أثبت أن الحرب لا تجرد الإنسان من إنسانيته.\n"
            ),
            
            "war_criminal": (
                "⚖️ محاكمة ⚖️\n\n"
                "تم تسليمك للمحكمة الدولية.\n"
                "الصور والشهادات عن الضحايا المدنيين انتشرت في العالم.\n"
                "القاضي يقرأ الحكم: 'مجرم حرب، السجن المؤبد'.\n"
                "عائلتك تخلت عنك... الصحفيون يطاردونك.\n"
                "في زنزانتك، ترى وجوه الضحايا كل ليلة.\n"
                "أنت تعيش مع الذنب إلى الأبد.\n"
            ),
            
            "broken_mind": (
                "🧠 الظلام الداخلي 🧠\n\n"
                "عدت إلى البيت، لكنك لم تعد أنت.\n"
                "الكوابيس لا تتوقف... أصوات الجنود الذين فقدتهم تطاردك.\n"
                "أغلقت الباب على نفسك... ولم يعد أحد يراك.\n"
                "الطبيب يقول: 'اضطراب ما بعد الصدمة حاد'.\n"
                "زوجتك تزورك في المستشفى، لكنك لا تعرفها.\n"
                "الحرب انتهت، لكنها لم تنتهِ بداخلك.\n"
            ),
            
            "last_standing": (
                "⚔️ الوحيد الباقي ⚔️\n\n"
                "أنت الوحيد الذي عاد.\n"
                "ستة قبور في المقبرة العسكرية تحمل أسماء رجالك.\n"
                "تقف أمام قبورهم في المطر... لا أحد غيرك.\n"
                "لقد حققت الانتصار، لكن الثمن كان كل شيء.\n"
                "كل ليلة، تتصل بأرقام هواتفهم... لا أحد يرد.\n"
                "النصر وحيد جداً.\n"
            ),
            
            "legend_respected": (
                "🌟 أسطورة محترمة 🌟\n\n"
                "اسمك يدرس في الأكاديميات العسكرية.\n"
                "الجنود الجدد يحلمون بأن يصبحوا مثلك.\n"
                "الرئيس يقلدك وسام الشرف.\n"
                "المدنيون يلوحون لك في الشوارع.\n"
                "لقد أصبحت رمزاً للأمة.\n"
                "لكن في داخلك، تعرف أنك مجرد إنسان.\n"
            ),
            
            "guardian_angel": (
                "👼 الملاك الحارس 👼\n\n"
                "المدنيون أطلقوا عليك اسم 'الملاك الحارس'.\n"
                "أنقذت العشرات من الأبرياء.\n"
                "أم تعانقك باكية: 'ابني حي بفضلك'.\n"
                "طفلة ترسمك كفارس على حصان.\n"
                "في القرية التي أنقذتها، هناك شارع باسمك.\n"
                "لقد انتصرت ليس فقط بالسلاح، بل بالإنسانية.\n"
            ),
            
            "perfect_soldier": (
                "🎯 الجندي المثالي 🎯\n\n"
                "القيادة تعتبرك النموذج الأكمل.\n"
                "لم تعص أمراً قط، ونفذت كل المهام بكفاءة.\n"
                "الترقية إلى أعلى الرتب أصبحت مسألة وقت.\n"
                "الجنود يحترمونك، الضباط يقتدون بك.\n"
                "لكن زوجتك تسألك: 'هل كنت سعيداً؟'\n"
                "وأنت لا تعرف الإجابة.\n"
            ),
            
            "standard_victory": (
                "🎖️ انتصار عادي 🎖️\n\n"
                "لقد أديت واجبك، وعُدت إلى البيت.\n"
                "النصر تحقق، والكتيبة تعود بسلام.\n"
                "ليس هناك بطولات استثنائية، ولا جرائم.\n"
                "حرب أخرى، نصر آخر... روتين.\n"
                "أحياناً، النصر العادي هو أفضل ما يمكن أن تتمناه.\n"
            ),
            
            "mutiny_deserter": (
                "🏃 هارب من الجيش 🏃\n\n"
                "رفضت الأوامر مرات عديدة... حتى حاكموك.\n"
                "الهروب بدا الخيار الوحيد.\n"
                "تعيش الآن في بلد بعيد بهوية مزورة.\n"
                "كل يوم تخشى أن يكتشفوك.\n"
                "عائلتك لا تعرف إن كنت حياً أم ميتاً.\n"
                "الحرية ثمنها الوحدة.\n"
            ),
            
            "haunted_commander": (
                "👻 قائد مسكون 👻\n\n"
                "لقد فقدت معظم رجالك.\n"
                "كل صباح تذهب إلى قبورهم.\n"
                "أرامل الجنود لا ينظرن إليك.\n"
                "في المنام، يسألونك: 'لماذا تركتنا؟'\n"
                "ليس لديك جواب.\n"
                "الانتصار لا يعني شيئاً عندما تعود وحدك.\n"
            ),
            
            "alone_in_dark": (
                "🌑 وحيد في الظلام 🌑\n\n"
                "عائلتك تخلت عنك.\n"
                "زوجتك أخذت الأطفال وذهبت.\n"
                "والدتك لا ترد على اتصالاتك.\n"
                "البيت فارغ، بارد، هادئ.\n"
                "تتساءل: 'لماذا اخترت الحرب؟'\n"
                "ولكن الأوان قد فات.\n"
            ),
            
            "defeat_survivor": (
                "🌧️ ناجٍ من الهزيمة 🌧️\n\n"
                "لقد خسرتم الحرب.\n"
                "لكنك نجوت.\n"
                "تعود إلى بيت مدمر، إلى حياة مختلفة.\n"
                "الجنود الباقون يجتمعون كل عام في ذكرى الهزيمة.\n"
                "تتذكرون من فقدتم.\n"
                "الهزيمة تعلمك التواضع.\n"
            )
        }
        
        story = endings.get(ending_type, "نهاية غير معروفة\n\nاللعبة انتهت.")
        
        print("═" * 70)
        print(story)
        print("═" * 70)
        
        print("\n📊  الإحصائيات النهائية:")
        print(f"🎖️  التقييم العسكري: {self.military_rank}%")
        print(f"🧠  الصحة النفسية: {self.mental_health}%")
        print(f"🎯  احترام الذات: {self.self_respect}%")
        print(f"👪  حب العائلة: {self.family_love}%")
        print(f"⚔️  تماسك الكتيبة: {self.platoon_cohesion}%")
        print(f"👥 الناجون: {sum(1 for s in self.platoon if s.is_alive)}/7")
        print(f"👨‍👩‍👧 مدنيون منقذون: {self.civilians_saved_total}")
        print(f"💔 ضحايا مدنيون: {self.civilians_killed_total}")
        print(f"⚖️ انتهاكات أخلاقية: {self.ethical_violations_total}")
        print(f"🛑 عصيان أوامر: {self.disobeyed_orders}")
        print(f"🏆 انتصارات: {self.victories}")
        print(f"⚔️ معارك: {self.battles_fought}")
        
        print("\n" + "─" * 70)
        print(random.choice(NIGHT_QUOTES))
        print("─" * 70)
        
        # تقييم نهائي حسب النهاية
        print("\n" + "⭐" * 25)
        if ending_type == "hero_savior":
            print("🌟  أنت أسطورة حية! اسمك سيخلد في التاريخ.")
        elif ending_type == "war_criminal":
            print("💔  الحرب جعلتك وحشاً... والعالم لن ينسى.")
        elif ending_type == "broken_mind":
            print("🧠  الحرب انتهت، لكنها لن تنتهي بداخلك.")
        elif ending_type == "last_standing":
            print("⚔️  أنت البطل الوحيد... لكن البطولة مؤلمة.")
        elif ending_type == "guardian_angel":
            print("👼  أنت أفضل ما في البشرية، حتى في الحرب.")
        else:
            print("🎖️  لقد أديت واجبك. السلام لشهدائك.")
        print("⭐" * 25)
        
        print("\n📌  كل قرار يغير النهاية... هل ستلعب مجدداً؟")
    
    # ========== دوال معالجة الأحداث ==========
    
    def process_turn(self):
        """معالجة دورة اللعبة"""
        
        self.days_in_service += 1
        
        # تغيير الطقس
        if random.random() < 0.2:
            self.weather = random.choice(list(Weather))
            self._slow_print(f"\n🌤️  تغير الطقس: {self.weather.icon} {self.weather.arabic_name}")
        
        # تحديث تواجد العدو
        self.map.update_enemy_presence()
        
        # تحديث العلاقات
        active = [s for s in self.platoon if s.is_alive]
        if len(active) >= 2:
            self.relationship_manager.update_relationships(active)
        
        # أحداث عشوائية (30% فرصة)
        if random.random() < 0.3:
            event = self.event_system.get_random_event()
            if event:
                self.event_system.handle_event(event)
                return True  # حدث حدث
        
        return False  # لا حدث
    
    # ========== القوائم ==========
    
    def main_menu(self) -> int:
        """القائمة الرئيسية"""
        
        self._clear_screen()
        self._print_header("🎖️  قائد الكتيبة: الحرب من الداخل")
        
        print("""
        ╔══════════════════════════════════════════════╗
        ║                                              ║
        ║    1. ▶️  بدء لعبة جديدة                     ║
        ║    2. 📂  تحميل لعبة محفوظة                  ║
        ║    3. ❓  تعليمات                            ║
        ║    4. 🚪  خروج                               ║
        ║                                              ║
        ╚══════════════════════════════════════════════╝
        """)
        
        return self._get_input("اختر رقم: ", 1, 4)
    
    def show_instructions(self):
        """عرض التعليمات"""
        
        self._clear_screen()
        self._print_header("📚  تعليمات اللعبة")
        
        print("""
        أنت قائد كتيبة صغيرة مكونة من 7 جنود.
        
        🎯  الهدف:
        البقاء إنساناً في ظروف لا إنسانية.
        الموازنة بين أوامر القائد وضميرك.
        
        📊  المؤشرات:
        • التقييم العسكري: رضا القائد عنك
        • الصحة النفسية: حالتك العقلية
        • احترام الذات: كيف ترى نفسك
        • حب العائلة: علاقتك بأهلك
        • تماسك الكتيبة: قوة الوحدة
        
        📢  السمعة:
        • بين الجنود: ثقتهم بك
        • بين المدنيين: نظرتهم لك
        • لدى القيادة: مكانتك
        
        🎮  طريقة اللعب:
        • واجه أوامر صعبة
        • اختر قراراتك بحكمة
        • كل قرار له عواقب
        • استشر كتيبتك عند الحاجة
        • أحداث عشوائية غير متوقعة (30% فرصة كل يوم)
        
        🏁  النهايات المتعددة:
        • 11 نهاية مختلفة حسب قراراتك
        • أنقذ المدنيين لتحصل على نهاية الملاك الحارس
        • اقتل مدنيين لتصبح مجرم حرب
        • انهيار نفسي إذا خسرت إنسانيتك
        • بطولة مؤلمة إذا خسرت كل رجالك
        
        💾  حفظ اللعبة:
        • يمكنك الحفظ في أي وقت
        • استخدم خيار الحفظ في القائمة
        """)
        
        input("\nاضغط Enter للعودة...")
    
    def _show_endings_stats(self):
        """عرض إحصائيات النهايات المحتملة"""
        self._clear_screen()
        self._print_header("📊  مسارك نحو النهاية")
        
        ethical_score = self.civilians_saved_total - self.civilians_killed_total * 3 - self.ethical_violations_total * 5
        
        print(f"""
        بناءً على قراراتك حتى الآن:
        
        👨‍👩‍👧 مدنيون منقذون: {self.civilians_saved_total}
        💔 ضحايا مدنيون: {self.civilians_killed_total}
        ⚖️ انتهاكات أخلاقية: {self.ethical_violations_total}
        🛑 عصيان أوامر: {self.disobeyed_orders}
        
        🧠 صحتك النفسية: {self.mental_health}%
        🎯 احترام الذات: {self.self_respect}%
        
        النهايات المحتملة حالياً:
        """)
        
        if ethical_score > 100:
            print("✅ أنت في طريقك لتصبح منقذاً (نهاية بطولية)")
        elif ethical_score < -50:
            print("⚠️ أنت في طريقك لتصبح مجرم حرب")
        
        if self.mental_health < 40:
            print("⚠️ صحتك النفسية خطيرة... خطر الانهيار قريب")
        
        if self.disobeyed_orders > 5:
            print("⚠️ كثرة العصيان قد تؤدي لمحاكمة عسكرية")
        
        if self.civilians_saved_total > 30:
            print("👼 قريب من نهاية الملاك الحارس")
        
        input("\nاضغط Enter للمتابعة...")
    
    # ========== دوال تنفيذ الإجراءات ==========
    
    def _handle_order(self):
        """معالجة أمر جديد - نظام ديناميكي بالكامل"""
        
        # توليد أمر ديناميكي
        order = get_dynamic_order(self)
        
        self._clear_screen()
        self._print_header(f"📢  {order['title']}")
        
        print(f"\n{order['full_description']}")
        
        # حساب قوة العدو ديناميكياً
        player_power = sum(s.combat_power() for s in self.platoon if s.is_alive)
        enemy_mult = random.uniform(0.5, 2.0)
        enemy_power = int(player_power * enemy_mult) if player_power > 0 else 100
        enemy_percent = int((enemy_power / player_power) * 100) if player_power > 0 else 100
        
        print(f"⚔️  تقدير قوة العدو: {enemy_percent}% من قوتكم")
        
        # إضافة تحذير حسب قوة العدو
        if enemy_percent > 150:
            print("⚠️  تحذير: العدو يتفوق عليكم عددياً بشكل كبير!")
        elif enemy_percent > 120:
            print("⚠️  تنبيه: العدو أقوى منكم")
        elif enemy_percent < 70:
            print("✅  فرصة جيدة: قوتكم تفوق قوة العدو")
        
        print("\n" + "─" * 70)
        print("🎯  خياراتك التكتيكية:")
        print("─" * 70)
        
        # عرض الخيارات
        for i, option in enumerate(order["display_options"], 1):
            # إضافة تحذيرات للخيارات الخطيرة
            if "اقتحام" in option or "هجوم" in option:
                risk = random.randint(40, 70)
                print(f"{i}. {option} [خطر: {risk}%]")
            elif "تسلل" in option:
                risk = random.randint(30, 50)
                print(f"{i}. {option} [خطر: {risk}%]")
            elif "انسحاب" in option:
                risk = random.randint(10, 30)
                print(f"{i}. {option} [خطر: {risk}%]")
            elif "ترك" in option or "تجاهل" in option:
                risk = random.randint(5, 20)
                print(f"{i}. {option} [خطر: {risk}%]")
            else:
                print(f"{i}. {option}")
        
        choice = self._get_input("\nاختر قرارك (0 للعودة): ", 0, len(order["display_options"]))
        
        if choice == 0:
            return
        
        selected = order["display_options"][choice-1]
        
        # استشارة الكتيبة (إذا اختارها)
        if "استشارة" in selected:
            self._slow_print("\n🗣️  تستشير الكتيبة...")
            advice = self.platoon_ai.get_collective_advice({
                'enemy_force': enemy_percent,
                'order_type': order['type'],
                'location': self.map.current_location
            })
            print(f"💬  {advice}")
            time.sleep(2)
            
            # إعادة الاختيار
            self._handle_order()
            return
        
        # تطبيق نتائج القرار
        self._apply_order_results(order, selected, enemy_percent)
    
    def _apply_order_results(self, order: Dict, selected: str, enemy_percent: int):
        """تطبيق نتائج الأمر"""
        
        self.days_in_service += 1
        self.battles_fought += 1
        
        print("\n" + "─" * 70)
        print("⚡  تنفيذ القرار...")
        
        # تحديد نتيجة القرار حسب نوع الأمر والخيار
        if "هجوم" in selected or "اقتحام" in selected:
            # قرار هجومي
            success_chance = 0.5 - (enemy_percent - 100) / 200  # كلما زاد العدو، قلت الفرصة
            success_chance = max(0.1, min(0.9, success_chance))  # تقييد بين 10% و 90%
            
            if random.random() < success_chance:
                print("✅  الهجوم ناجح! العدو يتكبد خسائر.")
                self.victories += 1
                self.military_rank = clamp(self.military_rank + 15)
                self.reputation['among_command'] = clamp(self.reputation['among_command'] + 10)
                
                # خسائر قليلة
                casualties = random.randint(0, 1)
                if casualties > 0:
                    self._apply_casualties_to_platoon(casualties)
                    print(f"⚠️  خسارة {casualties} جنود")
            else:
                print("❌  الهجوم فشل! خسائر فادحة.")
                self.military_rank = clamp(self.military_rank - 20)
                self.reputation['among_command'] = clamp(self.reputation['among_command'] - 15)
                
                # خسائر كبيرة
                casualties = random.randint(1, 3)
                self._apply_casualties_to_platoon(casualties)
                print(f"💔  استشهد {casualties} جنود")
        
        elif "تسلل" in selected:
            # قرار تسلل
            success_chance = 0.6
            
            if random.random() < success_chance:
                print("✅  التسلل ناجح! جمعتم معلومات قيمة.")
                self.reputation['among_command'] = clamp(self.reputation['among_command'] + 5)
            else:
                print("❌  تم اكتشافكم! العدو يهاجم.")
                casualties = random.randint(1, 2)
                self._apply_casualties_to_platoon(casualties)
                print(f"💔  استشهد {casualties} جنود")
        
        elif "تعزيزات" in selected or "دعم" in selected:
            # طلب تعزيزات
            if random.random() < 0.4:
                print("✅  التعزيزات وصلت! قوتكم ازدادت.")
                self.military_rank = clamp(self.military_rank + 10)
            else:
                print("❌  التعزيزات لم تصل في الوقت المناسب.")
                self.military_rank = clamp(self.military_rank - 5)
        
        elif "إخلاء" in selected or "مدنيين" in selected or "أنقذ" in selected:
            # قرار إنساني
            saved = random.randint(10, 50)
            self.civilians_saved += saved
            self.civilians_saved_total += saved
            self.reputation['among_civilians'] = clamp(self.reputation['among_civilians'] + 20)
            self.self_respect = clamp(self.self_respect + 15)
            print(f"✅  أنقذتم {saved} مدنياً! المدنيون يدعون لكم.")
            
        elif "ترك" in selected or "تجاهل" in selected or "غير أخلاقي" in selected:
            # قرار قاسٍ
            self.reputation['among_civilians'] = clamp(self.reputation['among_civilians'] - 30)
            self.self_respect = clamp(self.self_respect - 20)
            self.mental_health = clamp(self.mental_health - 15)
            self.ethical_violations += 1
            self.ethical_violations_total += 1
            
            # إذا كان فيه ضحايا مدنيين
            if "مدنيين" in selected or "ترك" in selected:
                killed = random.randint(5, 20)
                self.civilians_killed_total += killed
                print(f"😔  {killed} مدني استشهدوا بسبب قرارك...")
            else:
                print("😔  القرار يثقل ضميرك...")
        
        elif "انسحاب" in selected:
            # انسحاب
            print("🏃  تنسحبون من المنطقة.")
            self.military_rank = clamp(self.military_rank - 10)
            self.reputation['among_command'] = clamp(self.reputation['among_command'] - 10)
            
            # احتمال خسائر أثناء الانسحاب
            if random.random() < 0.3:
                casualties = random.randint(0, 1)
                if casualties > 0:
                    self._apply_casualties_to_platoon(casualties)
                    print(f"⚠️  خسارة {casualties} جنود أثناء الانسحاب")
        
        elif "عصيان" in selected or "قتال حتى آخر" in selected:
            # عصيان أوامر
            self.disobeyed_orders += 1
            print("⚠️  أنت تعصي أمر القائد! هذا قد يكلفك الكثير.")
            self.military_rank = clamp(self.military_rank - 25)
            self.reputation['among_command'] = clamp(self.reputation['among_command'] - 20)
            
            # معركة يائسة
            if random.random() < 0.3:
                print("✨  المفاجأة! العصيان كان صحيحاً! انتصار بطولي!")
                self.victories += 1
                self.self_respect = clamp(self.self_respect + 20)
                self.reputation['among_soldiers'] = clamp(self.reputation['among_soldiers'] + 25)
            else:
                print("💔  العصيان كلفكم الكثير...")
                casualties = random.randint(1, 4)
                self._apply_casualties_to_platoon(casualties)
                print(f"💔  استشهد {casualties} جنود")
        
        else:
            # قرار افتراضي
            print("🎲  تنفذ القرار...")
            if random.random() < 0.5:
                print("✅  القرار كان موفقاً!")
                self.military_rank = clamp(self.military_rank + 5)
            else:
                print("⚠️  النتائج لم تكن كما توقعت.")
                self.military_rank = clamp(self.military_rank - 5)
        
        # تحديث تماسك الكتيبة
        alive_count = len([s for s in self.platoon if s.is_alive])
        self.platoon_cohesion = clamp(self.platoon_cohesion + (alive_count - 4) * 2)
        
        print("─" * 70)
        time.sleep(3)
    
    def _apply_casualties_to_platoon(self, count: int):
        """تطبيق خسائر على الكتيبة"""
        alive = [s for s in self.platoon if s.is_alive]
        if not alive:
            return
        
        casualties = random.sample(alive, min(count, len(alive)))
        for soldier in casualties:
            soldier.is_alive = False
            self.soldiers_killed += 1
            
            # تأثير على العلاقات
            messages = self.relationship_manager.handle_death(soldier, self.platoon)
            for msg in messages:
                print(msg)
    
    def _handle_map(self):
        """معالجة التنقل على الخريطة"""
        
        self._clear_screen()
        print(self.map.show_map())
        
        moves = self.map.get_available_moves()
        if moves:
            print("\n📍  يمكنك التحرك إلى:")
            for i, (loc, name) in enumerate(moves, 1):
                danger = self.map.locations[loc]['enemies']
                print(f"{i}. {name} (خطر: {danger}%)")
            
            choice = self._get_input("\nاختر وجهتك (0 للإلغاء): ", 0, len(moves))
            if choice > 0:
                success, msg = self.map.move_to(moves[choice-1][0])
                print(f"\n{msg}")
                time.sleep(2)
    
    def _handle_medical(self):
        """معالجة العلاج - نسخة محسنة"""
        self._clear_screen()
        self._print_header("🩺  العلاج الميداني")
        
        # البحث عن الجرحى
        wounded = [s for s in self.platoon if s.is_alive and s.wounds]
        
        if not wounded:
            print("\n✅ لا يوجد جرحى حالياً.")
            time.sleep(1.5)
            return

        # البحث عن المسعف
        medic = next((s for s in self.platoon if s.role == "مسعف" and s.is_alive), None)
        
        print(f"\n👨‍⚕️  المسعف المتاح: {medic.name if medic else 'لا يوجد مسعف'}")
        print("\n📋  قائمة الجرحى:")
        
        for i, soldier in enumerate(wounded, 1):
            wounds_list = []
            for w in soldier.wounds:
                if hasattr(w, 'value') and isinstance(w.value, tuple):
                    wounds_list.append(w.value[1])  # الاسم العربي
                else:
                    wounds_list.append(str(w))
            wounds_str = ", ".join(wounds_list)
            print(f"{i}. {soldier.name} (الإصابة: {wounds_str})")

        choice = self._get_input("\nاختر جندياً لعلاجه (0 للعودة): ", 0, len(wounded))
        
        if choice > 0:
            target = wounded[choice-1]
            
            if medic:
                # نجاح العلاج يعتمد على مهارة المسعف
                success_chance = 0.7 + (medic.experience / 500)  # خبرة المسعف تزيد الفرصة
                
                if random.random() < success_chance:
                    target.wounds = []
                    target.health = min(100, target.health + 40)
                    print(f"\n✅ قام {medic.name} بتضميد جراح {target.name} بنجاح.")
                    logger.info(f"✅ {medic.name} عالج {target.name} بنجاح")
                    
                    # زيادة خبرة المسعف
                    medic.add_experience(10)
                else:
                    target.health = min(100, target.health + 15)
                    print(f"\n⚠️  محاولة العلاج لم تنجح تماماً، لكن الحالة تحسنت قليلاً.")
            else:
                print("\n⚠️ لا يوجد مسعف في الكتيبة! محاولة علاج بدائية...")
                target.health = min(100, target.health + 10)
                
                # فرصة 30% لتفاقم الإصابة بدون مسعف
                if random.random() < 0.3 and target.wounds:
                    extra_wound = random.choice(list(Wound))
                    target.add_wound(extra_wound)
                    print(f"❌ تفاقمت الإصابة! {target.name} أصيب بـ {extra_wound.value[1]}")
            
            time.sleep(2)
        
        # تحديث تماسك الكتيبة بعد العلاج
        cohesion_boost = len([s for s in self.platoon if s.is_alive and not s.wounds]) * 2
        self.platoon_cohesion = clamp(self.platoon_cohesion + cohesion_boost)
    
    # ========== الحلقة الرئيسية للعبة ==========
    
    def play(self):
        """بدء اللعبة"""
        
        # القائمة الرئيسية
        while True:
            choice = self.main_menu()
            
            if choice == 1:
                self._clear_screen()
                self.player_name = input("ما اسمك أيها القائد؟ ").strip()
                if not self.player_name:
                    self.player_name = "القائد المجهول"
                break
            elif choice == 2:
                saves = GameSaver.list_saves()
                if saves:
                    print("\n📂  الألعاب المحفوظة:")
                    for save in saves:
                        print(f"  Slot {save['slot']}")
                    slot = self._get_input("\nاختر slot: ", 1, 9)
                    self._load_game(slot)
                    break
                else:
                    print("\n⚠️  لا توجد ألعاب محفوظة")
                    time.sleep(2)
            elif choice == 3:
                self.show_instructions()
            else:
                print("\n👋  إلى اللقاء!")
                return
        
        self._slow_print(f"\nحظاً موفقاً أيها القائد {self.player_name}...")
        self._slow_print("كل قرار ستتخذه سيشكل مستقبلك ومستقبل رجالك.")
        self._slow_print("هناك 11 نهاية محتملة... أيكم ستكون؟")
        time.sleep(3)
        
        # حلقة اللعبة الرئيسية
        while not self.game_over:
            self.display_status()
            
            # حدث تلقائي (قد يحدث أو لا يحدث)
            event_happened = self.process_turn()
            if self.check_game_over():
                break
            
            # إذا لم يحدث حدث، اعرض القائمة
            if not event_happened:
                # قائمة الإجراءات
                print("\n🎮  ماذا تريد أن تفعل؟")
                print("1. 📢  استلام أمر جديد")
                print("2. 🗺️  عرض الخريطة والتنقل")
                print("3. 🩺  علاج الجرحى")
                print("4. 💾  حفظ اللعبة")
                print("5. 📊  عرض إحصائيات النهايات")
                print("6. 🚪  القائمة الرئيسية")
                
                action = self._get_input("\nاختر (1-6, 0 للخروج): ", 0, 6)
                
                if action == 0:
                    if input("هل تريد الخروج؟ (نعم/لا): ").strip() in ['نعم', 'y']:
                        break
                elif action == 1:
                    self._handle_order()
                elif action == 2:
                    self._handle_map()
                elif action == 3:
                    self._handle_medical()
                elif action == 4:
                    slot = self._get_input("اختر slot للحفظ (1-9): ", 1, 9)
                    self._save_game(slot)
                elif action == 5:
                    self._show_endings_stats()
                else:
                    break
            
            if self.check_game_over():
                break
        
        # عرض النهاية القصصية
        self._show_ending_story()