import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Dict, Optional

# ============== دالة Clamp ==============
def clamp(value: int, min_val: int = 0, max_val: int = 100) -> int:
    """تقييد قيمة بين حدين"""
    return max(min_val, min(max_val, value))

# ============== نظام Logging ==============
def setup_logging():
    """إعداد نظام تسجيل الأحداث"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f'game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# ============== نظام Save/Load ==============
class GameSaver:
    """حفظ وتحميل اللعبة"""
    
    SAVE_DIR = "saves"
    
    @classmethod
    def ensure_save_dir(cls):
        """التأكد من وجود مجلد الحفظ"""
        if not os.path.exists(cls.SAVE_DIR):
            os.makedirs(cls.SAVE_DIR)
    
    @classmethod
    def save_game(cls, game_state: Dict[str, Any], slot: int = 1) -> bool:
        """حفظ حالة اللعبة"""
        try:
            cls.ensure_save_dir()
            
            filename = f"{cls.SAVE_DIR}/save_{slot}.json"
            
            # تحويل البيانات إلى JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ تم حفظ اللعبة في slot {slot}")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل حفظ اللعبة: {e}")
            return False
    
    @classmethod
    def load_game(cls, slot: int = 1) -> Optional[Dict[str, Any]]:
        """تحميل لعبة محفوظة"""
        try:
            filename = f"{cls.SAVE_DIR}/save_{slot}.json"
            
            if not os.path.exists(filename):
                logger.warning(f"⚠️ لا يوجد حفظ في slot {slot}")
                return None
                
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.info(f"✅ تم تحميل اللعبة من slot {slot}")
            return data
            
        except Exception as e:
            logger.error(f"❌ فشل تحميل اللعبة: {e}")
            return None
    
    @classmethod
    def list_saves(cls) -> list:
        """عرض قائمة الحفظات"""
        cls.ensure_save_dir()
        saves = []
        
        for file in os.listdir(cls.SAVE_DIR):
            if file.endswith('.json'):
                slot = file.replace('save_', '').replace('.json', '')
                saves.append({
                    'slot': slot,
                    'file': file,
                    'modified': os.path.getmtime(os.path.join(cls.SAVE_DIR, file))
                })
                
        return saves

# ============== أدوات أخرى ==============
def weighted_choice(choices: Dict[str, int]) -> str:
    """اختيار عشوائي مع أوزان"""
    total = sum(choices.values())
    r = random.randint(1, total)
    
    upto = 0
    for choice, weight in choices.items():
        upto += weight
        if upto >= r:
            return choice
    
    return list(choices.keys())[0]

def format_time(seconds: int) -> str:
    """تنسيق الوقت"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"