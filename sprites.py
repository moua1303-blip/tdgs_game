"""
الصور المتحركة للعبة
sprites.py
"""

import pygame
import random
import math
from typing import Optional
from soldier import Soldier


class SoldierSprite(pygame.sprite.Sprite):
    """صورة متحركة للجندي"""
    
    def __init__(self, soldier: Soldier, x: int, y: int):
        super().__init__()
        self.soldier = soldier
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 2
        
        # إنشاء سطح للجندي
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        # ألوان حسب الدور
        self.colors = {
            "مسعف": (255, 100, 100),      # أحمر
            "قناص": (100, 100, 255),       # أزرق
            "مدفعي": (150, 150, 150),      # رمادي
            "اتصالات": (255, 255, 100),    # أصفر
            "مهندس قتالي": (255, 150, 50), # برتقالي
            "استطلاع": (100, 255, 100),    # أخضر
            "جندي مشاة": (200, 200, 200)   # فاتح
        }
        
        self.color = self.colors.get(soldier.role, (200, 200, 200))
        self.animation_frame = 0
        self.direction = 1  # 1 = يمين, -1 = يسار
        
        # رسم الجندي
        self.draw_soldier()
    
    def draw_soldier(self):
        """رسم شكل الجندي"""
        self.image.fill((0, 0, 0, 0))  # شفاف
        
        # الجسم
        body_color = self.color
        if not self.soldier.is_alive:
            body_color = (100, 100, 100)  # رمادي للموتى
        
        # رأس
        pygame.draw.circle(self.image, body_color, (20, 15), 8)
        
        # عينان
        eye_color = (255, 255, 255) if self.soldier.is_alive else (150, 150, 150)
        pygame.draw.circle(self.image, eye_color, (16, 12), 2)
        pygame.draw.circle(self.image, eye_color, (24, 12), 2)
        
        # قبعة (حسب الرتبة)
        hat_color = (255, 215, 0) if self.soldier.rank.multiplier > 2 else (200, 200, 200)
        pygame.draw.rect(self.image, hat_color, (12, 3, 16, 6))
        
        # جسم
        pygame.draw.rect(self.image, body_color, (12, 23, 16, 25))
        
        # سلاح حسب الدور
        if self.soldier.role == "قناص":
            pygame.draw.line(self.image, (50, 50, 50), (28, 30), (40, 25), 3)
        elif self.soldier.role == "مدفعي":
            pygame.draw.rect(self.image, (50, 50, 50), (28, 35, 15, 5))
        elif self.soldier.role == "مسعف":
            pygame.draw.circle(self.image, (255, 255, 255), (30, 30), 5)
            pygame.draw.line(self.image, (255, 0, 0), (27, 27), (33, 33), 2)
        
        # حالة الصحة
        health_percent = self.soldier.health / 100
        health_width = int(30 * health_percent)
        if health_width > 0:
            health_color = (0, 255, 0) if health_percent > 0.5 else (255, 255, 0) if health_percent > 0.2 else (255, 0, 0)
            pygame.draw.rect(self.image, health_color, (5, 55, health_width, 3))
    
    def update(self):
        """تحديث حركة الجندي"""
        if not self.soldier.is_alive:
            return
        
        # حركة عشوائية بسيطة
        self.animation_frame += 1
        
        if self.animation_frame % 60 == 0:
            self.target_x = self.x + random.randint(-20, 20)
            self.target_y = self.y + random.randint(-10, 10)
            
            # تحديث الاتجاه
            if self.target_x > self.x:
                self.direction = 1
            else:
                self.direction = -1
        
        # تحرك نحو الهدف
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        if abs(dx) > self.speed:
            self.x += self.speed if dx > 0 else -self.speed
        if abs(dy) > self.speed:
            self.y += self.speed if dy > 0 else -self.speed
        
        self.rect.center = (self.x, self.y)
        
        # إعادة الرسم كل فترة للتأثيرات
        if self.animation_frame % 10 == 0:
            self.draw_soldier()


class EffectSprite(pygame.sprite.Sprite):
    """تأثيرات بصرية (انفجارات، دخان، إلخ)"""
    
    def __init__(self, effect_type: str, x: int, y: int):
        super().__init__()
        self.effect_type = effect_type
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = 20
        
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.draw_effect()
    
    def draw_effect(self):
        """رسم التأثير حسب النوع"""
        self.image.fill((0, 0, 0, 0))
        
        if self.effect_type == "explosion":
            # انفجار
            size = int(50 * (1 - self.frame / self.max_frames))
            alpha = int(255 * (1 - self.frame / self.max_frames))
            
            # دائرة صفراء ثم حمراء
            color1 = (255, 255, 0, alpha) if self.frame < 10 else (255, 100, 0, alpha)
            color2 = (255, 0, 0, alpha // 2)
            
            pygame.draw.circle(self.image, color1[:3], (25, 25), size // 2)
            if self.frame > 5:
                pygame.draw.circle(self.image, color2[:3], (25, 25), size // 3)
        
        elif self.effect_type == "smoke":
            # دخان
            size = int(30 * (self.frame / self.max_frames))
            alpha = int(200 * (1 - self.frame / self.max_frames))
            
            for i in range(3):
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                smoke_color = (150, 150, 150, alpha)
                pygame.draw.circle(self.image, smoke_color[:3],
                                 (25 + offset_x, 25 + offset_y), size // 3)
        
        elif self.effect_type == "blood":
            # دم
            if self.frame < 10:
                for _ in range(5):
                    x = random.randint(15, 35)
                    y = random.randint(15, 35)
                    size = random.randint(2, 5)
                    blood_color = (150, 0, 0, 200)
                    pygame.draw.circle(self.image, blood_color[:3], (x, y), size)
    
    def update(self):
        """تحديث التأثير"""
        self.frame += 1
        self.draw_effect()
        
        if self.frame >= self.max_frames:
            self.kill()


class MapSprite(pygame.sprite.Sprite):
    """عناصر الخريطة"""
    
    def __init__(self, map_type: str, x: int, y: int):
        super().__init__()
        self.map_type = map_type
        self.x = x
        self.y = y
        
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.draw_map_element()
    
    def draw_map_element(self):
        """رسم عنصر الخريطة"""
        if self.map_type == "tree":
            # شجرة
            pygame.draw.rect(self.image, (101, 67, 33), (15, 25, 10, 15))  # جذع
            pygame.draw.circle(self.image, (34, 139, 34), (20, 15), 12)     # أوراق
        
        elif self.map_type == "rock":
            # صخرة
            pygame.draw.circle(self.image, (128, 128, 128), (20, 20), 15)
            pygame.draw.circle(self.image, (169, 169, 169), (20, 20), 12)
        
        elif self.map_type == "building":
            # مبنى
            pygame.draw.rect(self.image, (150, 150, 150), (5, 10, 30, 25))
            pygame.draw.rect(self.image, (200, 200, 200), (5, 10, 30, 25), 2)
            
            # نافذة
            pygame.draw.rect(self.image, (255, 255, 0), (12, 15, 8, 8))
            pygame.draw.rect(self.image, (255, 255, 0), (20, 15, 8, 8))
        
        elif self.map_type == "flag":
            # علم
            pygame.draw.line(self.image, (139, 69, 19), (20, 5), (20, 35), 3)
            
            # العلم حسب الانتماء
            flag_color = (0, 255, 0) if random.random() > 0.5 else (255, 0, 0)
            flag_points = [(21, 10), (40, 18), (21, 26)]
            pygame.draw.polygon(self.image, flag_color, flag_points)
        
        elif self.map_type == "campfire":
            # نار مخيم
            if random.random() < 0.5:  # وميض
                pygame.draw.circle(self.image, (255, 100, 0), (20, 25), 8)
                pygame.draw.circle(self.image, (255, 200, 0), (20, 20), 5)
            else:
                pygame.draw.circle(self.image, (255, 150, 0), (20, 23), 7)
                pygame.draw.circle(self.image, (255, 100, 0), (20, 18), 4)