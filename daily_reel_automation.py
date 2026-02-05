#!/usr/bin/env python3
"""
每日自動生成 Salford Reel 影片
整合內容生成 + 影片製作
"""

import os
import sys
from datetime import datetime
from reel_video_generator import ReelVideoGenerator

# Salford 主題故事庫
SALFORD_TOPICS = [
    {
        "query": "salford quays",
        "themes": ["urban development", "waterfront", "modern architecture"]
    },
    {
        "query": "salford history",
        "themes": ["industrial heritage", "victorian era", "working class history"]
    },
    {
        "query": "salford park",
        "themes": ["green spaces", "community", "nature"]
    },
    {
        "query": "salford night",
        "themes": ["urban legends", "ghost stories", "mysterious events"]
    },
    {
        "query": "salford street",
        "themes": ["local culture", "street art", "community life"]
    }
]

# 故事模板
STORY_TEMPLATES = [
    {
        "title": "The Ghost of Peel Park",
        "story": "Legend says that on foggy nights, a mysterious figure walks through Peel Park in Salford. Locals claim it is the spirit of a Victorian gentleman who once owned the land. Many have reported hearing footsteps and seeing shadows near the old gates. Whether you believe it or not, Peel Park holds many secrets.",
        "background_query": "park fog night mysterious",
        "hashtags": ["#Salford", "#UrbanLegend", "#PeelPark", "#GhostStory", "#Manchester"]
    },
    {
        "title": "Salford Quays Transformation",
        "story": "Once an industrial wasteland, Salford Quays has transformed into a vibrant cultural hub. From old docks to modern architecture, this area tells the story of regeneration. The BBC, Imperial War Museum, and The Lowry now call this place home. It is a testament to how cities can reinvent themselves.",
        "background_query": "salford quays modern architecture water",
        "hashtags": ["#SalfordQuays", "#UrbanTransformation", "#ModernCity", "#Architecture", "#Manchester"]
    },
    {
        "title": "Hidden Gardens of Salford",
        "story": "Tucked away from the busy streets, Salford has secret gardens waiting to be discovered. From community allotments to Victorian-era parks, these green spaces offer peace and tranquility. They are the lungs of the city, cherished by locals who know where to find them. Next time you visit, take a moment to explore.",
        "background_query": "garden nature green peaceful",
        "hashtags": ["#Salford", "#HiddenGems", "#UrbanGarden", "#Nature", "#CommunitySpaces"]
    },
    {
        "title": "Salford's Industrial Heritage",
        "story": "Salford was once the heart of the Industrial Revolution. Cotton mills, factories, and warehouses powered Britain's economy. The working-class spirit of this city shaped history. Today, old red brick buildings stand as monuments to that era. Walking through Salford is like stepping back in time.",
        "background_query": "industrial brick building heritage",
        "hashtags": ["#Salford", "#IndustrialHeritage", "#History", "#Manchester", "#WorkingClass"]
    },
    {
        "title": "The Lowry: Art Meets Community",
        "story": "Named after artist L.S. Lowry, The Lowry arts centre celebrates creativity and culture. It is more than just a venue. It is a gathering place for theatre, exhibitions, and performances. Thousands visit every year to experience world-class art. Salford's cultural heartbeat can be felt here.",
        "background_query": "art gallery modern theatre lights",
        "hashtags": ["#TheLowry", "#Salford", "#Arts", "#Culture", "#Theatre"]
    },
    {
        "title": "Ordsall Hall's Dark Past",
        "story": "Ordsall Hall is one of Salford's oldest buildings, dating back to medieval times. Rumours of hauntings and ghostly sightings have persisted for centuries. Visitors report cold spots, unexplained noises, and shadowy figures. Some say the spirits of former residents still roam the halls. Would you dare visit at night?",
        "background_query": "old mansion historic building dark",
        "hashtags": ["#OrdsallHall", "#Salford", "#Haunted", "#History", "#GhostStories"]
    },
    {
        "title": "Street Art Revolution",
        "story": "Salford's streets are canvases for talented artists. Vibrant murals tell stories of identity, struggle, and hope. From large-scale graffiti to hidden stencil art, creativity is everywhere. This urban art movement gives voice to the community. Salford is not just a city. It is a living gallery.",
        "background_query": "street art mural graffiti colorful",
        "hashtags": ["#StreetArt", "#Salford", "#UrbanArt", "#Graffiti", "#Community"]
    },
    {
        "title": "The Chapel Street Revival",
        "story": "Chapel Street was once Salford's main shopping district, bustling with life. Over the years, it fell into decline. But now, a revival is underway. New businesses, cafes, and cultural spaces are breathing life back into the area. The spirit of Chapel Street is returning, stronger than ever.",
        "background_query": "urban street revival shops lights",
        "hashtags": ["#ChapelStreet", "#Salford", "#UrbanRevival", "#Community", "#LocalBusiness"]
    }
]


def select_daily_story():
    """根據日期選擇今日故事"""
    day_of_year = datetime.now().timetuple().tm_yday
    story_index = day_of_year % len(STORY_TEMPLATES)
    return STORY_TEMPLATES[story_index]


def main():
    """主程式：生成今日 Reel"""
    
    print("=" * 60)
    print("📅 每日 Salford Reel 自動生成系統")
    print("=" * 60)
    print(f"⏰ 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 選擇今日故事
    story = select_daily_story()
    
    print(f"📖 今日主題: {story['title']}")
    print(f"🎬 背景搜尋: {story['background_query']}")
    print()
    
    # 初始化影片生成器
    generator = ReelVideoGenerator(
        output_dir="videos/reels",
        language="en-GB",  # 英式英語
        video_duration=30,
        pexels_api_key=os.getenv('PEXELS_API_KEY')
    )
    
    # 生成影片
    print("🎬 開始生成影片...\n")
    
    video_path = generator.generate_video(
        story_data=story,
        background_query=story['background_query']
    )
    
    if video_path:
        print("\n" + "=" * 60)
        print("✅ 每日 Reel 生成成功！")
        print("=" * 60)
        print(f"📁 檔案: {video_path}")
        print(f"📝 標題: {story['title']}")
        print(f"🏷️  Hashtags: {' '.join(story['hashtags'])}")
        print()
        print("💡 下一步:")
        print("   1. 檢查影片質量")
        print("   2. 上傳到 Instagram Reels")
        print("   3. 使用建議的 hashtags")
        print("=" * 60)
        
        return 0
    else:
        print("\n❌ 影片生成失敗")
        return 1


if __name__ == '__main__':
    sys.exit(main())
