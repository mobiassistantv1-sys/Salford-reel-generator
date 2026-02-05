#!/usr/bin/env python3
"""
Instagram Reel 影片生成器
整合 Salford Content Generator + Edge TTS + MoviePy

功能：
1. 生成 Salford 主題故事內容
2. 文字轉語音（廣東話/英文）
3. 從 Pexels 獲取背景影片
4. 組合成 Instagram Reels 格式影片
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, Optional, List
import tempfile

# 需要安裝的套件
try:
    import edge_tts
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ImageClip
    )
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print(f"⚠️  缺少必要套件: {e}")
    print("請執行: pip install edge-tts moviepy pillow requests")
    exit(1)


class ReelVideoGenerator:
    """Reel 影片生成器"""
    
    def __init__(
        self,
        output_dir: str = "videos/reels",
        language: str = "en-US",  # en-US, en-GB, yue-CN (廣東話)
        video_duration: int = 30,  # 秒
        pexels_api_key: Optional[str] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.language = language
        self.video_duration = video_duration
        
        # Pexels API Key (預設值已內置)
        self.pexels_api_key = pexels_api_key or "jGfFPRv1pDf617NAP4UIhITmFVX987cCP2rCssvkSGwEuL9mMcp7I5Hx"
        
        # TTS 語音選擇
        self.tts_voices = {
            'en-US': 'en-US-AriaNeural',  # 美式英語女聲
            'en-GB': 'en-GB-SoniaNeural',  # 英式英語女聲
            'yue-CN': 'zh-HK-HiuMaanNeural',  # 廣東話女聲
        }
        
    async def generate_tts(self, text: str, output_path: str) -> str:
        """生成 TTS 語音檔案"""
        voice = self.tts_voices.get(self.language, 'en-US-AriaNeural')
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        print(f"✅ TTS 生成完成: {output_path}")
        return output_path
    
    def search_pexels_videos(self, query: str, per_page: int = 5) -> List[Dict]:
        """從 Pexels 搜尋影片"""
        if not self.pexels_api_key:
            print("⚠️  未設定 PEXELS_API_KEY，使用預設背景")
            return []
        
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": "portrait",  # 豎屏格式
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for video in data.get('videos', []):
                # 選擇 HD 版本
                video_files = video.get('video_files', [])
                hd_file = next(
                    (f for f in video_files if f.get('quality') == 'hd' and f.get('width', 0) <= 1080),
                    video_files[0] if video_files else None
                )
                
                if hd_file:
                    videos.append({
                        'url': hd_file['link'],
                        'width': hd_file.get('width'),
                        'height': hd_file.get('height'),
                        'duration': video.get('duration', 10)
                    })
            
            print(f"✅ 從 Pexels 找到 {len(videos)} 條影片")
            return videos
            
        except Exception as e:
            print(f"⚠️  Pexels API 錯誤: {e}")
            return []
    
    def download_video(self, url: str, output_path: str) -> str:
        """下載影片"""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ 影片下載完成: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 影片下載失敗: {e}")
            return None
    
    def create_text_clip(
        self,
        text: str,
        duration: float,
        position: str = 'center',
        fontsize: int = 60,
        color: str = 'white'
    ) -> TextClip:
        """創建文字片段"""
        return TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(900, None),  # 寬度固定，高度自適應
        ).set_duration(duration).set_position(position)
    
    def create_solid_background(self, duration: float, size: tuple = (1080, 1920), color: tuple = (30, 30, 30)) -> ImageClip:
        """創建純色背景"""
        img = Image.new('RGB', size, color)
        return ImageClip(img).set_duration(duration)
    
    def generate_video(
        self,
        story_data: Dict,
        background_query: Optional[str] = None
    ) -> str:
        """生成完整的 Reel 影片"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"reel_{timestamp}.mp4"
        output_path = self.output_dir / output_filename
        
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # 1. 生成 TTS 語音
            print("\n🎙️  步驟 1/4: 生成 AI 配音...")
            story_text = story_data.get('story', story_data.get('content', ''))
            audio_path = temp_dir / "audio.mp3"
            
            # 執行 async TTS
            asyncio.run(self.generate_tts(story_text, str(audio_path)))
            
            audio_clip = AudioFileClip(str(audio_path))
            actual_duration = min(audio_clip.duration + 3, self.video_duration)  # 加 3 秒片頭片尾
            
            # 2. 準備背景影片
            print("\n🎬 步驟 2/4: 準備背景影片...")
            background_clip = None
            
            if background_query and self.pexels_api_key:
                videos = self.search_pexels_videos(background_query)
                if videos:
                    video_url = videos[0]['url']
                    video_path = temp_dir / "background.mp4"
                    
                    if self.download_video(video_url, str(video_path)):
                        bg_video = VideoFileClip(str(video_path))
                        
                        # 調整為豎屏 9:16
                        bg_video = bg_video.resize(height=1920)
                        if bg_video.w > 1080:
                            bg_video = bg_video.crop(
                                x1=(bg_video.w - 1080) // 2,
                                width=1080
                            )
                        
                        # 循環播放以匹配音頻長度
                        if bg_video.duration < actual_duration:
                            loops = int(actual_duration / bg_video.duration) + 1
                            bg_video = concatenate_videoclips([bg_video] * loops)
                        
                        background_clip = bg_video.subclip(0, actual_duration)
            
            # 如果沒有背景影片，使用純色背景
            if background_clip is None:
                print("使用純色背景...")
                background_clip = self.create_solid_background(actual_duration)
            
            # 3. 創建文字疊層
            print("\n📝 步驟 3/4: 添加文字和字幕...")
            
            # 片頭標題（前 3 秒）
            title = story_data.get('title', 'Salford Stories')
            title_clip = self.create_text_clip(
                title,
                duration=3,
                position=('center', 'center'),
                fontsize=70,
                color='white'
            ).fadein(0.5).fadeout(0.5)
            
            # 主要字幕（配合音頻）
            story_lines = story_text.split('. ')  # 簡單分句
            subtitle_clips = []
            
            time_per_line = (actual_duration - 3) / max(len(story_lines), 1)
            
            for i, line in enumerate(story_lines):
                if line.strip():
                    start_time = 3 + (i * time_per_line)
                    subtitle = self.create_text_clip(
                        line.strip() + '.',
                        duration=min(time_per_line, actual_duration - start_time),
                        position=('center', 1600),  # 底部字幕
                        fontsize=50,
                        color='white'
                    ).set_start(start_time).fadein(0.3).fadeout(0.3)
                    
                    subtitle_clips.append(subtitle)
            
            # Hashtags（最後 2 秒）
            hashtags = ' '.join(story_data.get('hashtags', ['#Salford', '#Stories']))
            hashtag_clip = self.create_text_clip(
                hashtags,
                duration=2,
                position=('center', 1700),
                fontsize=35,
                color='lightblue'
            ).set_start(actual_duration - 2)
            
            # 4. 組合影片
            print("\n🎥 步驟 4/4: 組合最終影片...")
            
            final_clips = [background_clip, title_clip] + subtitle_clips + [hashtag_clip]
            
            final_video = CompositeVideoClip(final_clips, size=(1080, 1920))
            final_video = final_video.set_audio(audio_clip)
            
            # 輸出影片
            final_video.write_videofile(
                str(output_path),
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(temp_dir / 'temp-audio.m4a'),
                remove_temp=True,
                preset='medium',
                threads=4
            )
            
            # 清理
            audio_clip.close()
            background_clip.close()
            final_video.close()
            
            print(f"\n✅ 影片生成成功！")
            print(f"📁 檔案位置: {output_path}")
            print(f"⏱️  影片長度: {actual_duration:.1f} 秒")
            
            return str(output_path)
            
        except Exception as e:
            print(f"\n❌ 影片生成失敗: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # 清理臨時檔案
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


def test_generate_sample_reel():
    """測試生成範例 Reel"""
    
    # 範例故事數據
    sample_story = {
        'title': 'The Ghost of Peel Park',
        'story': 'Legend says that on foggy nights, a mysterious figure walks through Peel Park in Salford. Locals claim it is the spirit of a Victorian gentleman who once owned the land. Many have reported hearing footsteps and seeing shadows near the old gates. Whether you believe it or not, Peel Park holds many secrets.',
        'hashtags': ['#Salford', '#UrbanLegend', '#PeelPark', '#GhostStory', '#Manchester']
    }
    
    print("🎬 開始生成測試 Reel...")
    print(f"📖 故事: {sample_story['title']}")
    
    generator = ReelVideoGenerator(
        language='en-GB',  # 英式英語
        video_duration=30,
        pexels_api_key=os.getenv('PEXELS_API_KEY')  # 可選
    )
    
    video_path = generator.generate_video(
        sample_story,
        background_query='salford city night fog'
    )
    
    if video_path:
        print(f"\n🎉 測試完成！影片已保存到: {video_path}")
    else:
        print("\n❌ 測試失敗")


if __name__ == '__main__':
    test_generate_sample_reel()
