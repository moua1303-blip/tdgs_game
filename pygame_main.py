"""
الملف الرئيسي لواجهة Pygame
pygame_main.py
"""

import pygame
import sys
import os
import random
from typing import Optional, Dict, List
from game import PlatoonCommanderGame
from sprites import SoldierSprite, EffectSprite, MapSprite
from ui_elements import Button, TextBox, ProgressBar, Notification
from sound_manager import SoundManager
from battle_view import BattleView
from utils import logger

# تهيئة Pygame
pygame.init()
pygame.mixer.init()

# إعدادات الشاشة
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# الألوان
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)

# حالات اللعبة
MENU = 0
GAME = 1
BATTLE = 2
EVENT = 3
MAP_VIEW = 4
END_SCREEN = 5


class PygameGame:
    """واجهة Pygame الرئيسية للعبة"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎖️ قائد الكتيبة - The Platoon Commander")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # تحميل الخطوط
        self.load_fonts()
        
        # مدير الصوت
        self.sound_manager = SoundManager()
        
        # حالة اللعبة
        self.state = MENU
        self.game: Optional[PlatoonCommanderGame] = None
        
        # عناصر الواجهة
        self.buttons: List[Button] = []
        self.notifications: List[Notification] = []
        
        # الصور المتحركة
        self.soldier_sprites: Dict[str, SoldierSprite] = {}
        self.effects: List[EffectSprite] = []
        
        # الخلفية
        self.background = self.create_background()
        
        # إنشاء القوائم
        self.create_menu_buttons()
        
        logger.info("✅ واجهة Pygame initialized")
    
    def load_fonts(self):
        """تحميل الخطوط"""
        try:
            # محاولة تحميل خط عربي
            self.title_font = pygame.font.Font("assets/fonts/arabic.ttf", 64)
            self.header_font = pygame.font.Font("assets/fonts/arabic.ttf", 48)
            self.normal_font = pygame.font.Font("assets/fonts/arabic.ttf", 32)
            self.small_font = pygame.font.Font("assets/fonts/arabic.ttf", 24)
        except:
            # إذا لم يوجد، استخدم الخط الافتراضي
            print("⚠️ لم يتم العثور على خط عربي، استخدام الخط الافتراضي")
            self.title_font = pygame.font.Font(None, 64)
            self.header_font = pygame.font.Font(None, 48)
            self.normal_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
    
    def create_background(self):
        """إنشاء خلفية متحركة"""
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # تدرج لوني
        for y in range(SCREEN_HEIGHT):
            color_value = int(40 + (y / SCREEN_HEIGHT) * 30)
            color = (color_value, color_value, color_value + 10)
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
        
        # نجوم عشوائية (للخلفية)
        for _ in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.randint(100, 255)
            background.set_at((x, y), (brightness, brightness, brightness))
        
        return background
    
    def create_menu_buttons(self):
        """إنشاء أزرار القائمة الرئيسية"""
        button_width = 300
        button_height = 60
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.menu_buttons = [
            Button(center_x, 250, button_width, button_height, 
                   "▶️ بدء لعبة جديدة", self.normal_font, GREEN, self.start_new_game),
            Button(center_x, 330, button_width, button_height,
                   "📂 تحميل لعبة", self.normal_font, BLUE, self.load_game),
            Button(center_x, 410, button_width, button_height,
                   "❓ تعليمات", self.normal_font, YELLOW, self.show_instructions),
            Button(center_x, 490, button_width, button_height,
                   "⚙️ إعدادات", self.normal_font, GRAY, self.show_settings),
            Button(center_x, 570, button_width, button_height,
                   "🚪 خروج", self.normal_font, RED, self.quit_game)
        ]
    
    def create_game_buttons(self):
        """إنشاء أزرار شاشة اللعبة"""
        self.game_buttons = [
            Button(50, SCREEN_HEIGHT - 80, 200, 50,
                   "📢 أمر جديد", self.small_font, WHITE, self.get_new_order),
            Button(280, SCREEN_HEIGHT - 80, 200, 50,
                   "🗺️ خريطة", self.small_font, WHITE, self.show_map),
            Button(510, SCREEN_HEIGHT - 80, 200, 50,
                   "🩺 علاج", self.small_font, WHITE, self.treat_wounded),
            Button(740, SCREEN_HEIGHT - 80, 200, 50,
                   "💾 حفظ", self.small_font, WHITE, self.save_game),
            Button(970, SCREEN_HEIGHT - 80, 200, 50,
                   "📊 إحصائيات", self.small_font, WHITE, self.show_stats)
        ]
    
    # ========== دوال الرسم ==========
    
    def draw_text(self, text, font, color, x, y, center=True):
        """رسم نص على الشاشة"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
    
    def draw_menu(self):
        """رسم القائمة الرئيسية"""
        self.screen.blit(self.background, (0, 0))
        
        # عنوان اللعبة مع ظل
        shadow_offset = 4
        self.draw_text("🎖️ قائد الكتيبة", self.title_font, DARK_GRAY, 
                      SCREEN_WIDTH//2 + shadow_offset, 120 + shadow_offset)
        self.draw_text("🎖️ قائد الكتيبة", self.title_font, GOLD, 
                      SCREEN_WIDTH//2, 120)
        
        self.draw_text("The Platoon Commander", self.normal_font, WHITE,
                      SCREEN_WIDTH//2, 180)
        
        # رسم الأزرار
        for button in self.menu_buttons:
            button.draw(self.screen)
    
    def draw_game_screen(self):
        """رسم شاشة اللعبة الرئيسية"""
        self.screen.blit(self.background, (0, 0))
        
        if not self.game:
            return
        
        # شريط المؤشرات العلوي
        self.draw_status_bar()
        
        # الخريطة المصغرة
        self.draw_minimap()
        
        # لوحة الجنود
        self.draw_soldiers_panel()
        
        # معلومات الموقع والطقس
        self.draw_location_info()
        
        # أزرار اللعبة
        for button in self.game_buttons:
            button.draw(self.screen)
        
        # الإشعارات
        for notification in self.notifications[:]:
            notification.update()
            notification.draw(self.screen)
            if notification.is_expired():
                self.notifications.remove(notification)
    
    def draw_status_bar(self):
        """رسم شريط المؤشرات العلوي"""
        bar_height = 80
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.line(self.screen, GOLD, (0, bar_height), (SCREEN_WIDTH, bar_height), 2)
        
        # المؤشرات
        indicators = [
            (f"🎖️ {self.game.military_rank}%", GREEN, 150),
            (f"🧠 {self.game.mental_health}%", BLUE, 300),
            (f"🎯 {self.game.self_respect}%", YELLOW, 450),
            (f"👪 {self.game.family_love}%", ORANGE, 600),
            (f"⚔️ {self.game.platoon_cohesion}%", PURPLE, 750)
        ]
        
        for text, color, x in indicators:
            self.draw_text(text, self.small_font, color, x, bar_height//2)
        
        # الأيام
        self.draw_text(f"📅 يوم {self.game.days_in_service}", self.normal_font, WHITE,
                      SCREEN_WIDTH - 100, bar_height//2)
    
    def draw_minimap(self):
        """رسم الخريطة المصغرة"""
        map_x = 20
        map_y = 100
        map_width = 250
        map_height = 180
        
        # خلفية الخريطة
        pygame.draw.rect(self.screen, (30, 30, 40), (map_x, map_y, map_width, map_height))
        pygame.draw.rect(self.screen, GOLD, (map_x, map_y, map_width, map_height), 2)
        
        if not self.game:
            return
        
        # رسم المناطق
        locations = list(self.game.map.locations.items())
        center_x = map_x + map_width // 2
        center_y = map_y + map_height // 2
        
        for i, (loc, info) in enumerate(locations):
            angle = (i / len(locations)) * 2 * 3.14159
            radius = 60
            loc_x = int(center_x + radius * cos(angle))
            loc_y = int(center_y + radius * sin(angle))
            
            # لون حسب تواجد العدو
            danger = info['enemies']
            if danger > 70:
                color = RED
            elif danger > 30:
                color = ORANGE
            else:
                color = GREEN
            
            # رسم الموقع
            pygame.draw.circle(self.screen, color, (loc_x, loc_y), 10)
            
            # علامة الموقع الحالي
            if loc == self.game.map.current_location:
                pygame.draw.circle(self.screen, GOLD, (loc_x, loc_y), 14, 2)
    
    def draw_soldiers_panel(self):
        """رسم لوحة الجنود"""
        panel_x = SCREEN_WIDTH - 320
        panel_y = 100
        panel_width = 300
        panel_height = 500
        
        # خلفية اللوحة
        pygame.draw.rect(self.screen, (20, 20, 30), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, GOLD, (panel_x, panel_y, panel_width, panel_height), 2)
        
        self.draw_text("👥 الكتيبة", self.normal_font, WHITE, 
                      panel_x + panel_width//2, panel_y + 25)
        
        if not self.game:
            return
        
        # رسم الجنود
        for i, soldier in enumerate(self.game.platoon):
            if i >= 7:
                break
            
            y = panel_y + 70 + i * 60
            
            # خلفية الجندي
            if soldier.is_alive:
                bg_color = (40, 40, 50)
                icon = "✅"
            else:
                bg_color = (50, 20, 20)
                icon = "💀"
            
            pygame.draw.rect(self.screen, bg_color, (panel_x + 10, y - 5, panel_width - 20, 50))
            
            # أيقونة الحالة
            self.draw_text(icon, self.small_font, WHITE, panel_x + 30, y + 15)
            
            # اسم الجندي
            self.draw_text(soldier.name, self.small_font, WHITE, panel_x + 80, y + 15, False)
            
            # شريط الصحة
            bar_x = panel_x + 180
            bar_y = y + 10
            health_width = (soldier.health / 100) * 100
            
            pygame.draw.rect(self.screen, RED, (bar_x, bar_y, 100, 8))
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, health_width, 8))
    
    def draw_location_info(self):
        """رسم معلومات الموقع والطقس"""
        x = 300
        y = 120
        
        if not self.game:
            return
        
        info_texts = [
            f"📍 الموقع: {self.game.map.locations[self.game.map.current_location]['name']}",
            f"🌤️ الطقس: {self.game.weather.icon} {self.game.weather.arabic_name}",
            f"⚔️ قوة العدو: {self.game.map.locations[self.game.map.current_location]['enemies']}%"
        ]
        
        for i, text in enumerate(info_texts):
            self.draw_text(text, self.small_font, WHITE, x, y + i * 30, False)
    
    # ========== دوال الإجراءات ==========
    
    def start_new_game(self):
        """بدء لعبة جديدة"""
        self.game = PlatoonCommanderGame()
        self.state = GAME
        self.create_game_buttons()
        self.add_notification("🎮 بدأت لعبة جديدة!", GREEN)
        self.sound_manager.play_sound("game_start")
        
        # إنشاء الصور المتحركة للجنود
        self.create_soldier_sprites()
    
    def load_game(self):
        """تحميل لعبة محفوظة"""
        saves = self.list_saves()
        if saves:
            # TODO: عرض قائمة الحفظات
            self.game = PlatoonCommanderGame(load_slot=1)
            self.state = GAME
            self.create_game_buttons()
            self.add_notification("📂 تم تحميل اللعبة", BLUE)
            self.create_soldier_sprites()
        else:
            self.add_notification("⚠️ لا توجد ألعاب محفوظة", RED)
    
    def show_instructions(self):
        """عرض التعليمات"""
        self.state = MENU  # سنضيف شاشة تعليمات لاحقاً
        self.add_notification("📚 قريباً: شاشة التعليمات", YELLOW)
    
    def show_settings(self):
        """عرض الإعدادات"""
        self.add_notification("⚙️ قريباً: الإعدادات", GRAY)
    
    def quit_game(self):
        """خروج من اللعبة"""
        self.running = False
    
    def get_new_order(self):
        """استلام أمر جديد"""
        if not self.game:
            return
        self.game._handle_order()
        self.add_notification("📢 تم استلام أمر جديد", BLUE)
        self.sound_manager.play_sound("order_received")
    
    def show_map(self):
        """عرض الخريطة"""
        self.state = MAP_VIEW
    
    def treat_wounded(self):
        """علاج الجرحى"""
        if not self.game:
            return
        self.game._handle_medical()
        self.add_notification("🩺 تم علاج الجرحى", GREEN)
    
    def save_game(self):
        """حفظ اللعبة"""
        if not self.game:
            return
        self.game._save_game(1)
        self.add_notification("💾 تم حفظ اللعبة", GREEN)
    
    def show_stats(self):
        """عرض الإحصائيات"""
        self.game._show_endings_stats()
    
    def add_notification(self, text: str, color: tuple, duration: int = 3):
        """إضافة إشعار"""
        notification = Notification(text, self.small_font, color, 
                                   SCREEN_WIDTH//2, 150, duration)
        self.notifications.append(notification)
    
    def create_soldier_sprites(self):
        """إنشاء الصور المتحركة للجنود"""
        if not self.game:
            return
        
        for soldier in self.game.platoon:
            if soldier.is_alive:
                # موقع عشوائي في الشاشة
                x = random.randint(500, 800)
                y = random.randint(200, 500)
                sprite = SoldierSprite(soldier, x, y)
                self.soldier_sprites[soldier.name] = sprite
    
    def list_saves(self) -> list:
        """عرض قائمة الحفظات"""
        saves = []
        if os.path.exists("saves"):
            for file in os.listdir("saves"):
                if file.endswith('.json'):
                    saves.append(file)
        return saves
    
    # ========== دالة تشغيل الأحداث ==========
    
    def handle_events(self):
        """معالجة أحداث Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GAME:
                        self.state = MENU
                    elif self.state == MENU:
                        self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # زر الفأرة الأيسر
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.state == MENU:
                        for button in self.menu_buttons:
                            if button.is_clicked(mouse_pos):
                                button.action()
                    
                    elif self.state == GAME:
                        for button in self.game_buttons:
                            if button.is_clicked(mouse_pos):
                                button.action()
    
    # ========== دالة التشغيل الرئيسية ==========
    
    def run(self):
        """تشغيل اللعبة"""
        while self.running:
            self.handle_events()
            
            # رسم حسب الحالة
            if self.state == MENU:
                self.draw_menu()
            elif self.state == GAME:
                self.draw_game_screen()
            elif self.state == BATTLE:
                # TODO: شاشة المعركة
                pass
            elif self.state == MAP_VIEW:
                # TODO: شاشة الخريطة الكاملة
                pass
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# دالة مساعدة
def cos(angle):
    """جيب تمام"""
    import math
    return math.cos(angle)


def sin(angle):
    """جيب"""
    import math
    return math.sin(angle)


if __name__ == "__main__":
    game = PygameGame()
    game.run()