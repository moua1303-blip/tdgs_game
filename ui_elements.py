"""
عناصر الواجهة الرسومية
ui_elements.py
"""

import pygame
import time
from typing import Callable, Optional


class Button:
    """زر تفاعلي"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, font: pygame.font.Font, color: tuple,
                 action: Callable, hover_color: tuple = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.normal_color = color
        self.hover_color = hover_color or self.lighten_color(color)
        self.action = action
        self.is_hovered = False
        self.clicked = False
        
    def lighten_color(self, color: tuple) -> tuple:
        """تفتيح اللون"""
        return tuple(min(255, c + 40) for c in color)
    
    def draw(self, screen: pygame.Surface):
        """رسم الزر"""
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # لون الخلفية
        color = self.hover_color if self.is_hovered else self.normal_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        
        # إطار
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=10)
        
        # النص
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """التحقق من النقر على الزر"""
        return self.rect.collidepoint(mouse_pos)


class TextBox:
    """مربع نص"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 font: pygame.font.Font, bg_color: tuple = (30, 30, 40),
                 text_color: tuple = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event: pygame.event.Event):
        """معالجة أحداث الإدخال"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    
    def draw(self, screen: pygame.Surface):
        """رسم مربع النص"""
        # خلفية
        color = (60, 60, 80) if self.active else self.bg_color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=5)
        
        # النص
        text_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # مؤشر الكتابة
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer % 60 < 30:
                cursor_x = self.rect.x + 10 + text_surface.get_width()
                pygame.draw.line(screen, self.text_color,
                               (cursor_x, self.rect.y + 10),
                               (cursor_x, self.rect.y + self.rect.height - 10), 2)


class ProgressBar:
    """شريط تقدم"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: int = 0, max_value: int = 100,
                 bg_color: tuple = (50, 50, 50),
                 fill_color: tuple = (0, 255, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = max_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        
    def set_value(self, value: int):
        """تحديث القيمة"""
        self.value = max(self.min_value, min(self.max_value, value))
    
    def get_percentage(self) -> float:
        """الحصول على النسبة المئوية"""
        return (self.value - self.min_value) / (self.max_value - self.min_value)
    
    def draw(self, screen: pygame.Surface):
        """رسم شريط التقدم"""
        # الخلفية
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=5)
        
        # التعبئة
        fill_width = int(self.rect.width * self.get_percentage())
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(screen, self.fill_color, fill_rect, border_radius=5)


class Notification:
    """إشعار منبثق"""
    
    def __init__(self, text: str, font: pygame.font.Font,
                 color: tuple, x: int, y: int, duration: int = 3):
        self.text = text
        self.font = font
        self.color = color
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = time.time()
        self.alpha = 255
        
    def update(self):
        """تحديث الإشعار"""
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            self.alpha = max(0, 255 - int((elapsed - self.duration) * 500))
    
    def is_expired(self) -> bool:
        """التحقق من انتهاء الإشعار"""
        return self.alpha <= 0
    
    def draw(self, screen: pygame.Surface):
        """رسم الإشعار"""
        if self.alpha <= 0:
            return
        
        # نص مع شفافية
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        
        # خلفية شفافة
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        bg_rect = text_rect.inflate(20, 10)
        
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, min(200, self.alpha)))
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(text_surface, text_rect)


class Dropdown:
    """قائمة منسدلة"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 options: list, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selected = options[0] if options else None
        self.expanded = False
        
    def handle_event(self, event: pygame.event.Event):
        """معالجة الأحداث"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
            elif self.expanded:
                # التحقق من النقر على الخيارات
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x, self.rect.y + (i + 1) * self.rect.height,
                        self.rect.width, self.rect.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.selected = option
                        self.expanded = False
                        break
    
    def draw(self, screen: pygame.Surface):
        """رسم القائمة"""
        # الزر الرئيسي
        pygame.draw.rect(screen, (60, 60, 80), self.rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=5)
        
        text = self.font.render(str(self.selected), True, (255, 255, 255))
        screen.blit(text, (self.rect.x + 10, self.rect.y + 10))
        
        # سهم
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ]
        if self.expanded:
            arrow_points = [(p[0], p[1] - 10) for p in arrow_points]
        
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)
        
        # الخيارات المنسدلة
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x, self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width, self.rect.height
                )
                pygame.draw.rect(screen, (80, 80, 100), option_rect, border_radius=5)
                pygame.draw.rect(screen, (200, 200, 200), option_rect, 2, border_radius=5)
                
                option_text = self.font.render(str(option), True, (255, 255, 255))
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 10))