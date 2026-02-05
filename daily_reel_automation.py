#!/usr/bin/env python3
"""
Daily Salford Reel Automation - Free Version
使用免費服務：Google Gemini AI
"""

import os
import sys
from datetime import datetime
import google.generativeai as genai
from reel_video_generator import ReelVideoGenerator

# Configuration
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Salford topics for daily content
SALFORD_TOPICS = [
    "Salford Quays history and transformation",
    "MediaCityUK and the BBC",
    "The Lowry Theatre and arts scene",
    "Salford's industrial heritage",
    "Ordsall Hall and historic buildings",
    "Salford shopping at the Lowry Outlet",
    "University of Salford innovation",
    "Salford parks and green spaces",
    "Local Salford food and restaurants",
    "Salford Lads Club history",
    "Chapel Street regeneration",
    "Salford Red Devils rugby",
    "Imperial War Museum North",
    "Salford community and culture",
    "Hidden gems in Salford"
]

def generate_salford_story(topic):
    """Generate Salford story using Google Gemini (FREE)"""
    print(f"\n🤖 Generating story with Google Gemini...")
    print(f"📌 Topic: {topic}")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""Create a short, engaging 30-second Instagram Reel script about {topic}.

Requirements:
- Write in British English
- 60-80 words maximum (for 30 seconds of speech)
- Start with a hook question or surprising fact
- Include specific details about Salford
- End with a call-to-action or interesting point
- Write in a casual, conversational tone
- Use simple, clear sentences
- Focus on one main idea

Format: Write only the narration text, no headings or extra formatting."""

    try:
        response = model.generate_content(prompt)
        story = response.text.strip()
        
        # Validate length
        word_count = len(story.split())
        print(f"✅ Story generated: {word_count} words")
        
        if word_count > 100:
            print("⚠️  Story too long, truncating...")
            words = story.split()[:80]
            story = ' '.join(words) + '...'
        
        return story
        
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        raise

def get_search_query(topic):
    """Generate Pexels search query from topic"""
    # Extract key terms for video search
    if "Quays" in topic:
        return "salford quays modern architecture waterfront"
    elif "MediaCityUK" in topic or "BBC" in topic:
        return "modern office building media technology"
    elif "Lowry" in topic:
        return "modern theatre art gallery"
    elif "industrial" in topic:
        return "industrial heritage factory brick building"
    elif "Ordsall Hall" in topic:
        return "historic english manor house"
    elif "shopping" in topic:
        return "modern shopping mall retail"
    elif "University" in topic:
        return "university campus students learning"
    elif "park" in topic or "green" in topic:
        return "urban park green space nature"
    elif "food" in topic or "restaurant" in topic:
        return "restaurant dining food british"
    elif "Lads Club" in topic:
        return "community center youth club"
    elif "Chapel Street" in topic:
        return "urban street modern development"
    elif "rugby" in topic:
        return "rugby match sports stadium"
    elif "War Museum" in topic:
        return "museum exhibition history"
    else:
        return "salford city modern urban"

def main():
    """Main automation workflow"""
    print("=" * 50)
    print("🎬 Daily Salford Reel Automation (FREE VERSION)")
    print("=" * 50)
    
    # Check environment variables
    if not PEXELS_API_KEY:
        print("❌ Error: PEXELS_API_KEY not found")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found")
        sys.exit(1)
    
    print(f"✅ API keys loaded")
    
    # Select today's topic (rotate based on day of month)
    day_of_month = datetime.now().day
    topic_index = day_of_month % len(SALFORD_TOPICS)
    today_topic = SALFORD_TOPICS[topic_index]
    
    print(f"\n📅 Today's topic: {today_topic}")
    
    try:
        # 1. Generate story using Gemini
        story_text = generate_salford_story(today_topic)
        print(f"\n📖 Story preview:")
        print("-" * 50)
        print(story_text)
        print("-" * 50)
        
        # 2. Generate search query
        search_query = get_search_query(today_topic)
        print(f"\n🔍 Video search query: {search_query}")
        
        # 3. Generate video
        generator = ReelVideoGenerator(PEXELS_API_KEY)
        
        # Create filename with date
        date_str = datetime.now().strftime("%Y%m%d")
        output_filename = f"salford_reel_{date_str}.mp4"
        
        output_path = generator.generate_reel(
            story_text=story_text,
            search_query=search_query,
            output_filename=output_filename
        )
        
        print("\n" + "=" * 50)
        print("✅ AUTOMATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"📹 Video: {output_path}")
        print(f"📊 Topic: {today_topic}")
        print(f"📝 Story: {len(story_text.split())} words")
        print("\n🎉 Ready to upload to Instagram/Facebook!")
        
        return output_path
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ AUTOMATION FAILED")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
