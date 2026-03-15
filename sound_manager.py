"""
مدير الصوت والموسيقى
sound_manager.py
"""

import pygame
import os
import random
from typing import Dict, Optional


class SoundManager:
    """إدارة الأصوات والموسيقى"""
    
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True
        self.volume = 0.7
        
        # تهيئة الميكسر
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # تحميل الأصوات (إذا وجدت)
        self.load_sounds()
    
    def load_sounds(self):
        """تحميل ملفات الصوت"""
        sound_files = {
            "click": "click.wav",
            "order_received": "order.wav",
            "game_start": "start.wav",
            "battle_start": "battle_start.wav",
            "gunshot": "gunshot.wav",
            "explosion": "explosion.wav",
            "victory": "victory.wav",
            "defeat": "defeat.wav",
            "soldier_hurt": "hurt.wav",
            "soldier_die": "die.wav",
            "notification": "notification.wav"
        }
        
        for name, filename in sound_files.items():
            try:
                path = os.path.join("assets", "sounds", "effects", filename)
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.volume)
                    self.sounds[name] = sound
            except:
                pass  # تجاهل الأصوات غير الموجودة
    
    def play_sound(self, sound_name: str):
        """تشغيل مؤثر صوتي"""
        if not self.sound_enabled:
            return
        
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            # إنشاء صوت افتراضي إذا لم يوجد
            self.create_default_sound(sound_name)
    
    def create_default_sound(self, sound_name: str):
        """إنشاء صوت افتراضي (beep)"""
        try:
            import array
            import math
            
            sample_rate = 22050
            duration = 0.1
            
            # إنشاء موجة جيبية بسيطة
            samples = []
            for i in range(int(sample_rate * duration)):
                value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
                samples.append(value)
            
            sound_array = array.array('h', samples)
            sound = pygame.sndarray.make_sound(sound_array)
            sound.set_volume(self.volume)
            self.sounds[sound_name] = sound
            sound.play()
        except:
            pass  # تجاهل إذا فشل
    
    def play_music(self, music_name: str, loop: bool = True):
        """تشغيل موسيقى خلفية"""
        if not self.music_enabled:
            return
        
        try:
            path = os.path.join("assets", "sounds", "music", f"{music_name}.mp3")
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.music_playing = True
            else:
                # موسيقى افتراضية بسيطة
                self.create_default_music()
        except:
            pass
    
    def create_default_music(self):
        """إنشاء موسيقى افتراضية بسيطة"""
        try:
            import array
            import math
            
            sample_rate = 22050
            duration = 2.0
            
            samples = []
            for i in range(int(sample_rate * duration)):
                # نغمة بسيطة تتغير
                freq = 220 + 20 * math.sin(2.0 * math.pi * 0.5 * i / sample_rate)
                value = int(16384.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                samples.append(value)
            
            sound_array = array.array('h', samples)
            sound = pygame.sndarray.make_sound(sound_array)
            sound.set_volume(self.volume * 0.3)
            
            # تشغيل في حلقة
            self.sounds["default_music"] = sound
            sound.play(-1)
            self.music_playing = True
        except:
            pass
    
    def stop_music(self):
        """إيقاف الموسيقى"""
        pygame.mixer.music.stop()
        self.music_playing = False
    
    def set_volume(self, volume: float):
        """تغيير مستوى الصوت"""
        self.volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            try:
                sound.set_volume(self.volume)
            except:
                pass
        
        pygame.mixer.music.set_volume(self.volume)
    
    def toggle_sound(self):
        """تشغيل/إيقاف المؤثرات الصوتية"""
        self.sound_enabled = not self.sound_enabled
    
    def toggle_music(self):
        """تشغيل/إيقاف الموسيقى"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_music("background")
        else:
            self.stop_music()