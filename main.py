#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
قائد الكتيبة - النسخة الرسومية
الملف الرئيسي للتشغيل
"""

import sys
import os

# إضافة المجلد الحالي إلى path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pygame_main import PygameGame
from utils import logger

def main():
    """الدالة الرئيسية"""
    try:
        logger.info("🎮 بدء تشغيل النسخة الرسومية")
        game = PygameGame()
        game.run()
        
    except KeyboardInterrupt:
        print("\n\n👋  تم إنهاء اللعبة. مع السلامة!")
        logger.info("تم إنهاء اللعبة بواسطة المستخدم")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")
        logger.error(f"خطأ غير متوقع: {e}", exc_info=True)
        print("الرجاء إعادة تشغيل اللعبة.")
        sys.exit(1)

if __name__ == "__main__":
    main()