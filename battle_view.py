"""
عرض المعارك بشكل مرئي
battle_view.py
"""

import pygame
import random
import math
from typing import List, Dict, Optional
from soldier import Soldier
from sprites import SoldierSprite, EffectSprite


class BattleView:
    """شاشة عرض المعركة"""
    
    def __init__(self, screen: pygame.Surface, platoon: List[Soldier]):
        self.screen = screen
        self.platoon = platoon
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # مجموعات الصور
        self.friendly_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.effect_sprites = pygame.sprite.Group()
        
        # مواقع الفريقين
        self.friendly_x = self.width // 4
        self.enemy_x = 3 * self.width // 4
        self.ground_y = self.height - 150
        
        # حالة المعركة
        self.battle_active = False
        self.turn = 0
        self.message = ""
        
        # إنشاء الجنود
        self.create_sprites()
    
    def create_sprites(self):
        """إنشاء صور الجنود في ساحة المعركة"""
        # الجنود الأصدقاء
        for i, soldier in enumerate(self.platoon):
            if soldier.is_alive:
                x = self.friendly_x + (i - 3) * 60
                y = self.ground_y - 30
                sprite = SoldierSprite(soldier, x, y)
                self.friendly_sprites.add(sprite)
        
        # جنود العدو (مؤقتين)
        for i in range(6):
            x = self.enemy_x + (i - 3) * 60
            y = self.ground_y - 30
            enemy = self.create_dummy_enemy(f"عدو {i+1}")
            sprite = SoldierSprite(enemy, x, y)
            self.enemy_sprites.add(sprite)
    
    def create_dummy_enemy(self, name: str) -> Soldier:
        """إنشاء عدو تجريبي"""
        from enums import Personality
        return Soldier(name, "جندي مشاة", 30, "أعزب", Personality.COWARD)
    
    def start_battle(self):
        """بدء المعركة"""
        self.battle_active = True
        self.turn = 0
        self.message = "⚔️ بدأت المعركة!"
    
    def update(self):
        """تحديث ساحة المعركة"""
        if not self.battle_active:
            return
        
        self.turn += 1
        
        # معركة تلقائية بسيطة
        if self.turn % 30 == 0:  # كل نصف ثانية (60 FPS)
            self.battle_turn()
        
        # تحديث الصور
        self.friendly_sprites.update()
        self.enemy_sprites.update()
        self.effect_sprites.update()
    
    def battle_turn(self):
        """جولة قتال"""
        if random.random() < 0.5:
            # صديق يهاجم
            if self.enemy_sprites:
                target = random.choice(self.enemy_sprites.sprites())
                self.create_effect("explosion", target.rect.centerx, target.rect.centery)
                
                # إزالة العدو
                self.enemy_sprites.remove(target)
                self.message = "✅ قتل عدو!"
                
                # نصر؟
                if not self.enemy_sprites:
                    self.message = "🏆 انتصار!"
                    self.battle_active = False
        else:
            # عدو يهاجم
            if self.friendly_sprites:
                target = random.choice(self.friendly_sprites.sprites())
                self.create_effect("blood", target.rect.centerx, target.rect.centery)
                
                # إصابة الجندي
                target.soldier.health -= 25
                target.draw_soldier()
                
                if target.soldier.health <= 0:
                    self.friendly_sprites.remove(target)
                    self.message = "💔 جندي استشهد!"
                    
                    # هزيمة؟
                    if not self.friendly_sprites:
                        self.message = "💔 هزيمة!"
                        self.battle_active = False
    
    def create_effect(self, effect_type: str, x: int, y: int):
        """إنشاء تأثير بصري"""
        effect = EffectSprite(effect_type, x, y)
        self.effect_sprites.add(effect)
    
    def draw(self):
        """رسم ساحة المعركة"""
        # خلفية
        self.draw_background()
        
        # رسم الجنود
        self.friendly_sprites.draw(self.screen)
        self.enemy_sprites.draw(self.screen)
        self.effect_sprites.draw(self.screen)
        
        # رسم رسالة المعركة
        self.draw_battle_message()
    
    def draw_background(self):
        """رسم خلفية ساحة المعركة"""
        # سماء
        for y in range(self.height):
            color_value = int(100 - y / self.height * 50)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 50),
                           (0, y), (self.width, y))
        
        # أرض
        ground_rect = pygame.Rect(0, self.ground_y, self.width, self.height - self.ground_y)
        pygame.draw.rect(self.screen, (101, 67, 33), ground_rect)
        
        # تفاصيل الأرض
        for i in range(10):
            x = i * self.width // 10
            pygame.draw.line(self.screen, (139, 69, 19),
                           (x, self.ground_y), (x + 20, self.ground_y + 20), 2)
    
    def draw_battle_message(self):
        """رسم رسالة المعركة"""
        if self.message:
            font = pygame.font.Font(None, 48)
            text = font.render(self.message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width//2, 100))
            
            # خلفية شفافة
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 128))
            self.screen.blit(bg_surface, bg_rect)
            
            self.screen.blit(text, text_rect)