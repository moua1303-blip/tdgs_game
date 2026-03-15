import random
from typing import List, Dict, Tuple, Optional
from enums import Location
from utils import clamp, logger

class GameMap:
    """نظام الخريطة والتنقل"""
    
    def __init__(self):
        self.locations = {
            Location.BASE: {
                'name': 'القاعدة',
                'connections': [Location.VALLEY, Location.FOREST],
                'description': 'موقعكم الرئيسي، آمن نسبياً',
                'enemies': 0
            },
            Location.VALLEY: {
                'name': 'الوادي',
                'connections': [Location.BASE, Location.ENEMY_CAMP, Location.MOUNTAINS],
                'description': 'منطقة مكشوفة، خطر كبير',
                'enemies': random.randint(30, 70)
            },
            Location.FOREST: {
                'name': 'الغابة',
                'connections': [Location.BASE, Location.MOUNTAINS],
                'description': 'غطاء طبيعي ممتاز، صعوبة في الرؤية',
                'enemies': random.randint(10, 40)
            },
            Location.MOUNTAINS: {
                'name': 'الجبال',
                'connections': [Location.VALLEY, Location.FOREST, Location.ENEMY_CAMP],
                'description': 'ارتفاع عالٍ، موقع استراتيجي للقناصة',
                'enemies': random.randint(20, 50)
            },
            Location.ENEMY_CAMP: {
                'name': 'معسكر العدو',
                'connections': [Location.VALLEY, Location.MOUNTAINS],
                'description': 'قلب الخطر، عمليات إنقاذ صعبة',
                'enemies': random.randint(80, 100)
            }
        }
        
        self.current_location = Location.BASE
        self.visited_locations = {Location.BASE}
        
    def show_map(self) -> str:
        """عرض الخريطة بشكل نصي"""
        
        lines = []
        lines.append("\n" + "🗺️ " * 15)
        lines.append("                    خريطة المنطقة")
        lines.append("🗺️ " * 15)
        
        # خريطة ASCII
        map_art = """
        
                    [🏔️ الجبال]
                    ⬋        ⬊
        [🌳 الغابة]           [⚠️ العدو]
            ⬋                    ⬋
            [🏠 القاعدة]----[⛰️ الوادي]
            
        """
        lines.append(map_art)
        
        lines.append(f"\n📍 موقعك الحالي: {self.locations[self.current_location]['name']}")
        lines.append(f"📝 {self.locations[self.current_location]['description']}")
        lines.append(f"⚠️  تواجد العدو: {self.locations[self.current_location]['enemies']}%")
        
        return '\n'.join(lines)
    
    def get_available_moves(self) -> List[Tuple[Location, str]]:
        """الحصول على الأماكن المتاحة للانتقال"""
        moves = []
        current = self.locations[self.current_location]
        
        for loc in current['connections']:
            moves.append((loc, self.locations[loc]['name']))
        
        return moves
    
    def move_to(self, location: Location) -> Tuple[bool, str]:
        """الانتقال إلى موقع جديد"""
        
        if location not in self.locations[self.current_location]['connections']:
            return False, "لا يمكنك الوصول إلى هناك مباشرة"
        
        self.current_location = location
        self.visited_locations.add(location)
        
        logger.info(f"انتقلت إلى {self.locations[location]['name']}")
        
        return True, f"انتقلت إلى {self.locations[location]['name']}"
    
    def get_location_info(self, location: Location = None) -> dict:
        """الحصول على معلومات الموقع"""
        if location is None:
            location = self.current_location
        
        return self.locations[location]
    
    def update_enemy_presence(self):
        """تحديث تواجد العدو في المواقع"""
        for loc in Location:
            if loc != Location.BASE:
                # تغير عشوائي
                change = random.randint(-10, 10)
                self.locations[loc]['enemies'] = clamp(
                    self.locations[loc]['enemies'] + change,
                    0, 100
                )