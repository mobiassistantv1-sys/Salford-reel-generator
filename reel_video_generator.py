#!/usr/bin/env python3
"""
Salford Reel Video Generator - Free Version
使用免費服務：gTTS (Google Text-to-Speech)
"""

import os
import requests
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.all import speedx
import tempfile
from pathlib import Path

class ReelVideoGenerator:
    def __init__(self, pexels_api_key):
        self.pexels_api_key = pexels_api_key
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def search_pexels_video(self, query, duration_min=15):
        """Search for video on Pexels"""
        print(f"🔍 Searching Pexels for: {query}")
        
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "per_page": 10,
            "orientation": "portrait"
        }
        
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Pexels API error: {response.status_code}")
        
        videos = response.json().get("videos", [])
        
        # Find video with suitable duration
        for video in videos:
            for file in video.get("video_files", []):
                if file.get("height", 0) >= 720:  # HD quality
                    return file["link"]
        
        # Fallback to first available
        if videos and videos[0].get("video_files"):
            return videos[0]["video_files"][0]["link"]
        
        raise Exception("No suitable video found on Pexels")
    
    def download_video(self, url, output_path):
        """Download video from URL"""
        print(f"⬇️  Downloading video...")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Video downloaded: {output_path}")
        return output_path
    
    def generate_voiceover(self, text, output_path):
        """Generate voiceover using gTTS (FREE)"""
        print(f"🎤 Generating voiceover with gTTS...")
        
        try:
            # Use gTTS with English UK accent
            tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
            tts.save(output_path)
            
            print(f"✅ Voiceover generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ gTTS error: {e}")
            raise
    
    def create_subtitles(self, text, video_duration, video_size):
        """Create subtitle clips"""
        print(f"📝 Creating subtitles...")
        
        # Split text into sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        # Calculate timing
        time_per_sentence = video_duration / len(sentences)
        subtitle_clips = []
        
        for i, sentence in enumerate(sentences):
            if not sentence:
                continue
                
            start_time = i * time_per_sentence
            
            # Create text clip
            txt_clip = TextClip(
                sentence,
                fontsize=40,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(video_size[0] - 40, None),
                align='center'
            )
            
            txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(start_time).set_duration(time_per_sentence)
            subtitle_clips.append(txt_clip)
        
        print(f"✅ Created {len(subtitle_clips)} subtitle clips")
        return subtitle_clips
    
    def generate_reel(self, story_text, search_query, output_filename="salford_reel.mp4"):
        """Generate complete reel video"""
        print("\n🎬 Starting Reel generation...")
        print(f"📖 Story: {story_text[:100]}...")
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 1. Generate voiceover (FREE with gTTS)
            audio_path = os.path.join(temp_dir, "voiceover.mp3")
            self.generate_voiceover(story_text, audio_path)
            
            # 2. Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            target_duration = audio_clip.duration
            
            print(f"⏱️  Target duration: {target_duration:.1f}s")
            
            # 3. Search and download background video
            video_url = self.search_pexels_video(search_query)
            video_path = os.path.join(temp_dir, "background.mp4")
            self.download_video(video_url, video_path)
            
            # 4. Load and process video
            print(f"🎥 Processing video...")
            video_clip = VideoFileClip(video_path)
            
            # Adjust video duration to match audio
            if video_clip.duration < target_duration:
                # Loop video if too short
                n_loops = int(target_duration / video_clip.duration) + 1
                video_clip = video_clip.loop(n=n_loops)
            
            video_clip = video_clip.subclip(0, target_duration)
            
            # 5. Create subtitles
            subtitle_clips = self.create_subtitles(
                story_text,
                target_duration,
                video_clip.size
            )
            
            # 6. Compose final video
            print(f"🎬 Composing final video...")
            
            if subtitle_clips:
                final_video = CompositeVideoClip([video_clip] + subtitle_clips)
            else:
                final_video = video_clip
            
            final_video = final_video.set_audio(audio_clip)
            
            # 7. Export
            output_path = self.output_dir / output_filename
            print(f"💾 Exporting to: {output_path}")
            
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                threads=4
            )
            
            # Cleanup
            video_clip.close()
            audio_clip.close()
            final_video.close()
            
            print(f"\n✅ Reel generated successfully: {output_path}")
            print(f"📊 Duration: {target_duration:.1f}s")
            print(f"📦 File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return str(output_path)
            
        except Exception as e:
            print(f"\n❌ Error generating reel: {e}")
            raise
        
        finally:
            # Cleanup temp files
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

def main():
    """Test function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reel_video_generator.py <pexels_api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Test story
    test_story = "Welcome to Salford! Did you know that Salford Quays was once one of the busiest docks in the world? Today it's home to MediaCityUK and the stunning Lowry Theatre. A perfect blend of industrial heritage and modern culture!"
    
    generator = ReelVideoGenerator(api_key)
    output_file = generator.generate_reel(
        story_text=test_story,
        search_query="salford quays modern city",
        output_filename="test_salford_reel.mp4"
    )
    
    print(f"\n🎉 Test completed! Video saved to: {output_file}")

if __name__ == "__main__":
    main()
